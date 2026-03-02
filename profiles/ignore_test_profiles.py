"""
Tests for the 'profiles' app.
Covers: Models, Views, Forms, URLs, Signals.
"""
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from profiles.models import (
    Profile, Game, GENDER_CHOICES, SKILL_CHOICES, RESULT_CHOICES,
)
from profiles.forms import ProfileForm, GameForm
from profiles.views import (
    profile_view, profile_edit, log_game,
    game_edit, game_delete, delete_account,
)
from datetime import date


# ──────────────────────────────────────────────
# MODEL TESTS
# ──────────────────────────────────────────────
class ProfileModelTest(TestCase):
    """Tests for the Profile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser", password="testpass123"
        )
        # Profile is auto-created by signal
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_created_on_user_creation(self):
        """Test that a Profile is auto-created via signal when a User is created."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_str(self):
        """Test the __str__ method returns the expected string."""
        self.assertEqual(str(self.profile), "profileuser's Profile")

    def test_profile_default_values(self):
        """Test that default values are set correctly."""
        self.assertFalse(self.profile.is_approved)
        self.assertEqual(self.profile.bio, "")
        self.assertEqual(self.profile.gender, "")
        self.assertEqual(self.profile.skill_level, "")
        self.assertIsNone(self.profile.date_of_birth)
        self.assertEqual(self.profile.profile_photo, "placeholder")

    def test_profile_cascade_delete_with_user(self):
        """Test that the profile is deleted when the user is deleted."""
        self.user.delete()
        self.assertEqual(Profile.objects.count(), 0)

    def test_profile_one_to_one_relationship(self):
        """Test that user.profile reverse accessor works."""
        self.assertEqual(self.user.profile, self.profile)


class GameModelTest(TestCase):
    """Tests for the Game model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="gamer", password="testpass123"
        )
        self.game = Game.objects.create(
            user=self.user,
            opponent_name="Magnus",
            date_played=date(2025, 1, 15),
            result="Win",
        )

    def test_game_creation(self):
        """Test that a Game is created correctly."""
        self.assertEqual(self.game.opponent_name, "Magnus")
        self.assertEqual(self.game.result, "Win")
        self.assertEqual(self.game.date_played, date(2025, 1, 15))

    def test_game_str(self):
        """Test the __str__ method returns the expected string."""
        expected = f"{self.user} vs Magnus - Win"
        self.assertEqual(str(self.game), expected)

    def test_game_ordering(self):
        """Test that games are ordered by -date_played."""
        game2 = Game.objects.create(
            user=self.user,
            opponent_name="Hikaru",
            date_played=date(2025, 3, 1),
            result="Loss",
        )
        games = list(Game.objects.filter(user=self.user))
        self.assertEqual(games[0], game2)
        self.assertEqual(games[1], self.game)

    def test_game_cascade_delete_with_user(self):
        """Test that games are deleted when the user is deleted."""
        self.user.delete()
        self.assertEqual(Game.objects.count(), 0)

    def test_game_result_choices(self):
        """Test that all valid result choices are accepted."""
        for choice_value, _ in RESULT_CHOICES:
            game = Game.objects.create(
                user=self.user,
                opponent_name="Opponent",
                date_played=date(2025, 2, 1),
                result=choice_value,
            )
            self.assertEqual(game.result, choice_value)


# ──────────────────────────────────────────────
# SIGNAL TESTS
# ──────────────────────────────────────────────
class ProfileSignalTest(TestCase):
    """Tests for the auto-creation signal."""

    def test_profile_created_for_new_user(self):
        """Test that creating a User automatically creates a Profile."""
        user = User.objects.create_user(
            username="signaltest", password="testpass123"
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_no_duplicate_profile_on_save(self):
        """Test that saving an existing user doesn't create a second profile."""
        user = User.objects.create_user(
            username="signaltest2", password="testpass123"
        )
        user.first_name = "Updated"
        user.save()
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)


# ──────────────────────────────────────────────
# FORM TESTS
# ──────────────────────────────────────────────
class ProfileFormTest(TestCase):
    """Tests for the ProfileForm."""

    def test_form_has_correct_fields(self):
        """Test the form contains the expected fields."""
        form = ProfileForm()
        self.assertEqual(
            list(form.fields.keys()),
            ["profile_photo", "skill_level", "bio"],
        )

    def test_form_valid_data(self):
        """Test the form is valid with correct data."""
        form = ProfileForm(data={
            "skill_level": "Intermediate",
            "bio": "I love chess!",
        })
        self.assertTrue(form.is_valid())

    def test_form_empty_data_valid(self):
        """Test the form is valid with empty optional fields."""
        form = ProfileForm(data={
            "skill_level": "",
            "bio": "",
        })
        self.assertTrue(form.is_valid())


class GameFormTest(TestCase):
    """Tests for the GameForm."""

    def test_form_has_correct_fields(self):
        """Test the form contains the expected fields."""
        form = GameForm()
        self.assertEqual(
            list(form.fields.keys()),
            ["opponent_name", "date_played", "result"],
        )

    def test_form_valid_data(self):
        """Test the form is valid with correct data."""
        form = GameForm(data={
            "opponent_name": "Bobby",
            "date_played": "2025-01-15",
            "result": "Win",
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test the form is invalid with missing required fields."""
        form = GameForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("opponent_name", form.errors)
        self.assertIn("date_played", form.errors)
        self.assertIn("result", form.errors)

    def test_form_date_widget(self):
        """Test that the date_played widget has the correct type attribute."""
        form = GameForm()
        self.assertEqual(
            form.fields["date_played"].widget.attrs.get("type"), "date"
        )


# ──────────────────────────────────────────────
# VIEW TESTS
# ──────────────────────────────────────────────
class ProfileViewTest(TestCase):
    """Tests for the profile_view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser", password="testpass123"
        )
        Game.objects.create(
            user=self.user, opponent_name="A",
            date_played=date(2025, 1, 1), result="Win",
        )
        Game.objects.create(
            user=self.user, opponent_name="B",
            date_played=date(2025, 1, 2), result="Loss",
        )
        Game.objects.create(
            user=self.user, opponent_name="C",
            date_played=date(2025, 1, 3), result="Draw",
        )

    def test_profile_view_status_200(self):
        """Test that the profile page returns HTTP 200."""
        response = self.client.get(reverse("profile", args=["viewuser"]))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_uses_correct_template(self):
        """Test the profile page renders the correct template."""
        response = self.client.get(reverse("profile", args=["viewuser"]))
        self.assertTemplateUsed(response, "profiles/profile.html")

    def test_profile_view_context(self):
        """Test the context contains profile, games, and stats."""
        response = self.client.get(reverse("profile", args=["viewuser"]))
        self.assertEqual(response.context["wins"], 1)
        self.assertEqual(response.context["draws"], 1)
        self.assertEqual(response.context["losses"], 1)
        self.assertEqual(len(response.context["games"]), 3)

    def test_profile_view_nonexistent_user_404(self):
        """Test that a non-existent username returns HTTP 404."""
        response = self.client.get(reverse("profile", args=["nobody"]))
        self.assertEqual(response.status_code, 404)


class ProfileEditViewTest(TestCase):
    """Tests for the profile_edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="edituser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

    def test_edit_own_profile_get(self):
        """Test that a user can access their own profile edit page."""
        self.client.login(username="edituser", password="testpass123")
        response = self.client.get(reverse("profile_edit", args=["edituser"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_edit.html")

    def test_edit_own_profile_post(self):
        """Test that a user can update their own profile."""
        self.client.login(username="edituser", password="testpass123")
        response = self.client.post(
            reverse("profile_edit", args=["edituser"]),
            data={"skill_level": "Advanced", "bio": "Updated bio."},
        )
        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.skill_level, "Advanced")
        self.assertEqual(profile.bio, "Updated bio.")

    def test_cannot_edit_other_users_profile(self):
        """Test that a user cannot edit another user's profile."""
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.get(
            reverse("profile_edit", args=["edituser"])
        )
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_redirects_to_login(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(
            reverse("profile_edit", args=["edituser"])
        )
        self.assertEqual(response.status_code, 302)


class LogGameViewTest(TestCase):
    """Tests for the log_game view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="logger", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="testpass123"
        )

    def test_log_game_get(self):
        """Test that the log game page loads for the correct user."""
        self.client.login(username="logger", password="testpass123")
        response = self.client.get(reverse("log_game", args=["logger"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/log_game.html")

    def test_log_game_post_valid(self):
        """Test that a valid game is logged."""
        self.client.login(username="logger", password="testpass123")
        response = self.client.post(
            reverse("log_game", args=["logger"]),
            data={
                "opponent_name": "Garry",
                "date_played": "2025-03-01",
                "result": "Win",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Game.objects.first().user, self.user)

    def test_cannot_log_game_on_other_profile(self):
        """Test that a user cannot log a game on someone else's profile."""
        self.client.login(username="other", password="testpass123")
        response = self.client.get(reverse("log_game", args=["logger"]))
        self.assertEqual(response.status_code, 302)

    def test_log_game_post_invalid(self):
        """Test that invalid data does not create a game."""
        self.client.login(username="logger", password="testpass123")
        self.client.post(
            reverse("log_game", args=["logger"]),
            data={"opponent_name": "", "date_played": "", "result": ""},
        )
        self.assertEqual(Game.objects.count(), 0)


class GameEditViewTest(TestCase):
    """Tests for the game_edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="gameeditor", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="notowner", password="testpass123"
        )
        self.game = Game.objects.create(
            user=self.user,
            opponent_name="Beth",
            date_played=date(2025, 2, 1),
            result="Loss",
        )

    def test_edit_own_game(self):
        """Test that a user can edit their own game."""
        self.client.login(username="gameeditor", password="testpass123")
        response = self.client.post(
            reverse("game_edit", args=["gameeditor", self.game.id]),
            data={
                "opponent_name": "Beth Updated",
                "date_played": "2025-02-01",
                "result": "Win",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertEqual(self.game.opponent_name, "Beth Updated")
        self.assertEqual(self.game.result, "Win")

    def test_cannot_edit_other_users_game(self):
        """Test that a user cannot edit another user's game."""
        self.client.login(username="notowner", password="testpass123")
        response = self.client.get(
            reverse("game_edit", args=["gameeditor", self.game.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_game_get_loads_form(self):
        """Test that GET request loads the edit form."""
        self.client.login(username="gameeditor", password="testpass123")
        response = self.client.get(
            reverse("game_edit", args=["gameeditor", self.game.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/edit_game.html")


class GameDeleteViewTest(TestCase):
    """Tests for the game_delete view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="gamedeleter", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="notowner", password="testpass123"
        )
        self.game = Game.objects.create(
            user=self.user,
            opponent_name="Opponent",
            date_played=date(2025, 1, 1),
            result="Draw",
        )

    def test_delete_own_game(self):
        """Test that a user can delete their own game."""
        self.client.login(username="gamedeleter", password="testpass123")
        self.client.post(
            reverse("game_delete", args=["gamedeleter", self.game.id])
        )
        self.assertEqual(Game.objects.count(), 0)

    def test_cannot_delete_other_users_game(self):
        """Test that a user cannot delete another user's game."""
        self.client.login(username="notowner", password="testpass123")
        self.client.post(
            reverse("game_delete", args=["gamedeleter", self.game.id])
        )
        self.assertEqual(Game.objects.count(), 1)

    def test_delete_redirects_to_profile(self):
        """Test that deletion redirects to the user's profile."""
        self.client.login(username="gamedeleter", password="testpass123")
        response = self.client.post(
            reverse("game_delete", args=["gamedeleter", self.game.id])
        )
        self.assertRedirects(
            response,
            reverse("profile", args=["gamedeleter"]),
        )


class DeleteAccountViewTest(TestCase):
    """Tests for the delete_account view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="deleteme", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="attacker", password="testpass123"
        )

    def test_delete_own_account(self):
        """Test that a user can delete their own account via POST."""
        self.client.login(username="deleteme", password="testpass123")
        response = self.client.post(
            reverse("delete_account", args=["deleteme"])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="deleteme").exists())

    def test_cannot_delete_other_users_account(self):
        """Test that a user cannot delete someone else's account."""
        self.client.login(username="attacker", password="testpass123")
        response = self.client.post(
            reverse("delete_account", args=["deleteme"])
        )
        self.assertTrue(User.objects.filter(username="deleteme").exists())

    def test_get_request_does_not_delete(self):
        """Test that a GET request does not delete the account."""
        self.client.login(username="deleteme", password="testpass123")
        self.client.get(reverse("delete_account", args=["deleteme"]))
        self.assertTrue(User.objects.filter(username="deleteme").exists())

    def test_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.post(
            reverse("delete_account", args=["deleteme"])
        )
        self.assertEqual(response.status_code, 302)


# ──────────────────────────────────────────────
# URL TESTS
# ──────────────────────────────────────────────
class ProfilesURLTest(TestCase):
    """Tests for profiles app URL routing."""

    def test_profile_url_resolves(self):
        """Test that the profile URL resolves to the correct view."""
        url = reverse("profile", args=["testuser"])
        self.assertEqual(resolve(url).func, profile_view)

    def test_profile_edit_url_resolves(self):
        """Test that the profile edit URL resolves correctly."""
        url = reverse("profile_edit", args=["testuser"])
        self.assertEqual(resolve(url).func, profile_edit)

    def test_log_game_url_resolves(self):
        """Test that the log game URL resolves correctly."""
        url = reverse("log_game", args=["testuser"])
        self.assertEqual(resolve(url).func, log_game)

    def test_game_edit_url_resolves(self):
        """Test that the game edit URL resolves correctly."""
        url = reverse("game_edit", args=["testuser", 1])
        self.assertEqual(resolve(url).func, game_edit)

    def test_game_delete_url_resolves(self):
        """Test that the game delete URL resolves correctly."""
        url = reverse("game_delete", args=["testuser", 1])
        self.assertEqual(resolve(url).func, game_delete)

    def test_delete_account_url_resolves(self):
        """Test that the delete account URL resolves correctly."""
        url = reverse("delete_account", args=["testuser"])
        self.assertEqual(resolve(url).func, delete_account)

    def test_profile_url_path(self):
        """Test the profile URL path format."""
        url = reverse("profile", args=["johndoe"])
        self.assertEqual(url, "/profiles/johndoe/")

    def test_log_game_url_path(self):
        """Test the log game URL path format."""
        url = reverse("log_game", args=["johndoe"])
        self.assertEqual(url, "/profiles/johndoe/log-game/")
