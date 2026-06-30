from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import Sum, Count, Avg
from submissions.models import Submission

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request,
            username=request.POST['username'],
            password=request.POST['password'])
        role = request.POST.get('role', 'candidate')
        if user:
            login(request, user)
            if role == 'admin' or user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('/questions/')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        email = request.POST.get('email', '')
        if username and password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password, email=email)
                return redirect('/accounts/login/')
    return render(request, 'accounts/register.html')

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
    easy_solved = submissions.filter(score__gt=0, question__difficulty='Easy').values('question').distinct().count()
    medium_solved = submissions.filter(score__gt=0, question__difficulty='Medium').values('question').distinct().count()
    hard_solved = submissions.filter(score__gt=0, question__difficulty='Hard').values('question').distinct().count()

    all_scores = Submission.objects.values('user').annotate(total=Sum('score')).order_by('-total')
    rank = 1
    for i, entry in enumerate(all_scores):
        if entry['user'] == profile_user.pk:
            rank = i + 1
            break

    recent_submissions = submissions.order_by('-submitted_at')[:10]

    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'total_submissions': total_submissions,
        'total_score': total_score,
        'problems_solved': problems_solved,
        'easy_solved': easy_solved,
        'medium_solved': medium_solved,
        'hard_solved': hard_solved,
        'rank': rank,
        'recent_submissions': recent_submissions,
    })