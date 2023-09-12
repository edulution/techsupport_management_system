import csv
from django.core.management.base import BaseCommand
from techsupport.models import Country, Region, Centre

class Command(BaseCommand):
    help = "Generate Countries, Regions and Centres for the application"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.generate_country_from_csv(row)
                self.generate_region_from_csv(row)
                self.generate_centre_from_csv(row)

    def generate_country_from_csv(self, data):
        country, created = Country.objects.get_or_create(name=data['country_name'], code=data['country_code'])
        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully generated Country: {country.name}"))

    def generate_region_from_csv(self, data):
        try:
            country = Country.objects.get(code=data['country_code'])
            region, created = Region.objects.get_or_create(name=data['region_name'], country=country)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully generated Region: {region.name}"))
        except Country.DoesNotExist:
            raise Exception("Country with code not found")

    def generate_centre_from_csv(self, data):
        try:
            region = Region.objects.get(name=data['region_name'])
            centre, created = Centre.objects.get_or_create(name=data['centre_name'], acronym=data['centre_acronym'], region=region)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully generated Centre: {centre.name}"))
        except Region.DoesNotExist:
            raise Exception("Region not found")
