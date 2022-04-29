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

# Define the home view
def home(request):
    return render(request, 'about.html')

def about(request):
    return render(request, 'about.html')