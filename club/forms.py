from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """
    Form for users to post a comment on a topic.
    """
    class Meta:
        model = Comment
        fields = ('body',)
