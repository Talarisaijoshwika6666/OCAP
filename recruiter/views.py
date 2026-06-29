from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from submissions.models import Submission
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def recruiter_dashboard(request):
    if not request.user.is_staff:
        return redirect('/questions/')

    top_candidates = (
        Submission.objects
        .values('user__username')
        .annotate(
            total_score=Sum('score'),
            problems_solved=Count('question', distinct=True),
            avg_score=Avg('score'),
        )
        .order_by('-total_score')[:10]
    )

    return render(request, 'recruiter/dashboard.html', {
        'assessments': [],
        'total_assessments': 0,
        'total_questions': Submission.objects.values('question').distinct().count(),
        'total_candidates': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'total_submissions': Submission.objects.count(),
        'top_candidates': top_candidates,
    })