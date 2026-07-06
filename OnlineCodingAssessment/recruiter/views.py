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
    total_questions   = Question.objects.count()
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

    # Question list (read-only, no solve button)
    questions = Question.objects.all().order_by('difficulty')

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