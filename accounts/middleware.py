from django.shortcuts import redirect

class CandidateAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser and not request.user.is_staff:
            # Block candidates from admin panel
            if request.path.startswith('/admin/'):
                return redirect('/')

            # Block candidates from making any changes (POST/PUT/DELETE)
            # Allow only these POST paths
            allowed_post_paths = [
                '/accounts/login/',
                '/accounts/logout/',
                '/accounts/register/',
                '/submissions/submit/',
                '/submissions/run/',
            ]
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                if not any(request.path.startswith(p) for p in allowed_post_paths):
                    return redirect('/')

        response = self.get_response(request)
        return response