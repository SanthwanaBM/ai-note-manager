from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Note, VoiceNote

# User Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Note Upload Form
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['name', 'description', 'file']

# Voice Note Upload Form
class VoiceNoteForm(forms.ModelForm):
    class Meta:
        model = VoiceNote
        fields = ['name', 'about', 'file']
