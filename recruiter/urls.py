from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('candidates/', views.recruiter_candidates, name='recruiter_candidates'),
    path('candidates/<int:candidate_id>/view/', views.recruiter_candidate_view, name='recruiter_candidate_view'),
    path('candidates/<int:candidate_id>/edit/', views.recruiter_candidate_edit, name='recruiter_candidate_edit'),
    path('candidates/<int:candidate_id>/delete/', views.recruiter_candidate_delete, name='recruiter_candidate_delete'),
]