from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('contest/', views.recruiter_contest_results, name='recruiter_contest_results'),
]