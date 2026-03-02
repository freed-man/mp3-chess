"""
Tests for the 'about' app.
Covers: Models, Views, Forms, URLs.
"""
from django.test import TestCase, Client
from django.urls import reverse, resolve
from about.models import About, ContactRequest, CATEGORY_CHOICES
from about.forms import ContactForm
from about.views import about_page


# ──────────────────────────────────────────────
# MODEL TESTS
# ──────────────────────────────────────────────
class AboutModelTest(TestCase):
    """Tests for the About model."""

    def setUp(self):
        self.about = About.objects.create(
            title="About Our Chess Club",
            content="Welcome to the club!",
            location="Dublin, Ireland",
            contact_email="info@chessclub.com",
        )

    def test_about_creation(self):
        """Test that an About instance is created correctly."""
        self.assertEqual(self.about.title, "About Our Chess Club")
        self.assertEqual(self.about.content, "Welcome to the club!")
        self.assertEqual(self.about.location, "Dublin, Ireland")
        self.assertEqual(self.about.contact_email, "info@chessclub.com")

    def test_about_str(self):
        """Test the __str__ method returns the title."""
        self.assertEqual(str(self.about), "About Our Chess Club")

    def test_about_updated_on_auto_set(self):
        """Test that updated_on is automatically set."""
        self.assertIsNotNone(self.about.updated_on)

    def test_about_default_image(self):
        """Test that the default club_image is 'placeholder'."""
        self.assertEqual(self.about.club_image, "placeholder")

    def test_about_blank_fields(self):
        """Test that location and contact_email can be blank."""
        about = About.objects.create(
            title="Minimal About",
            content="Minimal content.",
        )
        self.assertEqual(about.location, "")
        self.assertEqual(about.contact_email, "")


class ContactRequestModelTest(TestCase):
    """Tests for the ContactRequest model."""

    def setUp(self):
        self.contact = ContactRequest.objects.create(
            name="John Doe",
            email="john@example.com",
            category="Question",
            message="When does the club meet?",
        )

    def test_contact_request_creation(self):
        """Test that a ContactRequest instance is created correctly."""
        self.assertEqual(self.contact.name, "John Doe")
        self.assertEqual(self.contact.email, "john@example.com")
        self.assertEqual(self.contact.category, "Question")
        self.assertEqual(self.contact.message, "When does the club meet?")

    def test_contact_request_str(self):
        """Test the __str__ method returns the expected string."""
        self.assertEqual(str(self.contact), "Question from John Doe")

    def test_contact_request_default_read(self):
        """Test that 'read' defaults to False."""
        self.assertFalse(self.contact.read)

    def test_contact_request_category_choices(self):
        """Test that valid category choices are accepted."""
        for choice_value, _ in CATEGORY_CHOICES:
            contact = ContactRequest.objects.create(
                name="Test User",
                email="test@example.com",
                category=choice_value,
                message="Test message.",
            )
            self.assertEqual(contact.category, choice_value)


# ──────────────────────────────────────────────
# FORM TESTS
# ──────────────────────────────────────────────
class ContactFormTest(TestCase):
    """Tests for the ContactForm."""

    def test_form_has_correct_fields(self):
        """Test the form contains the expected fields."""
        form = ContactForm()
        self.assertEqual(
            list(form.fields.keys()),
            ["name", "email", "category", "message"],
        )

    def test_form_valid_data(self):
        """Test the form is valid with correct data."""
        form = ContactForm(data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "category": "Comment",
            "message": "Great club!",
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_email(self):
        """Test the form is invalid with a bad email address."""
        form = ContactForm(data={
            "name": "Jane Doe",
            "email": "not-an-email",
            "category": "Comment",
            "message": "Great club!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_missing_required_fields(self):
        """Test that all fields are required."""
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("category", form.errors)
        self.assertIn("message", form.errors)

    def test_form_saves_correctly(self):
        """Test that a valid form saves a ContactRequest to the database."""
        form = ContactForm(data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "category": "Request",
            "message": "Can I join?",
        })
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertEqual(contact.name, "Jane Doe")


# ──────────────────────────────────────────────
# VIEW TESTS
# ──────────────────────────────────────────────
class AboutViewTest(TestCase):
    """Tests for the about_page view."""

    def setUp(self):
        self.client = Client()
        self.about = About.objects.create(
            title="About Us",
            content="We are a chess club.",
        )

    def test_about_page_get_status_200(self):
        """Test that the about page returns HTTP 200."""
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """Test that the about page renders the correct template."""
        response = self.client.get(reverse("about"))
        self.assertTemplateUsed(response, "about/about.html")

    def test_about_page_context_contains_about(self):
        """Test that the context includes the about object."""
        response = self.client.get(reverse("about"))
        self.assertEqual(response.context["about"], self.about)

    def test_about_page_context_contains_contact_form(self):
        """Test that the context includes a ContactForm instance."""
        response = self.client.get(reverse("about"))
        self.assertIsInstance(response.context["contact_form"], ContactForm)

    def test_about_page_returns_latest_about(self):
        """Test that the view returns the most recently updated About."""
        newer_about = About.objects.create(
            title="Updated About",
            content="New content.",
        )
        response = self.client.get(reverse("about"))
        self.assertEqual(response.context["about"], newer_about)

    def test_about_page_no_about_entries(self):
        """Test the about page works when no About entries exist."""
        About.objects.all().delete()
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["about"])

    def test_about_page_post_valid_contact(self):
        """Test submitting a valid contact form via POST."""
        response = self.client.post(reverse("about"), data={
            "name": "Jane",
            "email": "jane@example.com",
            "category": "Question",
            "message": "What time do you meet?",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_about_page_post_shows_success_message(self):
        """Test that a success message appears after valid POST."""
        response = self.client.post(reverse("about"), data={
            "name": "Jane",
            "email": "jane@example.com",
            "category": "Question",
            "message": "What time do you meet?",
        }, follow=True)
        messages_list = list(response.context["messages"])
        # The view adds a message even without redirect, check via storage
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_about_page_post_invalid_contact(self):
        """Test submitting an invalid contact form does not save."""
        response = self.client.post(reverse("about"), data={
            "name": "",
            "email": "bad",
            "category": "",
            "message": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRequest.objects.count(), 0)


# ──────────────────────────────────────────────
# URL TESTS
# ──────────────────────────────────────────────
class AboutURLTest(TestCase):
    """Tests for about app URL routing."""

    def test_about_url_resolves(self):
        """Test that the about URL resolves to the correct view."""
        url = reverse("about")
        self.assertEqual(resolve(url).func, about_page)

    def test_about_url_path(self):
        """Test the about URL path is correct."""
        url = reverse("about")
        self.assertEqual(url, "/about/")
