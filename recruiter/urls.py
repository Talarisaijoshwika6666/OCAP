from django.urls import path

from accounts.views import settings_view as account_settings_view
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('candidates/', views.recruiter_candidates_view, name='recruiter_candidates'),
    path('candidates/<int:pk>/delete/', views.recruiter_delete_candidate, name='recruiter_delete_candidate'),
    path('all-submissions/', views.recruiter_all_submissions, name='recruiter_all_submissions'),
    path('settings/', account_settings_view, name='recruiter_settings'),
    path('contest/', views.recruiter_contest_results, name='recruiter_contest_results'),
    path('problems/', views.recruiter_problem_bank, name='recruiter_problem_bank'),
    path('problems/add/', views.recruiter_add_problem, name='recruiter_add_problem'),
    path('problems/<int:pk>/delete/', views.recruiter_delete_problem, name='recruiter_delete_problem'),
    path('reports/', views.reports_page, name='recruiter_reports'),
    path('reports/api/candidate-performance/', views.candidate_performance_api, name='candidate_performance_api'),
    path('reports/api/candidate-stats/', views.candidate_stats_api, name='candidate_stats_api'),
    path('reports/api/contest-results/', views.contest_results_api, name='contest_results_api'),
    path('reports/api/contest-analytics/', views.contest_analytics_api, name='contest_analytics_api'),
    path('reports/api/contest-stats/', views.contest_stats_api, name='contest_stats_api'),
]