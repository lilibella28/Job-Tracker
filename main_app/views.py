
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
        else:
            error_message = 'Invalid sign up - try again'
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
    fields = ['name', 'role', 'salary', 'location', 'link',
              'site', 'status', ] 


    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  
        return super().form_valid(form)


class ApplicationUpdate(LoginRequiredMixin, UpdateView):
    model = Application
    fields = ['role', 'salary', 'location', 'link', 'site', 'status']
    success_url = "/"


class ProfileCreate(LoginRequiredMixin, CreateView):
    model = Profile
    fields = ['name', 'role', 'salary', 'location', 'link',
              'site', 'status', ]  # this is two underscores
    # This inherited method is called when a
    # valid application form is being submitted

    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['name', 'intro', 'title', 'hobbies']
    success_url = '/profile/'

class ApplicationDelete(LoginRequiredMixin, DeleteView):
    model = Application
    success_url = '/applications/' # because our model is redirecting to specific application but we just deleted it


@login_required
def profile(request):
    User = get_user_model()
    profiles = Profile.objects.filter(user=request.user).values("networks")
    networks = []
    for profile in profiles:
        profiles = profile['networks']
        network = User.objects.filter(id=profiles).values('username')
        networks.append(network)
    profile = Profile.objects.filter(user=request.user).values("networks")
    network_request = Network_Request.objects.filter(to_user=request.user)
    return render(request, 'network/profile.html', {'network_request': network_request, 'profile': profile, 'networks': networks})

#Function to get all the network in the Profile Model
@login_required
def networks_index(request):
    User = get_user_model()
    network_requests = Network_Request.objects.filter(
        from_user=request.user).values('to_user_id')
    users = User.objects.all()
    networks = Profile.objects.filter(user=request.user).values('networks')
    for network in networks:
        networks = network['networks']
    for network_request in network_requests:
        network_requests = network_request['to_user_id']
    return render(request, 'network/index.html', {'users': users, 'networks': networks, 'network_requests': network_requests})

 # Function: Using our model to get all the rows in our application table in psql
@login_required
def applications_index(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'applications/index.html', {'applications': applications})


@login_required
def applications_detail(request, application_id):
    application = Application.objects.get(id=application_id)
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
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + \
            photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            Photo.objects.create(url=url, application_id=application_id)
        except:
            print(f"{S3_BASE_URL}, {BUCKET} , /{key}")
    return redirect('detail', application_id=application_id)


@login_required
def add_avatar(request, profile_id):
    avatar_file = request.FILES.get('avatar-file', None)
    if avatar_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + \
            avatar_file.name[avatar_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(avatar_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            Avatar.objects.create(url=url, profile_id=profile_id)
        except:
            print('We have an error here uploading to S3')
    return redirect('/profile/', profile_id=profile_id)
############################

# FUNCTIONS TO SEND AND REQUEST NETTWORK INVITATIONS
############################
# Function to send user request


@login_required
def send_network_request(request, profile_id):
    from_user = request.user
    User = get_user_model()
    to_user = User.objects.get(id=profile_id)
    network_request, created = Network_Request.objects.get_or_create(
        from_user=from_user, to_user=to_user)
    if created:
        return redirect('/networks/')
    else:
        return HttpResponse('network request was already sent')
        # Function to accept invittation request.


@login_required
def accept_network_request(request, request_id):
    network_request = Network_Request.objects.get(id=request_id)
    if network_request.to_user == request.user:
        profile = Profile.objects.get(user=network_request.to_user)
        Profile.objects.get(user=network_request.to_user).networks.add(
            network_request.from_user)
        Profile.objects.get(user=network_request.from_user).networks.add(
            network_request.to_user)
        network_request.delete()
        return redirect('/profile/')
    else:
        return HttpResponse('network request declined')
