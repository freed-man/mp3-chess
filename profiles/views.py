from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Game


def profile_view(request, username):
    """
    Displays a user's profile with their game history and stats.
    """
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    games = Game.objects.filter(user=user).order_by('-date_played')
    wins = games.filter(result='Win').count()
    draws = games.filter(result='Draw').count()
    losses = games.filter(result='Loss').count()

    return render(
        request,
        "profiles/profile.html",
        {
            "profile": profile,
            "games": games,
            "wins": wins,
            "draws": draws,
            "losses": losses,
        },
    )
