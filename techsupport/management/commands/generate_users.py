from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from techsupport.models import Country, Region, Centre
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Generate data for the application"

    def handle(self, *args, **options):
        self.generate_dummy_data()

    def generate_dummy_data(self):
        self.generate_countries()
        self.generate_regions()
        self.generate_centres()
        self.generate_users()

    def generate_countries(self):
        countries = [
            {"name": "Zambia", "code": "ZM"},
            {"name": "South Africa", "code": "ZA"},
        ]
        try:
            for country_data in countries:
                country, _ = Country.objects.get_or_create(**country_data)
            self.stdout.write(self.style.SUCCESS("Sucessfully generated Countries!"))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"An error occurred in generating Countries: {e}")
            )

    def generate_regions(self):
        regions = [
            {"name": "Eastern Region", "country": Country.objects.get(code="ZM")},
            {"name": "Western Region", "country": Country.objects.get(code="ZM")},
            {"name": "KwaZulu-Natal", "country": Country.objects.get(code="ZA")},
            {"name": "Mpumalanga", "country": Country.objects.get(code="ZA")},
            {"name": "Zambia Hub", "country": Country.objects.get(code="ZM")},
        ]
        try:
            for region_data in regions:
                Region.objects.create(**region_data)
            self.stdout.write(self.style.SUCCESS("Sucessfully generated Regions!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred Regions: {e}"))

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
                "name": "Zambia Hub",
                "acronym": "HUB",
                "region": Region.objects.get(name="Zambia Hub"),
            },
        ]
        try:
            for centre_data in centres:
                Centre.objects.create(**centre_data)
            self.stdout.write(self.style.SUCCESS("Sucessfully generated Centres!"))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"An error occurred in generating Centres: {e}")
            )

    def generate_users(self):
        users = [
            {
                "first_name": "Kapya",
                "last_name": "Sakala",
                "username": "superuser",
                "role": "admin",
                "password": "adminks10",
                "groups": ["admin"],
            },
            {
                "first_name": "Mulenga",
                "last_name": "Mwamba",
                "username": "mulenga",
                "role": "manager",
                "password": "manager1",
                "groups": ["manager"],
            },
            {
                "first_name": "Joseph",
                "last_name": "Kumwenda",
                "username": "joseph",
                "role": "manager",
                "password": "manager2",
                "groups": ["manager"],
            },
            {
                "first_name": "Levy",
                "last_name": "Mbewe",
                "username": "levy",
                "role": "technician",
                "password": "tech3",
                "groups": ["technician"],
            },
            {
                "first_name": "Sara",
                "last_name": "Chiteta",
                "username": "sara",
                "role": "manager",
                "password": "manager4",
                "groups": ["manager"],
            },
            {
                "first_name": "Newton",
                "last_name": "Mwale",
                "username": "newton",
                "role": "manager",
                "password": "manager5",
                "groups": ["manager"],
            },
            {
                "first_name": "Davies",
                "last_name": "Kabo",
                "username": "davies",
                "role": "manager",
                "password": "manager6",
                "groups": ["manager"],
            },
            {
                "first_name": "Dabwitso",
                "last_name": "Mweemba",
                "username": "dabwitso",
                "role": "technician",
                "password": "tech2",
                "groups": ["technician"],
            },
            {
                "first_name": "Ntipa",
                "last_name": "Chola",
                "username": "ntipa",
                "role": "technician",
                "password": "tech1",
                "groups": ["technician"],
            },
            {
                "first_name": "Zambian",
                "last_name": "Manager",
                "username": "zambia_mgr",
                "role": "manager",
                "password": "zambia_mgr",
                "groups": ["manager"],
                "country": Country.objects.get(code="ZM"),
                "region": Region.objects.get(name="Zambia Hub"),
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
                    user.save()
            self.stdout.write(self.style.SUCCESS("Sucessfully generated Users!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred Users: {e}"))


if __name__ == "__main__":
    Command().handle()
