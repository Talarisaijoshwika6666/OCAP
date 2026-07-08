from django.urls import path

from accounts.views import settings_view as account_settings_view
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('contests/', views.recruiter_contests, name='recruiter_contests'),
    path('all-submissions/', views.recruiter_all_submissions, name='recruiter_all_submissions'),
    path('settings/', account_settings_view, name='recruiter_settings'),
    path('candidates/', views.recruiter_candidates, name='recruiter_candidates'),
    path('reports/', views.recruiter_reports, name='recruiter_reports'),
    path('contest/', views.recruiter_contest_results, name='recruiter_contest_results'),
    path('problems/', views.recruiter_problem_bank, name='recruiter_problem_bank'),
    path('problems/add/', views.recruiter_add_problem, name='recruiter_add_problem'),
    path('problems/<int:pk>/delete/', views.recruiter_delete_problem, name='recruiter_delete_problem'),
]