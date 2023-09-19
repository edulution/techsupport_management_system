from django.test import TestCase
from techsupport.models import (
    SupportTicket,
    User,
    Centre,
    Category,
    SubCategory,
    Country,
    Region,
)
from techsupport.forms import SupportTicketForm


class SupportTicketFormTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create(username="testuser")

        # Create a country and region
        self.country = Country.objects.create(name="Zambia")
        self.region = Region.objects.create(name="Eastern Region", country=self.country)

        # Create a centre and assign it to the user and region
        self.centre = Centre.objects.create(name="Test Centre", region=self.region)
        self.user.centres.add(self.centre)

        # Create categories and subcategories
        self.category = Category.objects.create(name="Software")
        self.subcategory = SubCategory.objects.create(
            name="Kolibri Issue", category=self.category
        )

    def test_valid_support_ticket_form(self):
        data = {
            "title": "Test Ticket",
            "description": "This is a test ticket description.",
            "centre": self.centre.pk,
            "category": self.category.pk,
            "subcategory": self.subcategory.pk,
            "priority": "Medium",
        }

        form = SupportTicketForm(data=data, user=self.user)

        # Assert that the form is valid and has no errors
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_invalid_support_ticket_form(self):
        data = {
            "title": "This is a very long title that exceeds 20 characters",
            "description": "This is a test ticket description.",
            "centre": self.centre.pk,
            "category": self.category.pk,
            "subcategory": self.subcategory.pk,
            "priority": "Medium",
        }

        form = SupportTicketForm(data=data, user=self.user)

        # Assert that the form is not valid and has errors related to the title field
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_empty_form(self):
        data = {}

        # Create an empty form with the empty data and pass the user
        form = SupportTicketForm(data=data, user=self.user)

        # Assert that the form is not valid
        self.assertFalse(form.is_valid())

        # Assert that each field in the form has an error message for being required
        self.assertIn("title", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("centre", form.errors)
        self.assertIn("category", form.errors)
        self.assertIn("subcategory", form.errors)
        self.assertIn("priority", form.errors)

    def test_title_length(self):
        # Create a data dictionary with a title longer than 20 characters
        data = {
            "title": "This is a title longer than twenty characters.",
        }

        # Create a form with the data and pass the user
        form = SupportTicketForm(data=data, user=self.user)

        # Assert that the form is not valid
        self.assertFalse(form.is_valid())

        # Assert that the "title" field has an error message about exceeding the maximum length
        self.assertIn(
            "Ensure this value has at most 20 characters", form.errors["title"][0]
        )


    def test_priority_hidden(self):
        data = {
            "priority": "Medium",
        }

        # Include "priority" in the initial data
        initial = {"priority": "Medium"}
    
        form = SupportTicketForm(data=data, user=self.user, initial=initial)
    
        # Check if the "priority" field is in the form and is hidden
        self.assertIn("priority", form.fields)
        self.assertTrue(form.fields["priority"].widget.is_hidden)

        # Check if the initial value of "priority" is set to "Medium"
        self.assertEqual(form.initial["priority"], "Medium")


