from django.conf import settings
from django.db import models


class TopicProgress(models.Model):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (NOT_STARTED, 'Not Started'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    STATUS_PERCENT = {
        NOT_STARTED: 0,
        IN_PROGRESS: 50,
        COMPLETED: 100,
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quest_progress',
    )
    subject_slug = models.SlugField(max_length=100)
    topic_slug = models.SlugField(max_length=150)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=NOT_STARTED
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'subject_slug', 'topic_slug')

    def __str__(self):
        return f"{self.user} - {self.subject_slug}/{self.topic_slug} ({self.status})"

    @property
    def percent(self):
        return self.STATUS_PERCENT.get(self.status, 0)


class Topic(models.Model):
    CATEGORY_CHOICES = [
        ('quest', 'Quest'),
        ('study_plan', 'Study Plan'),
        ('explore', 'Explore'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='quest')
    icon = models.CharField(max_length=50, default='fas fa-code')
    color = models.CharField(max_length=20, default='#f59e0b')
    levels = models.IntegerField(default=5)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title