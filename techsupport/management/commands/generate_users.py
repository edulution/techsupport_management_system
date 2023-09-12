import csv
import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from techsupport.models import Country, Region, Centre, UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Generate users for the application"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        with open(csv_file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.generate_user_from_csv(row)

    def generate_user_from_csv(self, data):
        user_data = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "username": data["username"],
            "email": data["email"],
            "role": data["role"],
        }

        user, created = User.objects.get_or_create(username=data["username"])
        user.__dict__.update(**user_data)

        # Adjust the password length as needed
        password_length = 5
        
        # Generate a random password
        password_characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(password_characters) for i in range(password_length))


        user.set_password(password)
        user.save()

        # Create a user profile and link it to the user
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.bio = f"{user.first_name} {user.last_name}"
        profile.save()

        groups = data["groups"].split(",")
        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name.strip())
            user.groups.add(group)

        if data['role'] in ['admin', 'technician']:
            # Admin and technician roles have access to all countries and regions
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully created admin/technician user: {user.username}"))
        elif data['role'] == 'manager':
            # Managers have access to one country and its regions
            if data['country_code'] and data['region_name'] and data['centre_name']:
                try:
                    country = Country.objects.get(code=data['country_code'])
                    region = Region.objects.get(name=data['region_name'])
                    centre = Centre.objects.get(name=data['centre_name'], region=region)
                    user.country = country
                    user.region = region
                    user.centres.add(centre)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Successfully created manager user: {user.username}"))

                    # Create or update user profile
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f"Successfully created user profile for: {user.username}"))
                except (Country.DoesNotExist, Region.DoesNotExist, Centre.DoesNotExist):
                    self.stderr.write(self.style.ERROR(f"Country, Region, or Centre not found for user: {user.username}"))
            else:
                self.stderr.write(self.style.ERROR(f"Invalid manager data for user: {user.username}"))
        else:
            self.stderr.write(self.style.ERROR(f"Invalid role for user: {user.username}"))
