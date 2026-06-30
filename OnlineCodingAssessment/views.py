from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


@login_required
def home_view(request):
    from questions.models import Question
    from submissions.models import Submission

    total_problems = Question.objects.count()
    submissions = Submission.objects.filter(user=request.user)
    problems_solved = submissions.filter(score__gt=0).values('question').distinct().count()
    total_score = submissions.aggregate(total=Sum('score'))['total'] or 0

    all_scores = Submission.objects.values('user').annotate(
        total=Sum('score')
    ).order_by('-total')
    rank = 1
    for i, entry in enumerate(all_scores):
        if entry['user'] == request.user.pk:
            rank = i + 1
            break

    return render(request, 'home.html', {
        'total_problems': total_problems,
        'problems_solved': problems_solved,
        'total_score': total_score,
        'global_rank': rank,
    })