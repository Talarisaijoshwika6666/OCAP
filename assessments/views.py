from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
 
from .models import Assessment, Question
 
 
def assessment_list(request):
    assessments = Assessment.objects.all().order_by('id')
    return render(request, 'assessments/list.html', {'assessments': assessments})
 
 
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
 
