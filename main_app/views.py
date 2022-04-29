from django.shortcuts import render, redirect
from django.http import HttpResponse

# Add the following import
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse  # res.send in express
from .models import Application, Note, Photo  # importing our model
from .forms import NoteForm

from django.contrib.auth import login # this is a function to log in the user
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
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
    return render(request, 'about.html')

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
def applications_index(request):
    applications = Application.objects.filter(user=request.user)  # using our model to get all the rows in our application table in psql
    #another way: applications = request.user.application_set.all()
    return render(request, 'applications/index.html', {'applications': applications})


# path('cats/<int:cat_id>/' <- this is where cat_id comes from-
@login_required
def applications_detail(request, application_id):
    application = Application.objects.get(id=application_id)
    # toys_application_doesnt_have = Toy.objects.exclude(id__in = application.toys.all().values_list('id'))
    # create an instance of FeedingForm
    note_form = NoteForm()

    return render(request, 'applications/detail.html', {'application': application, 'note_form': note_form})