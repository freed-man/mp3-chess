from django.contrib import admin
from .models import Profile, Game


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill_level', 'is_approved')
    list_filter = ('is_approved', 'skill_level')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('user', 'opponent_name', 'date_played', 'result')
    list_filter = ('result',)
