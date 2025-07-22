from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from notes.models import Lecture

class Command(BaseCommand):
    help = 'Send email reminders for upcoming lectures'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        window = now + timedelta(hours=24)

        upcoming = Lecture.objects.filter(
            reminder_sent=False,
            scheduled_at__lte=window,
            scheduled_at__gt=now
        )

        for lecture in upcoming:
            subject = f"Reminder: Upcoming Lecture - {lecture.title}"
            message = f"Hi {lecture.user.username},\n\nYou have a lecture titled '{lecture.title}' scheduled at {lecture.scheduled_at.strftime('%Y-%m-%d %H:%M')}.\n\nDon't forget!"
            send_mail(
                subject,
                message,
                None,
                [lecture.user.email],
                fail_silently=False,
            )

            lecture.reminder_sent = True
            lecture.save()

            self.stdout.write(f"Reminder sent to {lecture.user.email} for lecture: {lecture.title}")
