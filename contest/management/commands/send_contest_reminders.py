from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from contest.models import Contest

class Command(BaseCommand):
    help = 'Sends email reminders to registered candidates 20 minutes before a contest starts.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Find contests starting in exactly 20 to 25 minutes
        # (Assuming the cron might run every 5 minutes)
        target_start_time = now + timedelta(minutes=20)
        target_end_time = now + timedelta(minutes=25)
        
        contests = Contest.objects.filter(
            start_time__gte=target_start_time,
            start_time__lt=target_end_time
        )
        
        for contest in contests:
            registrations = contest.registrations.all()
            if not registrations.exists():
                self.stdout.write(f'No registrations for contest: {contest.title}')
                continue
                
            emails = []
            for reg in registrations:
                emails.append(reg.registration_email)
                
            question_count = contest.mcqs.count() + contest.programming_questions.count()
            
            subject = f"Reminder: Contest '{contest.title}' is starting soon!"
            message = f"""
Dear Candidate,

This is a reminder that the contest '{contest.title}' will start in about 20 minutes.

- Start Time: {contest.start_time.strftime('%B %d, %Y at %I:%M %p')}
- Format: {contest.get_format_type_display()}
- Questions: {question_count}
- Duration: {contest.duration_minutes} minutes

Please get ready and be prepared to enter your email and Exam PIN to start the exam.

Good luck!
LogicLabs Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=True,
            )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully sent reminders for contest: {contest.title} to {len(emails)} candidates.'))
            
        if not contests.exists():
            self.stdout.write('No contests starting in ~20 minutes.')
