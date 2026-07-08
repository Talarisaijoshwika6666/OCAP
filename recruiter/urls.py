from django.urls import path

from accounts.views import settings_view as account_settings_view
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('settings/', account_settings_view, name='recruiter_settings'),
    path('contest/', views.recruiter_contest_results, name='recruiter_contest_results'),
    path('reports/', views.reports_page, name='recruiter_reports'),
    path('reports/api/candidate-performance/', views.candidate_performance_api, name='candidate_performance_api'),
    path('reports/api/candidate-stats/', views.candidate_stats_api, name='candidate_stats_api'),
    path('reports/api/contest-results/', views.contest_results_api, name='contest_results_api'),
    path('reports/api/contest-analytics/', views.contest_analytics_api, name='contest_analytics_api'),
    path('reports/api/contest-stats/', views.contest_stats_api, name='contest_stats_api'),
]