from django.core.management.base import BaseCommand, CommandError
from weather_maniac.data_loader import main


class Command(BaseCommand):
    help = 'Loads and archives data for today.'

    def handle(self, *args, **options):
        main()