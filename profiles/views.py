from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Game
from .forms import ProfileForm

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

from .forms import ProfileForm


@login_required
def profile_edit(request, username):
    """
    Allows a user to edit their own profile.
    """
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    if request.user != user:
        messages.add_message(request, messages.ERROR, 'You can only edit your own profile!')
        return redirect('profile', username=username)

    if request.method == "POST":
        profile_form = ProfileForm(data=request.POST, files=request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, 'Profile updated!')
            return redirect('profile', username=username)
    else:
        profile_form = ProfileForm(instance=profile)

    return render(
        request,
        "profiles/profile_edit.html",
        {
            "profile_form": profile_form,
            "profile": profile,
        },
    )
