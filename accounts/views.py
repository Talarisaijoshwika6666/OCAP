from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from submissions.models import Submission
from .models import UserSettings
from .forms import (
    UserProfileForm, SettingsPasswordChangeForm, NotificationsSettingsForm,
    AppearanceSettingsForm, EditorPreferencesForm, PrivacySettingsForm,
)

User = get_user_model()

RECRUITER_USERNAME = "recruiter"
RECRUITER_PASSWORD = "Recruiter@1234"


def login_view(request):
    panel = request.GET.get('panel', 'recruiter')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        panel    = request.POST.get('panel', 'recruiter')

        if panel == 'recruiter':
            if username == RECRUITER_USERNAME and password == RECRUITER_PASSWORD:
                user, _ = User.objects.get_or_create(
                    username=RECRUITER_USERNAME,
                    defaults={'is_staff': True}
                )
                if not user.is_staff:
                    user.is_staff = True
                    user.save()
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/recruiter/dashboard/')
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid recruiter credentials.',
                    'panel': 'recruiter'
                })
        else:
            # Candidate panel — open to anyone
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'role': 'candidate'}
            )
            if created:
                user.set_password(password)
                user.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'
            if next_url == '/':
                next_url = '/dashboard/'
            return redirect(next_url)

    return render(request, 'accounts/login.html', {'panel': panel})

def logout_view(request):
    logout(request)
    return redirect('/')


def register_view(request):
    if request.method == 'POST':
        username         = request.POST.get('username', '').strip()
        email            = request.POST.get('email', '').strip()
        password         = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            return render(request, 'accounts/register.html', {
                'error': 'All fields are required.'
            })
        if len(password) < 8:
            return render(request, 'accounts/register.html', {
                'error': 'Password must be at least 8 characters long.'
            })
        if password != confirm_password:
            return render(request, 'accounts/register.html', {
                'error': 'Passwords do not match.'
            })
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Username already taken.'
            })
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Email already registered.'
            })

        user = User.objects.create_user(
            username=username, email=email, password=password)
        login(request, user)
        return redirect('/questions/')

    return render(request, 'accounts/register.html')


def profile_view(request, username=None):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    if username is None:
        profile_user = request.user
    else:
        profile_user = User.objects.filter(username=username).first()
        if not profile_user:
            return redirect('/')

    submissions       = Submission.objects.filter(user=profile_user)
    total_submissions = submissions.count()
    total_score       = submissions.aggregate(total=Sum('score'))['total'] or 0
    problems_solved   = submissions.filter(
        score__gt=0).values('question').distinct().count()

    return render(request, 'accounts/profile.html', {
        'profile_user':      profile_user,
        'total_submissions': total_submissions,
        'total_score':       total_score,
        'problems_solved':   problems_solved,
    })

@login_required(login_url='/accounts/login/')
def settings_view(request):
    """Single-page Settings module: Account, Notifications, Appearance,
    Editor Preferences, Privacy, About. Each tab posts back to this same
    view with a hidden `section` field so we know which form to process."""
    user = request.user
    user_settings, _ = UserSettings.objects.get_or_create(user=user)
    active_tab = request.GET.get('tab', 'account')

    if request.method == 'POST':
        section = request.POST.get('section')
        active_tab = section or active_tab

        if section == 'profile':
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
            else:
                for field_errors in profile_form.errors.values():
                    for err in field_errors:
                        messages.error(request, err)
            active_tab = 'account'

        elif section == 'password':
            password_form = SettingsPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
            else:
                for field_errors in password_form.errors.values():
                    for err in field_errors:
                        messages.error(request, err)
            active_tab = 'account'

        elif section == 'notifications':
            form = NotificationsSettingsForm(
                request.POST, instance=user_settings)
            # Unchecked checkboxes are absent from POST, so make sure the
            # ModelForm sees them as False instead of falling back to a
            # stale instance value.
            for field in form.fields:
                if field not in request.POST:
                    request.POST = request.POST.copy()
                    request.POST[field] = False
            form = NotificationsSettingsForm(
                request.POST, instance=user_settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Notification preferences saved.')
            active_tab = 'notifications'

        elif section == 'appearance':
            form = AppearanceSettingsForm(request.POST, instance=user_settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Appearance updated.')
            active_tab = 'appearance'

        elif section == 'editor':
            post_data = request.POST.copy()
            for field in ['show_line_numbers', 'word_wrap', 'auto_complete', 'auto_save']:
                if field not in post_data:
                    post_data[field] = False
            form = EditorPreferencesForm(post_data, instance=user_settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Editor preferences saved.')
            else:
                for field_errors in form.errors.values():
                    for err in field_errors:
                        messages.error(request, err)
            active_tab = 'editor'

        elif section == 'privacy':
            post_data = request.POST.copy()
            for field in ['public_profile', 'show_solved_problems',
                          'show_contest_ranking', 'show_activity']:
                if field not in post_data:
                    post_data[field] = False
            form = PrivacySettingsForm(post_data, instance=user_settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Privacy settings saved.')
            active_tab = 'privacy'

        return redirect(f'/accounts/settings/?tab={active_tab}')

    return render(request, 'accounts/settings.html', {
        'user_settings': user_settings,
        'active_tab': active_tab,
        'password_form': SettingsPasswordChangeForm(user),
    })
