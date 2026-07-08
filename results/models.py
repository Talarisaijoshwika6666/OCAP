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

    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    total_marks = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate.username} - {self.assessment.title}"


class CandidateAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('assessments.Question', on_delete=models.CASCADE, related_name='candidate_answers')

    # MCQ fields
    selected_option = models.CharField(max_length=1, blank=True, null=True)

    # Coding fields
    code = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=20, blank=True, null=True)
    test_cases_passed = models.PositiveIntegerField(default=0)
    total_test_cases = models.PositiveIntegerField(default=0)

    is_correct = models.BooleanField(default=False)
    marks_awarded = models.FloatField(default=0)

    class Meta:
        ordering = ['question__id']

    def __str__(self):
        return f"Answer to {self.question} in {self.result}"
