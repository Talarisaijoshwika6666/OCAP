from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Submission
from .executor import run_code
from questions.models import Question

@login_required
def submit_code(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        test_cases = question.test_cases.all()
        total = test_cases.count()
        passed = 0
        results = []

        for tc in test_cases:
            output, error = run_code(code, language, tc.input_data)
            expected = tc.expected_output.strip()
            ok = (output == expected)
            if ok:
                passed += 1
            if not tc.is_hidden:
                results.append({
                    'input': tc.input_data,
                    'expected': expected,
                    'got': output,
                    'error': error,
                    'passed': ok,
                })

        score = round((passed / total) * 100) if total > 0 else 0

        sub = Submission.objects.create(
            user=request.user,
            question=question,
            code=code,
            language=language,
            score=score,
            passed_cases=passed,
            total_cases=total,
            result=str(results),
        )

        return render(request, 'submissions/result.html', {
            'question': question,
            'passed': passed,
            'total': total,
            'score': score,
            'results': results,
            'language': language,
        })

    return redirect(f'/questions/{question_id}/')

@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(
        user=request.user
    ).select_related('question').order_by('-submitted_at')[:20]
    return render(request, 'submissions/my_submissions.html', {
        'submissions': submissions
    })