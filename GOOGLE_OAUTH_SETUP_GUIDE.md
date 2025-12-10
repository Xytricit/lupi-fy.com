# Google OAuth Setup Guide for Lupify

## Current Status
- **Framework**: Django with django-allauth
- **Current Credentials**: PLACEHOLDER_CLIENT_ID (development only)
- **Local Login**: ✅ Working
- **Google OAuth**: ⏳ Needs real Google credentials

## How to Set Up Real Google OAuth

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Create Project**
3. Name it "Lupify" or similar
4. Wait for the project to be created

### Step 2: Enable Google+ API
1. In the Cloud Console, search for "Google+ API"
2. Click on it and press **Enable**
3. Search for "Google Identity" and enable "Google Identity Services API"

### Step 3: Create OAuth 2.0 Credentials
1. Go to **Credentials** (left sidebar)
2. Click **Create Credentials** → **OAuth Client ID**
3. You may be prompted to configure the OAuth Consent Screen first:
   - Click **Configure Consent Screen**
   - Choose **External** user type
   - Fill in:
     - App name: `Lupify`
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes: `email` and `profile`
   - Save and continue

4. Back to creating OAuth Client ID:
   - Application type: **Web Application**
   - Name: `Lupify Web Client`
   - Authorized JavaScript origins:
     - `http://127.0.0.1:8000`
     - `http://localhost:8000`
     - Your production domain (if deployed)
   - Authorized redirect URIs:
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/callback/`
     - Your production callback URL (if deployed)
   - Click **Create**

5. Copy the **Client ID** and **Client Secret**

### Step 4: Update Lupify with Real Credentials

#### Option A: Via Django Admin (Recommended)
1. Start the server: `python manage.py runserver`
2. Go to `http://127.0.0.1:8000/admin/` (login with superuser)
3. Navigate to **Social Applications**
4. Edit the Google application:
   - **Client ID**: Paste your Google Client ID
   - **Secret Key**: Paste your Google Client Secret
   - Make sure **Sites** includes `127.0.0.1:8000`
5. Save

#### Option B: Via Command Line
```bash
python manage.py shell
```

```python
from allauth.socialaccount.models import SocialApp, Site
from django.contrib.sites.models import Site as DjangoSite

# Get or create the site
site = DjangoSite.objects.get_or_create(
    domain='127.0.0.1:8000',
    defaults={'name': 'Lupify Dev'}
)[0]

# Update or create the Google social app
google_app = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google',
        'client_id': 'YOUR_GOOGLE_CLIENT_ID_HERE',
        'secret': 'YOUR_GOOGLE_CLIENT_SECRET_HERE',
    }
)[0]

# Update existing
google_app.client_id = 'YOUR_GOOGLE_CLIENT_ID_HERE'
google_app.secret = 'YOUR_GOOGLE_CLIENT_SECRET_HERE'
google_app.save()

# Ensure the site is associated
if site not in google_app.sites.all():
    google_app.sites.add(site)

print("✅ Google OAuth credentials updated!")
```

### Step 5: Test It Out
1. Go to `http://127.0.0.1:8000/accounts/login/`
2. Click "Continue with Google"
3. You'll be redirected to Google's login page
4. After logging in, you'll be redirected back and automatically signed in to Lupify!
5. First-time users will be automatically registered with their Google email and name

## What Happens with Google OAuth

### Successful Login Flow:
1. User clicks "Continue with Google"
2. → Redirected to Google's OAuth consent screen
3. → User grants permission
4. → Redirected back to Lupify
5. → Account auto-created or existing account logged in
6. → User is signed in and redirected to dashboard

### Data Collected:
- Email
- Name
- Profile picture

## Troubleshooting

### "redirect_uri_mismatch" Error
- Make sure your redirect URI in Google Cloud Console **exactly matches** the one in Django
- Check protocol (http vs https)
- Check domain and port number
- Common issue: missing trailing slash

### "Invalid Client ID" Error
- Verify credentials were copied correctly (no extra spaces)
- Ensure credentials are updated in the database
- Restart the Django development server

### "Unauthorized redirect_uri" Error
- Double-check authorized redirect URIs in Google Cloud Console
- Must include full path: `.../accounts/google/login/callback/`

## For Production Deployment

When deploying to production:

1. Update Google Cloud Console with production domain
2. Add to **Authorized JavaScript origins**:
   - `https://yourdomain.com`
   - `https://www.yourdomain.com`
3. Add to **Authorized redirect URIs**:
   - `https://yourdomain.com/accounts/google/login/callback/`
4. Update Django settings `SITE_ID` and `ALLOWED_HOSTS`
5. Update social app in database or admin

## Security Notes

- ✅ Never commit credentials to git
- ✅ Use environment variables for client ID/secret in production
- ✅ Keep client secret secure
- ✅ Use HTTPS in production (not just HTTP)
- ✅ Verify callback URLs match exactly

## More Info

- [Django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
