from django.core.management import BaseCommand

from metrics.data_importer import Importer


class Command(BaseCommand):
    help = 'Imports metrics data from ETL_CSV_URL'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--data_source', action='store_true', help="url to json file that contains data")

    def handle(self, *args, **options):
        Importer(data_source=options['data_source']).run()
        self.stdout.write(self.style.SUCCESS('Successfully imported all data'))