"""
Setup script for Google OAuth credentials
Run this script to configure Google OAuth for development
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_google_oauth():
    """Setup Google OAuth app in database"""
    
    print("=" * 60)
    print("Google OAuth Setup for Lupi")
    print("=" * 60)
    
    # Ensure site exists
    site, created = Site.objects.get_or_create(
        pk=1,
        defaults={'domain': '127.0.0.1:8000', 'name': 'Lupi'}
    )
    print(f"\n✓ Site configured: {site.domain}")
    
    # Create placeholder Google app
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': 'PLACEHOLDER_CLIENT_ID',
            'secret': 'PLACEHOLDER_CLIENT_SECRET',
        }
    )
    
    if created:
        google_app.sites.add(site)
        print("✓ Google OAuth app created with placeholder credentials")
    else:
        if site not in google_app.sites.all():
            google_app.sites.add(site)
        print("✓ Google OAuth app already configured")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("\n1. Get real Google OAuth credentials:")
    print("   - Go to: https://console.cloud.google.com/")
    print("   - Create a new project or select existing one")
    print("   - Enable 'Google+ API'")
    print("   - Create OAuth 2.0 Client ID (Web application)")
    print("   - Add redirect URI: http://127.0.0.1:8000/accounts/google/callback/")
    print("   - Copy your Client ID and Client Secret")
    
    print("\n2. Update credentials in Django shell:")
    print("   python manage.py shell")
    print("   >>> from allauth.socialaccount.models import SocialApp")
    print("   >>> app = SocialApp.objects.get(provider='google')")
    print("   >>> app.client_id = 'YOUR_REAL_CLIENT_ID'")
    print("   >>> app.secret = 'YOUR_REAL_CLIENT_SECRET'")
    print("   >>> app.save()")
    print("   >>> exit()")
    
    print("\n3. Or use the management command:")
    print("   python manage.py setup_google_oauth --client-id YOUR_ID --client-secret YOUR_SECRET")
    
    print("\n4. Then test the login:")
    print("   http://127.0.0.1:8000/accounts/login/")
    
    print("\n" + "=" * 60)
    print("✓ Setup complete! Credentials are ready for Google OAuth.")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    setup_google_oauth()
