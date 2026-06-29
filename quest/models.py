from django.db import models

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