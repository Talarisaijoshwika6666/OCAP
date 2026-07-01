from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model

User = get_user_model()

# ── Hardcoded recruiter credentials ──────────────────────────
RECRUITER_USERNAME = 'recruiter'
RECRUITER_PASSWORD = 'Recruiter@123'
# ─────────────────────────────────────────────────────────────

def login_view(request):
    panel = request.GET.get('panel', 'recruiter')
    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        panel    = request.POST.get('panel', 'recruiter')

        if panel == 'recruiter':
            if username == RECRUITER_USERNAME and password == RECRUITER_PASSWORD:
                request.session['is_recruiter'] = True
                request.session['recruiter_username'] = username
                return redirect('/recruiter/dashboard/')
            else:
                error = "Invalid recruiter credentials."

        else:  # candidate — auto-login / auto-register, no real password check
            if not username:
                error = "Username is required."
            else:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'role': 'candidate'}
                )
                if created:
                    user.set_password(password or 'changeme123')
                    user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/questions/')

    return render(request, 'accounts/login.html', {
        'panel': panel,
        'error': error,
    })


def logout_view(request):
    # Clear recruiter session too
    request.session.flush()
    logout(request)
    return redirect('/accounts/login/')


def register_view(request):
    error = None
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        password  = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        email     = request.POST.get('email', '')

        if not username or not password:
            error = "Username and password are required."
        elif password != password2:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif User.objects.filter(username=username).exists():
            error = "Username already taken."
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                role='candidate'
            )
            return redirect('/accounts/login/?panel=candidate')

    return render(request, 'accounts/register.html', {'error': error})


def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('/accounts/login/')


from django.db.models import Sum
from submissions.models import Submission

def profile_view(request, username=None):
    if username is None:
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        profile_user = request.user
    else:
        profile_user = User.objects.filter(username=username).first()
        if not profile_user:
            return redirect('/questions/')

    submissions = Submission.objects.filter(user=profile_user)
    total_submissions = submissions.count()
    total_score = submissions.aggregate(total=Sum('score'))['total'] or 0
    problems_solved = submissions.filter(score__gt=0).values('question').distinct().count()
    easy_solved   = submissions.filter(score__gt=0, question__difficulty='Easy').values('question').distinct().count()
    medium_solved = submissions.filter(score__gt=0, question__difficulty='Medium').values('question').distinct().count()
    hard_solved   = submissions.filter(score__gt=0, question__difficulty='Hard').values('question').distinct().count()

    all_scores = Submission.objects.values('user').annotate(total=Sum('score')).order_by('-total')
    rank = 1
    for i, entry in enumerate(all_scores):
        if entry['user'] == profile_user.pk:
            rank = i + 1
            break

    recent_submissions = submissions.order_by('-submitted_at')[:10]

    return render(request, 'accounts/profile.html', {
        'profile_user':      profile_user,
        'total_submissions': total_submissions,
        'total_score':       total_score,
        'problems_solved':   problems_solved,
        'easy_solved':       easy_solved,
        'medium_solved':     medium_solved,
        'hard_solved':       hard_solved,
        'rank':              rank,
        'recent_submissions': recent_submissions,
    })