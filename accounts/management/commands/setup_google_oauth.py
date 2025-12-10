from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os
import sys


class Command(BaseCommand):
    help = 'Setup Google OAuth credentials for Lupi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth Client ID',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Google OAuth Client Secret',
        )
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Try to read from environment variables',
        )

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        auto_mode = options.get('auto', False)

        # Try environment variables if auto mode
        if auto_mode:
            client_id = client_id or os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
            client_secret = client_secret or os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

        # Prompt if not provided
        if not client_id:
            client_id = input('Enter your Google OAuth Client ID: ').strip()
        if not client_secret:
            client_secret = input('Enter your Google OAuth Client Secret: ').strip()

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR('Client ID and Secret are required!'))
            return

        # Get or create the current site
        try:
            site = Site.objects.get(pk=1)
        except Site.DoesNotExist:
            site = Site.objects.create(pk=1, domain='127.0.0.1:8000', name='Lupi')
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))

        # Get or create Google OAuth app
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if created:
            google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✓ Google OAuth app created successfully!'))
        else:
            # Update existing app
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
            if site not in google_app.sites.all():
                google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✓ Google OAuth app updated successfully!'))

        self.stdout.write(self.style.SUCCESS(f'\nGoogle OAuth is now configured!'))
        self.stdout.write(f'Site: {site.domain}')
        self.stdout.write(f'Provider: Google')
        self.stdout.write(f'Client ID: {client_id[:10]}...')
        self.stdout.write(f'\nYou can now log in with Google at http://127.0.0.1:8000/accounts/login/')
