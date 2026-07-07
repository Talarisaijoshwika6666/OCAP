from django.db import models
from django.contrib.auth import get_user_model
from questions.models import Question

User = get_user_model()

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20, default='python')
    score = models.FloatField(default=0)
    passed_cases = models.IntegerField(default=0)
    total_cases = models.IntegerField(default=0)
    result = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.title}"