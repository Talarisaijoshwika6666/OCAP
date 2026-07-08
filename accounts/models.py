from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('examiner', 'Examiner'),
        ('admin', 'Admin'),
    )

    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    mobile = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.full_name or self.username

class UserSettings(models.Model):
    THEME_CHOICES = (
        ('dark', 'Dark'),
        ('light', 'Light'),
    )
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('c', 'C'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    email_notifications = models.BooleanField(default=True)
    contest_notifications = models.BooleanField(default=True)
    course_update_notifications = models.BooleanField(default=True)
    submission_result_notifications = models.BooleanField(default=True)
    team_member_notifications = models.BooleanField(default=True)
    spam_filtering = models.BooleanField(default=True)
    theme = models.CharField(choices=THEME_CHOICES, default='dark', max_length=10)
    default_language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=20)
    font_size = models.PositiveSmallIntegerField(default=14)
    show_line_numbers = models.BooleanField(default=True)
    word_wrap = models.BooleanField(default=True)
    auto_complete = models.BooleanField(default=True)
    auto_save = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=True)
    show_solved_problems = models.BooleanField(default=True)
    show_contest_ranking = models.BooleanField(default=True)
    show_activity = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f"{self.user.username}'s settings"

class ChatRateLimit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]


class UserSettings(models.Model):
    """Stores per-user preferences for the Settings module."""

    THEME_CHOICES = (
        ('dark', 'Dark'),
        ('light', 'Light'),
    )

    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('c', 'C'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings'
    )

    # Notifications
    email_notifications = models.BooleanField(default=True)
    contest_notifications = models.BooleanField(default=True)
    course_update_notifications = models.BooleanField(default=True)
    submission_result_notifications = models.BooleanField(default=True)
    team_member_notifications = models.BooleanField(default=True)
    spam_filtering = models.BooleanField(default=True)

    # Appearance
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='dark'
    )

    # Editor Preferences
    default_language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='python'
    )
    font_size = models.PositiveSmallIntegerField(default=14)
    show_line_numbers = models.BooleanField(default=True)
    word_wrap = models.BooleanField(default=True)
    auto_complete = models.BooleanField(default=True)
    auto_save = models.BooleanField(default=False)

    # Privacy
    public_profile = models.BooleanField(default=True)
    show_solved_problems = models.BooleanField(default=True)
    show_contest_ranking = models.BooleanField(default=True)
    show_activity = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return f"Settings for {self.user.username}"


class ChatRateLimit(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.timestamp}"
        return f"{self.ip_address} - {self.timestamp}"


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.get_or_create(user=instance)