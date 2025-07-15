from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Note, VoiceNote

admin.site.register(Note)
admin.site.register(VoiceNote)
