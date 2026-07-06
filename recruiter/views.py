from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg
from submissions.models import Submission
from questions.models import Question
from assessments.models import Assessment

User = get_user_model()

def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    # Stats
    total_candidates  = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_assessments = Assessment.objects.count()
    total_problems    = Question.objects.count()
    total_submissions = Submission.objects.count()
    active_assessments = Assessment.objects.filter(is_active=True).count()
    
    avg_score_query = Submission.objects.aggregate(Avg('score'))['score__avg']
    avg_score = round(avg_score_query, 1) if avg_score_query is not None else 0.0

    # Recent Assessments with candidate count
    recent_assessments = Assessment.objects.annotate(
        candidate_count=Count('results')
    ).order_by('-id')[:5]

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
    recent_activity = (
        Submission.objects.select_related('user', 'question')
        .order_by('-submitted_at')[:8]
    )

    return render(request, 'recruiter/dashboard.html', {
        'username': request.user.username,
        'total_candidates': total_candidates,
        'total_assessments': total_assessments,
        'total_problems': total_problems,
        'total_submissions': total_submissions,
        'active_assessments': active_assessments,
        'avg_score': avg_score,
        'recent_assessments': recent_assessments,
        'insights': insights,
        'recent_activity': recent_activity,
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