from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from assessments.models import Assessment
from assessments.models import Question
from results.models import Result
from submissions.models import Submission

@login_required
def candidate_dashboard(request):
    """Main dashboard for candidates"""
    user = request.user
    
    # Get upcoming assessments
    upcoming_assessments = Assessment.objects.filter(is_active=True).exclude(
        id__in=Result.objects.filter(candidate=user).values_list('assessment_id', flat=True)
    )[:5]
    
    # Get previous results
    previous_results = Result.objects.filter(candidate=user).order_by('-submitted_at')[:5]
    
    # Get statistics
    total_tests = Result.objects.filter(candidate=user).count()
    avg_score = Result.objects.filter(candidate=user).aggregate(Avg('score'))['score__avg'] or 0
    best_rank = Result.objects.filter(candidate=user).order_by('rank').first()

    submissions = Submission.objects.filter(candidate=user)
    questions = Question.objects.filter(id__in=submissions.values_list('question_id', flat=True)).distinct()
    total_submissions = submissions.count()
    best_score = Result.objects.filter(candidate=user).aggregate(Avg('score'))['score__avg'] or 0

    problems_solved = submissions.filter(result__in=['AC','Accepted']).values('question').distinct().count()
    easy_solved = submissions.filter(result__in=['AC','Accepted'], question__difficulty='Easy').values('question').distinct().count()
    medium_solved = submissions.filter(result__in=['AC','Accepted'], question__difficulty='Medium').values('question').distinct().count()
    hard_solved = submissions.filter(result__in=['AC','Accepted'], question__difficulty='Hard').values('question').distinct().count()

    context = {
        'questions': questions,
        'total_submissions': total_submissions,
        'best_score': best_score,
        'problems_solved': problems_solved,
        'easy_solved': easy_solved,
        'medium_solved': medium_solved,
        'hard_solved': hard_solved,
        'user': user,
        'upcoming_assessments': upcoming_assessments,
        'previous_results': previous_results,
        'total_tests': total_tests,
        'avg_score': round(avg_score, 1),
        'best_rank': best_rank.rank if best_rank else 'N/A',
    }
    return render(request, 'candidates/dashboard.html', context)

@login_required
def assessment_detail(request, assessment_id):
    """View assessment details"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = Question.objects.filter(assessment=assessment)
    
    context = {
        'assessment': assessment,
        'questions': questions,
        'total_questions': questions.count(),
    }
    return render(request, 'candidates/assessment_detail.html', context)

@login_required
def start_assessment(request, assessment_id):
    """Start assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if already attempted
    if Result.objects.filter(candidate=request.user, assessment=assessment).exists():
        messages.warning(request, 'You have already attempted this assessment!')
        return redirect('candidate_dashboard')
    
    questions = Question.objects.filter(assessment=assessment)
    
    context = {
        'assessment': assessment,
        'questions': questions,
        'duration_minutes': assessment.duration,
    }
    return render(request, 'candidates/take_assessment.html', context)