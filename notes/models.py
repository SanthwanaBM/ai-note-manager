from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User



# Note Model
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)   
    glossary = models.TextField(blank=True, null=True) 
    quiz = models.TextField(blank=True, null=True)  


    def __str__(self):
        return self.name


# Voice Note Model
class VoiceNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    about = models.TextField()
    file = models.FileField(upload_to='voice_notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    converted_text = models.TextField(blank=True, null=True)  # we'll keep it simple for now

    def __str__(self):
        return self.name



class Lecture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_sent = models.BooleanField(default=False)  


    def __str__(self):
        return f"{self.title} on {self.scheduled_at.strftime('%Y-%m-%d %H:%M')}"




class StudyTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title