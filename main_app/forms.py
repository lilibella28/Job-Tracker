from django.forms import ModelForm
from .models import Note, Profile


class NoteForm(ModelForm):
	class Meta:
		model = Note
		fields = ['date', 'name', 'note']

class ProfileUpdate(ModelForm):
	class Meta:
		model = Profile
		fields = ['name', 'intro', 'title', 'hobies']