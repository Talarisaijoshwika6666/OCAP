from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from assessments.models import Assessment
from assessments.models import Question
from .models import Result, CandidateAnswer


@login_required
def take_test(request, assessment_id):
    """Show test questions to candidate."""
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = Question.objects.filter(assessment=assessment)

    if not questions.exists():
        messages.error(request, '❌ No questions found for this assessment.')
        return redirect('assessment_list')

    return render(request, 'results/take_test.html', {
        'assessment': assessment,
        'questions': questions,
    })


@login_required
def submit_test(request, assessment_id):
    """Handle form submission and calculate score."""
    if request.method != 'POST':
        return redirect('take_test', assessment_id=assessment_id)

    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = Question.objects.filter(assessment=assessment)

    # Calculate score
    correct_answers = 0
    wrong_answers = 0
    total_score = 0
    total_marks = sum(q.marks for q in questions)
    answered_questions = []

    for question in questions:
        selected = request.POST.get(f'question_{question.id}')
        if selected:
            is_correct = (selected == question.correct_option)
            if is_correct:
                correct_answers += 1
                total_score += question.marks
            else:
                wrong_answers += 1
            answered_questions.append({
                'question': question,
                'selected': selected,
                'is_correct': is_correct,
            })

    # Calculate percentage
    percentage = (total_score / total_marks * 100) if total_marks > 0 else 0
    passed = percentage >= 50  # Pass mark is 50%

    # Save result to database
    result = Result.objects.create(
        candidate=request.user,
        assessment=assessment,
        total_questions=questions.count(),
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        score=total_score,
        total_marks=total_marks,
        percentage=round(percentage, 2),
        passed=passed,
    )

    # Save each answer
    for item in answered_questions:
        CandidateAnswer.objects.create(
            result=result,
            question=item['question'],
            selected_option=item['selected'],
            is_correct=item['is_correct'],
        )

    return redirect('result_detail', result_id=result.id)


@login_required
def result_detail(request, result_id):
    """Show detailed result after test submission."""
    result = get_object_or_404(Result, pk=result_id, candidate=request.user)
    answers = result.answers.select_related('question').all()
    return render(request, 'results/result_detail.html', {
        'result': result,
        'answers': answers,
    })


@login_required
def my_results(request):
    """Show all results for logged in candidate."""
    results = Result.objects.filter(candidate=request.user).order_by('-submitted_at')
    return render(request, 'results/my_results.html', {'results': results})