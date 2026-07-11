from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Contest, ContestRegistration, CandidateResult, MCQSubmission, ProgrammingSubmission
import json
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from submissions.executor import run_code as execute_code

@login_required
def contest_view(request):
    now = timezone.now()
    upcoming = Contest.objects.filter(start_time__gt=now).order_by('start_time')
    active = Contest.objects.filter(start_time__lte=now, end_time__gte=now)
    past = Contest.objects.filter(end_time__lt=now).order_by('-end_time')[:5]
    
    user_registrations = ContestRegistration.objects.filter(candidate=request.user).values_list('contest_id', flat=True)
    user_submissions = CandidateResult.objects.filter(candidate=request.user).values_list('contest_id', flat=True)
    
    return render(request, 'contest/contest.html', {
        'upcoming_contests': upcoming,
        'active': active,
        'past': past,
        'now': now,
        'user_registrations': user_registrations,
        'user_submissions': user_submissions,
    })

@login_required
def register_contest(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    
    if request.method == 'POST':
        candidate_email = request.POST.get('candidate_email')
        candidate_name = request.POST.get('candidate_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('/contest/')
            
        if ContestRegistration.objects.filter(candidate=request.user, contest=contest).exists():
            messages.error(request, 'You are already registered for this contest.')
            return redirect('/contest/')
            
        hashed_password = make_password(password)
        
        ContestRegistration.objects.create(
            candidate=request.user,
            contest=contest,
            registration_email=candidate_email,
            registration_name=candidate_name,
            exam_password=hashed_password
        )
        
        # Send Email
        question_count = contest.mcqs.count() + contest.programming_questions.count()
        subject = f"Registration Confirmed: {contest.title}"
        message = f"""
Dear {candidate_name},

You have successfully registered for the contest '{contest.title}'. Here are the details about the contest:

- When the exam will open: {contest.start_time.strftime('%B %d, %Y at %I:%M %p')}
- Format: {contest.get_format_type_display()}
- Questions: {question_count}
- Duration of the exam: {contest.duration_minutes} minutes

Your Exam PIN has been saved securely. You will need to enter your email ({candidate_email}) and Exam PIN to start the contest when the time arrives.

Good luck!
LogicLabs Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [candidate_email],
            fail_silently=False,
        )
        
        messages.success(request, f'Successfully registered for {contest.title}! Confirmation email sent.')
        
    return redirect('/contest/')

@login_required
def start_contest_auth(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        try:
            registration = ContestRegistration.objects.get(candidate=request.user, contest=contest, registration_email=email)
        except ContestRegistration.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Invalid email or you are not registered for this contest.'})
            messages.error(request, 'Invalid email or you are not registered for this contest.')
            return redirect('/contest/')
            
        if check_password(password, registration.exam_password):
            exam_url = reverse('contest_exam', args=[contest.id])
            if is_ajax:
                return JsonResponse({'success': True, 'exam_url': exam_url})
            messages.success(request, 'Authentication successful! Starting exam...')
            return redirect('contest_exam', pk=contest.id)
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Invalid Exam PIN.'})
            messages.error(request, 'Invalid Exam PIN.')
            return redirect('/contest/')
            
    return redirect('/contest/')

@login_required
def contest_exam(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    
    if CandidateResult.objects.filter(candidate=request.user, contest=contest).exists():
        messages.info(request, 'You have already completed this exam.')
        return redirect('view_result', pk=contest.id)

    if contest.format_type == 'objective':
        questions = contest.mcqs.all()
        return render(request, 'contest/exam_objective.html', {'contest': contest, 'questions': questions})
    else:
        questions = contest.programming_questions.all()
        return render(request, 'contest/exam_interactive.html', {'contest': contest, 'questions': questions})

@login_required
def submit_exam(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    
    if request.method == 'POST':
        if CandidateResult.objects.filter(candidate=request.user, contest=contest).exists():
            return JsonResponse({'success': False, 'message': 'Exam already submitted.'})
            
        score = 0
        total_marks = 0
        
        result = CandidateResult.objects.create(
            candidate=request.user,
            contest=contest,
            score=0,
            total_marks=0
        )
        
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
        except json.JSONDecodeError:
            answers = {}
        
        if contest.format_type == 'objective':
            questions = contest.mcqs.all()
            for q in questions:
                total_marks += q.marks
                selected_option = answers.get(str(q.id), '')
                is_correct = (selected_option == q.correct_answer)
                if is_correct:
                    score += q.marks
                MCQSubmission.objects.create(
                    result=result,
                    question=q,
                    selected_option=selected_option,
                    is_correct=is_correct
                )
        else:
            questions = contest.programming_questions.prefetch_related('test_cases').all()
            for q in questions:
                total_marks += q.marks
                
                ans_data = answers.get(str(q.id), {})
                if isinstance(ans_data, str):
                    # fallback if frontend just sends code string
                    code = ans_data
                    language = "python"
                else:
                    code = ans_data.get('code', '')
                    language = ans_data.get('language', 'python')
                
                test_cases = q.test_cases.all()
                total_cases = test_cases.count()
                passed_cases = 0
                
                if total_cases > 0 and len(code.strip()) > 0:
                    for tc in test_cases:
                        stdout, stderr = execute_code(code, language, input_data=tc.input_data or '')
                        if not stderr and stdout and stdout.strip() == tc.expected_output.strip():
                            passed_cases += 1
                            
                    partial_score = round((passed_cases / total_cases) * q.marks)
                    score += partial_score
                    is_correct = (passed_cases == total_cases)
                else:
                    is_correct = False
                    
                ProgrammingSubmission.objects.create(
                    result=result,
                    question=q,
                    code=code,
                    language=language,
                    is_correct=is_correct
                )
                
        result.score = score
        result.total_marks = total_marks
        result.save()
        
        return JsonResponse({'success': True, 'redirect_url': reverse('view_result', args=[contest.id])})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def view_result(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    try:
        result = CandidateResult.objects.get(candidate=request.user, contest=contest)
    except CandidateResult.DoesNotExist:
        messages.error(request, 'You did not participate in this contest.')
        return redirect('/contest/')
        
    if contest.format_type == 'objective':
        correct_count = result.mcq_submissions.filter(is_correct=True).count()
        wrong_count = result.mcq_submissions.filter(is_correct=False).count()
    else:
        correct_count = result.prog_submissions.filter(is_correct=True).count()
        wrong_count = result.prog_submissions.filter(is_correct=False).count()
        
    return render(request, 'contest/view_result.html', {
        'contest': contest, 
        'result': result,
        'correct_count': correct_count,
        'wrong_count': wrong_count
    })

@login_required
def view_exam(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    try:
        result = CandidateResult.objects.get(candidate=request.user, contest=contest)
    except CandidateResult.DoesNotExist:
        messages.error(request, 'You did not participate in this contest.')
        return redirect('/contest/')
    
    if contest.format_type == 'objective':
        submissions = result.mcq_submissions.select_related('question').all()
        return render(request, 'contest/exam_review_objective.html', {'contest': contest, 'result': result, 'submissions': submissions})
    else:
        submissions = result.prog_submissions.select_related('question').all()
        return render(request, 'contest/exam_review_interactive.html', {'contest': contest, 'result': result, 'submissions': submissions})

@login_required
def candidate_analytics(request):
    results = CandidateResult.objects.filter(candidate=request.user).select_related('contest').order_by('-completed_at')
    
    total_contests = Contest.objects.count()
    registered = ContestRegistration.objects.filter(candidate=request.user).count()
    completed = results.count()
    
    total_score = sum(r.score for r in results)
    total_possible = sum(r.total_marks for r in results)
    
    understanding_level = int((total_score / total_possible * 100) if total_possible > 0 else 0)
    
    from django.db.models import Sum
    leaderboard = CandidateResult.objects.values('candidate__username').annotate(
        total_score=Sum('score')
    ).order_by('-total_score')
    
    leaderboard_list = list(leaderboard)
    top_3 = leaderboard_list[:3]
    candidate_rank = None
    for index, item in enumerate(leaderboard_list):
        if item['candidate__username'] == request.user.username:
            candidate_rank = index + 1
            break
    
    return render(request, 'contest/candidate_analytics.html', {
        'results': results,
        'total_contests': total_contests,
        'registered': registered,
        'completed': completed,
        'understanding_level': understanding_level,
        'top_3': top_3,
        'candidate_rank': candidate_rank
    })

@csrf_exempt
@login_required
def run_contest_code(request, question_id):
    if request.method == 'POST':
        from .models import ProgrammingQuestion
        question = get_object_or_404(ProgrammingQuestion, pk=question_id)
        
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            language = data.get('language', 'python')
        except json.JSONDecodeError:
            return JsonResponse({'output': '// Invalid request', 'results': []})
            
        # For RUN button, test against sample input/output
        input_data = question.sample_input or ''
        expected_output = question.sample_output or ''
        
        if not input_data and not expected_output:
            return JsonResponse({'output': '// No sample input/output provided for this question.', 'results': []})
            
        stdout, stderr = execute_code(code, language, input_data=input_data)
        
        actual = stdout if stdout else ''
        error = stderr if stderr else ''
        passed = (actual.strip() == expected_output.strip()) and not error
        
        status = '✓ Passed' if passed else '✗ Failed'
        output_text = (
            f"Sample Test: {status}\n"
            f"  Input:    {input_data}\n"
            f"  Expected: {expected_output}\n"
            f"  Got:      {error if error else actual}"
        )
        
        return JsonResponse({
            'output': output_text,
            'results': [{
                'input': input_data,
                'expected': expected_output,
                'actual': error if error else actual,
                'passed': passed
            }]
        })
    return JsonResponse({'output': '// Method not allowed', 'results': []})