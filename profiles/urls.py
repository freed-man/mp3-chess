from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.profile_view, name='profile'),
    path('<str:username>/edit/', views.profile_edit, name='profile_edit'),
    path('<str:username>/log-game/', views.log_game, name='log_game'),
    path('<str:username>/edit-game/<int:game_id>/', views.game_edit, name='game_edit'),
    path('<str:username>/delete-game/<int:game_id>/', views.game_delete, name='game_delete'),
]
