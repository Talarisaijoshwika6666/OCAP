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
    created_at = models.DateTimeField(auto_now_add=True)

    def get_effective_test_cases(self):
        """
        Returns the test cases to judge against.
        - If this question has TestCase rows (added in Django admin), use those.
        - Otherwise, fall back to a single synthetic case built from
          sample_input / sample_output -- treated as visible "Test Case 0".
        """
        cases = list(self.test_cases.all().order_by('id'))
        if cases:
            return cases
        return [TestCase(
            question=self,
            input_data=self.sample_input or '',
            expected_output=self.sample_output or '',
            is_hidden=False,
        )]

    def get_answer_for_language(self, language):
        """
        Returns the reference answer to show a candidate, matched to the
        programming language they were working in.
        Falls back to the question's general `answer` field if no
        language-specific answer has been set for that language.
        """
        language = (language or '').lower()
        if language:
            entry = self.language_contents.filter(language=language).first()
            if entry and entry.answer.strip():
                return entry.answer
        return self.answer

    def __str__(self):
        return self.title


class QuestionLanguage(models.Model):
    """
    Per-language content for a Question. Lets a recruiter/admin provide a
    different reference answer (and optionally hint/starter code) depending
    on which programming language the candidate is solving the problem in.
    """
    LANGUAGE_CHOICES = [
        ('python', 'Python3'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('c', 'C'),
        ('cpp', 'C++'),
        ('ruby', 'Ruby'),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='language_contents')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    starter_code = models.TextField(blank=True, help_text="Boilerplate code pre-filled in the editor when this language is selected. Leave blank to use the default template.")
    hint = models.TextField(blank=True, help_text="Hint shown to candidates when this language is selected")
    answer = models.TextField(blank=True, help_text="Reference solution shown after 3 failed attempts, for this language")

    class Meta:
        ordering = ['language']
        unique_together = ('question', 'language')

    def __str__(self):
        return f"{self.question.title} — {self.get_language_display()}"


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