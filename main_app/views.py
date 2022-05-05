
from django.shortcuts import render, redirect
# CRUD OPERRATIONS##
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView  # Generc datatype
from django.http import HttpResponse  # res.send in express
# importing our model###
from .models import Application, Note, Photo, Profile, Network_Request, Avatar
from .forms import NoteForm  # Rendering Form##
from django.contrib.auth import get_user_model  # getting user model
from django.contrib.auth import login  # this is a function to log in the user
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'jobapptracker'
import boto3 
import uuid 

# sign up
def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else: error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

# Define the home view
def home(request):
    return render(request, 'home.html')

# define about view
def about(request):
    return render(request, 'about.html')

# Application Create Form
class ApplicationCreate(LoginRequiredMixin, CreateView):
    model = Application
    fields = ['name', 'role', 'salary', 'location', 'link','site', 'status', ] #only the fields we want from the model


    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  
        return super().form_valid(form)

# Application update form with only the fields we want users to be able to change
class ApplicationUpdate(LoginRequiredMixin, UpdateView):
    model = Application
    fields = ['role', 'salary', 'location', 'link', 'site', 'status']

# Profile Create Form/ created incase we want users to manually initiate their profile(currently not in use)
class ProfileCreate(LoginRequiredMixin, CreateView):
    model = Profile
    fields = ['name', 'role', 'salary', 'location', 'link','site', 'status', ]

    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)

#Profile update form giving only the fields users can change
class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['name', 'intro', 'title', 'hobbies']
    success_url = '/profile/' # on successful update, redirect to the profile page

# Application comfirmation of delete
class ApplicationDelete(LoginRequiredMixin, DeleteView):
    model = Application
    success_url = '/applications/' # on delete, redirect to all the job applications since the current one is deleted

# This grabs everything that we want to display on the users profile
@login_required
def profile(request):
    User = get_user_model() # we need the user model from django
    profiles = Profile.objects.filter(user=request.user).values("networks") #grabing the networks of the user that is making the request
    networks = [] # creating an empy intance to hold data
    for profile in profiles: #looping through all of the networks grabbed earlier
        profiles = profile['networks'] # from those networks separating the id of them
        network = User.objects.filter(id=profiles).values('username') # finding the user the network id is from and getting the username
        networks.append(network) # appending the username to the empty intance created earlier
    profile = Profile.objects.filter(user=request.user).values("networks") #looking for the same networks but leaving intact
    network_request = Network_Request.objects.filter(to_user=request.user) # finding the network request belonging to the user that made the request
    return render(request, 'network/profile.html', {'network_request': network_request, 'profile': profile, 'networks': networks}) # rendering the profile page and sending over all the data we want to display

#Function to get all the network in the Profile Model
@login_required
def networks_index(request):
    User = get_user_model()
    network_requests = Network_Request.objects.filter(from_user=request.user).values_list('to_user_id', flat = True) #Find all of the network request from the user and send the id of to what user the request was being made to
    users = User.objects.all() #get all users
    networks = Profile.objects.filter(user=request.user).values('networks') #find the networks of the user making the request
    return render(request, 'network/index.html', {'users': users, 'networks': networks, 'network_requests': network_requests}) #send back all of the data to the all networks page

 # Function: Using our model to get all the rows in our application table in psql
@login_required
def applications_index(request):
    applications = Application.objects.filter(user=request.user) #find all job applications belonging to the user
    return render(request, 'applications/index.html', {'applications': applications})


@login_required
def applications_detail(request, application_id):
    application = Application.objects.get(id=application_id) # find the application being requested by the user
    # create an instance of NoteForm
    note_form = NoteForm()
    return render(request, 'applications/detail.html', {'application': application, 'note_form': note_form})

#Function  to allow user add note.
@login_required
def add_note(request, application_id):
    form = NoteForm(request.POST)  # instance of the ModelForm
    if form.is_valid():  # Validate the form
        # Create an instance of the note and save to db
        new_note = form.save(commit=False)
        # Look and match the application Field =[]db model
        new_note.application_id = application_id
        new_note.save()  # Add and save the notes in the database.
    return redirect('detail', application_id=application_id)


###################################################
# Functions ADD Photo, profile and Avattar
################################################
@login_required
def add_photo(request, application_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file: # make sure a file was selected
        s3 = boto3.client('s3') 
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):] #create a unique key for the image
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}" # create the url where image will be stored
            Photo.objects.create(url=url, application_id=application_id) # store it using the model created for photo
        except:
            print(f"{S3_BASE_URL}, {BUCKET} , /{key}")
    return redirect('detail', application_id=application_id)


@login_required
def add_avatar(request, profile_id):
    avatar_file = request.FILES.get('avatar-file', None)
    if avatar_file: # make sure a file was selected
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + avatar_file.name[avatar_file.name.rfind('.'):] #create a unique key for the image
        try:
            s3.upload_fileobj(avatar_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}" # create the url where image will be stored
            Avatar.objects.create(url=url, profile_id=profile_id) # store it using the model created for photo
        except:
            print('We have an error here uploading to S3')
    return redirect('/profile/', profile_id=profile_id)

############################
# FUNCTIONS TO SEND AND REQUEST NETTWORK INVITATIONS
############################
# Function to send user request

@login_required
def send_network_request(request, profile_id):
    from_user = request.user # create an instance of who is sending the request
    User = get_user_model()
    to_user = User.objects.get(id=profile_id) # create an instance holding to who the request is going to
    network_request, created = Network_Request.objects.get_or_create(from_user=from_user, to_user=to_user) # save as the model created 
    if created:
        return redirect('/networks/') # redirect to the same page on success
    else:
        return HttpResponse('network request was already sent') # if able to click it twice let user know it already tried to connect


@login_required
def accept_network_request(request, request_id):
    network_request = Network_Request.objects.get(id=request_id) # find the network requests user has received
    if network_request.to_user == request.user: #make sure user logged in is the user who is receiving the requests
        profile = Profile.objects.get(user=network_request.to_user) # get the right user
        Profile.objects.get(user=network_request.to_user).networks.add(network_request.from_user) #on accept add the user to the networks of the one who accepted it
        Profile.objects.get(user=network_request.from_user).networks.add(network_request.to_user) #on accept add the user to the networks of the one who sent it
        network_request.delete() # delete the request
        return redirect('/profile/') #redirect to the same page
    else:
        return HttpResponse('network request declined')
