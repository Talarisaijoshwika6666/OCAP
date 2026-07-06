from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from submissions.models import Submission
from questions.models import Question

User = get_user_model()

def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    # Stats
    # Problem Bank only counts standalone questions, never contest-only ones.
    total_questions   = Question.objects.filter(contests__isnull=True).count()
    total_candidates  = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_submissions = Submission.objects.count()

    # Top candidates by score
    top_candidates = (
        User.objects.filter(is_staff=False, is_superuser=False)
        .annotate(
            total_score=Sum('submission__score'),
            problems_solved=Count('submission__question', distinct=True)
        )
        .order_by('-total_score')[:10]
    )

    # Question list (read-only, no solve button) — Problem Bank only,
    # excludes any question that belongs to a contest.
    questions = Question.objects.filter(contests__isnull=True).order_by('difficulty')

    # Recent submissions
    recent_submissions = (
        Submission.objects.select_related('user', 'question')
        .order_by('-submitted_at')[:20]
    )

    return render(request, 'recruiter/dashboard.html', {
        'total_questions':    total_questions,
        'total_candidates':   total_candidates,
        'total_submissions':  total_submissions,
        'top_candidates':     top_candidates,
        'questions':          questions,
        'recent_submissions': recent_submissions,
    })
