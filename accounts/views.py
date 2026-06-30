from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Sum
from submissions.models import Submission

User = get_user_model()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@1234"

def login_view(request):
    panel = request.GET.get('panel', 'admin')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        panel    = request.POST.get('panel', 'admin')

        if panel == 'admin':
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                try:
                    db_user = User.objects.get(username=username)
                    login(request, db_user)
                    return redirect('/admin/')
                except User.DoesNotExist:
                    return render(request, 'accounts/login.html', {
                        'error': 'Admin user not found. Run: python manage.py createsuperuser',
                        'panel': 'admin'
                    })
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid admin credentials.',
                    'panel': 'admin'
                })
        else:
            # Candidate panel — admin can also login here
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_superuser or user.is_staff:
                    return redirect('/admin/')
                    return redirect('/')
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid username or password.',
                    'panel': 'candidate'
                })

    return render(request, 'accounts/login.html', {'panel': panel})


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


def register_view(request):
    error = None
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            error = 'Username and password are required.'
        elif len(password1) < 8:
            error = 'Password must be at least 8 characters.'
        elif password1 != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already taken.'
        else:
            User.objects.create_user(username=username, password=password1, email=email)
            return redirect('/accounts/login/?panel=candidate')

    return render(request, 'accounts/register.html', {'error': error})


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
    problems_solved   = submissions.filter(score__gt=0).values('question').distinct().count()
    easy_solved       = submissions.filter(score__gt=0, question__difficulty='Easy').values('question').distinct().count()
    medium_solved     = submissions.filter(score__gt=0, question__difficulty='Medium').values('question').distinct().count()
    hard_solved       = submissions.filter(score__gt=0, question__difficulty='Hard').values('question').distinct().count()

    all_scores = Submission.objects.values('user').annotate(total=Sum('score')).order_by('-total')
    rank = 1
    for i, entry in enumerate(all_scores):
        if entry['user'] == profile_user.pk:
            rank = i + 1
            break

    recent_submissions = submissions.select_related('question').order_by('-submitted_at')[:10]

    return render(request, 'accounts/profile.html', {
        'profile_user':       profile_user,
        'total_submissions':  total_submissions,
        'total_score':        total_score,
        'problems_solved':    problems_solved,
        'easy_solved':        easy_solved,
        'medium_solved':      medium_solved,
        'hard_solved':        hard_solved,
        'rank':               rank,
        'recent_submissions': recent_submissions,
    })