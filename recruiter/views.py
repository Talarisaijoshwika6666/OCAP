from django.shortcuts import render, redirect

def recruiter_dashboard(request):
    if not request.session.get('is_recruiter'):
        return redirect('/accounts/login/?panel=recruiter')
    return render(request, 'recruiter/dashboard.html', {
        'username': request.session.get('recruiter_username', 'Recruiter')
    })