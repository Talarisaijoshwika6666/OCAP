from django.conf import settings
from django.db import models
from django.utils import timezone
 
 
class Contest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    questions = models.ManyToManyField(
        'questions.Question', related_name='contests', blank=True
    )
 
    class Meta:
        ordering = ['-start_time']
 
    def __str__(self):
        return self.title
 
    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'
        if self.start_time <= now <= self.end_time:
            return 'live'
        return 'ended'
 
    @property
    def problem_count(self):
        return self.questions.count()
 
    @property
    def duration_minutes(self):
        return int((self.end_time - self.start_time).total_seconds() // 60)
 
    @property
    def time_range(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
 
    @property
    def date(self):
        return self.start_time.strftime('%a %d %b, %H:%M')
 
    @property
    def remaining_seconds(self):
        """Seconds until the contest ends (if live) or starts (if upcoming)."""
        now = timezone.now()
        target = self.end_time if self.status == 'live' else self.start_time
        return max(0, int((target - now).total_seconds()))
 
 
class ContestRegistration(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contest_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ('contest', 'user')
 
    def __str__(self):
        return f"{self.user} -> {self.contest}"
