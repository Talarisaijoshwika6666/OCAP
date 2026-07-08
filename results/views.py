import json
 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
 
from assessments.models import Assessment, Question
from submissions.executor import run_code
 
from .models import CandidateAnswer, Result
 
 
@login_required
def take_test(request, assessment_id):
    """Show test questions to candidate — one question at a time, MCQ + Coding."""
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = Question.objects.filter(assessment=assessment).order_by('id')
 
    if not questions.exists():
        messages.error(request, 'No questions found for this assessment.')
        return redirect('assessments')
 
    total_marks = sum(q.marks for q in questions)
 
    return render(request, 'results/take_test.html', {
        'assessment': assessment,
        'questions': questions,
        'total_marks': total_marks,
    })
 
 
@login_required
@require_POST
def run_sample(request, assessment_id, question_id):
    """AJAX: run candidate code against this coding question's sample test cases only."""
    question = get_object_or_404(Question, pk=question_id, assessment_id=assessment_id)
 
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST
 
    code = data.get('code', '')
    language = data.get('language', question.language or 'python')
 
    sample_cases = list(question.test_cases.filter(is_sample=True))
    results = []
    for tc in sample_cases:
        stdout, stderr = run_code(code, language, tc.input_data or '')
        passed = stdout.strip() == (tc.expected_output or '').strip() and not stderr
        results.append({
            'input': tc.input_data,
            'expected': tc.expected_output,
            'actual': stdout if not stderr else stderr,
            'passed': passed,
            'error': bool(stderr),
        })
 
    return JsonResponse({'results': results})
 
 
@login_required
@require_POST
def submit_test(request, assessment_id):
    """Handle full test submission — scores MCQ + Coding questions and stores answers."""
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    questions = Question.objects.filter(assessment=assessment).order_by('id')
 
    correct_answers = 0
    wrong_answers = 0
    total_score = 0.0
    total_marks = sum(q.marks for q in questions)
    answered_questions = []

    for question in questions:
        selected = request.POST.get(f'question_{question.id}')
        if selected:
            is_correct = (selected.lower() == question.correct_option.lower())
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
    )
 
    for question in questions:
        if question.question_type == 'coding':
            code = request.POST.get(f'code_{question.id}', '')
            language = request.POST.get(f'language_{question.id}', question.language or 'python')
 
            test_cases = list(question.test_cases.all())
            total_tc = len(test_cases)
            passed_tc = 0
 
            if code.strip():
                for tc in test_cases:
                    stdout, stderr = run_code(code, language, tc.input_data or '')
                    if not stderr and stdout.strip() == (tc.expected_output or '').strip():
                        passed_tc += 1
 
            marks_awarded = round((passed_tc / total_tc) * question.marks, 2) if total_tc else 0
            is_correct = total_tc > 0 and passed_tc == total_tc
            total_score += marks_awarded
 
            if is_correct:
                correct_answers += 1
            else:
                wrong_answers += 1
 
            CandidateAnswer.objects.create(
                result=result,
                question=question,
                code=code,
                language=language,
                test_cases_passed=passed_tc,
                total_test_cases=total_tc,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
            )
        else:
            selected = request.POST.get(f'question_{question.id}', '')
            is_correct = bool(selected) and selected.upper() == (question.correct_option or '').upper()
            marks_awarded = question.marks if is_correct else 0
            total_score += marks_awarded
 
            if is_correct:
                correct_answers += 1
            else:
                wrong_answers += 1
 
            CandidateAnswer.objects.create(
                result=result,
                question=question,
                selected_option=selected or None,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
            )
 
    percentage = (total_score / total_marks * 100) if total_marks > 0 else 0
    passed = percentage >= 50
 
    result.score = round(total_score, 2)
    result.correct_answers = correct_answers
    result.wrong_answers = wrong_answers
    result.total_marks = total_marks
    result.percentage = round(percentage, 2)
    result.passed = passed
    result.save()
 
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
    """Show all results for logged in candidate, with pass/fail filter."""
    results = Result.objects.filter(candidate=request.user).order_by('-submitted_at')
 
    status = request.GET.get('status')
    if status == 'passed':
        results = results.filter(passed=True)
    elif status == 'failed':
        results = results.filter(passed=False)
 
    return render(request, 'results/my_results.html', {
        'results': results,
        'status': status or 'all',
    })
