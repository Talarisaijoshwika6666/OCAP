from django.conf import settings
from django.db import models

class Result(models.Model):
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    assessment = models.ForeignKey(
        'assessments.Assessment', 
        on_delete=models.CASCADE,
        related_name='results'
    )
    score = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.candidate.username} - {self.assessment.title}"