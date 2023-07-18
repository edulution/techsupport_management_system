from django.core.management import BaseCommand

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techsupport_management.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


class Command(BaseCommand):
    """
    Custom Django management command to handle subcommands.
    """

    def add_arguments(self, parser):
        parser.add_argument('subcommand', nargs='?', help='Subcommand to run.')

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')
        if subcommand == 'generate_dummy_data':
            from your_app.management.commands.generate_dummy_data import Command as GenerateDummyDataCommand
            GenerateDummyDataCommand().handle(*args, **options)
        else:
            self.stdout.write(self.help)
