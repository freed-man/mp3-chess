"""
Tests for the 'club' app.
Covers: Models, Views, Forms, URLs.
"""
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from club.models import Topic, Comment, Vote, STATUS    # noqa
from club.forms import CommentForm, VoteForm
from club.views import (
    TopicList, topic_detail, topic_search,
    topic_vote, comment_edit, comment_delete,
)


# ──────────────────────────────────────────────
# MODEL TESTS
# ──────────────────────────────────────────────
class TopicModelTest(TestCase):
    """Tests for the Topic model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Best Chess Openings",
            slug="best-chess-openings",
            user=self.user,
            content="Let's discuss the best openings.",
            status=1,
            excerpt="A discussion about openings.",
        )

    def test_topic_creation(self):
        """Test that a Topic is created correctly."""
        self.assertEqual(self.topic.title, "Best Chess Openings")
        self.assertEqual(self.topic.slug, "best-chess-openings")
        self.assertEqual(self.topic.user, self.user)
        self.assertEqual(self.topic.status, 1)

    def test_topic_str(self):
        """Test the __str__ method returns the title."""
        self.assertEqual(str(self.topic), "Best Chess Openings")

    def test_topic_default_status_is_draft(self):
        """Test that the default status is 0 (Draft)."""
        topic = Topic.objects.create(
            title="Draft Topic",
            slug="draft-topic",
            user=self.user,
            content="Draft content.",
        )
        self.assertEqual(topic.status, 0)

    def test_topic_default_image(self):
        """Test that the default featured_image is 'placeholder'."""
        self.assertEqual(self.topic.featured_image, "placeholder")

    def test_topic_ordering(self):
        """Test that topics are ordered by -created_on."""
        topic2 = Topic.objects.create(
            title="Second Topic",
            slug="second-topic",
            user=self.user,
            content="Content.",
            status=1,
        )
        topics = list(Topic.objects.all())
        self.assertEqual(topics[0], topic2)
        self.assertEqual(topics[1], self.topic)

    def test_topic_title_unique(self):
        """Test that topic titles must be unique."""
        with self.assertRaises(Exception):
            Topic.objects.create(
                title="Best Chess Openings",
                slug="best-chess-openings-2",
                user=self.user,
                content="Duplicate title.",
            )

    def test_topic_slug_unique(self):
        """Test that topic slugs must be unique."""
        with self.assertRaises(Exception):
            Topic.objects.create(
                title="Different Title",
                slug="best-chess-openings",
                user=self.user,
                content="Duplicate slug.",
            )

    def test_topic_cascade_delete_with_user(self):
        """Test that topics are deleted when the user is deleted."""
        self.user.delete()
        self.assertEqual(Topic.objects.count(), 0)


class CommentModelTest(TestCase):
    """Tests for the Comment model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="commenter", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Discussion Topic",
            slug="discussion-topic",
            user=self.user,
            content="Discussion content.",
            status=1,
        )
        self.comment = Comment.objects.create(
            topic=self.topic,
            user=self.user,
            body="Great discussion!",
        )

    def test_comment_creation(self):
        """Test that a Comment is created correctly."""
        self.assertEqual(self.comment.body, "Great discussion!")
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.topic, self.topic)

    def test_comment_str(self):
        """Test the __str__ method returns the expected string."""
        expected = f"Comment by {self.user} on {self.topic}"
        self.assertEqual(str(self.comment), expected)

    def test_comment_ordering(self):
        """Test that comments are ordered by created_on ascending."""
        comment2 = Comment.objects.create(
            topic=self.topic, user=self.user, body="Second comment."
        )
        comments = list(self.topic.comments.all())
        self.assertEqual(comments[0], self.comment)
        self.assertEqual(comments[1], comment2)

    def test_comment_cascade_delete_with_topic(self):
        """Test that comments are deleted when the topic is deleted."""
        self.topic.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_cascade_delete_with_user(self):
        """Test that comments are deleted when the user is deleted."""
        self.user.delete()
        self.assertEqual(Comment.objects.count(), 0)


class VoteModelTest(TestCase):
    """Tests for the Vote model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="voter", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Vote Topic",
            slug="vote-topic",
            user=self.user,
            content="Vote on this.",
            status=1,
        )
        self.vote = Vote.objects.create(
            topic=self.topic, user=self.user, vote_type=1
        )

    def test_vote_creation(self):
        """Test that a Vote is created correctly."""
        self.assertEqual(self.vote.vote_type, 1)
        self.assertEqual(self.vote.user, self.user)
        self.assertEqual(self.vote.topic, self.topic)

    def test_vote_str(self):
        """Test the __str__ method returns the expected string."""
        expected = f"{self.user} voted 1 on {self.topic}"
        self.assertEqual(str(self.vote), expected)

    def test_vote_unique_together(self):
        """Test that a user can only vote once per topic."""
        with self.assertRaises(Exception):
            Vote.objects.create(
                topic=self.topic, user=self.user, vote_type=-1
            )

    def test_vote_cascade_delete_with_topic(self):
        """Test that votes are deleted when the topic is deleted."""
        self.topic.delete()
        self.assertEqual(Vote.objects.count(), 0)


# ──────────────────────────────────────────────
# FORM TESTS
# ──────────────────────────────────────────────
class CommentFormTest(TestCase):
    """Tests for the CommentForm."""

    def test_form_has_correct_fields(self):
        """Test the form only exposes the 'body' field."""
        form = CommentForm()
        self.assertEqual(list(form.fields.keys()), ["body"])

    def test_form_valid_data(self):
        """Test the form is valid with a body provided."""
        form = CommentForm(data={"body": "Nice topic!"})
        self.assertTrue(form.is_valid())

    def test_form_empty_body_invalid(self):
        """Test the form is invalid without a body."""
        form = CommentForm(data={"body": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("body", form.errors)


class VoteFormTest(TestCase):
    """Tests for the VoteForm."""

    def test_form_has_correct_fields(self):
        """Test the form only exposes the 'vote_type' field."""
        form = VoteForm()
        self.assertEqual(list(form.fields.keys()), ["vote_type"])

    def test_form_valid_upvote(self):
        """Test the form is valid with an upvote."""
        form = VoteForm(data={"vote_type": 1})
        self.assertTrue(form.is_valid())

    def test_form_valid_downvote(self):
        """Test the form is valid with a downvote."""
        form = VoteForm(data={"vote_type": -1})
        self.assertTrue(form.is_valid())


# ──────────────────────────────────────────────
# VIEW TESTS
# ──────────────────────────────────────────────
class TopicListViewTest(TestCase):
    """Tests for the TopicList view (homepage)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Create published and draft topics
        for i in range(8):
            Topic.objects.create(
                title=f"Topic {i}",
                slug=f"topic-{i}",
                user=self.user,
                content=f"Content for topic {i}",
                status=1,
            )
        self.draft = Topic.objects.create(
            title="Draft Topic",
            slug="draft-topic",
            user=self.user,
            content="Draft content.",
            status=0,
        )

    def test_homepage_status_200(self):
        """Test the homepage returns HTTP 200."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        """Test the homepage renders the correct template."""
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "club/index.html")

    def test_homepage_only_shows_published(self):
        """Test that only published topics appear on the homepage."""
        response = self.client.get(reverse("home"))
        for topic in response.context["object_list"]:
            self.assertEqual(topic.status, 1)

    def test_homepage_pagination(self):
        """Test that the homepage paginates at 6 items."""
        response = self.client.get(reverse("home"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["object_list"]), 6)

    def test_homepage_second_page(self):
        """Test the second page of pagination works."""
        response = self.client.get(reverse("home") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 2)


class TopicSearchViewTest(TestCase):
    """Tests for the topic_search view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.topic1 = Topic.objects.create(
            title="Sicilian Defense",
            slug="sicilian-defense",
            user=self.user,
            content="The Sicilian Defense is popular.",
            status=1,
        )
        self.topic2 = Topic.objects.create(
            title="French Defense",
            slug="french-defense",
            user=self.user,
            content="The French Defense is solid.",
            status=1,
        )
        self.draft = Topic.objects.create(
            title="Secret Draft",
            slug="secret-draft",
            user=self.user,
            content="Sicilian variant notes.",
            status=0,
        )

    def test_search_status_200(self):
        """Test the search page returns HTTP 200."""
        response = self.client.get(reverse("topic_search"), {"q": "test"})
        self.assertEqual(response.status_code, 200)

    def test_search_uses_correct_template(self):
        """Test the search page renders the correct template."""
        response = self.client.get(reverse("topic_search"), {"q": "test"})
        self.assertTemplateUsed(response, "club/search_results.html")

    def test_search_finds_by_title(self):
        """Test that search finds topics by title."""
        response = self.client.get(reverse("topic_search"), {"q": "Sicilian"})
        self.assertIn(self.topic1, response.context["results"])

    def test_search_finds_by_content(self):
        """Test that search finds topics by content."""
        response = self.client.get(reverse("topic_search"), {"q": "solid"})
        self.assertIn(self.topic2, response.context["results"])

    def test_search_excludes_drafts(self):
        """Test that search does not return draft topics."""
        response = self.client.get(reverse("topic_search"), {"q": "Sicilian"})
        self.assertNotIn(self.draft, response.context["results"])

    def test_search_empty_query(self):
        """Test that an empty query returns no results."""
        response = self.client.get(reverse("topic_search"), {"q": ""})
        self.assertEqual(len(response.context["results"]), 0)

    def test_search_no_match(self):
        """Test that a non-matching query returns no results."""
        response = self.client.get(reverse("topic_search"), {"q": "xyz123"})
        self.assertEqual(len(response.context["results"]), 0)


class TopicDetailViewTest(TestCase):
    """Tests for the topic_detail view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Detail Topic",
            slug="detail-topic",
            user=self.user,
            content="Detailed content.",
            status=1,
        )
        self.comment = Comment.objects.create(
            topic=self.topic, user=self.user, body="A comment."
        )
        Vote.objects.create(topic=self.topic, user=self.user, vote_type=1)

    def test_detail_status_200(self):
        """Test that a published topic detail page returns HTTP 200."""
        response = self.client.get(
            reverse("topic_detail", args=["detail-topic"])
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        """Test the detail page renders the correct template."""
        response = self.client.get(
            reverse("topic_detail", args=["detail-topic"])
        )
        self.assertTemplateUsed(response, "club/topic_detail.html")

    def test_detail_context(self):
        """Test that the context contains the expected keys."""
        response = self.client.get(
            reverse("topic_detail", args=["detail-topic"])
        )
        self.assertEqual(response.context["topic"], self.topic)
        self.assertEqual(response.context["comment_count"], 1)
        self.assertEqual(response.context["upvotes"], 1)
        self.assertEqual(response.context["downvotes"], 0)
        self.assertIsInstance(response.context["comment_form"], CommentForm)

    def test_detail_draft_returns_404(self):
        """Test that a draft topic returns HTTP 404."""
        Topic.objects.create(
            title="Draft",
            slug="draft",
            user=self.user,
            content="Draft.",
            status=0,
        )
        response = self.client.get(reverse("topic_detail", args=["draft"]))
        self.assertEqual(response.status_code, 404)

    def test_detail_nonexistent_slug_returns_404(self):
        """Test that a non-existent slug returns HTTP 404."""
        response = self.client.get(
            reverse("topic_detail", args=["nonexistent"])
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_user_vote_context_anonymous(self):
        """Test user_vote is None for anonymous users."""
        response = self.client.get(
            reverse("topic_detail", args=["detail-topic"])
        )
        self.assertIsNone(response.context["user_vote"])

    def test_detail_user_vote_context_authenticated(self):
        """Test user_vote is populated for authenticated users."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("topic_detail", args=["detail-topic"])
        )
        self.assertIsNotNone(response.context["user_vote"])

    def test_post_comment_authenticated(self):
        """Test that an authenticated user can post a comment."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("topic_detail", args=["detail-topic"]),
            data={"body": "New comment!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)

    def test_post_comment_invalid_data(self):
        """Test that an invalid comment does not save."""
        self.client.login(username="testuser", password="testpass123")
        self.client.post(
            reverse("topic_detail", args=["detail-topic"]),
            data={"body": ""},
        )
        self.assertEqual(Comment.objects.count(), 1)


class TopicVoteViewTest(TestCase):
    """Tests for the topic_vote view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="voter", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Votable Topic",
            slug="votable-topic",
            user=self.user,
            content="Vote on this.",
            status=1,
        )

    def test_vote_redirects_to_detail(self):
        """Test that voting redirects to the topic detail page."""
        self.client.login(username="voter", password="testpass123")
        response = self.client.get(
            reverse("topic_upvote", args=["votable-topic"])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("topic_detail", args=["votable-topic"]),
        )

    def test_upvote_creates_vote(self):
        """Test that upvoting creates a new vote."""
        self.client.login(username="voter", password="testpass123")
        self.client.get(reverse("topic_upvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote_type, 1)

    def test_downvote_creates_vote(self):
        """Test that downvoting creates a new vote."""
        self.client.login(username="voter", password="testpass123")
        self.client.get(reverse("topic_downvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote_type, -1)

    def test_toggle_same_vote_removes_it(self):
        """Test that voting the same type twice removes the vote."""
        self.client.login(username="voter", password="testpass123")
        self.client.get(reverse("topic_upvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.count(), 1)
        self.client.get(reverse("topic_upvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.count(), 0)

    def test_change_vote_type(self):
        """Test that voting a different type updates the vote."""
        self.client.login(username="voter", password="testpass123")
        self.client.get(reverse("topic_upvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.first().vote_type, 1)
        self.client.get(reverse("topic_downvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote_type, -1)

    def test_anonymous_vote_does_not_create(self):
        """Test that anonymous users cannot vote."""
        self.client.get(reverse("topic_upvote", args=["votable-topic"]))
        self.assertEqual(Vote.objects.count(), 0)


class CommentEditViewTest(TestCase):
    """Tests for the comment_edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="editor", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Edit Topic",
            slug="edit-topic",
            user=self.user,
            content="Content.",
            status=1,
        )
        self.comment = Comment.objects.create(
            topic=self.topic, user=self.user, body="Original comment."
        )

    def test_edit_own_comment(self):
        """Test that a user can edit their own comment."""
        self.client.login(username="editor", password="testpass123")
        response = self.client.post(
            reverse("comment_edit", args=["edit-topic", self.comment.id]),
            data={"body": "Updated comment."},
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Updated comment.")

    def test_cannot_edit_other_users_comment(self):
        """Test that a user cannot edit another user's comment."""
        self.client.login(username="other", password="testpass123")
        self.client.post(
            reverse("comment_edit", args=["edit-topic", self.comment.id]),
            data={"body": "Hacked!"},
        )
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Original comment.")

    def test_edit_redirects_to_detail(self):
        """Test that editing redirects to the topic detail page."""
        self.client.login(username="editor", password="testpass123")
        response = self.client.post(
            reverse("comment_edit", args=["edit-topic", self.comment.id]),
            data={"body": "Updated."},
        )
        self.assertRedirects(
            response,
            reverse("topic_detail", args=["edit-topic"]),
        )


class CommentDeleteViewTest(TestCase):
    """Tests for the comment_delete view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="deleter", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )
        self.topic = Topic.objects.create(
            title="Delete Topic",
            slug="delete-topic",
            user=self.user,
            content="Content.",
            status=1,
        )
        self.comment = Comment.objects.create(
            topic=self.topic, user=self.user, body="Delete me."
        )

    def test_delete_own_comment(self):
        """Test that a user can delete their own comment."""
        self.client.login(username="deleter", password="testpass123")
        self.client.post(
            reverse("comment_delete", args=["delete-topic", self.comment.id])
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_cannot_delete_other_users_comment(self):
        """Test that a user cannot delete another user's comment."""
        self.client.login(username="other", password="testpass123")
        self.client.post(
            reverse("comment_delete", args=["delete-topic", self.comment.id])
        )
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_redirects_to_detail(self):
        """Test that deleting redirects to the topic detail page."""
        self.client.login(username="deleter", password="testpass123")
        response = self.client.post(
            reverse("comment_delete", args=["delete-topic", self.comment.id])
        )
        self.assertRedirects(
            response,
            reverse("topic_detail", args=["delete-topic"]),
        )


# ──────────────────────────────────────────────
# URL TESTS
# ──────────────────────────────────────────────
class ClubURLTest(TestCase):
    """Tests for club app URL routing."""

    def test_home_url_resolves(self):
        """Test that the home URL resolves to TopicList."""
        url = reverse("home")
        self.assertEqual(resolve(url).func.view_class, TopicList)

    def test_search_url_resolves(self):
        """Test that the search URL resolves correctly."""
        url = reverse("topic_search")
        self.assertEqual(resolve(url).func, topic_search)

    def test_detail_url_resolves(self):
        """Test that the detail URL resolves correctly."""
        url = reverse("topic_detail", args=["test-slug"])
        self.assertEqual(resolve(url).func, topic_detail)

    def test_upvote_url_resolves(self):
        """Test that the upvote URL resolves correctly."""
        url = reverse("topic_upvote", args=["test-slug"])
        self.assertEqual(resolve(url).func, topic_vote)

    def test_downvote_url_resolves(self):
        """Test that the downvote URL resolves correctly."""
        url = reverse("topic_downvote", args=["test-slug"])
        self.assertEqual(resolve(url).func, topic_vote)

    def test_comment_edit_url_resolves(self):
        """Test that the comment edit URL resolves correctly."""
        url = reverse("comment_edit", args=["test-slug", 1])
        self.assertEqual(resolve(url).func, comment_edit)

    def test_comment_delete_url_resolves(self):
        """Test that the comment delete URL resolves correctly."""
        url = reverse("comment_delete", args=["test-slug", 1])
        self.assertEqual(resolve(url).func, comment_delete)

    def test_home_url_path(self):
        """Test the home URL path."""
        self.assertEqual(reverse("home"), "/")

    def test_search_url_path(self):
        """Test the search URL path."""
        self.assertEqual(reverse("topic_search"), "/search/")
