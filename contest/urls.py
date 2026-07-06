from django.urls import path
from . import views

urlpatterns = [
    path('', views.contest_view, name='contest'),
    path('leaderboard/', views.contest_leaderboard_view, name='contest_leaderboard'),
    path('register/<int:pk>/', views.register_contest, name='register_contest'),
    path('leave/<int:pk>/', views.leave_contest, name='leave_contest'),
    path('<int:pk>/', views.contest_detail, name='contest_detail'),
    path('<int:pk>/take-test/', views.contest_take_test, name='contest_take_test'),
    path('<int:pk>/result/', views.contest_result, name='contest_result'),
    path('<int:pk>/solve/<int:question_pk>/', views.contest_solve, name='contest_solve'),
    path('<int:pk>/solve/<int:question_pk>/run/', views.contest_run_code, name='contest_run_code'),
    path('<int:pk>/solve/<int:question_pk>/submit/', views.contest_submit_solution, name='contest_submit_solution'),
]
