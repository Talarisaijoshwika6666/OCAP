from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, timedelta
from collections import Counter
import calendar as cal_module


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)

from django.views.decorators.cache import never_cache
from django.utils import timezone


def compute_lifetime_stats(user):
    """Lifetime, never-resets-when-you-browse-the-calendar numbers:
    current/longest streak, total active days, and the full set of
    solved/attempted dates used to color every month of the calendar."""
    from submissions.models import Submission

    all_times = list(
        Submission.objects.filter(user=user).values_list('submitted_at', flat=True)
    )
    accepted_times = list(
        Submission.objects.filter(user=user, result='Accepted')
        .values_list('submitted_at', flat=True)
    )

    today = timezone.localdate()

    def to_local_date(dt):
        return timezone.localtime(dt).date()

    attempted_dates = {to_local_date(t) for t in all_times}
    solved_dates_list = [to_local_date(t) for t in accepted_times]
    solved_dates = set(solved_dates_list)

    # ---- current streak (counts back from today, or yesterday if
    # today has no solve yet so an active streak isn't shown as broken) ----
    current_streak = 0
    cursor = today
    if cursor not in solved_dates:
        cursor -= timedelta(days=1)
    while cursor in solved_dates:
        current_streak += 1
        cursor -= timedelta(days=1)

    # ---- longest streak ever ----
    longest_streak = 0
    streak_run = 0
    prev = None
    for d in sorted(solved_dates):
        if prev is not None and (d - prev).days == 1:
            streak_run += 1
        else:
            streak_run = 1
        longest_streak = max(longest_streak, streak_run)
        prev = d

    total_active_days = len(attempted_dates)

    week_start = today - timedelta(days=today.weekday())
    this_week_active = len({d for d in attempted_dates if week_start <= d <= today})

    if current_streak >= 7:
        streak_message = f"{current_streak}-day streak! You're on fire — don't break the chain now."
    elif current_streak >= 1:
        streak_message = f"{current_streak}-day streak going. Solve one more today to keep it alive."
    else:
        streak_message = "No active streak yet. Solve a problem today to light the fire."

    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'total_active_days': total_active_days,
        'this_week_active': this_week_active,
        'streak_message': streak_message,
        'solved_dates': solved_dates,
        'attempted_dates': attempted_dates,
    }


def _build_insight(series, unit_label):
    values = [d['value'] for d in series]
    n = len(values)
    if n < 2 or sum(values) == 0:
        return f"Solve a few more problems to start seeing your {unit_label} trend here."
    half = n // 2
    first_avg = sum(values[:half]) / half if half else 0
    second_avg = sum(values[half:]) / (n - half) if (n - half) else 0
    if second_avg > first_avg * 1.1:
        return f"Your {unit_label} solved trend is accelerating upward. Keep up the current pace to stay ahead of schedule."
    elif second_avg < first_avg * 0.9:
        return f"Your {unit_label} solve rate has cooled off recently. One quick problem today restarts the climb."
    else:
        return f"Your {unit_label} solve rate is holding steady. Consistency like this compounds fast over time."


def compute_month_scoped_stats(user, year, month):
    """Everything on the left side of the Streak page (velocity chart,
    focus-hours breakdown, peak activity, etc.) recomputed for whichever
    month/year the candidate has picked in the calendar."""
    from submissions.models import Submission

    days_in_month = cal_module.monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)

    today = timezone.localdate()
    reference_date = min(today, month_end)

    def to_local_date(dt):
        return timezone.localtime(dt).date()

    # ---- activity within the SELECTED month only (drives daily series,
    # focus hours, peak activity, and most active weekday) ----
    month_times = list(
        Submission.objects.filter(
            user=user,
            submitted_at__date__gte=month_start,
            submitted_at__date__lte=month_end,
        ).values_list('submitted_at', flat=True)
    )
    month_accepted_times = list(
        Submission.objects.filter(
            user=user, result='Accepted',
            submitted_at__date__gte=month_start,
            submitted_at__date__lte=month_end,
        ).values_list('submitted_at', flat=True)
    )
    month_solved_dates_list = [to_local_date(t) for t in month_accepted_times]
    month_solved_count_by_date = Counter(month_solved_dates_list)

    daily_series = []
    for d_num in range(1, days_in_month + 1):
        d = date(year, month, d_num)
        daily_series.append({'label': str(d_num), 'value': month_solved_count_by_date.get(d, 0)})

    hour_buckets = ['12–4 AM', '4–8 AM', '8 AM–12 PM', '12–4 PM', '4–8 PM', '8 PM–12 AM']
    bucket_counts = [0] * 6
    for t in month_times:
        h = timezone.localtime(t).hour
        bucket_counts[h // 4] += 1
    peak_label = hour_buckets[bucket_counts.index(max(bucket_counts))] if any(bucket_counts) else '—'

    weekday_counts = Counter(timezone.localtime(t).strftime('%A') for t in month_times)
    most_active_weekday = weekday_counts.most_common(1)[0][0] if weekday_counts else '—'

    avg_solved_per_active_day = (
        round(len(month_accepted_times) / len(set(month_solved_dates_list)), 1)
        if month_solved_dates_list else 0
    )

    # ---- weekly / monthly trailing windows anchor on the selected
    # month so "Weekly"/"Monthly" tabs stay meaningful when browsing
    # the past, but pull from full history so the windows have data ----
    all_accepted_times = list(
        Submission.objects.filter(user=user, result='Accepted').values_list('submitted_at', flat=True)
    )
    all_solved_count_by_date = Counter(to_local_date(t) for t in all_accepted_times)

    week_start = reference_date - timedelta(days=reference_date.weekday())
    weekly_series = []
    for i in range(7, -1, -1):
        w_start = week_start - timedelta(weeks=i)
        w_end = w_start + timedelta(days=6)
        total = sum(v for d, v in all_solved_count_by_date.items() if w_start <= d <= w_end)
        weekly_series.append({'label': w_start.strftime('%d %b'), 'value': total})

    monthly_series = []
    y, m = reference_date.year, reference_date.month
    for i in range(5, -1, -1):
        mm = m - i
        yy = y
        while mm <= 0:
            mm += 12
            yy -= 1
        total = sum(v for d, v in all_solved_count_by_date.items() if d.year == yy and d.month == mm)
        monthly_series.append({'label': date(yy, mm, 1).strftime('%b'), 'value': total})

    return {
        'avg_solved_per_active_day': avg_solved_per_active_day,
        'peak_label': peak_label,
        'most_active_weekday': most_active_weekday,
        'daily_series': daily_series,
        'weekly_series': weekly_series,
        'monthly_series': monthly_series,
        'insights': {
            'daily': _build_insight(daily_series, 'daily'),
            'weekly': _build_insight(weekly_series, 'weekly'),
            'monthly': _build_insight(monthly_series, 'monthly'),
        },
        'bucket_data': list(zip(hour_buckets, bucket_counts)),
    }


def build_month_calendar(year, month, solved_dates, attempted_dates, today):
    """Returns a week-by-week grid (Mon-first) for the given month.
    Each day cell carries a status used to color it in the template:
    'solved', 'attempted', or 'none'."""
    weeks = cal_module.Calendar(firstweekday=0).monthdayscalendar(year, month)
    grid = []
    for week in weeks:
        row = []
        for day in week:
            if day == 0:
                row.append(None)
                continue
            d = date(year, month, day)
            if d in solved_dates:
                status = 'solved'
            elif d in attempted_dates:
                status = 'attempted'
            elif d > today:
                status = 'future'
            else:
                status = 'none'
            row.append({'day': day, 'status': status, 'is_today': d == today})
        grid.append(row)
    return grid


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

    streak_stats = compute_lifetime_stats(request.user)

    return render(request, 'home.html', {
        'total_problems': total_problems,
        'problems_solved': problems_solved,
        'total_score': total_score,
        'global_rank': rank,
        'current_streak': streak_stats['current_streak'],
    })


@never_cache
@login_required(login_url='/accounts/login/')
def streak_view(request):
    lifetime = compute_lifetime_stats(request.user)
    today = timezone.localdate()

    try:
        year = int(request.GET.get('y', today.year))
        month = int(request.GET.get('m', today.month))
    except ValueError:
        year, month = today.year, today.month

    if month < 1:
        month, year = 12, year - 1
    elif month > 12:
        month, year = 1, year + 1
    # keep the picker within a sane range so a stray query param can't
    # blow up calendar.monthrange()
    year = max(2000, min(year, today.year + 5))

    month_scoped = compute_month_scoped_stats(request.user, year, month)

    month_grid = build_month_calendar(year, month, lifetime['solved_dates'], lifetime['attempted_dates'], today)
    month_label = date(year, month, 1).strftime('%B %Y')

    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
    next_month, next_year = (1, year + 1) if month == 12 else (month + 1, year)

    milestone_days = [3, 7, 14, 30, 60, 100]
    milestones = [
        {'days': d, 'unlocked': lifetime['longest_streak'] >= d}
        for d in milestone_days
    ]
    this_week_active_pct = round((lifetime['this_week_active'] / 7) * 100)

    month_choices = [(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    year_choices = list(range(today.year - 5, today.year + 2))

    context = {
        **lifetime,
        **month_scoped,
        'month_grid': month_grid,
        'month_label': month_label,
        'cur_year': year,
        'cur_month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'is_current_month': (year == today.year and month == today.month),
        'milestones': milestones,
        'this_week_active_pct': this_week_active_pct,
        'month_choices': month_choices,
        'year_choices': year_choices,
    }
    return render(request, 'streak.html', context)