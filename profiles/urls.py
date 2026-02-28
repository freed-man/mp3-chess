from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.profile_view, name='profile'),
    path('<str:username>/edit/', views.profile_edit, name='profile_edit'),
    path('<str:username>/log-game/', views.log_game, name='log_game'),
]
