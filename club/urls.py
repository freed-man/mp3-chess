from django.urls import path
from . import views

urlpatterns = [
    path('', views.TopicList.as_view(), name='home'),
    path('<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('<slug:slug>/upvote/', views.topic_vote, {'vote_type': 1}, name='topic_upvote'),
    path('<slug:slug>/downvote/', views.topic_vote, {'vote_type': -1}, name='topic_downvote'),
]
