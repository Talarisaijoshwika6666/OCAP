from django.shortcuts import redirect
from functools import wraps


def recruiter_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?panel=recruiter')
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('/accounts/login/?panel=recruiter')
        return view_func(request, *args, **kwargs)
    return wrapper


def candidate_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?panel=candidate')
        # Superusers get dual access; block plain staff (recruiter-only) accounts
        if request.user.is_staff and not request.user.is_superuser:
            return redirect('/recruiter/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper