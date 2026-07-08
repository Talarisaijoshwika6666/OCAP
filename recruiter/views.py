from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q as models_Q
from django.utils import timezone
from django.db import models
from django.db.models import Sum, Count
from django.db.models import Count, Avg
from django.utils import timezone
from submissions.models import Submission
from questions.models import Question
from assessments.models import Assessment
from assessments.models import Assessment
from results.models import Result
from assessments.models import Assessment

User = get_user_model()

def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    from assessments.utils import ensure_assessments_exist
    ensure_assessments_exist()

    from assessments.utils import ensure_assessments_exist
    ensure_assessments_exist()

    # Stats
    total_questions   = Question.objects.count()
    total_candidates  = User.objects.filter(role='candidate').count()
    total_candidates  = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_assessments = Assessment.objects.count()
    total_problems    = Question.objects.count()
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

    # Top candidates by score
    top_candidates = (
        User.objects.filter(role='candidate')
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
        # Get real results if available
        results_qs = Result.objects.filter(assessment__title__icontains=c.title).order_by('-score', 'submitted_at')
        results_list = []
        for idx, r in enumerate(results_qs):
            rank = r.rank if r.rank > 0 else (idx + 1)
            results_list.append({
                'rank': rank,
                'candidate': r.candidate.username,
                'score': r.score
            })
        
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
        # Get real results if available
        results_qs = Result.objects.filter(assessment__title__icontains=c.title).order_by('-score', 'submitted_at')
        results_list = []
        for idx, r in enumerate(results_qs):
            rank = r.rank if r.rank > 0 else (idx + 1)
            results_list.append({
                'rank': rank,
                'candidate': r.candidate.username,
                'score': r.score
            })
        
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


def recruiter_candidates(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    q = request.GET.get('q', '').strip()
    assessment_filter = request.GET.get('assessment', '').strip()
    status_filter = request.GET.get('status', '').strip()
    language_filter = request.GET.get('language', '').strip()

    candidates = User.objects.filter(role='candidate').order_by('username')

    if q:
        candidates = candidates.filter(
            models.Q(username__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(full_name__icontains=q)
        )

    rows = []
    for candidate in candidates:
        # Latest assessment result taken by this candidate
        latest_result = (
            Result.objects.filter(candidate=candidate)
            .select_related('assessment')
            .order_by('-submitted_at')
            .first()
        )

        # Most recent code submission, used to show which language they coded in
        latest_submission = (
            Submission.objects.filter(user=candidate)
            .order_by('-submitted_at')
            .first()
        )

        if latest_result:
            assessment_name = latest_result.assessment.title
            score_display = f"{round(latest_result.score)}/{int(latest_result.assessment.total_marks)}"
            rank_display = latest_result.rank if latest_result.rank else "—"
            status = "Completed"
        else:
            assessment_name = "—"
            score_display = "—"
            rank_display = "—"
            status = "Pending"

        language_display = latest_submission.language.title() if latest_submission else "—"

        row = {
            'id': candidate.id,
            'name': candidate.get_full_name(),
            'email': candidate.email,
            'assessment': assessment_name,
            'score': score_display,
            'rank': rank_display,
            'language': language_display,
            'status': status,
        }

        # Apply column filters on the computed row values
        if assessment_filter and row['assessment'] != assessment_filter:
            continue
        if status_filter and row['status'] != status_filter:
            continue
        if language_filter and row['language'].lower() != language_filter.lower():
            continue

        rows.append(row)

    assessment_options = list(
        Assessment.objects.order_by('title').values_list('title', flat=True).distinct()
    )
    language_options = list(
        Submission.objects.order_by('language').values_list('language', flat=True).distinct()
    )

    return render(request, 'recruiter/candidates.html', {
        'candidates': rows,
        'assessment_options': assessment_options,
        'language_options': language_options,
        'filters': {
            'q': q,
            'assessment': assessment_filter,
            'status': status_filter,
            'language': language_filter,
        },
    })


def recruiter_candidate_view(request, candidate_id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    candidate = get_object_or_404(User, id=candidate_id, role='candidate')

    results = (
        Result.objects.filter(candidate=candidate)
        .select_related('assessment')
        .order_by('-submitted_at')
    )
    submissions = (
        Submission.objects.filter(user=candidate)
        .select_related('question')
        .order_by('-submitted_at')[:20]
    )

    return render(request, 'recruiter/candidate_view.html', {
        'candidate': candidate,
        'results': results,
        'submissions': submissions,
    })


def recruiter_candidate_edit(request, candidate_id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    candidate = get_object_or_404(User, id=candidate_id, role='candidate')

    if request.method == 'POST':
        candidate.full_name = request.POST.get('full_name', '').strip()
        candidate.email = request.POST.get('email', '').strip()
        candidate.mobile = request.POST.get('mobile', '').strip()
        candidate.organization = request.POST.get('organization', '').strip()
        candidate.bio = request.POST.get('bio', '').strip()
        candidate.save()
        return redirect('recruiter_candidates')

    return render(request, 'recruiter/candidate_edit.html', {
        'candidate': candidate,
    })


def recruiter_candidate_delete(request, candidate_id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    candidate = get_object_or_404(User, id=candidate_id, role='candidate')

    if request.method == 'POST':
        candidate.delete()
        return redirect('recruiter_candidates')

    return render(request, 'recruiter/candidate_confirm_delete.html', {
        'candidate': candidate,
    })