from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
   path('about/', views.about, name='about'),
    path('applications/', views.applications_index, name='index'),
    path('applications/<int:application_id>/', views.applications_detail, name='detail'),
]