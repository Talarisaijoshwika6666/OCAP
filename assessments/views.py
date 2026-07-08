from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
 
from .models import Assessment, Question
 
 
def assessment_list(request):
    assessments = Assessment.objects.all().order_by('id')
    return render(request, 'assessments/list.html', {'assessments': assessments})
 
 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Assessment, Question
from submissions.models import Submission

@login_required
def assessment_list(request):
    assessments = Assessment.objects.filter(is_active=True)
    return render(request, 'assessments/list.html', {'assessments': assessments})

@login_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    questions = Question.objects.filter(assessment=assessment)
    return render(request, 'assessments/detail.html', {
        'assessment': assessment,
        'questions': questions,
    })
 
 
@login_required
def take_assessment(request, pk):
    """Entry point kept for backwards-compat URLs — hands off to the real test-taking flow."""
    get_object_or_404(Assessment, pk=pk)
    return redirect('take_test', assessment_id=pk)
 
        'questions': questions
    })

@login_required
def take_assessment(request, pk):
    return redirect('take_test', assessment_id=pk)

def leaderboard(request):
    scores = Submission.objects.values('user__username').annotate(total=Sum('score')).order_by('-total')
    return render(request, 'leaderboard/leaderboard.html', {'scores': scores})
