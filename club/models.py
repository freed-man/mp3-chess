from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

STATUS = ((0, "Draft"), (1, "Published"))


class Topic(models.Model):
    """
    Stores a single topic entry related to :model:`auth.User`.
    """
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="topics")
    content = models.TextField()
    featured_image = CloudinaryField('image', default='placeholder')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)
    excerpt = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    """
    Stores a single comment related to :model:`club.Topic` and :model:`auth.User`.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment by {self.user} on {self.topic}"


class Vote(models.Model):
    """
    Stores a single vote related to :model:`club.Topic` and :model:`auth.User`.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.IntegerField(choices=((1, "Upvote"), (-1, "Downvote")))

    class Meta:
        unique_together = ('topic', 'user')

    def __str__(self):
        return f"{self.user} voted {self.vote_type} on {self.topic}"
