from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .forms import RegisterForm, NoteForm, VoiceNoteForm
from .models import Note, VoiceNote
from django.contrib.auth.decorators import login_required

from .utils import extract_text_from_file, generate_summary, extract_glossary, generate_quiz
from .utils import convert_voice_to_text


import os


# User Registration
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# User Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('welcome')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# User Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Welcome Page
@login_required
def welcome_view(request):
    time_now = timezone.localtime()
    return render(request, 'welcome.html', {'time_now': time_now})

# Upload Note
@login_required
def upload_note_view(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()  # Save file first to generate file path

            file_path = note.file.path
            print("👉 File saved at:", file_path)

            # Extract text
            text_content = extract_text_from_file(file_path)
            print("👉 Extracted Text Length:", len(text_content))
            print("👉 Text Preview:", text_content[:500])

            # Generate summary (safe length handling)
            if len(text_content) < 50:
                summary = "Text too short to summarize."
            elif len(text_content) > 5000:
                summary = "Note too large to summarize. Please upload a smaller file or split it."
            else:
                summary = generate_summary(text_content)
            print("👉 Generated Summary:", summary)

            # Extract glossary terms
            glossary_terms = extract_glossary(text_content)
            print("👉 Extracted Glossary Terms:", glossary_terms)

            note.summary = summary
            note.glossary = ', '.join(glossary_terms)
            note.save()

            # Generate quiz
            print("👉 Summary content for quiz:", summary)
            if "too short" in summary.lower() or "too large" in summary.lower():
                quiz_text = generate_quiz(text_content)
            else:
                quiz_text = generate_quiz(summary)

            print("👉 Generated Quiz Questions:", quiz_text)
            note.quiz = quiz_text
            note.save()

            return redirect('my_notes')
    else:
        form = NoteForm()

    return render(request, 'upload_note.html', {'form': form})


# List Notes
@login_required
def my_notes_view(request):
    notes = Note.objects.filter(user=request.user)
    return render(request, 'my_notes.html', {'notes': notes})

# Upload Voice Note

@login_required
def upload_voice_note_view(request):
    if request.method == 'POST':
        form = VoiceNoteForm(request.POST, request.FILES)
        if form.is_valid():
            voice = form.save(commit=False)
            voice.user = request.user
            voice.save()

            file_path = voice.file.path
            print("👉 Voice file saved at:", file_path)

            converted_text = convert_voice_to_text(file_path)
            print("👉 Converted Text:", converted_text)

            voice.converted_text = converted_text
            voice.save()

            return redirect('my_voice_notes')
    else:
        form = VoiceNoteForm()

    return render(request, 'upload_voice_note.html', {'form': form})

# List Voice Notes
@login_required
def my_voice_notes_view(request):
    voices = VoiceNote.objects.filter(user=request.user)
    return render(request, 'my_voice_notes.html', {'voices': voices})
