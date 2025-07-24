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
from .models import Lecture
from .forms import LectureForm
from datetime import timedelta
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timesince import timeuntil
from .models import StudyTask
from .forms import StudyTaskForm





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
          
            note.quiz = json.dumps(quiz_text)
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



@login_required
def schedule_lecture_view(request):
    if request.method == 'POST':
        form = LectureForm(request.POST)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.user = request.user
            lecture.save()
            return redirect('my_lectures')
    else:
        form = LectureForm()
    return render(request, 'schedule_lecture.html', {'form': form})





@login_required
def my_lectures_view(request):
    now = timezone.now()
    reminder_window = now + timedelta(hours=24)

    filter_option = request.GET.get('filter', 'all')

    lectures = Lecture.objects.filter(user=request.user)

    if filter_option == 'upcoming':
        lectures = lectures.filter(scheduled_at__gte=now)
    elif filter_option == 'completed':
        lectures = lectures.filter(scheduled_at__lt=now)

    completed_count = lectures.filter(scheduled_at__lt=now).count()
    upcoming_count = lectures.filter(scheduled_at__gte=now).count()
    total = lectures.count()
    completed_percent = round((completed_count / total) * 100) if total > 0 else 0

    # Annotate remaining time for upcoming lectures
    for lecture in lectures:
        if lecture.scheduled_at > now:
            delta = lecture.scheduled_at - now
            total_minutes = int(delta.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            lecture.remaining_time = f"{hours} hours, {minutes} minutes"
        else:
            lecture.remaining_time = None

    return render(request, 'my_lectures.html', {
        'lectures': lectures,
        'now': now,
        'reminder_window': reminder_window,
        'completed_count': completed_count,
        'upcoming_count': upcoming_count,
        'completed_percent': completed_percent,
        'selected_filter': filter_option
    })





@login_required
def delete_voice_note_view(request, pk):
    voice_note = get_object_or_404(VoiceNote, pk=pk, user=request.user)
    voice_note.delete()
    return redirect('my_voice_notes')  # or use: return HttpResponseRedirect(reverse('my_voice_notes'))



@login_required
def delete_note_view(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    note.delete()
    return redirect('my_notes')

from .models import StudyTask
from .forms import StudyTaskForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def study_planner_view(request):
    tasks = StudyTask.objects.filter(user=request.user).order_by('due_date')
    total = tasks.count()
    completed = tasks.filter(completed=True).count()
    percent = round((completed / total) * 100) if total > 0 else 0

    status = request.GET.get('status')
    if status == "completed":
        tasks = tasks.filter(completed=True)
    elif status == "pending":
        tasks = tasks.filter(completed=False)

    return render(request, 'study_planner.html', {
        'tasks': tasks,
        'completed_tasks': completed,
        'total_tasks': total,
        'progress_percent': percent,
        'status': status,
    })

@login_required
def add_study_task(request):
    if request.method == 'POST':
        form = StudyTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('study_planner')
    else:
        form = StudyTaskForm()
    return render(request, 'study_task_form.html', {'form': form, 'form_title': 'Add New Study Task'})

@login_required
def edit_study_task(request, pk):
    task = get_object_or_404(StudyTask, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StudyTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('study_planner')
    else:
        form = StudyTaskForm(instance=task)
    return render(request, 'study_task_form.html', {'form': form, 'form_title': 'Edit Study Task'})

@login_required
def toggle_task_status(request, pk):
    task = get_object_or_404(StudyTask, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('study_planner')

@login_required
def delete_study_task(request, pk):
    task = get_object_or_404(StudyTask, pk=pk, user=request.user)
    task.delete()
    return redirect('study_planner')
