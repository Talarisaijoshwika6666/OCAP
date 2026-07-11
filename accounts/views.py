from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from submissions.models import Submission
from .models import UserSettings
from .forms import (
    UserProfileForm, SettingsPasswordChangeForm, NotificationsSettingsForm,
    EditorPreferencesForm, PrivacySettingsForm,
)

User = get_user_model()

RECRUITER_USERNAME = "recruiter"
RECRUITER_PASSWORD = "Recruiter@1234"


def login_view(request):
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
            user = User.objects.filter(username=username).first()
            if user is None:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid credentials.',
                    'panel': 'candidate'
                })

            user = authenticate(request, username=username, password=password)
            if user is None:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid credentials.',
                    'panel': 'candidate'
                })

            if not getattr(user, 'is_registered_candidate', False):
                user.is_registered_candidate = True
                user.save(update_fields=['is_registered_candidate'])

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

    panel = request.GET.get('panel', 'recruiter')
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
            username=username,
            email=email,
            password=password,
            role='candidate',
            is_staff=False,
            is_superuser=False,
            is_registered_candidate=True,
        )
        login(request, user)
        return redirect('/dashboard/')

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
    recent_submissions = submissions.order_by('-submitted_at')[:5]
    easy_solved = submissions.filter(question__difficulty='Easy', score__gt=0).count()
    medium_solved = submissions.filter(question__difficulty='Medium', score__gt=0).count()
    hard_solved = submissions.filter(question__difficulty='Hard', score__gt=0).count()
    total_submissions = submissions.count()
    total_score       = submissions.aggregate(total=Sum('score'))['total'] or 0
    problems_solved   = submissions.filter(
        score__gt=0).values('question').distinct().count()

    return render(request, 'accounts/profile.html', {
        'profile_user':      profile_user,
        'total_submissions': total_submissions,
        'total_score':       total_score,
        'problems_solved':   problems_solved,
        'recent_submissions': recent_submissions,
        'easy_solved': easy_solved,
        'medium_solved': medium_solved,
        'hard_solved': hard_solved,
    })

@login_required
def settings_view(request):
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)

    context = {
        "profile_form": UserProfileForm(instance=request.user),
        "password_form": SettingsPasswordChangeForm(request.user),
        "notifications_form": NotificationsSettingsForm(instance=settings_obj),
        "editor_form": EditorPreferencesForm(instance=settings_obj),
        "privacy_form": PrivacySettingsForm(instance=settings_obj),
        "settings": settings_obj,
        "user_settings": settings_obj,
    }

    return render(request, "accounts/settings.html", context)