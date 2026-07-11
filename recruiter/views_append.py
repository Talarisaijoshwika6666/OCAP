
def recruiter_contest_analytics(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/accounts/login/')
    
    from contest.models import Contest, ContestRegistration, CandidateResult
    
    # 1. Top level metrics
    total_contests = Contest.objects.count()
    registered_candidates_count = ContestRegistration.objects.count()
    completed_exams_count = CandidateResult.objects.count()
    incomplete_exams_count = registered_candidates_count - completed_exams_count

    # 2. Registrations details
    registered_details = ContestRegistration.objects.select_related('candidate', 'contest').all()
    # 3. Completed details
    completed_details = CandidateResult.objects.select_related('candidate', 'contest').all()

    # 4. Global Leaderboard (Ranks)
    from django.db.models import Sum
    leaderboard = CandidateResult.objects.values('candidate__username').annotate(
        total_score=Sum('score')
    ).order_by('-total_score')[:10]

    return render(request, 'recruiter/contest_analytics.html', {
        'username': request.user.username,
        'total_contests': total_contests,
        'registered_count': registered_candidates_count,
        'completed_count': completed_exams_count,
        'incomplete_count': incomplete_exams_count,
        'registered_details': registered_details,
        'completed_details': completed_details,
        'leaderboard': leaderboard,
    })
