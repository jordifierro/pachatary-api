from django.core.management.base import BaseCommand, CommandError
from scenes.factories import create_index_experiences_interactor

class Command(BaseCommand):
    help = 'Reindex all words on search engine'

    def handle(self, *args, **options):
        create_index_experiences_interactor().set_params(from_id='0', to_id='100').execute()

        self.stdout.write(self.style.SUCCESS('Successfully reindexed all experiences'))
