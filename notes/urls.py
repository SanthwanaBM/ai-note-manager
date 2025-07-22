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


]
