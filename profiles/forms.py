from django import forms
from .models import Profile, Game


class ProfileForm(forms.ModelForm):
    """
    Form for users to edit their profile.
    """
    class Meta:
        model = Profile
        fields = ('profile_photo', 'date_of_birth', 'gender', 'skill_level', 'bio')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class GameForm(forms.ModelForm):
    """
    Form for users to log a game.
    """
    class Meta:
        model = Game
        fields = ('opponent_name', 'date_played', 'result')
