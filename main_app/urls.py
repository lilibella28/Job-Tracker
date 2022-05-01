from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('profile/', views.profile, name='profile'),
  path('networks/', views.networks_index, name='networkindex'),
  path('applications/', views.applications_index, name='index'),
  path('applications/<int:application_id>/', views.applications_detail, name='detail'),
  path('applications/create/', views.ApplicationCreate.as_view(), name='applications_create'),
  path('applications/<int:pk>/update/', views.ApplicationUpdate.as_view(), name='applications_update'),
  path('applications/<int:pk>/delete/', views.ApplicationDelete.as_view(), name='applications_delete'),
  path('applications/<int:application_id>/add_note/', views.add_note, name='add_note'),
  path('applications/<int:application_id>/add_photo/', views.add_photo, name='add_photo'),
  path('accounts/signup/', views.signup, name='signup'),
  path('send_network_request/<int:profile_id>/', views.send_network_request, name='send_network_request'),
  path('accept_network_request/<int:request_id>/', views.accept_network_request, name='accept_network_request'),
]