from django import forms
from .models import ContactRequest


class ContactForm(forms.ModelForm):
    """
    Form for users to send a contact request.
    """
    class Meta:
        model = ContactRequest
        fields = ('name', 'email', 'category', 'message')
