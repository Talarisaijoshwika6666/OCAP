from django.shortcuts import redirect

class CandidateAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            # RECRUITER — block code submission and solving
            if user.is_staff and not user.is_superuser:
                blocked = [
                    '/questions/submit/',
                    '/submissions/run/',
                    '/submissions/submit/',
                ]
                if any(request.path.startswith(b) for b in blocked):
                    return redirect('/recruiter/dashboard/')

            # CANDIDATE — block recruiter and admin areas
            if not user.is_staff and not user.is_superuser:
                if request.path.startswith('/admin/'):
                    return redirect('/candidates/dashboard/')
                if request.path.startswith('/recruiter/'):
                    return redirect('/candidates/dashboard/')

        response = self.get_response(request)
        return response