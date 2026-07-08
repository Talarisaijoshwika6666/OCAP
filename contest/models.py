from django.conf import settings
from django.db import models
from django.utils import timezone
 
 
class Contest(models.Model):
    # Comma-separated language codes a recruiter allows for this contest.
    # Codes match what the judge (submissions/executor.py) understands:
    # python, javascript, java, cpp. 'c' can be selected in the recruiter
    # form for completeness (per the requirements), but there's currently
    # no C backend in the judge, so it just won't show up as a runnable
    # option for candidates -- see Contest.runnable_languages_list.
    LANGUAGE_CHOICES = [
        ('c', 'C'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
    ]
    RUNNABLE_LANGUAGES = {'python', 'javascript', 'java', 'cpp'}

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=120, blank=True, default='')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    allowed_languages = models.CharField(
        max_length=200,
        blank=True,
        default='python,cpp,java,javascript',
        help_text='Comma-separated language codes candidates may use (see LANGUAGE_CHOICES).',
    )
    questions = models.ManyToManyField(
        'questions.Question', related_name='contests', blank=True
    )
 
    class Meta:
        ordering = ['-start_time']
 
    def __str__(self):
        return self.title
 
    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'
        if self.start_time <= now <= self.end_time:
            return 'live'
        return 'ended'
 
    @property
    def problem_count(self):
        return self.questions.count()

    @property
    def mcq_count(self):
        return self.mcqs.count()

    @property
    def total_question_count(self):
        return self.problem_count + self.mcq_count

    @property
    def allowed_languages_list(self):
        return [l.strip() for l in self.allowed_languages.split(',') if l.strip()]

    @property
    def runnable_languages_list(self):
        """Allowed languages that the judge actually supports right now."""
        return [l for l in self.allowed_languages_list if l in self.RUNNABLE_LANGUAGES]
 
    @property
    def duration_minutes(self):
        return int((self.end_time - self.start_time).total_seconds() // 60)
 
    @property
    def time_range(self):
        start = timezone.localtime(self.start_time)
        end = timezone.localtime(self.end_time)
        return f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
 
    @property
    def date(self):
        return timezone.localtime(self.start_time).strftime('%a %d %b, %H:%M')
 
    @property
    def remaining_seconds(self):
        """Seconds until the contest ends (if live) or starts (if upcoming)."""
        now = timezone.now()
        target = self.end_time if self.status == 'live' else self.start_time
        return max(0, int((target - now).total_seconds()))
 
 
class ContestRegistration(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contest_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    # --- Proctoring / anti-tab-switching state ---
    # Persisted on the registration row (not just the session) so the
    # warning count survives page refreshes and can be validated
    # server-side before an automatic submission is ever performed.
    violation_count = models.PositiveSmallIntegerField(
        default=0,
        help_text='Number of tab-switch / focus-loss violations recorded during this contest.',
    )
    auto_submitted = models.BooleanField(
        default=False,
        help_text='True once the test was force-submitted due to repeated proctoring violations.',
    )
    auto_submitted_at = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        unique_together = ('contest', 'user')
 
    def __str__(self):
        return f"{self.user} -> {self.contest}"


class ContestMCQ(models.Model):
    """A multiple-choice question that belongs to exactly one contest
    (unlike programming questions, MCQs aren't shared with the Problem
    Bank — they only make sense in the context of a contest)."""

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='mcqs')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Easy')
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"MCQ #{self.pk} ({self.contest.title})"

    def option_text(self, letter):
        return getattr(self, f'option_{letter.lower()}', '')

    @property
    def options(self):
        """[(letter, text), ...] — handy for rendering in templates."""
        return [(letter, self.option_text(letter)) for letter, _ in self.OPTION_CHOICES]


class ContestMCQAnswer(models.Model):
    """A candidate's selected answer for one ContestMCQ. One row per
    (mcq, user) — selecting again just updates the existing row, same
    autosave-style behaviour as the code editor."""

    mcq = models.ForeignKey(ContestMCQ, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contest_mcq_answers')
    selected_option = models.CharField(max_length=1, choices=ContestMCQ.OPTION_CHOICES)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('mcq', 'user')

    def __str__(self):
        return f"{self.user} -> {self.mcq_id} = {self.selected_option}"