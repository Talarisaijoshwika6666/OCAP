from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Contest
from django.utils import timezone

def contest_view(request):
    now = timezone.now()
    upcoming = Contest.objects.filter(start_time__gt=now).order_by('start_time')
    active = Contest.objects.filter(start_time__lte=now, end_time__gte=now)
    past = Contest.objects.filter(end_time__lt=now).order_by('-end_time')[:5]
    return render(request, 'contest/contest.html', {
        'upcoming_contests': upcoming,
        'active': active,
        'past': past,
        'now': now,
    })

@login_required
def register_contest(request, pk):
    from django.contrib import messages
    from .models import Contest
    contest = get_object_or_404(Contest, pk=pk)
    messages.success(request, f'Registered for {contest.title}!')
    return redirect('/contest/')