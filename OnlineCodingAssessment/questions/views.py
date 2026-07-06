from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question
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
    return render(request, 'questions/question_list.html', {
        'questions': questions,
        'total_problems': Question.objects.count(),
        'search': search,
        'difficulty': difficulty,
    })

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