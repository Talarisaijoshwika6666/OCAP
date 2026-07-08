from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Exists, OuterRef, Value, BooleanField
from .models import Question
from submissions.executor import run_code as execute_code
import json

SUPPORTED_EXECUTION_LANGUAGES = {'python', 'python3', 'java', 'javascript', 'c', 'cpp', 'ruby'}


def question_list(request):
    questions = Question.objects.all().order_by('id')

    search = request.GET.get('search', '')
    if search:
        questions = questions.filter(title__icontains=search)

    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    status = request.GET.get('status', '')

    if request.user.is_authenticated:
        from submissions.models import Submission
        solved_subquery = Submission.objects.filter(
            user=request.user,
            question=OuterRef('pk'),
            result='Accepted',
        )
        questions = questions.annotate(is_solved=Exists(solved_subquery))

        if status == 'solved':
            questions = questions.filter(is_solved=True)
        elif status == 'unsolved':
            questions = questions.filter(is_solved=False)
    else:
        questions = questions.annotate(
            is_solved=Value(False, output_field=BooleanField())
        )
        status = ''

    return render(request, 'questions/question_list.html', {
        'questions': questions,
        'total_problems': Question.objects.count(),
        'search': search,
        'difficulty': difficulty,
        'status': status,
    })


@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    next_question = Question.objects.filter(id__gt=question.id).order_by('id').first()
    sample_cases = question.test_cases.filter(is_hidden=False)
    return render(request, 'questions/question_detail.html', {
        'question': question,
        'next_question': next_question,
        'sample_cases': sample_cases,
    })


@csrf_exempt
@login_required
def run_code(request, pk):
    """
    RUN button — runs against visible (non-hidden) test cases only.
    Input piped via stdin so input() / scanf / Scanner all work.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')

        if language not in SUPPORTED_EXECUTION_LANGUAGES:
            return JsonResponse({
                'output': f'// {language} is not supported. Supported: Python 3, Java, JavaScript, C, C++, Ruby.'
            })

        question = get_object_or_404(Question, pk=pk)
        sample_cases = question.test_cases.filter(is_hidden=False)

        if not sample_cases.exists():
            # No test cases yet — run with sample_input from question
            input_data = question.sample_input or ''
            stdout, stderr = execute_code(code, language, input_data=input_data)
            output = stderr if stderr else (stdout if stdout else '// (no output)')
            return JsonResponse({'output': output, 'results': []})

        # Run against each visible test case
        results = []
        for tc in sample_cases:
            stdout, stderr = execute_code(code, language, input_data=tc.input_data or '')
            actual = stdout if stdout else ''
            expected = tc.expected_output.strip()
            error = stderr if stderr else ''
            passed = (actual.strip() == expected) and not error
            results.append({
                'input': tc.input_data or '(none)',
                'expected': expected,
                'actual': error if error else actual,
                'passed': passed,
            })

        output_lines = []
        for i, r in enumerate(results, 1):
            status = '✓ Passed' if r['passed'] else '✗ Failed'
            output_lines.append(
                f"Test {i}: {status}\n"
                f"  Input:    {r['input']}\n"
                f"  Expected: {r['expected']}\n"
                f"  Got:      {r['actual']}"
            )

        return JsonResponse({
            'output': '\n\n'.join(output_lines),
            'results': results,
        })


@login_required
def submit_solution(request, pk):
    """
    SUBMIT button — runs against ALL test cases (visible + hidden).
    Accepted only when every test case passes.
    Score = (passed / total) * 100.
    """
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=pk)
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        is_auto_submit = request.POST.get('auto_submit') == '1'

        from submissions.models import Submission

        passed_cases = 0
        total_cases = 0
        result = 'Wrong Answer'
        score = 0

        if language not in SUPPORTED_EXECUTION_LANGUAGES:
            result = f'{language} is not supported'
        else:
            all_cases = question.test_cases.all()
            total_cases = all_cases.count()

            if total_cases == 0:
                # Fallback: use sample_input / sample_output
                input_data = question.sample_input or ''
                expected_output = question.sample_output.strip() if question.sample_output else ''
                stdout, error = execute_code(code, language, input_data)

                if error == 'Time Limit Exceeded':
                    result = 'Time Limit Exceeded'
                elif error and not stdout:
                    result = 'Runtime Error'
                else:
                    passed_cases = 1 if stdout.strip() == expected_output else 0
                    result = 'Accepted' if passed_cases == 1 else 'Wrong Answer'
                total_cases = 1
            else:
                result = 'Accepted'
                for tc in all_cases:
                    stdout, error = execute_code(
                        code, language, input_data=tc.input_data or ''
                    )
                    if error == 'Time Limit Exceeded':
                        result = 'Time Limit Exceeded'
                        break
                    elif error and not stdout:
                        result = 'Runtime Error'
                        break
                    elif stdout.strip() == tc.expected_output.strip():
                        passed_cases += 1

                if result == 'Accepted' and passed_cases < total_cases:
                    result = 'Wrong Answer'

            score = round((passed_cases / total_cases) * 100) if total_cases > 0 else 0

        Submission.objects.create(
            user=request.user,
            question=question,
            code=code,
            language=language,
            result=result,
            score=score,
            passed_cases=passed_cases,
            total_cases=total_cases,
        )

        if is_auto_submit:
            return redirect(f'/questions/?timeout_submitted={pk}')

        return redirect(
            f'/questions/{pk}/?result={result}'
            f'&passed={passed_cases}&total={total_cases}'
        )

    return redirect(f'/questions/{pk}/')