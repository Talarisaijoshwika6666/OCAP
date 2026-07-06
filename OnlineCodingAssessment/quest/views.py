from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Topic

User = get_user_model()

def quest_view(request):
    topics = Topic.objects.filter(category='quest').order_by('order')
    return render(request, 'quest/quest.html', {'topics': topics})

def explore_view(request):
    topics = Topic.objects.filter(category='explore').order_by('order')
    return render(request, 'quest/explore.html', {'topics': topics})

def study_plan_view(request):
    topics = Topic.objects.filter(category='study_plan').order_by('order')
    return render(request, 'quest/study_plan.html', {'topics': topics})

def home_view(request):
    return render(request, 'home.html')

def discuss_view(request):
    return render(request, 'discuss/discuss.html', {'posts': []})