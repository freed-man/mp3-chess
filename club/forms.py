from django import forms
from .models import Comment, Vote


class CommentForm(forms.ModelForm):
    """
    Form for users to post a comment on a topic.
    """
    class Meta:
        model = Comment
        fields = ('body',)


class VoteForm(forms.ModelForm):
    """
    Form for users to vote on a topic.
    """
    class Meta:
        model = Vote
        fields = ('vote_type',)
