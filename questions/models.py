from django.db import models
from django.conf import settings

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    topic = models.CharField(max_length=100, default='General', blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    hint = models.TextField(blank=True, help_text="Hint shown to candidates")
    answer = models.TextField(blank=True, help_text="Reference solution shown after 3 failed attempts")
    time_limit = models.PositiveIntegerField(default=60, help_text="Time limit in minutes for this question")
    # --- Contest-authoring fields (recruiter 'Add Programming Questions' form) ---
    # All optional/blank so existing Problem Bank questions (created before
    # this feature existed) keep working exactly as before.
    constraints = models.TextField(blank=True, default='')
    input_format = models.TextField(blank=True, default='')
    output_format = models.TextField(blank=True, default='')
    memory_limit_mb = models.PositiveIntegerField(default=256, help_text='Memory limit in MB for this question')
    marks = models.PositiveIntegerField(default=0, help_text='Marks this question is worth in a contest (0 = untracked / Problem Bank question)')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField(blank=True, default='')
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"TestCase for {self.question.title}"


class Bookmark(models.Model):
    """Tracks which questions a user has bookmarked. Backed by the DB so
    the state survives page refreshes / logins from other devices."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.question.title}"