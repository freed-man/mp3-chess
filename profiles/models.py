from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

GENDER_CHOICES = (("Male", "Male"), ("Female", "Female"), ("Prefer not to say", "Prefer not to say"))
SKILL_CHOICES = (("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced"))
RESULT_CHOICES = (("Win", "Win"), ("Draw", "Draw"), ("Loss", "Loss"))


class Profile(models.Model):
    """
    Stores a single profile related to :model:`auth.User`.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_photo = CloudinaryField('image', default='placeholder')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_CHOICES, blank=True)
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Game(models.Model):
    """
    Stores a single game record related to :model:`auth.User`.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    opponent_name = models.CharField(max_length=100)
    date_played = models.DateField()
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)

    class Meta:
        ordering = ["-date_played"]

    def __str__(self):
        return f"{self.user} vs {self.opponent_name} - {self.result}"
