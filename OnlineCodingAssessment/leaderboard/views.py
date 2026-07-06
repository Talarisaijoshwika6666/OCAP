from django.shortcuts import render
from django.contrib.auth import get_user_model
from submissions.models import Submission
from django.db.models import Count

User = get_user_model()

def leaderboard_view(request):
    users = User.objects.all()
    leaderboard = []
    for user in users:
        solved = Submission.objects.filter(
            user=user, result='Accepted'
        ).values('question').distinct().count()
        if solved > 0:
            leaderboard.append({
                'username': user.username,
                'solved': solved,
                'score': solved * 10,
            })
    leaderboard = sorted(leaderboard, key=lambda x: x['solved'], reverse=True)[:50]
    return render(request, 'leaderboard/leaderboard.html', {
        'leaderboard': leaderboard
    })