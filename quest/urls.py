from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('quest/', views.quest_view, name='quest'),

    path(
        'study-plan/<str:topic>/',
        views.study_plan_view,
        name='study_plan'
    ),

    path(
        'learning-path/<str:subject>/',
        views.learning_path_view,
        name='learning_path'
    ),

    path(
        'learning-path/<str:subject>/<str:topic_slug>/',
        views.topic_detail_view,
        name='topic_detail'
    ),

    path(
        'api/progress/<str:subject>/<str:topic_slug>/',
        views.update_topic_progress,
        name='update_topic_progress'
    ),
]