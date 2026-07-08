from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import re

try:
    from PIL import Image as PILImage
except ImportError:  # pragma: no cover - Pillow may be unavailable in some environments
    PILImage = None

from .models import User, UserSettings

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'id': 'password'
        }),
        label='Password'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'confirm_password'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'mobile', 'username']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your mobile number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')
        
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm = self.cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise ValidationError('Passwords do not match.')
        return confirm

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Profile update form for the settings module."""

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'full_name', 'email',
            'mobile', 'profile_picture', 'bio', 'organization'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '254'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '15'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '500'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('Username is required.')
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email is already registered.')
        return email

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if not picture:
            return picture
        if picture.size > 2 * 1024 * 1024:
            raise ValidationError('Profile picture must be 2MB or smaller.')

        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        extension = picture.name.lower().rsplit('.', 1)[-1] if '.' in picture.name else ''
        if extension not in {'jpg', 'jpeg', 'png', 'webp', 'gif'}:
            raise ValidationError('Please upload a valid image file.')

        try:
            if PILImage is not None:
                picture.seek(0)
                with PILImage.open(picture) as img:
                    img.verify()
                picture.seek(0)
            else:
                get_image_dimensions(picture)
        except Exception:
            raise ValidationError('Please upload a valid image file.')
        return picture

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.full_name:
            full_name = ' '.join(part for part in [instance.first_name, instance.last_name] if part).strip()
            instance.full_name = full_name
        if commit:
            instance.save()
        return instance

# ─────────────────────────────────────────────────────────
# Settings module forms
# ─────────────────────────────────────────────────────────

class SettingsPasswordChangeForm(forms.Form):
    """Change-password form for the Settings > Account tab.
    Validates against the real authenticated user's hashed password."""
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter current password'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter new password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm new password'
    }))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise ValidationError('Current password is incorrect.')
        return current

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        validate_password(new_password, user=self.user)
        return new_password

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get('new_password')
        confirm_password = cleaned.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError('New passwords do not match.')
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user


class NotificationsSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'email_notifications', 'contest_notifications',
            'course_update_notifications', 'submission_result_notifications',
            'team_member_notifications', 'spam_filtering',
        ]
        widgets = {name: forms.CheckboxInput() for name in fields}


class AppearanceSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['theme']


class EditorPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'default_language', 'font_size', 'show_line_numbers',
            'word_wrap', 'auto_complete', 'auto_save',
        ]
        widgets = {
            'default_language': forms.Select(attrs={'class': 'settings-form-control'}),
            'font_size': forms.NumberInput(attrs={'class': 'settings-form-control'}),
            'show_line_numbers': forms.CheckboxInput(),
            'word_wrap': forms.CheckboxInput(),
            'auto_complete': forms.CheckboxInput(),
            'auto_save': forms.CheckboxInput(),
        }

    def clean_font_size(self):
        size = self.cleaned_data.get('font_size')
        if size is None or size < 10 or size > 24:
            raise ValidationError('Font size must be between 10 and 24.')
        return size


class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'public_profile', 'show_solved_problems',
            'show_contest_ranking', 'show_activity',
        ]
