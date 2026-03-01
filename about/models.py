from django.db import models
from cloudinary.models import CloudinaryField


class About(models.Model):
    """
    Stores a single about page entry for the chess club.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    club_image = CloudinaryField('image', default='placeholder')
    location = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


CATEGORY_CHOICES = (
    ("Question", "Question"),
    ("Comment", "Comment"),
    ("Request", "Request"),
    ("Technical Issue", "Technical Issue"),
)


class ContactRequest(models.Model):
    """
    Stores a single contact request from a site visitor.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    message = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} from {self.name}"
