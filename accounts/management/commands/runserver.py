"""
Custom runserver command that uses Daphne ASGI server instead of Django's default.
This enables WebSocket support for real-time features like games.

Usage: python manage.py runserver
"""
import subprocess
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start Daphne ASGI server with WebSocket support (replaces default runserver)"

    def add_arguments(self, parser):
        parser.add_argument(
            'addrport',
            nargs='?',
            default='0.0.0.0:8000',
            help='Optional address:port (default: 0.0.0.0:8000)'
        )

    def handle(self, *args, **options):
        addrport = options['addrport']
        
        # Parse address and port
        if ':' in addrport:
            addr, port = addrport.rsplit(':', 1)
        else:
            addr = addrport
            port = '8000'
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🚀 Starting Daphne ASGI server at {addr}:{port} (with WebSocket support)\n'
            )
        )
        
        # Start Daphne
        cmd = [
            'daphne',
            '-b', addr,
            '-p', port,
            'mysite.asgi:application'
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(
                    '\n❌ Error: Daphne not found. Make sure it\'s installed:\n'
                    '   pip install daphne\n'
                )
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n\n⚠️  Server stopped by user\n')
            )
            sys.exit(0)
