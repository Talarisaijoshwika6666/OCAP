from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Exists, OuterRef, Value, BooleanField
from .models import Question
from submissions.executor import run_code as execute_code

from django.views.decorators.http import require_POST
from .models import Question, Bookmark, TestCase
import subprocess

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
    topic = request.GET.get('topic', '')
    if topic:
        questions = questions.filter(topic=topic)
    bookmarked_only = request.GET.get('bookmarked', '')

    bookmarked_ids = set()
    solved_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(
            Bookmark.objects.filter(user=request.user).values_list('question_id', flat=True)
        )
        from submissions.models import Submission
        solved_ids = set(
            Submission.objects.filter(user=request.user, result='Accepted')
            .values_list('question_id', flat=True)
        )

    if bookmarked_only:
        questions = questions.filter(pk__in=bookmarked_ids)

    topics = Question.objects.order_by('topic').values_list('topic', flat=True).distinct()

    from assessments.utils import ensure_assessments_exist
    ensure_assessments_exist()

    from assessments.models import Assessment
    assessments_qs = Assessment.objects.filter(is_active=True).order_by('-id')[:6]
    assessments = list(assessments_qs)

    return render(request, 'questions/question_list.html', {
        'questions': questions,
        'total_problems': Question.objects.count(),
        'search': search,
        'difficulty': difficulty,
        'status': status,
        'topic': topic,
        'topics': topics,
        'bookmarked_only': bookmarked_only,
        'bookmarked_ids': bookmarked_ids,
        'solved_ids': solved_ids,
        'assessments': assessments,
    })
@login_required
@require_POST
def toggle_bookmark(request, pk):
    """AJAX endpoint: toggle bookmark state for a question and persist it
    immediately so it survives a page refresh."""
    question = get_object_or_404(Question, pk=pk)
    bookmark = Bookmark.objects.filter(user=request.user, question=question).first()
    if bookmark:
        bookmark.delete()
        bookmarked = False
    else:
        Bookmark.objects.create(user=request.user, question=question)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    next_question = Question.objects.filter(id__gt=question.id).order_by('id').first()
    sample_cases = question.test_cases.filter(is_hidden=False)

    # Per-language reference answers, so the "Answer" box can show the
    # candidate the solution in whichever language they're currently coding
    # in, once they've unlocked it after 3 wrong attempts.
    answer_data = {
        'default': question.answer or '',
        'by_language': {
            entry.language: entry.answer
            for entry in question.language_contents.all()
            if entry.answer
        },
    }

    return render(request, 'questions/question_detail.html', {
        'question': question,
        'next_question': next_question,
        'sample_cases': sample_cases,
        'answer_data': answer_data,
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
        visible_cases = [tc for tc in question.get_effective_test_cases() if not tc.is_hidden]

        if not visible_cases and question.sample_input and question.sample_output:
            # This question has real Test case rows in admin, but every one
            # of them is marked "Is hidden" -- fall back to the Sample
            # Input/Output shown on the page so RUN always has something to
            # try against. This only affects the RUN button; Submit still
            # scores against the full hidden test suite as configured.
            visible_cases = [TestCase(
                question=question,
                input_data=question.sample_input,
                expected_output=question.sample_output,
                is_hidden=False,
            )]

        if not visible_cases:
            return JsonResponse({'output': '// No visible sample to run against.', 'results': []})

        # Run against each visible test case
        results = []
        for tc in visible_cases:
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
        result = 'Accepted'
        score = 0

        if language not in SUPPORTED_EXECUTION_LANGUAGES:
            result = f'{language} is not supported'
        else:
            all_cases = question.get_effective_test_cases()
            total_cases = len(all_cases)

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