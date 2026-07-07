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
    AppearanceSettingsForm, EditorPreferencesForm, PrivacySettingsForm,
)

User = get_user_model()

RECRUITER_USERNAME = "recruiter"


def _apply_unchecked_checkbox_fields(post_data, fields):
    data = post_data.copy()
    for field in fields:
        if field not in data:
            data[field] = False
    return data
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
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if section == 'profile':
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                user.refresh_from_db()
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Profile updated successfully.',
                        'username': user.username,
                        'profile_picture_url': user.profile_picture.url if user.profile_picture else None,
                    })
                messages.success(request, 'Profile updated successfully.')
            else:
                errors = []
                for field_errors in profile_form.errors.values():
                    for err in field_errors:
                        errors.append(err)
                        if not is_ajax:
                            messages.error(request, err)
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            active_tab = 'account'

        elif section == 'password':
            password_form = SettingsPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Password updated successfully.',
                    })
                messages.success(request, 'Password updated successfully.')
            else:
                errors = []
                for field_errors in password_form.errors.values():
                    for err in field_errors:
                        errors.append(err)
                        if not is_ajax:
                            messages.error(request, err)
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            active_tab = 'account'

        elif section == 'notifications':
            post_data = _apply_unchecked_checkbox_fields(
                request.POST,
                ['email_notifications', 'contest_notifications',
                 'course_update_notifications', 'submission_result_notifications',
                 'team_member_notifications', 'spam_filtering']
            )
            form = NotificationsSettingsForm(post_data, instance=user_settings)
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Notification preferences saved.',
                    })
                messages.success(request, 'Notification preferences saved.')
            else:
                errors = []
                for field_errors in form.errors.values():
                    for err in field_errors:
                        errors.append(err)
                        if not is_ajax:
                            messages.error(request, err)
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            active_tab = 'notifications'

        elif section == 'appearance':
            form = AppearanceSettingsForm(request.POST, instance=user_settings)
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Appearance updated.',
                        'theme': user_settings.theme,
                    })
                messages.success(request, 'Appearance updated.')
            else:
                errors = []
                for field_errors in form.errors.values():
                    for err in field_errors:
                        errors.append(err)
                        if not is_ajax:
                            messages.error(request, err)
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            active_tab = 'appearance'

        elif section == 'editor':
            post_data = _apply_unchecked_checkbox_fields(
                request.POST,
                ['show_line_numbers', 'word_wrap', 'auto_complete', 'auto_save']
            )
            form = EditorPreferencesForm(post_data, instance=user_settings)
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Editor preferences saved.',
                    })
                messages.success(request, 'Editor preferences saved.')
            else:
                errors = []
                for field_errors in form.errors.values():
                    for err in field_errors:
                        errors.append(err)
                        if not is_ajax:
                            messages.error(request, err)
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            active_tab = 'editor'

        elif section == 'privacy':
            post_data = _apply_unchecked_checkbox_fields(
                request.POST,
                ['public_profile', 'show_solved_problems',
                 'show_contest_ranking', 'show_activity']
            )
            form = PrivacySettingsForm(post_data, instance=user_settings)
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Privacy settings saved.',
                    })
                messages.success(request, 'Privacy settings saved.')
            else:
                errors = []
                for field_errors in form.errors.values():
                    for err in field_errors:
                        errors.append(err)
                        if not is_ajax:
                            messages.error(request, err)
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            active_tab = 'privacy'

        return redirect(f'/accounts/settings/?tab={active_tab}')

    return render(request, 'accounts/settings.html', {
        'user_settings': user_settings,
        'active_tab': active_tab,
        'password_form': SettingsPasswordChangeForm(user),
    })
