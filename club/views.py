from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Topic, Comment, Vote
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
    upvotes = topic.votes.filter(vote_type=1).count()
    downvotes = topic.votes.filter(vote_type=-1).count()
    user_vote = None

    if request.user.is_authenticated:
        user_vote = topic.votes.filter(user=request.user).first()

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
            "upvotes": upvotes,
            "downvotes": downvotes,
            "user_vote": user_vote,
        },
    )


def topic_vote(request, slug, vote_type):
    """
    Handles upvoting and downvoting a topic.
    """
    topic = get_object_or_404(Topic, slug=slug, status=1)

    if request.user.is_authenticated:
        existing_vote = topic.votes.filter(user=request.user).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                existing_vote.delete()
                messages.add_message(request, messages.SUCCESS, 'Vote removed!')
            else:
                existing_vote.vote_type = vote_type
                existing_vote.save()
                messages.add_message(request, messages.SUCCESS, 'Vote updated!')
        else:
            Vote.objects.create(topic=topic, user=request.user, vote_type=vote_type)
            messages.add_message(request, messages.SUCCESS, 'Vote recorded!')

    return HttpResponseRedirect(reverse('topic_detail', args=[slug]))


def comment_edit(request, slug, comment_id):
    """
    Allows a user to edit their own comment.
    """
    queryset = Topic.objects.filter(status=1)
    topic = get_object_or_404(queryset, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment_form = CommentForm(data=request.POST, instance=comment)

    if request.method == "POST":
        if comment_form.is_valid() and comment.user == request.user:
            comment = comment_form.save(commit=False)
            comment.topic = topic
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Comment updated!')
        else:
            messages.add_message(request, messages.ERROR, 'Error updating comment!')

    return HttpResponseRedirect(reverse('topic_detail', args=[slug]))


def comment_delete(request, slug, comment_id):
    """
    Allows a user to delete their own comment.
    """
    queryset = Topic.objects.filter(status=1)
    topic = get_object_or_404(queryset, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.user == request.user:
        comment.delete()
        messages.add_message(request, messages.SUCCESS, 'Comment deleted!')
    else:
        messages.add_message(request, messages.ERROR, 'You can only delete your own comments!')

    return HttpResponseRedirect(reverse('topic_detail', args=[slug]))
