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
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.candidate.username} - {self.assessment.title}"

class CandidateAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('assessments.Question', on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer by {self.result.candidate.username} for {self.question}"