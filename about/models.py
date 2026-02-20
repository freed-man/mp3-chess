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
