from django.urls import path
from . import views

urlpatterns = [
    path('', views.TopicList.as_view(), name='home'),
    path('<slug:slug>/', views.topic_detail, name='topic_detail'),
]
