from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import datetime
from django.utils import timezone


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


@never_cache
def home_view(request):
    return render(request, 'landing.html')

@never_cache
@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    from questions.models import Question
    from submissions.models import Submission

    total_problems = Question.objects.count()
    submissions = Submission.objects.filter(user=request.user)
    problems_solved = submissions.filter(score__gt=0).values('question').distinct().count()
    total_score = submissions.aggregate(total=Sum('score'))['total'] or 0

    all_scores = Submission.objects.values('user').annotate(
        total=Sum('score')
    ).order_by('-total')
    rank = 1
    for i, entry in enumerate(all_scores):
        if entry['user'] == request.user.pk:
            rank = i + 1
            break

    return render(request, 'home.html', {
        'total_problems': total_problems,
        'problems_solved': problems_solved,
        'total_score': total_score,
        'global_rank': rank,
    })

@never_cache
@login_required(login_url='/accounts/login/')
def dashboard_api(request):
    from questions.models import Question
    from submissions.models import Submission

    total_problems = Question.objects.count()
    submissions = Submission.objects.filter(user=request.user)
    problems_solved = submissions.filter(score__gt=0).values('question').distinct().count()

    # Calculate streak
    submission_dates = list(submissions.values_list('submitted_at', flat=True))
    local_dates = sorted(
        {timezone.localdate(dt) for dt in submission_dates},
        reverse=True
    )
    
    streak = 0
    today = timezone.localdate()
    yesterday = today - datetime.timedelta(days=1)
    
    if local_dates:
        if local_dates[0] in (today, yesterday):
            current = local_dates[0]
            streak = 1
            for d in local_dates[1:]:
                if d == current - datetime.timedelta(days=1):
                    streak += 1
                    current = d
                elif d == current:
                    continue
                else:
                    break

    # Calculate global rank
    all_scores = Submission.objects.values('user').annotate(
        total=Sum('score')
    ).order_by('-total')
    rank = "—"
    for i, entry in enumerate(all_scores):
        if entry['user'] == request.user.pk:
            rank = i + 1
            break

    # Skill Radar
    total_easy = Question.objects.filter(difficulty='Easy').count()
    easy_solved = submissions.filter(score__gt=0, question__difficulty='Easy').values('question').distinct().count()
    
    total_medium = Question.objects.filter(difficulty='Medium').count()
    medium_solved = submissions.filter(score__gt=0, question__difficulty='Medium').values('question').distinct().count()
    
    total_hard = Question.objects.filter(difficulty='Hard').count()
    hard_solved = submissions.filter(score__gt=0, question__difficulty='Hard').values('question').distinct().count()

    skills = {
        'data_structures': {
            'solved': easy_solved,
            'total': total_easy,
            'percentage': int((easy_solved / total_easy * 100)) if total_easy > 0 else 0
        },
        'algorithms': {
            'solved': medium_solved,
            'total': total_medium,
            'percentage': int((medium_solved / total_medium * 100)) if total_medium > 0 else 0
        },
        'system_design': {
            'solved': hard_solved,
            'total': total_hard,
            'percentage': int((hard_solved / total_hard * 100)) if total_hard > 0 else 0
        },
        'sql_databases': {
            'solved': problems_solved,
            'total': total_problems,
            'percentage': int((problems_solved / total_problems * 100)) if total_problems > 0 else 0
        }
    }

    # Recent activities
    recent = submissions.select_related('question').order_by('-submitted_at')[:5]
    activities = []
    for sub in recent:
        if sub.score == 100:
            status = 'Accepted'
        elif sub.score > 0:
            status = 'Partial'
        else:
            status = 'Failed'
            
        activities.append({
            'id': sub.id,
            'question_id': sub.question.id,
            'question_title': sub.question.title,
            'submitted_at': sub.submitted_at.isoformat(),
            'score': sub.score,
            'passed_cases': sub.passed_cases,
            'total_cases': sub.total_cases,
            'status': status
        })

    # AI Insights
    unsolved = Question.objects.exclude(submission__user=request.user, submission__score__gt=0).first()
    if unsolved:
        rec_title = unsolved.title
        rec_id = unsolved.id
        rec_desc = f"Based on your progress, we recommend tackling '{unsolved.title}' next."
    else:
        rec_title = "None"
        rec_id = None
        rec_desc = "Amazing job! You have solved all available problems."

    if problems_solved == 0:
        insights = [
            {
                'type': 'info',
                'title': 'Get Started',
                'desc': 'Solve your first problem to help the AI Mentor analyze your coding strengths.',
                'icon': 'fas fa-rocket',
                'color': '#00d4ff',
                'bg': 'rgba(0, 212, 255, 0.08)',
                'border': 'rgba(0, 212, 255, 0.2)'
            },
            {
                'type': 'gap',
                'title': 'Topic Recommendation',
                'desc': 'We recommend starting with basic Data Structures to build a solid foundation.',
                'icon': 'fas fa-triangle-exclamation',
                'color': '#ff2d78',
                'bg': 'rgba(255, 45, 120, 0.08)',
                'border': 'rgba(255, 45, 120, 0.2)'
            },
            {
                'type': 'recommendation',
                'title': 'Next Recommended Challenge',
                'desc': rec_desc,
                'icon': 'fas fa-lightbulb',
                'color': '#b026ff',
                'bg': 'rgba(176, 38, 255, 0.08)',
                'border': 'rgba(176, 38, 255, 0.2)',
                'question_id': rec_id
            }
        ]
    else:
        if easy_solved >= medium_solved:
            strength_title = "Strength: Basic coding & implementation"
            strength_desc = f"You have solved {easy_solved} Easy problems. You are comfortable with foundational questions."
            gap_title = "Gap found: Algorithmic complexity"
            gap_desc = "Challenge yourself with Medium difficulty problems to grow your algorithmic skills."
        else:
            strength_title = "Strength: Problem-solving depth"
            strength_desc = f"You have solved {medium_solved + hard_solved} Medium/Hard problems. You handle complex logic well!"
            gap_title = "Gap found: Implementation speed"
            gap_desc = "Practicing Easy problems can help you write cleaner code faster."

        insights = [
            {
                'type': 'strength',
                'title': strength_title,
                'desc': strength_desc,
                'icon': 'fas fa-arrow-trend-up',
                'color': '#00ff82',
                'bg': 'rgba(0, 255, 130, 0.08)',
                'border': 'rgba(0, 255, 130, 0.2)'
            },
            {
                'type': 'gap',
                'title': gap_title,
                'desc': gap_desc,
                'icon': 'fas fa-triangle-exclamation',
                'color': '#ff2d78',
                'bg': 'rgba(255, 45, 120, 0.08)',
                'border': 'rgba(255, 45, 120, 0.2)'
            },
            {
                'type': 'recommendation',
                'title': 'Suggested Next Problem',
                'desc': rec_desc,
                'icon': 'fas fa-lightbulb',
                'color': '#b026ff',
                'bg': 'rgba(176, 38, 255, 0.08)',
                'border': 'rgba(176, 38, 255, 0.2)',
                'question_id': rec_id
            }
        ]

    # Calculate gamified developer profile progress
    total_score = submissions.aggregate(total=Sum('score'))['total'] or 0
    xp = problems_solved * 100 + int(total_score)
    level = (xp // 500) + 1
    xp_in_level = xp % 500
    xp_progress_pct = int((xp_in_level / 500) * 100) if xp > 0 else 0
    
    # Weekly Goal Progress (Target: 5 problems solved in 7 days)
    seven_days_ago = timezone.now() - datetime.timedelta(days=7)
    solved_this_week = submissions.filter(
        score__gt=0, 
        submitted_at__gte=seven_days_ago
    ).values('question').distinct().count()
    
    weekly_goal = 5
    weekly_progress_pct = int((solved_this_week / weekly_goal) * 100) if weekly_goal > 0 else 0
    if weekly_progress_pct > 100:
        weekly_progress_pct = 100

    # Accuracy percentage: accepted submissions (score == 100) / total submissions
    total_subs = submissions.count()
    accepted_subs = submissions.filter(score=100).count()
    accuracy = int((accepted_subs / total_subs) * 100) if total_subs > 0 else 0

    # 14-day activity history grid
    activity_grid = []
    for day_offset in range(13, -1, -1):
        target_day = today - datetime.timedelta(days=day_offset)
        has_sub = any(d == target_day for d in local_dates)
        activity_grid.append({
            'date': target_day.strftime('%b %d'),
            'active': has_sub
        })

    return JsonResponse({
        'total_problems': total_problems,
        'problems_solved': problems_solved,
        'streak': streak,
        'global_rank': rank,
        'skills': skills,
        'activities': activities,
        'insights': insights,
        'active_dates': [d.isoformat() for d in local_dates],
        'gamified': {
            'xp': xp,
            'level': level,
            'xp_progress_pct': xp_progress_pct,
            'xp_in_level': xp_in_level,
            'xp_next_level': 500,
            'weekly_solved': solved_this_week,
            'weekly_goal': weekly_goal,
            'weekly_progress_pct': weekly_progress_pct,
            'accuracy': accuracy,
            'activity_grid': activity_grid
        }
    })