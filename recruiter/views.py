import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.utils import timezone

from submissions.models import Submission
from questions.models import Question, TestCase
from contest.models import Contest, ContestMCQ, ContestRegistration

User = get_user_model()

def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    # Stats
    # Problem Bank only counts standalone questions, never contest-only ones.
    total_questions   = Question.objects.filter(contests__isnull=True).count()
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

    # Question list (read-only, no solve button) — Problem Bank only,
    # excludes any question that belongs to a contest.
    questions = Question.objects.filter(contests__isnull=True).order_by('difficulty')

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
    })


def recruiter_contests(request):
    """The dedicated 'Contests' page — lists contests a recruiter has
    created and hosts the contest-creation form (name, MCQs, programming
    questions, allowed languages, etc). GET renders the page; POST (JSON,
    from the Create Contest button) validates and persists everything."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    if request.method == 'POST':
        return _create_contest(request)

    contests = Contest.objects.all().order_by('-start_time')
    # Annotate registration counts for the management list.
    contest_rows = []
    for c in contests:
        contest_rows.append({
            'contest': c,
            'registrations': c.registrations.count(),
        })

    return render(request, 'recruiter/contests.html', {
        'username': request.user.username,
        'contest_rows': contest_rows,
        'language_choices': Contest.LANGUAGE_CHOICES,
        'difficulty_choices': ContestMCQ.DIFFICULTY_CHOICES,
    })


def _create_contest(request):
    """Validates and persists a new contest, its MCQs, and its programming
    questions (as fresh Question + TestCase rows) in one transaction.
    Returns JSON — the page's JS shows field errors or a success toast."""
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'errors': {'__all__': 'Invalid request payload.'}}, status=400)

    errors = {}

    title = (payload.get('title') or '').strip()
    if not title:
        errors['title'] = 'Contest name is required.'

    description = (payload.get('description') or '').strip()
    topic = (payload.get('topic') or '').strip()

    start_date = (payload.get('start_date') or '').strip()
    start_time_str = (payload.get('start_time') or '').strip()
    start_dt = None
    if not start_date or not start_time_str:
        errors['start'] = 'Start date and start time are required.'
    else:
        try:
            naive = datetime.strptime(f'{start_date} {start_time_str}', '%Y-%m-%d %H:%M')
            start_dt = timezone.make_aware(naive) if timezone.is_naive(naive) else naive
        except ValueError:
            errors['start'] = 'Invalid start date/time format.'

    if start_dt and start_dt < timezone.now():
        errors['start'] = 'Contest start date/time cannot be in the past.'

    duration = payload.get('duration')
    try:
        duration = int(duration)
        if duration <= 0:
            errors['duration'] = 'Duration must be greater than zero.'
            duration = None
    except (TypeError, ValueError):
        errors['duration'] = 'Duration must be a whole number of minutes.'
        duration = None

    valid_lang_codes = {code for code, _ in Contest.LANGUAGE_CHOICES}
    allowed_languages = [l for l in (payload.get('allowed_languages') or []) if l in valid_lang_codes]
    if not allowed_languages:
        errors['allowed_languages'] = 'Select at least one allowed programming language.'

    raw_mcqs = payload.get('mcqs') or []
    raw_questions = payload.get('programming_questions') or []
    if not raw_mcqs and not raw_questions:
        errors['questions'] = 'Add at least one MCQ or programming question.'

    clean_mcqs = []
    for i, m in enumerate(raw_mcqs):
        q_text = (m.get('question_text') or '').strip()
        opts = {k: (m.get(k) or '').strip() for k in ('option_a', 'option_b', 'option_c', 'option_d')}
        correct = (m.get('correct_option') or '').strip().upper()
        if not q_text or not all(opts.values()) or correct not in ('A', 'B', 'C', 'D'):
            errors[f'mcq_{i}'] = f'MCQ #{i + 1} is missing the question text, an option, or the correct answer.'
            continue
        clean_mcqs.append({
            'question_text': q_text,
            **opts,
            'correct_option': correct,
            'difficulty': m.get('difficulty') if m.get('difficulty') in dict(ContestMCQ.DIFFICULTY_CHOICES) else 'Easy',
            'marks': max(1, int(m.get('marks') or 1)),
            'order': i,
        })

    clean_questions = []
    for i, q in enumerate(raw_questions):
        q_title = (q.get('title') or '').strip()
        q_desc = (q.get('description') or '').strip()
        if not q_title or not q_desc:
            errors[f'question_{i}'] = f'Programming question #{i + 1} needs at least a title and a description.'
            continue
        clean_questions.append({
            'title': q_title,
            'description': q_desc,
            'constraints': (q.get('constraints') or '').strip(),
            'input_format': (q.get('input_format') or '').strip(),
            'output_format': (q.get('output_format') or '').strip(),
            'sample_input': (q.get('sample_input') or '').strip(),
            'sample_output': (q.get('sample_output') or '').strip(),
            'hidden_test_cases': q.get('hidden_test_cases') or [],
            'memory_limit_mb': max(16, int(q.get('memory_limit_mb') or 256)),
            'marks': max(0, int(q.get('marks') or 0)),
        })

    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    end_dt = start_dt + timedelta(minutes=duration)

    with transaction.atomic():
        contest = Contest.objects.create(
            title=title,
            description=description,
            topic=topic,
            start_time=start_dt,
            end_time=end_dt,
            allowed_languages=','.join(allowed_languages),
            is_active=True,
        )

        for m in clean_mcqs:
            ContestMCQ.objects.create(contest=contest, **m)

        for q in clean_questions:
            hidden_cases = q.pop('hidden_test_cases')
            question = Question.objects.create(
                title=q['title'],
                description=q['description'],
                difficulty='Medium',  # not collected by this form; a sensible default
                sample_input=q['sample_input'],
                sample_output=q['sample_output'],
                constraints=q['constraints'],
                input_format=q['input_format'],
                output_format=q['output_format'],
                memory_limit_mb=q['memory_limit_mb'],
                marks=q['marks'],
            )
            # The sample also doubles as a visible test case so "Run Code"
            # has something to check against right away.
            if q['sample_output']:
                TestCase.objects.create(
                    question=question, input_data=q['sample_input'],
                    expected_output=q['sample_output'], is_hidden=False,
                )
            for tc in hidden_cases:
                out = (tc.get('output') or '').strip()
                if not out:
                    continue
                TestCase.objects.create(
                    question=question,
                    input_data=(tc.get('input') or '').strip(),
                    expected_output=out,
                    is_hidden=True,
                )
            contest.questions.add(question)

    return JsonResponse({
        'ok': True,
        'contest_id': contest.pk,
        'message': f'Contest "{contest.title}" created successfully!',
    })
