from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Sum, Count
from submissions.models import Submission
from questions.models import Question
from .forms import QuestionForm

User = get_user_model()

def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    # Stats
    total_questions   = Question.objects.count()
    total_candidates  = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_submissions = Submission.objects.count()

    # Top candidates by score
    top_candidates = (
        User.objects.filter(is_staff=False, is_superuser=False)
        .annotate(
            total_score=Sum('submission__score'),
            problems_solved=Count('submission__question', distinct=True)
        )
        .order_by('-total_score')[:10]
    )

    # Question list (read-only, no solve button)
    questions = Question.objects.all().order_by('difficulty')

    # Recent submissions
    recent_submissions = (
        Submission.objects.select_related('user', 'question')
        .order_by('-submitted_at')[:20]
    )

    return render(request, 'recruiter/dashboard.html', {
        'total_questions':    total_questions,
        'total_candidates':   total_candidates,
        'total_submissions':  total_submissions,
        'top_candidates':     top_candidates,
        'questions':          questions,
        'recent_submissions': recent_submissions,
        'active_nav':         'overview',
    })


def recruiter_problem_bank(request):
    """Read-only problem bank for recruiters: same search/filter behaviour as
    the candidate-side Problem Bank, but with a Created Date column instead
    of the Solve action."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    questions = Question.objects.all().order_by('-created_at')

    search = request.GET.get('search', '')
    if search:
        questions = questions.filter(title__icontains=search)

    topic = request.GET.get('topic', '')
    if topic:
        questions = questions.filter(topic=topic)

    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    topics = Question.objects.order_by('topic').values_list('topic', flat=True).distinct()

    return render(request, 'recruiter/problem_bank.html', {
        'questions':       questions,
        'search':          search,
        'topic':           topic,
        'difficulty':      difficulty,
        'topics':          topics,
        'total_questions': Question.objects.count(),
        'active_nav':      'problems',
    })


def recruiter_add_question(request):
    """Lets a recruiter add a new question directly to the problem bank,
    the same underlying Question model candidates solve from."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added to the problem bank.')
            return redirect('/recruiter/problems/')
    else:
        form = QuestionForm()

    return render(request, 'recruiter/question_form.html', {
        'form':       form,
        'active_nav': 'problems',
    })


def recruiter_delete_question(request, pk):
    """Deletes a question from the problem bank. POST only, with a
    confirm prompt handled client-side in the template."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    if request.method == 'POST':
        question = Question.objects.filter(pk=pk).first()
        if question:
            question.delete()
            messages.success(request, 'Question deleted from the problem bank.')
        else:
            messages.error(request, 'Question not found.')

    return redirect('/recruiter/problems/')


def recruiter_submissions(request):
    """All Submissions view, aggregated per problem: title, level, total
    number of submissions across all candidates, and (once tracked) the
    average time taken to submit."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    questions = Question.objects.annotate(
        submission_count=Count('submission')
    ).order_by('-submission_count')

    search = request.GET.get('search', '')
    if search:
        questions = questions.filter(title__icontains=search)

    topic = request.GET.get('topic', '')
    if topic:
        questions = questions.filter(topic=topic)

    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    topics = Question.objects.order_by('topic').values_list('topic', flat=True).distinct()

    return render(request, 'recruiter/all_submissions.html', {
        'questions':  questions,
        'search':     search,
        'topic':      topic,
        'difficulty': difficulty,
        'topics':     topics,
        'active_nav': 'submissions',
    })
