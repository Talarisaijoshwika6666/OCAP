from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('assessment/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('assessment/<int:assessment_id>/start/', views.start_assessment, name='start_assessment'),
]