from django.urls import path

from accounts.views import settings_view as account_settings_view
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('settings/', account_settings_view, name='recruiter_settings'),
    path('contest/', views.recruiter_contest_results, name='recruiter_contest_results'),
    path('problems/', views.recruiter_problem_bank, name='recruiter_problem_bank'),
    path('problems/add/', views.recruiter_add_problem, name='recruiter_add_problem'),
    path('problems/<int:pk>/delete/', views.recruiter_delete_problem, name='recruiter_delete_problem'),
]