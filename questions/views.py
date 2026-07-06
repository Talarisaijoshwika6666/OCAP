from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Question, Bookmark
import subprocess
import json

def question_list(request):
    questions = Question.objects.all().order_by('id')
    search = request.GET.get('search', '')
    if search:
        questions = questions.filter(title__icontains=search)
    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
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
    return render(request, 'questions/question_detail.html', {
        'question': question,
    })

@csrf_exempt
@login_required
def run_code(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')
        try:
            if language == 'python':
                proc = subprocess.run(
                    ['python', '-c', code],
                    capture_output=True, text=True, timeout=5
                )
                output = proc.stdout or proc.stderr
            else:
                output = '// Only Python execution supported currently.'
        except subprocess.TimeoutExpired:
            output = '// Error: Code timed out (5 second limit)'
        except Exception as e:
            output = f'// Error: {str(e)}'
        return JsonResponse({'output': output})

@login_required
def submit_solution(request, pk):
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=pk)
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        try:
            proc = subprocess.run(
                ['python', '-c', code],
                capture_output=True, text=True, timeout=5
            )
            actual_output = proc.stdout.strip()
            expected_output = question.sample_output.strip() if question.sample_output else ''
            result = 'Accepted' if actual_output == expected_output else 'Wrong Answer'
        except subprocess.TimeoutExpired:
            result = 'Time Limit Exceeded'
        except Exception:
            result = 'Runtime Error'

        from submissions.models import Submission
        score = 100 if result == 'Accepted' else 0
        Submission.objects.create(
            user=request.user,
            question=question,
            code=code,
            language=language,
            result=result,
            score=score
        )
        return redirect(f'/questions/{pk}/?result={result}')
    return redirect(f'/questions/{pk}/')