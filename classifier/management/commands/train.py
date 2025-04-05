from django.db.models.signals import post_save
from django.core.management.base import BaseCommand, CommandError

from browser.models import HydrogenaseSequence


class Command(BaseCommand):

    help = 'Force train the primary hydrogenase classifier.'

    def handle(self, *args, **options):
        post_save.send(HydrogenaseSequence, instance=None, created=True)
