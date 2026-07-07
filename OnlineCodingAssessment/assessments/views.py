from django.shortcuts import render
from assessments.models import Submission
from django.db.models import Sum

def leaderboard(request):
    scores = Submission.objects.values('user_username').annotate(total=Sum('score')).order_by('-total')
    total=Sum('Score').order_by('-total')
    return render(request, 'leaderboard/leaderboard.html',{'scores':scores})