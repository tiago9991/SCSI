import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Wait until the configured default database is ready to accept connections.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Maximum number of seconds to wait for the database (default: 60).',
        )
        parser.add_argument(
            '--interval',
            type=float,
            default=1.0,
            help='Seconds between connection attempts (default: 1.0).',
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        started = time.monotonic()

        self.stdout.write('Waiting for database...', ending=' ')

        while True:
            try:
                connection = connections['default']
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS('available'))
                return
            except OperationalError:
                elapsed = time.monotonic() - started
                if elapsed >= timeout:
                    self.stdout.write(self.style.ERROR('timeout'))
                    raise SystemExit(1)
                time.sleep(interval)