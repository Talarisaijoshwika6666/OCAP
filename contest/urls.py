from django.urls import path
from . import views

urlpatterns = [
    path('', views.contest_view, name='contest'),
    path('register/<int:pk>/', views.register_contest, name='register_contest'),
    path('start/<int:pk>/', views.start_contest_auth, name='start_contest_auth'),
    path('exam/<int:pk>/', views.contest_exam, name='contest_exam'),
    path('submit/<int:pk>/', views.submit_exam, name='submit_exam'),
    path('result/<int:pk>/', views.view_result, name='view_result'),
    path('review/<int:pk>/', views.view_exam, name='view_exam'),
    path('analytics/', views.candidate_analytics, name='candidate_analytics'),
    path('run/<int:question_id>/', views.run_contest_code, name='run_contest_code'),
]