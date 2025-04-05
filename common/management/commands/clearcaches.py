from django.core.management.base import BaseCommand

from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear caches.'

    def handle(self, *args, **options):
        cache.clear()
