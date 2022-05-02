from django.contrib import admin
from .models import Application, Note, Photo, Profile, Network_Request
# Register your models here.
admin.site.register(Application) # allow crud updatess for our application table in our admin app
admin.site.register(Note)
admin.site.register(Photo)
admin.site.register(Profile)
admin.site.register(Network_Request)