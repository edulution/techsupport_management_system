from django.test import TestCase
from django.contrib.auth.models import Permission
from techsupport.models import (
    Country,
    Region,
    Centre,
    User,
    UserProfile,
    Settings,
    Category,
    SubCategory,
    SupportTicket,
)


class ModelsTestCase(TestCase):
    def setUp(self):
        # Create sample data for testing

        # Create a sample country with code 'ZM'
        self.country = Country.objects.create(name="Zambia", code="ZM")

        # Create a sample region named 'Eastern Region' associated with the 'Zambia' country
        self.region = Region.objects.create(name="Eastern Region", country=self.country)

        # Create a sample support center named 'Lumezi Primary' with acronym 'LDL' in the 'Eastern Region'
        self.centre = Centre.objects.create(
            name="Lumezi Primary", acronym="LDL", region=self.region
        )

        # Create a sample user named 'testuser' with the role 'USER' in 'Zambia' and 'Eastern Region'
        self.user = User.objects.create(
            username="testuser",
            role=User.RoleType.USER,
            country=self.country,
            region=self.region,
        )

        # Set the password for the user
        self.user.set_password("testpassword")
        self.user.save()

        # Create a user profile for the 'testuser' with a bio
        self.user_profile = UserProfile.objects.create(
            user=self.user, bio="Test User bio"
        )

        # Create settings for the 'testuser' with dark mode enabled
        self.settings = Settings.objects.create(user=self.user, dark_mode_enabled=True)

        # Create a sample category named 'Software' with code 'SW'
        self.category = Category.objects.create(name="Software", code="SW")

        # Create a sample subcategory named 'Kolibri Issue' with code 'TSC' under the 'Software' category
        self.subcategory = SubCategory.objects.create(
            name="Kolibri Issue", category=self.category
        )

        # Create a sample support ticket with various attributes
        self.support_ticket = SupportTicket.objects.create(
            status=SupportTicket.Status.OPEN,
            priority=SupportTicket.Priority.MEDIUM,
            centre=self.centre,
            submitted_by=self.user,
            resolved_by=self.user,
            category=self.category,
            subcategory=self.subcategory,
            description="Test description",
            title="Test title",
            resolution_notes="Test resolution notes",
            assigned_to=self.user,
        )

    # Test cases for models

    def test_country_model(self):
        # Retrieve the country with the name 'Zambia' and assert its code is 'ZM'
        country = Country.objects.get(name="Zambia")
        self.assertEqual(country.code, "ZM")

    def test_region_model(self):
        # Retrieve the region with the name 'Eastern Region' and assert its associated country's name is 'Zambia'
        region = Region.objects.get(name="Eastern Region")
        self.assertEqual(region.country.name, "Zambia")

    def test_centre_model(self):
        # Retrieve the center with the name 'Lumezi Primary' and assert its acronym is 'LDL'
        centre = Centre.objects.get(name="Lumezi Primary")
        self.assertEqual(centre.acronym, "LDL")

    def test_user_model(self):
        # Retrieve the user with the username 'testuser' and verify their password is correct
        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password("testpassword"))

    def test_user_profile_model(self):
        # Retrieve the user profile for 'testuser' and assert its bio is 'Test User bio'
        user_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(user_profile.bio, "Test User bio")

    def test_settings_model(self):
        # Retrieve the settings for 'testuser' and check if dark mode is enabled
        settings = Settings.objects.get(user=self.user)
        self.assertTrue(settings.dark_mode_enabled)

    def test_category_model(self):
        # Retrieve the category with the name 'Software' and assert its code is 'SW'
        category = Category.objects.get(name="Software")
        self.assertEqual(category.code, "SW")

    def test_subcategory_model(self):
        # Retrieve the subcategory with the name 'Kolibri Issue' and assert its parent category's name is 'Software'
        subcategory = SubCategory.objects.get(name="Kolibri Issue")
        self.assertEqual(subcategory.category.name, "Software")

    def test_support_ticket_model(self):
        # Retrieve the support ticket with the description 'Test description' and verify its status is 'OPEN'
        support_ticket = SupportTicket.objects.get(description="Test description")
        self.assertEqual(support_ticket.status, SupportTicket.Status.OPEN)
