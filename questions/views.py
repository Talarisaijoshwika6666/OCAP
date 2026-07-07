from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Exists, OuterRef, Value, BooleanField
from .models import Question
from submissions.executor import run_code as execute_code
import json

SUPPORTED_EXECUTION_LANGUAGES = {'python', 'javascript', 'java', 'ruby', 'cpp', 'c'}


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
        # Anonymous users can't have a solved status, and can't filter by it.
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
    return render(request, 'questions/question_detail.html', {
        'question': question,
        'next_question': next_question,
        'lang_content_json': '{}',
        'supported_languages_json': json.dumps(sorted(SUPPORTED_EXECUTION_LANGUAGES)),
    })

@csrf_exempt
@login_required
def run_code(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')

        if language not in SUPPORTED_EXECUTION_LANGUAGES:
            return JsonResponse({
                'output': f'// {language} execution isn\'t wired up on the server yet.'
            })

        stdout, stderr = execute_code(code, language, input_data='')
        output = stdout if stdout else (stderr or '// (no output)')
        return JsonResponse({'output': output})

@login_required
def submit_solution(request, pk):
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=pk)
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        is_auto_submit = request.POST.get('auto_submit') == '1'

        from submissions.models import Submission

        if language not in SUPPORTED_EXECUTION_LANGUAGES:
            result = f'{language} not supported yet'
            score = 0
        else:
            input_data = question.sample_input or ''
            actual_output, error = execute_code(code, language, input_data)
            expected_output = question.sample_output.strip() if question.sample_output else ''
            if error and not actual_output:
                result = error if error in ('Time Limit Exceeded',) else 'Runtime Error'
            else:
                result = 'Accepted' if actual_output.strip() == expected_output else 'Wrong Answer'
            score = 100 if result == 'Accepted' else 0

        Submission.objects.create(
            user=request.user,
            question=question,
            code=code,
            language=language,
            result=result,
            score=score
        )

        if is_auto_submit:
            return redirect(f'/questions/?timeout_submitted={pk}')

        return redirect(f'/questions/{pk}/?result={result}')
    return redirect(f'/questions/{pk}/')