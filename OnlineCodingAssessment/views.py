from django.shortcuts import render

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    from questions.models import Question
    total_problems = Question.objects.count()
    return render(request, 'home.html', {'total_problems': total_problems})