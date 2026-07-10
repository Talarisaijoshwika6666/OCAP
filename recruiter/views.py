from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q as models_Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from collections import defaultdict
from submissions.models import Submission
from questions.models import Question
from assessments.models import Assessment
from results.models import Result
from contest.models import Contest
from accounts.models import UserSettings
from accounts.forms import (
    UserProfileForm, SettingsPasswordChangeForm, NotificationsSettingsForm,
    EditorPreferencesForm, PrivacySettingsForm,
)
from django.contrib.auth.decorators import login_required

User = get_user_model()

def recruiter_delete_candidate(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    if request.method != 'POST':
        return redirect('recruiter_candidates')

    candidate = get_object_or_404(
        User,
        pk=pk,
        is_staff=False,
        is_superuser=False,
        role='candidate',
        is_registered_candidate=True,
    )
    candidate.delete()
    messages.success(request, 'Candidate deleted successfully.')
    return redirect('recruiter_candidates')


def recruiter_candidates_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    search = request.GET.get('search', '').strip()
    preferred_language_filter = request.GET.get('preferred_language', '').strip()
    problems_solved_filter = request.GET.get('problems_solved', '').strip()
    status_filter = request.GET.get('status', '').strip()

    candidates_qs = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        role='candidate',
        is_registered_candidate=True,
    ).order_by('username')
    if search:
        candidates_qs = candidates_qs.filter(
            models_Q(full_name__icontains=search) |
            models_Q(email__icontains=search) |
            models_Q(username__icontains=search)
        )

    def normalize_language(value):
        if not value:
            return 'Not available'
        mapping = {
            'python': 'Python',
            'java': 'Java',
            'cpp': 'C++',
            'c++': 'C++',
            'c': 'C',
            'javascript': 'JavaScript',
            'js': 'JavaScript',
        }
        return mapping.get(str(value).lower(), str(value).title())

    def is_successful_submission(submission):
        result_value = str(getattr(submission, 'result', '') or '').strip().lower()
        if result_value in {'ac', 'accepted', 'pass', 'passed', 'success', 'successful', 'correct', 'ok'}:
            return True
        if getattr(submission, 'passed_cases', 0) and getattr(submission, 'total_cases', 0):
            if submission.passed_cases >= submission.total_cases:
                return True
        return getattr(submission, 'score', 0) >= 50

    def count_problems_solved(submissions):
        solved_question_ids = set()
        for submission in submissions:
            if is_successful_submission(submission) and getattr(submission.question, 'id', None):
                solved_question_ids.add(submission.question.id)
        return len(solved_question_ids)

    def count_contest_participation(results):
        matched_contest_ids = set()
        for result in results:
            assessment_title = str(getattr(result.assessment, 'title', '') or '').lower()
            for contest in Contest.objects.all():
                contest_title = str(getattr(contest, 'title', '') or '').lower()
                if contest_title and (contest_title in assessment_title or assessment_title in contest_title):
                    matched_contest_ids.add(contest.id)
                    break
        return len(matched_contest_ids)

    candidate_rows = []
    for candidate in candidates_qs:
        results = Result.objects.filter(candidate=candidate).select_related('assessment')
        submissions = Submission.objects.filter(user=candidate).select_related('question')
        avg_score = round(submissions.aggregate(Avg('score'))['score__avg'] or 0, 1)
        preferred_language = 'Not available'
        successful_submissions = [submission for submission in submissions if is_successful_submission(submission)]
        if successful_submissions:
            language_counts = {}
            for submission in successful_submissions:
                language_name = normalize_language(getattr(submission, 'language', ''))
                if language_name == 'Not available':
                    continue
                language_counts[language_name] = language_counts.get(language_name, 0) + 1
            if language_counts:
                preferred_language = max(language_counts.items(), key=lambda item: (item[1], item[0]))[0]
        problems_solved = count_problems_solved(successful_submissions)
        easy_solved = sum(1 for submission in successful_submissions if str(getattr(submission.question, 'difficulty', '') or '').lower() == 'easy')
        medium_solved = sum(1 for submission in successful_submissions if str(getattr(submission.question, 'difficulty', '') or '').lower() == 'medium')
        hard_solved = sum(1 for submission in successful_submissions if str(getattr(submission.question, 'difficulty', '') or '').lower() == 'hard')
        status = 'Active' if (problems_solved > 0 or results.exists() or submissions.exists()) else 'Inactive'

        recent_assessment_history = [
            {
                'title': result.assessment.title,
                'detail': f"Score {result.score} • {'Passed' if result.passed else 'Failed'} • {result.submitted_at.strftime('%b %d, %Y')}",
            }
            for result in results.order_by('-submitted_at')[:5]
        ]

        recent_submission_history = [
            {
                'title': submission.question.title,
                'detail': f"{normalize_language(submission.language)} • {submission.score} • {submission.result or 'Pending'} • {submission.submitted_at.strftime('%b %d, %Y')}",
            }
            for submission in submissions.order_by('-submitted_at')[:5]
        ]

        recent_contest_history = []
        contest_titles = {str(result.assessment.title or '').lower() for result in results}
        for contest in Contest.objects.order_by('-start_time')[:5]:
            contest_title = str(contest.title or '').lower()
            if any(contest_title in assessment_title or assessment_title in contest_title for assessment_title in contest_titles):
                recent_contest_history.append({
                    'title': contest.title,
                    'detail': f"{contest.start_time.strftime('%b %d, %Y')} • Score {next((result.score for result in results if str(result.assessment.title or '').lower() in contest_title or contest_title in str(result.assessment.title or '').lower()), 0)} • Rank {next((result.rank for result in results if str(result.assessment.title or '').lower() in contest_title or contest_title in str(result.assessment.title or '').lower()), 0)}",
                })

        row = {
            'id': candidate.id,
            'name': candidate.full_name or candidate.username,
            'username': candidate.username,
            'email': candidate.email or 'Not provided',
            'mobile': candidate.mobile or 'Not provided',
            'registration_date': candidate.date_joined.strftime('%b %d, %Y') if candidate.date_joined else 'N/A',
            'last_login': candidate.last_login.strftime('%b %d, %Y %H:%M') if candidate.last_login else 'Never',
            'problems_solved': problems_solved,
            'average_score': avg_score,
            'preferred_language': preferred_language,
            'status': status,
            'contest_participation': count_contest_participation(results),
            'total_problems_solved': problems_solved,
            'easy_problems_solved': easy_solved,
            'medium_problems_solved': medium_solved,
            'hard_problems_solved': hard_solved,
            'recent_assessment_history': recent_assessment_history,
            'recent_submission_history': recent_submission_history,
            'recent_contest_history': recent_contest_history,
        }

        if preferred_language_filter and row['preferred_language'] != preferred_language_filter:
            continue
        if problems_solved_filter:
            if problems_solved_filter == 'below-40':
                if row['problems_solved'] >= 40:
                    continue
            elif problems_solved_filter == '40+':
                if row['problems_solved'] < 40:
                    continue
            elif problems_solved_filter == '50+':
                if row['problems_solved'] < 50:
                    continue
            elif problems_solved_filter == '75+':
                if row['problems_solved'] < 75:
                    continue
            elif problems_solved_filter == '100+':
                if row['problems_solved'] < 100:
                    continue
        if status_filter and row['status'] != status_filter:
            continue

        candidate_rows.append(row)

    candidate_rows.sort(key=lambda item: (-item['average_score'], item['name'].lower(), item['id']))
    for index, item in enumerate(candidate_rows, start=1):
        item['global_rank'] = index

    languages = sorted({
        normalize_language(language)
        for language in Submission.objects.exclude(language='').values_list('language', flat=True)
        if normalize_language(language) != 'Not available'
    })
    problem_ranges = [
        ('Below 40', 'below-40'),
        ('40+', '40+'),
        ('50+', '50+'),
        ('75+', '75+'),
        ('100+', '100+'),
    ]

    return render(request, 'recruiter/candidates.html', {
        'username': request.user.username,
        'candidates': candidate_rows,
        'languages': languages,
        'problem_ranges': problem_ranges,
        'search': search,
        'preferred_language': preferred_language_filter,
        'problems_solved': problems_solved_filter,
        'status': status_filter,
    })


def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    from assessments.utils import ensure_assessments_exist
    ensure_assessments_exist()

    # Stats
    total_candidates  = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_assessments = Assessment.objects.count()
    total_problems    = Question.objects.count()
    total_submissions = Submission.objects.count()
    active_assessments = Assessment.objects.filter(is_active=True).count()
    
    avg_score_query = Submission.objects.aggregate(Avg('score'))['score__avg']
    avg_score = round(avg_score_query, 1) if avg_score_query is not None else 0.0

    # Recent Questions (Problem Bank) with submission count
    recent_questions = list(Question.objects.annotate(
        submission_count=Count('submission')
    ).order_by('-id')[:5])

    # Recruitment Insights
    total_subs = Submission.objects.count()
    passed_subs = Submission.objects.filter(score__gte=50).count()
    pass_rate = round((passed_subs / total_subs * 100), 1) if total_subs > 0 else 0.0
    active_candidates_count = Submission.objects.values('user').distinct().count()
    
    popular_lang_query = Submission.objects.values('language').annotate(count=Count('id')).order_by('-count').first()
    popular_lang = popular_lang_query['language'].title() if popular_lang_query else 'N/A'

    insights = {
        'pass_rate': pass_rate,
        'active_candidates': active_candidates_count,
        'popular_lang': popular_lang,
        'avg_score': avg_score,
    }

    # Recent Activity (latest submissions)
    from results.models import Result
    
    class MockUser:
        def __init__(self, username):
            self.username = username

    class MockQuestion:
        def __init__(self, title):
            self.title = title

    class UnifiedActivity:
        def __init__(self, username, submitted_at, question_title, language, score, result):
            self.user = MockUser(username)
            self.submitted_at = submitted_at
            self.question = MockQuestion(question_title)
            self.language = language
            self.score = score
            self.result = result

    real_activity = []
    
    # 1. Fetch real Submissions
    for s in Submission.objects.select_related('user', 'question').order_by('-submitted_at')[:8]:
        real_activity.append(
            UnifiedActivity(
                username=s.user.username,
                submitted_at=s.submitted_at,
                question_title=s.question.title,
                language=s.language.title(),
                score=s.score,
                result=s.result
            )
        )
        
    # 2. Fetch real Results
    for r in Result.objects.select_related('candidate', 'assessment').order_by('-submitted_at')[:8]:
        real_activity.append(
            UnifiedActivity(
                username=r.candidate.username,
                submitted_at=r.submitted_at,
                question_title=r.assessment.title,
                language="Assessment",
                score=r.score,
                result="Passed" if r.passed else "Failed"
            )
        )
        
    # 3. Sort by submitted_at descending
    real_activity.sort(key=lambda x: x.submitted_at, reverse=True)
    recent_activity = real_activity[:8]

    return render(request, 'recruiter/dashboard.html', {
        'username': request.user.username,
        'total_candidates': total_candidates,
        'total_assessments': total_assessments,
        'total_problems': total_problems,
        'total_submissions': total_submissions,
        'active_assessments': active_assessments,
        'avg_score': avg_score,
        'recent_questions': recent_questions,
        'insights': insights,
        'recent_activity': recent_activity,
    })

def _get_contest_results_for_contest(contest):
    results_qs = Result.objects.filter(assessment__title__icontains=contest.title).order_by('-score', 'submitted_at')
    results_list = []
    for idx, r in enumerate(results_qs):
        rank = r.rank if getattr(r, 'rank', 0) > 0 else (idx + 1)
        results_list.append({
            'rank': rank,
            'candidate': r.candidate.username,
            'score': r.score
        })
    return results_list


def recruiter_problem_bank(request):
    """Problem Bank view for recruiters — mirrors the candidate-facing
    question list (search / topic / difficulty filters) but adds
    recruiter-relevant context like per-question submission counts."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    questions = Question.objects.all().order_by('-id')

    search = request.GET.get('search', '')
    if search:
        questions = questions.filter(title__icontains=search)

    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    topic = request.GET.get('topic', '')
    if topic:
        questions = questions.filter(topic=topic)

    topics = Question.objects.order_by('topic').values_list('topic', flat=True).distinct()

    # Annotate with submission stats so recruiters can see how each
    # problem is performing across candidates at a glance.
    questions = questions.annotate(
        submission_count=Count('submission', distinct=True),
        solved_count=Count(
            'submission',
            filter=models_Q(submission__result__in=['AC', 'Accepted']),
            distinct=True,
        ),
    )

    total_problems = Question.objects.count()
    easy_count = Question.objects.filter(difficulty='Easy').count()
    medium_count = Question.objects.filter(difficulty='Medium').count()
    hard_count = Question.objects.filter(difficulty='Hard').count()

    return render(request, 'recruiter/problems.html', {
        'username': request.user.username,
        'questions': questions,
        'search': search,
        'difficulty': difficulty,
        'topic': topic,
        'topics': topics,
        'total_problems': total_problems,
        'easy_count': easy_count,
        'medium_count': medium_count,
        'hard_count': hard_count,
    })


def recruiter_delete_problem(request, pk):
    """Delete a question from the problem bank. Staff-only, POST-only."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    if request.method == 'POST':
        question = get_object_or_404(Question, pk=pk)
        question.delete()

    # Preserve any active filters when redirecting back to the list.
    querystring = request.POST.get('querystring', '')
    redirect_url = '/recruiter/problems/'
    if querystring:
        redirect_url += f'?{querystring}'
    return redirect(redirect_url)


def recruiter_add_problem(request):
    """Create a new question in the problem bank. Staff-only."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    errors = {}
    form_data = {
        'title': '',
        'topic': '',
        'difficulty': 'Easy',
        'description': '',
        'sample_input': '',
        'sample_output': '',
        'hint': '',
        'answer': '',
        'time_limit': 60,
    }

    if request.method == 'POST':
        form_data['title'] = request.POST.get('title', '').strip()
        form_data['topic'] = request.POST.get('topic', '').strip() or 'General'
        form_data['difficulty'] = request.POST.get('difficulty', 'Easy')
        form_data['description'] = request.POST.get('description', '').strip()
        form_data['sample_input'] = request.POST.get('sample_input', '').strip()
        form_data['sample_output'] = request.POST.get('sample_output', '').strip()
        form_data['hint'] = request.POST.get('hint', '').strip()
        form_data['answer'] = request.POST.get('answer', '').strip()
        form_data['time_limit'] = request.POST.get('time_limit', '60').strip()

        if not form_data['title']:
            errors['title'] = 'Title is required.'
        if not form_data['description']:
            errors['description'] = 'Description is required.'
        if form_data['difficulty'] not in dict(Question.DIFFICULTY_CHOICES):
            errors['difficulty'] = 'Choose a valid difficulty.'
        try:
            time_limit_value = int(form_data['time_limit'] or 60)
            if time_limit_value <= 0:
                raise ValueError
        except ValueError:
            errors['time_limit'] = 'Time limit must be a positive whole number.'
            time_limit_value = 60

        if not errors:
            Question.objects.create(
                title=form_data['title'],
                topic=form_data['topic'],
                difficulty=form_data['difficulty'],
                description=form_data['description'],
                sample_input=form_data['sample_input'],
                sample_output=form_data['sample_output'],
                hint=form_data['hint'],
                answer=form_data['answer'],
                time_limit=time_limit_value,
            )
            return redirect('/recruiter/problems/')

    return render(request, 'recruiter/problem_form.html', {
        'username': request.user.username,
        'form_data': form_data,
        'errors': errors,
        'difficulty_choices': Question.DIFFICULTY_CHOICES,
    })


def recruiter_all_submissions(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    def format_duration(seconds):
        if seconds is None:
            return '0m 0s'
        total_seconds = int(seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if hours:
            parts.append(f'{hours}h')
        if minutes:
            parts.append(f'{minutes}m')
        if secs or not parts:
            parts.append(f'{secs}s')
        return ' '.join(parts)

    questions = Question.objects.all().order_by('title')
    rows = []

    for question in questions:
        submissions = Submission.objects.filter(question=question)
        total_submissions = submissions.count()
        accepted = submissions.filter(result__icontains='accepted').count()
        rejected = total_submissions - accepted
        acceptance_rate = round((accepted / total_submissions) * 100, 1) if total_submissions else 0.0
        average_time_seconds = submissions.aggregate(Avg('time_taken_seconds'))['time_taken_seconds__avg'] or 0
        latest_submission = submissions.order_by('-submitted_at').first()
        highest_score = submissions.order_by('-score').first().score if submissions.exists() else 0
        lowest_score = submissions.order_by('score').first().score if submissions.exists() else 0

        rows.append({
            'id': question.id,
            'title': question.title,
            'difficulty': question.difficulty,
            'difficulty_class': question.difficulty.lower(),
            'total_submissions': total_submissions,
            'average_time_seconds': int(average_time_seconds),
            'average_time_display': format_duration(average_time_seconds),
            'accepted': accepted,
            'rejected': rejected,
            'acceptance_rate': acceptance_rate,
            'acceptance_class': 'success' if acceptance_rate >= 70 else 'warning' if acceptance_rate >= 40 else 'danger',
            'last_submission': latest_submission.submitted_at if latest_submission else None,
            'last_submission_display': latest_submission.submitted_at.strftime('%b %d, %Y %H:%M') if latest_submission else 'No submissions',
            'highest_score': int(highest_score) if isinstance(highest_score, (int, float)) else 0,
            'lowest_score': int(lowest_score) if isinstance(lowest_score, (int, float)) else 0,
        })

    total_problems = len(rows)
    total_submissions = sum(item['total_submissions'] for item in rows)
    overall_accepted = sum(item['accepted'] for item in rows)
    overall_acceptance_rate = round((overall_accepted / total_submissions) * 100, 1) if total_submissions else 0.0
    average_submission_time = round(Submission.objects.aggregate(Avg('time_taken_seconds'))['time_taken_seconds__avg'] or 0, 1)
    difficulty_distribution = {
        'Easy': Submission.objects.filter(question__difficulty='Easy').count(),
        'Medium': Submission.objects.filter(question__difficulty='Medium').count(),
        'Hard': Submission.objects.filter(question__difficulty='Hard').count(),
    }
    submissions_by_problem = [
        {'title': item['title'], 'count': item['total_submissions']} for item in rows if item['total_submissions'] > 0
    ]
    daily_trend = []
    for offset in range(6, -1, -1):
        day = timezone.now().date() - timezone.timedelta(days=offset)
        count = Submission.objects.filter(submitted_at__date=day).count()
        daily_trend.append({'label': day.strftime('%b %d'), 'count': count})

    return render(request, 'recruiter/all_submissions.html', {
        'username': request.user.username,
        'rows': rows,
        'stats': {
            'total_problems': total_problems,
            'total_submissions': total_submissions,
            'average_submission_time': int(average_submission_time),
            'overall_acceptance_rate': overall_acceptance_rate,
        },
        'difficulty_distribution': difficulty_distribution,
        'submissions_by_problem': submissions_by_problem,
        'daily_trend': daily_trend,
    })


def recruiter_contest_results(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')

    from django.utils import timezone
    from contest.models import Contest
    from results.models import Result

    now = timezone.now()

    # 1. Fetch upcoming contests
    upcoming_qs = Contest.objects.filter(start_time__gt=now).order_by('start_time')
    upcoming_list = []
    for c in upcoming_qs:
        upcoming_list.append({
            'id': c.id,
            'title': c.title,
            'start_time': c.start_time,
        })
    
    # Fallback to display mock upcoming contests if DB is empty
    if not upcoming_list:
        upcoming_list = [
            {
                'id': 101,
                'title': 'LogicLabs Weekly Contest #43',
                'start_time': timezone.now() + timezone.timedelta(days=6 - timezone.now().weekday() if timezone.now().weekday() < 6 else 6, hours=20 - timezone.now().hour), # Sunday 8 PM
            },
            {
                'id': 102,
                'title': 'LogicLabs Biweekly Contest #22',
                'start_time': timezone.now() + timezone.timedelta(days=12 - timezone.now().weekday() if timezone.now().weekday() < 5 else 5, hours=20 - timezone.now().hour), # Next Saturday 8 PM
            }
        ]

    # 2. Fetch past contests (strict real data from database only)
    past_qs = Contest.objects.filter(end_time__lt=now).order_by('-end_time')
    past_list = []
    
    for c in past_qs:
        results_list = _get_contest_results_for_contest(c)
        
        # Real registrations (number of unique candidates who submitted tests)
        registrations_count = Result.objects.filter(assessment__title__icontains=c.title).values('candidate').distinct().count()
        # Real submissions (total test submissions)
        submissions_count = Result.objects.filter(assessment__title__icontains=c.title).count()

        past_list.append({
            'id': c.id,
            'title': c.title,
            'start_time': c.start_time,
            'registrations': registrations_count,
            'submissions': submissions_count,
            'results': results_list
        })

    return render(request, 'recruiter/contest_results.html', {
        'username': request.user.username,
        'upcoming_contests': upcoming_list,
        'past_contests': past_list
    })


def reports_page(request):
    """Render the main reports dashboard page."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')
    
    return render(request, 'recruiter/reports.html', {
        'username': request.user.username,
    })


@require_http_methods(["GET"])
def contest_results_api(request):
    """Return past contest options and the selected contest's ranked results."""
    try:
        now = timezone.now()
        contest_id = request.GET.get('contest_id')

        past_contests = Contest.objects.filter(end_time__lt=now).order_by('-end_time')
        contests = [
            {'id': contest.id, 'title': contest.title}
            for contest in past_contests
        ]

        selected_contest = None
        if contest_id:
            selected_contest = past_contests.filter(id=contest_id).first()
        if selected_contest is None and past_contests.exists():
            selected_contest = past_contests.first()

        if selected_contest is None:
            selected_contest_payload = {'id': None, 'title': '', 'results': []}
        else:
            selected_contest_payload = {
                'id': selected_contest.id,
                'title': selected_contest.title,
                'results': _get_contest_results_for_contest(selected_contest),
            }

        return JsonResponse({
            'success': True,
            'contests': contests,
            'selected_contest': selected_contest_payload,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def candidate_performance_api(request):
    """
    API endpoint for candidate performance data with pagination.
    Returns sorted candidate scores for bar chart visualization.
    
    Query parameters:
    - page: page number (default: 1)
    - per_page: candidates per page (default: 15)
    """
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 15))
        
        # Ensure valid pagination parameters
        if page < 1:
            page = 1
        if per_page < 5 or per_page > 100:
            per_page = 15
        
        # Get all candidates with their best scores
        # Aggregating from both Submission and Result models
        candidate_scores = {}
        
        # From Submissions (coding problems)
        submission_scores = Submission.objects.values('user__username', 'user__id').annotate(
            score=Avg('score'),
            submission_count=Count('id')
        ).order_by('user__username')
        
        for item in submission_scores:
            username = item['user__username']
            score = item['score'] if item['score'] is not None else 0
            candidate_scores[username] = {
                'user_id': item['user__id'],
                'score': round(score, 2),
                'submission_count': item['submission_count'],
            }
        
        # From Results (assessments)
        result_scores = Result.objects.values('candidate__username', 'candidate__id').annotate(
            score=Avg('score'),
            result_count=Count('id')
        ).order_by('candidate__username')
        
        for item in result_scores:
            username = item['candidate__username']
            score = item['score'] if item['score'] is not None else 0
            if username in candidate_scores:
                # Average both submission and result scores
                candidate_scores[username]['score'] = round(
                    (candidate_scores[username]['score'] + score) / 2, 2
                )
                candidate_scores[username]['result_count'] = item['result_count']
            else:
                candidate_scores[username] = {
                    'user_id': item['candidate__id'],
                    'score': round(score, 2),
                    'result_count': item['result_count'],
                }
        
        # Sort by score (highest first)
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Calculate pagination
        total_candidates = len(sorted_candidates)
        total_pages = (total_candidates + per_page - 1) // per_page
        
        # Validate page number
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # Get page data
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_candidates = sorted_candidates[start_idx:end_idx]
        
        # Format response
        candidates = [
            {
                'name': name,
                'score': score_data['score'],
                'rank': start_idx + idx + 1,
            }
            for idx, (name, score_data) in enumerate(page_candidates)
        ]
        
        return JsonResponse({
            'success': True,
            'candidates': candidates,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'per_page': per_page,
                'total_candidates': total_candidates,
                'has_previous': page > 1,
                'has_next': page < total_pages,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def candidate_stats_api(request):
    """
    API endpoint for candidate performance statistics.
    Returns aggregated stats for the analytics card.
    """
    try:
        # Get all candidates
        all_users = User.objects.filter(is_staff=False, is_superuser=False)
        total_candidates = all_users.count()
        
        # Get all scores from both submissions and results
        all_scores = []
        
        # From Submissions
        submission_avgs = Submission.objects.values('user__id').annotate(
            avg_score=Avg('score')
        )
        for item in submission_avgs:
            if item['avg_score'] is not None:
                all_scores.append(item['avg_score'])
        
        # From Results
        result_avgs = Result.objects.values('candidate__id').annotate(
            avg_score=Avg('score')
        )
        for item in result_avgs:
            if item['avg_score'] is not None:
                all_scores.append(item['avg_score'])
        
        # Calculate statistics
        if all_scores:
            highest_score = max(all_scores)
            lowest_score = min(all_scores)
            average_score = sum(all_scores) / len(all_scores)
        else:
            highest_score = 0
            lowest_score = 0
            average_score = 0
        
        # Get highest scorer name
        highest_scorer_name = "N/A"
        try:
            highest_submission = Submission.objects.order_by('-score').first()
            if highest_submission:
                highest_scorer_name = highest_submission.user.username
            else:
                highest_result = Result.objects.order_by('-score').first()
                if highest_result:
                    highest_scorer_name = highest_result.candidate.username
        except:
            pass
        
        # Count passed/failed candidates (score >= 50)
        passed_submissions = Submission.objects.filter(score__gte=50).values('user').distinct().count()
        failed_submissions = Submission.objects.filter(score__lt=50).values('user').distinct().count()
        
        passed_results = Result.objects.filter(passed=True).values('candidate').distinct().count()
        failed_results = Result.objects.filter(passed=False).values('candidate').distinct().count()
        
        total_passed = passed_submissions + passed_results
        total_failed = failed_submissions + failed_results
        
        # Calculate pass percentage
        total_evaluated = total_passed + total_failed
        pass_percentage = (total_passed / total_evaluated * 100) if total_evaluated > 0 else 0
        
        # Score distribution
        score_distribution = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81-100': 0,
        }
        
        for score in all_scores:
            if score <= 20:
                score_distribution['0-20'] += 1
            elif score <= 40:
                score_distribution['21-40'] += 1
            elif score <= 60:
                score_distribution['41-60'] += 1
            elif score <= 80:
                score_distribution['61-80'] += 1
            else:
                score_distribution['81-100'] += 1
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_candidates': total_candidates,
                'highest_score': round(highest_score, 2),
                'lowest_score': round(lowest_score, 2),
                'average_score': round(average_score, 2),
                'highest_scorer': highest_scorer_name,
                'passed_candidates': total_passed,
                'failed_candidates': total_failed,
                'pass_percentage': round(pass_percentage, 2),
                'score_distribution': score_distribution,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def contest_analytics_api(request):
    """
    API endpoint for contest analytics data.
    Returns monthly contest counts for line chart.
    """
    try:
        # Get contests grouped by month (last 12 months)
        now = timezone.now()
        twelve_months_ago = now - timedelta(days=365)
        
        contests = Contest.objects.filter(
            start_time__gte=twelve_months_ago
        ).order_by('start_time')
        
        # Group by month
        monthly_data = defaultdict(int)
        
        # Initialize all months
        for i in range(12):
            month_date = now - timedelta(days=30*i)
            month_key = month_date.strftime('%b')  # 'Jan', 'Feb', etc.
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
        
        # Count contests by month
        for contest in contests:
            month_key = contest.start_time.strftime('%b')
            monthly_data[month_key] += 1
        
        # Format for chart (in chronological order)
        months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        contest_data = [
            {'month': month, 'count': monthly_data.get(month, 0)}
            for month in months_order
        ]
        
        return JsonResponse({
            'success': True,
            'data': contest_data,
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def contest_stats_api(request):
    """
    API endpoint for contest statistics.
    Returns aggregated stats for the contest analytics card.
    """
    try:
        now = timezone.now()
        
        # Total contests
        total_contests = Contest.objects.count()
        
        # Current month contests
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month_start = now.replace(year=now.year+1, month=1, day=1)
        else:
            next_month_start = now.replace(month=now.month+1, day=1)
        
        current_month_contests = Contest.objects.filter(
            start_time__gte=current_month_start,
            start_time__lt=next_month_start
        ).count()
        
        # Average contests per month (last 12 months)
        twelve_months_ago = now - timedelta(days=365)
        contests_last_year = Contest.objects.filter(
            start_time__gte=twelve_months_ago
        ).count()
        avg_contests_per_month = round(contests_last_year / 12, 2) if contests_last_year > 0 else 0
        
        # Most active month (last 12 months)
        monthly_counts = defaultdict(int)
        for contest in Contest.objects.filter(start_time__gte=twelve_months_ago):
            month_key = contest.start_time.strftime('%B')  # 'January', etc.
            monthly_counts[month_key] += 1
        
        most_active_month = max(monthly_counts, key=monthly_counts.get) if monthly_counts else "N/A"
        least_active_month = min(monthly_counts, key=monthly_counts.get) if monthly_counts else "N/A"
        
        # Contest growth rate (compare this month vs last month)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        if current_month_start.month == 1:
            prev_month_end = current_month_start - timedelta(days=1)
        else:
            prev_month_end = current_month_start - timedelta(days=1)
        
        last_month_contests = Contest.objects.filter(
            start_time__gte=last_month_start,
            start_time__lt=current_month_start
        ).count()
        
        if last_month_contests > 0:
            growth_rate = round(
                ((current_month_contests - last_month_contests) / last_month_contests * 100), 2
            )
        else:
            growth_rate = 0.0 if current_month_contests == 0 else 100.0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_contests': total_contests,
                'current_month_contests': current_month_contests,
                'avg_contests_per_month': avg_contests_per_month,
                'most_active_month': most_active_month,
                'least_active_month': least_active_month,
                'growth_rate': growth_rate,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def recruiter_settings(request):
    """Recruiter-specific settings page. Staff-only."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')
    
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)

    context = {
        "profile_form": UserProfileForm(instance=request.user),
        "password_form": SettingsPasswordChangeForm(request.user),
        "notifications_form": NotificationsSettingsForm(instance=settings_obj),
        "editor_form": EditorPreferencesForm(instance=settings_obj),
        "privacy_form": PrivacySettingsForm(instance=settings_obj),
        "settings": settings_obj,
    }

    return render(request, "recruiter/settings.html", context)
    

@login_required
def recruiter_settings(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    return render(
        request,
        'recruiter/settings.html',
        {
            'username': request.user.username,
        }
    )
    