from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Sum
from submissions.models import Submission

User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/questions/')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'accounts/login.html', {})


def logout_view(request):
    logout(request)
    return redirect('/')


def register_view(request):
    if request.method == 'POST':
        username         = request.POST.get('username', '').strip()
        email            = request.POST.get('email', '').strip()
        password         = request.POST.get('password1', '')
        confirm_password = request.POST.get('password2', '')

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
