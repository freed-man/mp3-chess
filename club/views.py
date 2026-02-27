from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib import messages
from .models import Topic, Comment
from .forms import CommentForm


class TopicList(generic.ListView):
    """
    Displays a list of published topics on the homepage.
    """
    queryset = Topic.objects.filter(status=1)
    template_name = "club/index.html"
    paginate_by = 6


def topic_detail(request, slug):
    """
    Displays a single topic with its comments and comment form.
    """
    queryset = Topic.objects.filter(status=1)
    topic = get_object_or_404(queryset, slug=slug)
    comments = topic.comments.all().order_by("created_on")
    comment_count = topic.comments.count()

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.topic = topic
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Comment posted!')

    comment_form = CommentForm()

    return render(
        request,
        "club/topic_detail.html",
        {
            "topic": topic,
            "comments": comments,
            "comment_count": comment_count,
            "comment_form": comment_form,
        },
    )
