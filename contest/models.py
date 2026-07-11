from django.db import models

class Contest(models.Model):
    FORMAT_CHOICES = [
        ('objective', 'Objective Format'),
        ('interactive', 'Interactive Format'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=100, blank=True)
    duration_minutes = models.PositiveIntegerField(default=90)
    allowed_languages = models.JSONField(default=list, blank=True)
    format_type = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='objective')
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class MCQQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='mcqs')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=10) # Expected "Option A", "Option B", etc.
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Easy')
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"MCQ for {self.contest.title}"

class ProgrammingQuestion(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='programming_questions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    constraints = models.TextField(blank=True)
    input_format = models.TextField(blank=True)
    output_format = models.TextField(blank=True)
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    memory_limit = models.PositiveIntegerField(default=256)
    marks = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.title

class HiddenTestCase(models.Model):
    question = models.ForeignKey(ProgrammingQuestion, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)

    def __str__(self):
        return f"Test Case for {self.question.title}"
class ContestRegistration(models.Model):
    candidate = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='contest_registrations')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='registrations')
    registration_email = models.EmailField()
    registration_name = models.CharField(max_length=255)
    exam_password = models.CharField(max_length=255) # hashed password
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'contest')

    def __str__(self):
        return f'{self.candidate.username} - {self.contest.title}'

class CandidateResult(models.Model):
    candidate = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='contest_results')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='contest_results')
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('candidate', 'contest')

    def __str__(self):
        return f'{self.candidate.username} - {self.contest.title} - Score: {self.score}'

class MCQSubmission(models.Model):
    result = models.ForeignKey(CandidateResult, on_delete=models.CASCADE, related_name='mcq_submissions')
    question = models.ForeignKey(MCQQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=20, blank=True) # e.g. "Option A"
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.result.candidate.username} - {self.question.id}'

class ProgrammingSubmission(models.Model):
    result = models.ForeignKey(CandidateResult, on_delete=models.CASCADE, related_name='prog_submissions')
    question = models.ForeignKey(ProgrammingQuestion, on_delete=models.CASCADE)
    code = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.result.candidate.username} - {self.question.title}'
