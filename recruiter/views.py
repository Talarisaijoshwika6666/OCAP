from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, Count
from submissions.models import Submission
from questions.models import Question
from results.models import Result
from assessments.models import Assessment

User = get_user_model()

def recruiter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    # Stats
    total_questions   = Question.objects.count()
    total_candidates  = User.objects.filter(role='candidate').count()
    total_submissions = Submission.objects.count()

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

    return render(request, 'recruiter/dashboard.html', {
        'total_questions':    total_questions,
        'total_candidates':   total_candidates,
        'total_submissions':  total_submissions,
        'top_candidates':     top_candidates,
        'questions':          questions,
        'recent_submissions': recent_submissions,
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