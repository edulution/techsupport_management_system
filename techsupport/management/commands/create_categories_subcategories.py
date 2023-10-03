import random
from termcolor import colored
from django.core.management.base import BaseCommand
from techsupport.models import Category, SubCategory


class Command(BaseCommand):
    help = "Generates sample data for the tech support ticket system."

    def handle(self, *args, **options):
        category_data = [
            {"name": "Hardware", "code": "HWE"},
            {"name": "Software", "code": "SWE"},
            {"name": "Operations", "code": "OPS"},
        ]

        subcategory_data = {
            "Hardware": [
                "Tablet Issues",
                "Laptop Issues",
                "Router Issues",
                "Headphones Issues",
                "Solar Kit Issues",
                "General Power Issues",
                "Other Hardware Issue",
            ],
            "Software": [
                "Google Drive Issues",
                "Kolibri Issues",
                "Tests/Assessments Issues",
                "Assign/Enroll Learners",
                "Delete/Insert Learners",
                "Classlist Issues",
                "Other Software Issue",
            ],
            "Operations": ["Stock Sheet Issues", "Other Operational Issue"],
        }

        try:
            for category_info in category_data:
                category = Category.objects.create(
                    name=category_info["name"], code=category_info["code"]
                )
                subcategories = subcategory_data.get(category_info["name"], [])
                for subcategory_name in subcategories:
                    SubCategory.objects.create(name=subcategory_name, category=category)
            self.stdout.write(
                self.style.SUCCESS(
                    "Technical Support Management Categories and Subcategories created successfully!"
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
