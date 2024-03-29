import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from techsupport.models import (
    Country,
    Region,
    Centre,
    Category,
    SubCategory,
    SupportTicket,
)
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Generate dummy data for the application"

    def handle(self, *args, **options):
        self.generate_dummy_data()

    def generate_dummy_data(self):
        self.generate_countries()
        self.generate_regions()
        self.generate_centres()
        self.generate_users()
        self.generate_categories()
        self.generate_subcategories()
        self.generate_support_tickets()

    def generate_countries(self):
        countries = [
            {"name": "Zambia", "code": "ZM"},
            {"name": "South Africa", "code": "ZA"},
        ]
        try:
            for country_data in countries:
                Country.objects.create(**country_data)
            self.stdout.write(
                self.style.SUCCESS("Sucessfully generated dummy Countries!")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"An error occurred in generating dummy Countries: {e}"
                )
            )

    def generate_regions(self):
        regions = [
            {"name": "Eastern Region", "country": Country.objects.get(code="ZM")},
            {"name": "Western Region", "country": Country.objects.get(code="ZM")},
            {"name": "Mpumalanga", "country": Country.objects.get(code="ZA")},
            {"name": "KwaZulu Natal", "country": Country.objects.get(code="ZA")},
        ]
        try:
            for region_data in regions:
                Region.objects.create(**region_data)
            self.stdout.write(
                self.style.SUCCESS("Sucessfully generated dummy Regions!")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"An error occurred in generating dummy Regions: {e}")
            )

    def generate_centres(self):
        centres = [
            {
                "name": "Lumezi Primary",
                "acronym": "LDL",
                "region": Region.objects.get(name="Eastern Region"),
            },
            {
                "name": "Mayukwayukwa Secondary",
                "acronym": "MYS",
                "region": Region.objects.get(name="Western Region"),
            },
            {
                "name": "Kanyajalo",
                "acronym": "INK",
                "region": Region.objects.get(name="KwaZulu Natal"),
            },
            {
                "name": "Zwelisha",
                "acronym": "WRZ",
                "region": Region.objects.get(name="Mpumalanga"),
            },
        ]

        try:
            for centre_data in centres:
                Centre.objects.create(**centre_data)
            self.stdout.write(
                self.style.SUCCESS("Sucessfully generated dummy Centres!")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"An error occurred in generating dummy Centres: {e}")
            )

    def generate_users(self):
        users = [
            {
                "first_name": "Admin",
                "last_name": "All",
                "username": "admin1",
                "role": "admin",
                "password": "admin",
                "groups": ["admin"],
            },
            {
                "first_name": "Manager",
                "last_name": "All",
                "username": "manager1",
                "role": "manager",
                "password": "manager1",
                "groups": ["manager"],
            },
            {
                "first_name": "Technician",
                "last_name": "Zambia",
                "username": "tech1",
                "role": "technician",
                "password": "tech1",
                "groups": ["technician"],
            },
            {
                "first_name": "Technician2",
                "last_name": "South Africa",
                "username": "tech2",
                "role": "technician",
                "password": "tech2",
                "groups": ["technician"],
            },
            {
                "first_name": "Sandile",
                "last_name": "Ncobile",
                "username": "ZA_SN09",
                "role": "user",
                "password": "A_SN09",
                "groups": ["user"],
                "centres": ["Lumezi Primary"],
            },
            {
                "first_name": "Jose",
                "last_name": "Zulu",
                "username": "ZM_JZ13",
                "role": "user",
                "password": "ZM_JZ13",
                "groups": ["user"],
                "centres": ["Mayukwayukwa Secondary"],
            },
            {
                "first_name": "Thobekile",
                "last_name": "Gumede",
                "username": "ZA_TG20",
                "role": "user",
                "password": "ZA_TG20",
                "groups": ["user"],
                "centres": ["Kanyajalo"],
            },
            {
                "first_name": "Matildah",
                "last_name": "Mbuzi",
                "username": "ZM_MM23",
                "role": "user",
                "password": "ZM_MM23",
                "groups": ["user"],
                "centres": ["Zwelisha"],
            },
            # Manager for Zambia, Eastern Region
            {
                "first_name": "Zambian",
                "last_name": "Manager",
                "username": "zambia_mgr",
                "role": "manager",
                "password": "zambia_mgr",
                "groups": ["manager"],
                "country": Country.objects.get(code="ZM"),
                "region": Region.objects.get(name="Eastern Region"),
            },
            # Manager for South Africa, KwaZulu Natal Region
            {
                "first_name": "SA",
                "last_name": "Manager",
                "username": "sa_mgr",
                "role": "manager",
                "password": "sa_mgr",
                "groups": ["manager"],
                "country": Country.objects.get(code="ZA"),
                "region": Region.objects.get(name="KwaZulu Natal"),
            },
        ]

        try:
            for user_data in users:
                if "country" in user_data and "region" in user_data:
                    country = user_data.pop("country")
                    region = user_data.pop("region")
                else:
                    country = None
                    region = None

                password = user_data.pop("password")
                groups = user_data.pop("groups", [])
                centre_names = user_data.pop("centres", [])

                user_data["password"] = password
                user = User.objects.create_user(**user_data)

                for group_name in groups:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)

                for centre_name in centre_names:
                    centre = Centre.objects.get(name=centre_name)
                    user.centres.add(centre)

                # Assign the country and region to the manager user
                if country and region:
                    user.country = country
                    user.region = region

            # Assign all regions and centres to technicians and admins
            if user_data["role"] in ["technician", "admin"]:
                all_regions = Region.objects.all()
                all_centres = Centre.objects.all()

                for region in all_regions:
                    user.regions.add(region)
                for centre in all_centres:
                    user.centres.add(centre)

            self.stdout.write(self.style.SUCCESS("Sucessfully generated dummy Users!"))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"An error occurred in generating dummy Users: {e}")
            )

    def generate_categories(self):
        categories = [
            {"name": "Hardware", "code": "001"},
            {"name": "Software", "code": "002"},
        ]

        try:
            for category_data in categories:
                Category.objects.create(**category_data)
                self.stdout.write(
                    self.style.SUCCESS("Sucessfully generated dummy Categories!")
                )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"An error occurred in generating dummy Categories: {e}"
                )
            )

    def generate_subcategories(self):
        subcategories = [
            {"name": "Laptop Issue", "category": Category.objects.get(code="001")},
            {"name": "Tablet Issue", "category": Category.objects.get(code="001")},
            {"name": "Router Issue", "category": Category.objects.get(code="001")},
            {"name": "Charging Issue", "category": Category.objects.get(code="001")},
            {"name": "Kolibri", "category": Category.objects.get(code="002")},
            {"name": "Baseline", "category": Category.objects.get(code="002")},
            {"name": "Network", "category": Category.objects.get(code="002")},
        ]

        try:
            for subcategory_data in subcategories:
                SubCategory.objects.create(**subcategory_data)
            self.stdout.write(
                self.style.SUCCESS("Sucessfully generated dummy SubCategories!")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"An error occurred in generating dummy SubCategories: {e}"
                )
            )

    def generate_support_tickets(self):
        centres = Centre.objects.all()
        users = User.objects.all()
        categories = Category.objects.all()
        subcategories = SubCategory.objects.all()
        statuses = [
            SupportTicket.Status.OPEN,
            SupportTicket.Status.RESOLVED,
            SupportTicket.Status.IN_PROGRESS,
        ]
        priorities = [
            SupportTicket.Priority.LOW,
            SupportTicket.Priority.MEDIUM,
            SupportTicket.Priority.HIGH,
        ]

        try:
            for i in range(20):
                centre = random.choice(centres)
                user = random.choice(users)
                category = random.choice(categories)
                subcategory = random.choice(subcategories)
                status = random.choice(statuses)
                priority = random.choice(priorities)

                SupportTicket.objects.create(
                    status=status,
                    priority=priority,
                    centre=centre,
                    submitted_by=user,
                    category=category,
                    subcategory=subcategory,
                    description=f"Support Ticket {i + 1}",
                    title=f"Ticket-{i + 1}",
                )
            self.stdout.write(
                self.style.SUCCESS("Sucessfully generated dummy SupportTickets!")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"An error occurred in generating dummy SupportTickets: {e}"
                )
            )
