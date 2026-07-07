import json

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Contest, ContestRegistration
from submissions.models import Submission
from submissions.executor import run_code as execute_code


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _auto_submitted_result_redirect(contest):
    """Bounce a locked-out (auto-submitted) candidate to the results page,
    with a flag the template uses to show the 'auto-submitted' banner."""
    return redirect(reverse('contest_result', kwargs={'pk': contest.pk}) + '?auto_submitted=1')


def _get_live_contest_and_question(request, pk, question_pk):
    """Shared guard for the contest arena: must be registered, contest must
    be live right now, and the question must actually belong to it.

    Also enforces proctoring: once a candidate has been auto-submitted
    (3rd tab-switch violation), they are locked out of the arena entirely
    and bounced to the results page — this is what stops someone from
    dodging the lockout with a page refresh or by navigating back in."""
    contest = get_object_or_404(Contest, pk=pk)
    question = get_object_or_404(contest.questions, pk=question_pk)

    registration = ContestRegistration.objects.filter(contest=contest, user=request.user).first()
    if registration is None:
        return contest, question, None, redirect('contest')

    if registration.auto_submitted:
        return contest, question, registration, _auto_submitted_result_redirect(contest)

    now = timezone.now()
    if now < contest.start_time:
        return contest, question, registration, redirect('contest')
    if now > contest.end_time:
        return contest, question, registration, redirect('contest_result', pk=contest.pk)

    return contest, question, registration, None


SUPPORTED_LANGUAGES = [
    {'name': 'Python', 'icon': 'fa-brands fa-python', 'color': '#00fff7'},
    {'name': 'JavaScript', 'icon': 'fa-brands fa-js', 'color': '#ffc107'},
    {'name': 'Java', 'icon': 'fa-brands fa-java', 'color': '#ff2d78'},
    {'name': 'C++', 'icon': 'fa-solid fa-code', 'color': '#b026ff'},
]


def contest_detail(request, pk):
    """The 'Register' landing page for a contest — mirrors a typical
    contest-info page: description, rules, supported languages and a
    preview of the problems, with the actual Register action living here."""
    contest = get_object_or_404(Contest, pk=pk)
    questions = contest.questions.all().order_by('id')

    is_registered = False
    if request.user.is_authenticated:
        is_registered = ContestRegistration.objects.filter(contest=contest, user=request.user).exists()

    difficulty_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}
    for q in questions:
        if q.difficulty in difficulty_counts:
            difficulty_counts[q.difficulty] += 1

    return render(request, 'contest/contest_detail.html', {
        'contest': contest,
        'questions': questions,
        'is_registered': is_registered,
        'languages': SUPPORTED_LANGUAGES,
        'difficulty_counts': difficulty_counts,
        'now': timezone.now(),
    })


def contest_leaderboard_view(request):
    """Overall contest leaderboard — every contestant who has registered for
    at least one contest, ranked across ALL contests by total score (and
    problems solved as the tiebreaker)."""
    contests = Contest.objects.all()
 
    totals = {}   # user_id -> {'username': ..., 'score': 0, 'solved': 0, 'contests': set()}
 
    for contest in contests:
        questions = contest.questions.all()
        window_end = min(timezone.now(), contest.end_time)
 
        subs = Submission.objects.filter(
            question__in=questions,
            submitted_at__gte=contest.start_time,
            submitted_at__lte=window_end,
        ).select_related('user', 'question')
 
        best_scores = {}  # user_id -> {question_id: score}
        for s in subs:
            uid = s.user_id
            best_scores.setdefault(uid, {})
            if s.question_id not in best_scores[uid] or s.score > best_scores[uid][s.question_id]:
                best_scores[uid][s.question_id] = s.score
 
        for uid, qscores in best_scores.items():
            row = totals.setdefault(uid, {'username': None, 'score': 0, 'solved': 0, 'contests': set()})
            row['score'] += sum(qscores.values())
            row['solved'] += sum(1 for v in qscores.values() if v == 100)
            row['contests'].add(contest.pk)
 
    # Make sure every registered contestant appears, even with 0 activity.
    registrations = ContestRegistration.objects.select_related('user').all()
    for reg in registrations:
        row = totals.setdefault(reg.user_id, {'username': None, 'score': 0, 'solved': 0, 'contests': set()})
        row['username'] = reg.user.username
        row['contests'].add(reg.contest_id)
 
    User = get_user_model()
    usernames = {u.id: u.username for u in User.objects.filter(id__in=totals.keys())}
 
    leaderboard = []
    for uid, row in totals.items():
        leaderboard.append({
            'user_id': uid,
            'username': row['username'] or usernames.get(uid, 'unknown'),
            'score': round(row['score'], 1),
            'solved': row['solved'],
            'contests_taken': len(row['contests']),
            'is_me': request.user.is_authenticated and uid == request.user.id,
        })
 
    leaderboard.sort(key=lambda r: (-r['score'], -r['solved'], -r['contests_taken']))
    for i, row in enumerate(leaderboard, start=1):
        row['rank'] = i
 
    return render(request, 'contest/leaderboard.html', {
        'leaderboard': leaderboard,
    })
 
 
def contest_view(request):
    now = timezone.now()
    upcoming = Contest.objects.filter(is_active=True, start_time__gt=now).order_by('start_time')
    active_all = Contest.objects.filter(is_active=True, start_time__lte=now, end_time__gte=now)
    past = Contest.objects.filter(end_time__lt=now).order_by('-end_time')[:10]

    registered_ids = []
    my_submitted_ids = []

    if request.user.is_authenticated:
        registered_ids = list(
            ContestRegistration.objects.filter(user=request.user).values_list('contest_id', flat=True)
        )
        for c in past:
            solved_any = Submission.objects.filter(
                user=request.user,
                question__in=c.questions.all(),
                submitted_at__gte=c.start_time,
                submitted_at__lte=c.end_time,
            ).exists()
            if solved_any:
                my_submitted_ids.append(c.pk)

    # A contest only moves into "Live Now" for candidates who registered
    # while it was still upcoming — unregistered candidates aren't allowed
    # to take the test, so it shouldn't surface there for them at all.
    if request.user.is_authenticated:
        active = active_all.filter(pk__in=registered_ids)
    else:
        active = Contest.objects.none()

    has_unregistered_live = active_all.exclude(pk__in=registered_ids).exists()

    return render(request, 'contest/contest.html', {
        'active_contests': active,
        'upcoming_contests': upcoming,
        'past_contests': past,
        'registered_ids': registered_ids,
        'my_submitted_ids': my_submitted_ids,
        'has_unregistered_live': has_unregistered_live,
        'now': now,
    })


@login_required
def register_contest(request, pk):
    contest = get_object_or_404(Contest, pk=pk)

    # Registration is only allowed before a contest goes live — once it
    # starts, late registrants shouldn't be able to join and take the test.
    if timezone.now() >= contest.start_time:
        if _is_ajax(request):
            return JsonResponse({'ok': False, 'error': 'Registration is closed — this contest has already started.'}, status=403)
        messages.error(request, f'Registration for {contest.title} is closed — it has already started.')
        return redirect('/contest/')

    ContestRegistration.objects.get_or_create(contest=contest, user=request.user)

    if _is_ajax(request):
        return JsonResponse({'ok': True, 'registered': True})

    messages.success(request, f'Registered for {contest.title}!')
    return redirect('/contest/')


@login_required
def leave_contest(request, pk):
    contest = get_object_or_404(Contest, pk=pk)

    # Once a contest has gone live, registrants must not be able to leave it
    # (and thereby dodge/re-join) mid-contest.
    if timezone.now() >= contest.start_time:
        if _is_ajax(request):
            return JsonResponse({'ok': False, 'error': 'You cannot leave a contest that is already live.'}, status=403)
        messages.error(request, f'You cannot leave {contest.title} — it has already started.')
        return redirect('/contest/')

    ContestRegistration.objects.filter(contest=contest, user=request.user).delete()

    if _is_ajax(request):
        return JsonResponse({'ok': True, 'registered': False})

    messages.success(request, f'You left {contest.title}.')
    return redirect('/contest/')


# ─────────────────────────────────────────────────────────────────
# Proctoring — anti-tab-switching
#
# The browser only ever *reports* a suspected violation; the server is
# the single source of truth for the count and for deciding when the
# 3-strikes threshold is crossed. This means:
#   - refreshing the page can't reset the count (it lives on the
#     ContestRegistration row, not in localStorage/sessionStorage),
#   - a user can't spoof "auto_submit: true" client-side — the server
#     only reports it once its own persisted counter says so,
#   - concurrent/duplicate beacons (e.g. blur + visibilitychange firing
#     for the same tab-switch) are handled with a row-level lock so the
#     count can't be inflated by a race condition.
# ─────────────────────────────────────────────────────────────────

MAX_CONTEST_VIOLATIONS = 3  # 2 warnings; the 3rd violation triggers auto-submit


@login_required
@require_POST
def contest_report_violation(request, pk):
    """Called by the arena's JS whenever the candidate switches tabs,
    switches apps, minimizes the window, or otherwise loses focus/
    visibility while a contest is live. Increments the persisted
    violation counter and tells the client whether this crossed the
    auto-submit threshold.

    Uses normal (non-exempt) CSRF protection — the arena template already
    sends the session's CSRF token via the X-CSRFToken header, same as
    the existing run/submit endpoints.
    """
    contest = get_object_or_404(Contest, pk=pk)

    # Only meaningful while the contest is actually live; ignore stray
    # beacons from a stale/backgrounded tab for a contest that has since
    # ended or hasn't started (nothing to enforce in either case).
    if contest.status != 'live':
        return JsonResponse({'ok': False, 'error': 'Contest is not currently live.'}, status=400)

    with transaction.atomic():
        registration = ContestRegistration.objects.select_for_update().filter(
            contest=contest, user=request.user
        ).first()

        if registration is None:
            return JsonResponse({'ok': False, 'error': 'You are not registered for this contest.'}, status=403)

        # Already locked out by an earlier violation report (e.g. a
        # duplicate beacon arriving after the auto-submit one) — tell the
        # client to redirect without counting it again.
        if registration.auto_submitted:
            return JsonResponse({
                'ok': True,
                'violation_count': registration.violation_count,
                'auto_submit': True,
            })

        registration.violation_count += 1
        should_auto_submit = registration.violation_count >= MAX_CONTEST_VIOLATIONS

        update_fields = ['violation_count']
        if should_auto_submit:
            registration.auto_submitted = True
            registration.auto_submitted_at = timezone.now()
            update_fields += ['auto_submitted', 'auto_submitted_at']

        registration.save(update_fields=update_fields)

    return JsonResponse({
        'ok': True,
        'violation_count': registration.violation_count,
        'auto_submit': should_auto_submit,
    })


@login_required
def contest_take_test(request, pk):
    """The 'test page' — the live problem set for a contest a user has registered for."""
    contest = get_object_or_404(Contest, pk=pk)
    registration = ContestRegistration.objects.filter(contest=contest, user=request.user).first()

    if registration is None:
        messages.error(request, 'You need to register for this contest before taking the test.')
        return redirect('/contest/')

    # Proctoring lockout: once auto-submitted, the candidate can't come
    # back to the problem list either — straight to the results page.
    if registration.auto_submitted:
        return _auto_submitted_result_redirect(contest)

    now = timezone.now()

    if now < contest.start_time:
        messages.info(request, 'This contest has not started yet.')
        return redirect('/contest/')

    if now > contest.end_time:
        messages.info(request, 'This contest has ended. Here are the results.')
        return redirect('contest_result', pk=contest.pk)

    questions = contest.questions.all().order_by('id')

    solved_ids = set(
        Submission.objects.filter(
            user=request.user,
            question__in=questions,
            submitted_at__gte=contest.start_time,
            submitted_at__lte=now,
            score=100,
        ).values_list('question_id', flat=True)
    )

    attempted_ids = set(
        Submission.objects.filter(
            user=request.user,
            question__in=questions,
            submitted_at__gte=contest.start_time,
            submitted_at__lte=now,
        ).values_list('question_id', flat=True)
    )

    return render(request, 'contest/take_test.html', {
        'contest': contest,
        'questions': questions,
        'solved_ids': solved_ids,
        'attempted_ids': attempted_ids,
        'now': now,
        # Nav-lock: this view already guarantees the contest is live,
        # registered, and not auto-submitted by this point — so it's
        # exactly the right moment to lock sidebar/topbar navigation.
        'contest_lock': True,
    })


@login_required
def contest_result(request, pk):
    """The 'result page' — real-time leaderboard for a contest, computed from live Submission data."""
    contest = get_object_or_404(Contest, pk=pk)
    questions = contest.questions.all()
    total_problems = questions.count()

    now = timezone.now()
    window_end = min(now, contest.end_time)

    subs = Submission.objects.filter(
        question__in=questions,
        submitted_at__gte=contest.start_time,
        submitted_at__lte=window_end,
    ).select_related('user', 'question').order_by('submitted_at')

    best_scores = {}       # user_id -> {question_id: score}
    last_submission = {}   # user_id -> latest submitted_at counted
    usernames = {}

    for s in subs:
        uid = s.user_id
        usernames[uid] = s.user.username
        best_scores.setdefault(uid, {})
        if s.question_id not in best_scores[uid] or s.score > best_scores[uid][s.question_id]:
            best_scores[uid][s.question_id] = s.score
        if uid not in last_submission or s.submitted_at > last_submission[uid]:
            last_submission[uid] = s.submitted_at

    leaderboard = []
    for uid, qscores in best_scores.items():
        total_score = sum(qscores.values())
        solved = sum(1 for v in qscores.values() if v == 100)
        leaderboard.append({
            'user_id': uid,
            'username': usernames[uid],
            'total_score': round(total_score, 1),
            'solved': solved,
            'last_submission': last_submission.get(uid),
            'is_me': uid == request.user.id,
        })

    leaderboard.sort(key=lambda r: (-r['total_score'], r['last_submission']))
    for i, row in enumerate(leaderboard, start=1):
        row['rank'] = i

    my_row = next((r for r in leaderboard if r['is_me']), None)

    # Proctoring: whether this candidate is permanently locked out of the
    # arena because they were auto-submitted (3rd violation). Read from
    # the persisted registration row — not the one-time '?auto_submitted=1'
    # query param — so the banner/lockout stay correct even if the
    # candidate reloads this page later without that param in the URL.
    registration = ContestRegistration.objects.filter(contest=contest, user=request.user).first()
    auto_submitted_notice = bool(registration and registration.auto_submitted)

    return render(request, 'contest/result.html', {
        'contest': contest,
        'leaderboard': leaderboard,
        'my_row': my_row,
        'total_problems': total_problems,
        'is_live': contest.status == 'live',
        'auto_submitted_notice': auto_submitted_notice,
    })


# ─────────────────────────────────────────────────────────────────
# Contest Arena — a separate, contest-only code editor.
# This is NOT the /questions/<pk>/ editor: it shares the countdown
# with the contest, lets you jump between the contest's problems
# without leaving the arena, and submits against real test cases.
# ─────────────────────────────────────────────────────────────────

@login_required
def contest_solve(request, pk, question_pk):
    contest, question, registration, guard = _get_live_contest_and_question(request, pk, question_pk)
    if guard:
        return guard

    questions = list(contest.questions.all().order_by('id'))
    now = timezone.now()

    subs_qs = Submission.objects.filter(
        user=request.user,
        question__in=questions,
        submitted_at__gte=contest.start_time,
        submitted_at__lte=now,
    )

    solved_ids = set(subs_qs.filter(score=100).values_list('question_id', flat=True))
    attempted_ids = set(subs_qs.values_list('question_id', flat=True))

    last_submission = subs_qs.filter(question=question).order_by('-submitted_at').first()

    current_index = next((i for i, q in enumerate(questions) if q.pk == question.pk), 0)
    prev_question = questions[current_index - 1] if current_index > 0 else None
    next_question = questions[current_index + 1] if current_index < len(questions) - 1 else None

    return render(request, 'contest/solve.html', {
        'contest': contest,
        'question': question,
        'questions': questions,
        'question_number': current_index + 1,
        'total_questions': len(questions),
        'prev_question': prev_question,
        'next_question': next_question,
        'solved_ids': solved_ids,
        'attempted_ids': attempted_ids,
        'last_submission': last_submission,
        # Proctoring: restore the candidate's current warning count so a
        # page refresh doesn't reset it back to zero on the client.
        'initial_violation_count': registration.violation_count,
        # Nav-lock: same reasoning as contest_take_test — arena guard has
        # already confirmed this is a live, in-progress attempt.
        'contest_lock': True,
    })


@csrf_exempt
@login_required
@require_POST
def contest_run_code(request, pk, question_pk):
    """Quick 'Run' against the question's visible sample I/O only —
    does not touch hidden test cases and never creates a Submission."""
    contest, question, registration, guard = _get_live_contest_and_question(request, pk, question_pk)
    if guard:
        return JsonResponse({'error': 'Contest is not currently live for you.'}, status=403)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    code = data.get('code', '')
    language = data.get('language', 'python')
    sample_input = question.sample_input or ''

    stdout, stderr = execute_code(code, language, sample_input)

    return JsonResponse({
        'stdout': stdout,
        'stderr': stderr,
        'expected': question.sample_output or '',
    })


@csrf_exempt
@login_required
@require_POST
def contest_submit_solution(request, pk, question_pk):
    """Runs the code against every test case for the question, stores a
    Submission (so the arena table + live leaderboard update instantly),
    and returns per-case verdicts (hidden cases are reported pass/fail only)."""
    contest, question, registration, guard = _get_live_contest_and_question(request, pk, question_pk)
    if guard:
        return JsonResponse({'error': 'Contest is not currently live for you.'}, status=403)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    code = data.get('code', '')
    language = data.get('language', 'python')

    test_cases = list(question.test_cases.all())
    if not test_cases:
        # Fall back to the sample input/output pair if no TestCase rows exist.
        stdout, stderr = execute_code(code, language, question.sample_input or '')
        passed = int(stdout.strip() == (question.sample_output or '').strip())
        total = 1
        case_results = [{
            'label': 'Sample',
            'passed': bool(passed),
            'hidden': False,
            'input': question.sample_input or '',
            'expected': question.sample_output or '',
            'actual': stdout,
            'stderr': stderr,
        }]
    else:
        passed = 0
        total = len(test_cases)
        case_results = []
        for i, tc in enumerate(test_cases, start=1):
            stdout, stderr = execute_code(code, language, tc.input_data or '')
            ok = stdout.strip() == (tc.expected_output or '').strip()
            passed += int(ok)
            case_results.append({
                'label': f'Test Case {i}',
                'passed': ok,
                'hidden': tc.is_hidden,
                'input': '' if tc.is_hidden else (tc.input_data or ''),
                'expected': '' if tc.is_hidden else (tc.expected_output or ''),
                'actual': '' if tc.is_hidden else stdout,
                'stderr': '' if tc.is_hidden else stderr,
            })

    score = round((passed / total) * 100, 1) if total else 0
    result = 'Accepted' if passed == total and total > 0 else 'Wrong Answer'

    Submission.objects.create(
        user=request.user,
        question=question,
        code=code,
        language=language,
        result=result,
        score=score,
        passed_cases=passed,
        total_cases=total,
    )

    return JsonResponse({
        'result': result,
        'score': score,
        'passed': passed,
        'total': total,
        'cases': case_results,
    })
 
 
