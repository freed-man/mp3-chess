from django.shortcuts import render
from django.contrib import messages
from .models import About
from .forms import ContactForm


def about_page(request):
    """
    Displays the about page with club information and contact form.
    """
    if request.method == "POST":
        contact_form = ContactForm(data=request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.add_message(
                request, messages.SUCCESS,
                'Message sent! We will get back to you soon.'
            )

    about = About.objects.all().order_by('-updated_on').first()
    contact_form = ContactForm()

    return render(
        request,
        "about/about.html",
        {
            "about": about,
            "contact_form": contact_form,
        },
    )
