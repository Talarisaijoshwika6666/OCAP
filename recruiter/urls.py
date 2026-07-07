from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('problems/', views.recruiter_problem_bank, name='recruiter_problem_bank'),
    path('problems/add/', views.recruiter_add_question, name='recruiter_add_question'),
    path('problems/delete/<int:pk>/', views.recruiter_delete_question, name='recruiter_delete_question'),
    path('submissions/', views.recruiter_submissions, name='recruiter_submissions'),
]
