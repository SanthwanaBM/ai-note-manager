from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload_note/', views.upload_note_view, name='upload_note'),
    path('my_notes/', views.my_notes_view, name='my_notes'),
    path('upload_voice_note/', views.upload_voice_note_view, name='upload_voice_note'),
    path('my_voice_notes/', views.my_voice_notes_view, name='my_voice_notes'),
    path('schedule_lecture/', views.schedule_lecture_view, name='schedule_lecture'),
    path('my_lectures/', views.my_lectures_view, name='my_lectures'),
    path('voice_notes/delete/<int:pk>/', views.delete_voice_note_view, name='delete_voice_note'),
    path('notes/delete/<int:note_id>/', views.delete_note_view, name='delete_note'),

    path('study_planner/', views.study_planner_view, name='study_planner'),
    path('add_study_task/', views.add_study_task, name='add_study_task'),
    path('edit_study_task/<int:pk>/', views.edit_study_task, name='edit_study_task'),
    path('toggle_task_status/<int:pk>/', views.toggle_task_status, name='toggle_task_status'),
    path('delete_study_task/<int:pk>/', views.delete_study_task, name='delete_study_task'),




]
