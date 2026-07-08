from django.urls import path
from . import views

urlpatterns = [
    path('', views.discuss_view, name='discuss'),
    path('new/', views.new_post_view, name='new_post'),
    path('<int:pk>/', views.post_detail_view, name='post_detail'),
    path('<int:pk>/like/', views.like_post_view, name='like_post'),
]