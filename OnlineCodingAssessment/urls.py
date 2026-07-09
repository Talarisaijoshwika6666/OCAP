from django.contrib import admin
from django.urls import path, include
from OnlineCodingAssessment.views import home_view, dashboard_view, streak_view, dashboard_api
from quest import views as quest_views
from recruiter import views as recruiter_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('questions/', include('questions.urls')),
    path('submissions/', include('submissions.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('contest/', include('contest.urls')),
    path('discuss/', include('discuss.urls')),
    path('results/', include('results.urls')),
    path('assessments/', include('assessments.urls')),
    path('candidates/', include('candidates.urls')),
    path('recruiter/', include('recruiter.urls')),
    path('study-plan/', quest_views.study_plan_view, name='study_plan'),
    path('', home_view, name='home'),
    path('home/', home_view, name='home_alt'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/api/', dashboard_api, name='dashboard_api'),
    path('streak/', streak_view, name='streak'),
    path('quest/', include('quest.urls')),
    
]
