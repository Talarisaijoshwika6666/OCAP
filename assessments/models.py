from django.db import models
from django.contrib.auth.models import User

QUESTION_TYPE_CHOICES = [
    ('mcq', 'Multiple Choice'),
    ('coding', 'Coding'),
]

LANGUAGE_CHOICES = [
    ('python', 'Python'),
    ('java', 'Java'),
    ('cpp', 'C++'),
    ('javascript', 'JavaScript'),
]

DIFFICULTY_Q_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]


# 1. Assessment first
class Assessment(models.Model):
    DIFFICULTY = [('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]
    title = models.CharField(max_length=200, default='')
    duration = models.IntegerField(default=60)
    total_marks = models.IntegerField(default=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY, default='Beginner')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# 2. Question second (needs Assessment)
class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')

    # Existing simple MCQ fields (kept so old data still works)
    text = models.TextField(default='')
    correct_option = models.CharField(max_length=1, default='a')

    # Fields to support full MCQ + Coding questions
    title = models.CharField(max_length=255, blank=True, default='')
    problem_statement = models.TextField(blank=True, default='')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_Q_CHOICES, default='easy')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='mcq')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, blank=True, null=True)
    hint = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    time_limit = models.PositiveIntegerField(default=60, help_text="Time limit in minutes for this question")
    marks = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def get_options(self):
        options = []
        if self.option_a:
            options.append(('A', self.option_a))
        if self.option_b:
            options.append(('B', self.option_b))
        if self.option_c:
            options.append(('C', self.option_c))
        if self.option_d:
            options.append(('D', self.option_d))
        return options

    def __str__(self):
        return self.title or self.text

    def get_options(self):
        """Return list of (label, text) tuples for non-empty options, for MCQ rendering."""
        opts = [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]
        return [(label, text) for label, text in opts if text]

    @property
    def sample_test_cases(self):
        return self.test_cases.filter(is_sample=True)


# 3. TestCase third (needs Question)
class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField(blank=True)
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"TestCase #{self.id} for {self.question}"
