from django.shortcuts import render, redirect
from django.http import HttpResponse

# Add the following import
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse  # res.send in express
from .models import Application, Note, Photo, Profile, Network_Request # importing our model
from .forms import NoteForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login # this is a function to log in the user
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'jobapptracker'
import boto3 
import uuid 

#sign up
def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

# Define the home view

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

# Application Create Form
class ApplicationCreate(LoginRequiredMixin, CreateView):
    model = Application
    fields = ['name', 'role', 'salary', 'location', 'site']  # this is two underscores
    # This inherited method is called when a
    # valid application form is being submitted

    def form_valid(self, form):
      # Assign the logged in user (self.request.user)
      form.instance.user = self.request.user  # form.instance is the cat
      # Let the CreateView do its job as usual
      return super().form_valid(form)

class ApplicationUpdate(LoginRequiredMixin, UpdateView):
    model = Application
    # we dont want to let anyone change cats name, so lets not include the name in the fields
    fields = ['role', 'salary', 'location', 'site']
    # where's the redirect defined at for a put request?

class ApplicationDelete(LoginRequiredMixin, DeleteView):
    model = Application
    # because our model is redirecting to specific application but we just deleted it
    success_url = '/applications/'

@login_required
def profile(request):
  network_request = Network_Request.objects.filter(to_user=request.user)
  return render(request, 'network/profile.html', {'network_request':network_request})

@login_required
def networks_index(request):
  User = get_user_model()
  users = User.objects.all()
  return render(request, 'network/index.html', {'users': users})


@login_required
def applications_index(request):
    applications = Application.objects.filter(user=request.user)  # using our model to get all the rows in our application table in psql
    #another way: applications = request.user.application_set.all()
    return render(request, 'applications/index.html', {'applications': applications})



@login_required
def applications_detail(request, application_id):
    application = Application.objects.get(id=application_id)
    # create an instance of NoteForm
    note_form = NoteForm()

    return render(request, 'applications/detail.html', {'application': application, 'note_form': note_form})


@login_required
def add_note(request, application_id):
	# create a ModelForm Instance using the data in the request
	form = NoteForm(request.POST)
	# validate
	if form.is_valid():
		# do somestuff
		# creates an instance of note to be put in the database
		# lets not save it yet, commit=False because we didnt add the foreign key
		new_note = form.save(commit=False)
		#look at the note for application field in the Feeding Model
		new_note.application_id = application_id
		new_note.save() # adds the note to the database, and the note be associated with the cat
		# with same id as the argument to the function cat_id


	return redirect('detail', application_id=application_id)

@login_required
def add_photo(request, application_id):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try: 
      s3.upload_fileojb(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      Photo.objects.create(url=url, application_id=application_id)
    except:
      print('We have an error here uploading to S3')
  return redirect('detail', application_id=application_id)

@login_required
def send_network_request(request, profile_id):
  from_user = request.user
  User = get_user_model()
  print(profile_id)
  to_user = User.objects.get(id=profile_id)
  network_request, created = Network_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
  if created:
    return HttpResponse('network request sent')
  else:
    return HttpResponse('network request was already sent')

@login_required
def accept_network_request(request, request_id):
  network_request= Network_Request.objects.get(id=request_id)
  if network_request.to_user == request.user:
    profile = Profile.objects.get(user=network_request.to_user)
    print(f"{profile} and ----------------------------------------------------------------------------------------------------------------------")
    a = Profile.objects.get(user=network_request.to_user).networks.add(network_request.from_user)
    # network_request.to_user.networks.add(network_request.from_user)
    b = Profile.objects.get(user=network_request.from_user).networks.add(network_request.to_user)
    # network_request.from_user.networks.add(network_request.to_user)
    network_request.delete()
    return HttpResponse('network request accepted')
  else:
    return HttpResponse('network request declined')