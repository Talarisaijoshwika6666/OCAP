from django.contrib import admin
from django.urls import path, include
from OnlineCodingAssessment.views import home_view
from quest import views as quest_views
from recruiter import views as recruiter_views

urlpatterns = [
    path('admin/',        admin.site.urls),
    path('accounts/',     include('accounts.urls')),
    path('questions/',    include('questions.urls')),
    path('submissions/',  include('submissions.urls')),
    path('leaderboard/',  include('leaderboard.urls')),
    path('contest/',      include('contest.urls')),
    path('discuss/',      include('discuss.urls')),
    path('study-plan/',   quest_views.study_plan_view, name='study_plan'),
    path('',              home_view, name='home'),
    path('quest/',        include('quest.urls')),
    path('recruiter/',    include('recruiter.urls')),
]