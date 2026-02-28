from django.shortcuts import render
from .models import About


def about_page(request):
    """
    Displays the about page with club information.
    """
    about = About.objects.all().order_by('-updated_on').first()

    return render(
        request,
        "about/about.html",
        {
            "about": about,
        },
    )
