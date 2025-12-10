# Quick Google OAuth Setup

Your Lupi application is now ready to use Google OAuth! Here's how to complete the setup:

## Step 1: Get Real Google OAuth Credentials

1. **Go to Google Cloud Console:**
   - Open: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or select a project:**
   - Click on the project dropdown at the top
   - Click "NEW PROJECT"
   - Name it "Lupify" (or any name you prefer)
   - Click "CREATE"

3. **Enable Google+ API:**
   - In the search bar, search for "Google+ API"
   - Click on "Google+ API" in the results
   - Click "ENABLE"

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "CREATE CREDENTIALS"
   - Choose "OAuth 2.0 Client ID"
   - If asked to configure OAuth consent screen:
     - Choose "External" user type
     - Fill in required fields (app name, user support email, etc.)
     - Save and continue
   - Back to credentials: choose "Web application"
   - Add authorized redirect URIs:
     ```
     http://127.0.0.1:8000/accounts/google/callback/
     http://localhost:8000/accounts/google/callback/
     https://your-domain.com/accounts/google/callback/  (for production)
     ```
   - Click "CREATE"
   - Copy your **Client ID** and **Client Secret**

## Step 2: Add Credentials to Django

Option A: **Using Django Shell** (Recommended)
```bash
python manage.py shell
```

Then paste this code:
```python
from allauth.socialaccount.models import SocialApp

app = SocialApp.objects.get(provider='google')
app.client_id = 'YOUR_REAL_CLIENT_ID_HERE'
app.secret = 'YOUR_REAL_CLIENT_SECRET_HERE'
app.save()

print("✓ Google OAuth credentials updated!")
exit()
```

Option B: **Using Management Command**
```bash
python manage.py setup_google_oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Option C: **Using Django Admin**
1. Go to: http://127.0.0.1:8000/admin/
2. Navigate to: Socialaccount > Social applications
3. Click on "Google"
4. Update Client ID and Secret
5. Click "Save"

## Step 3: Test It!

1. Go to: http://127.0.0.1:8000/accounts/login/
2. Click "Continue with Google"
3. You should be redirected to Google's login page
4. After signing in, you'll be redirected back to your Lupi account

## Troubleshooting

**Problem: "Redirect URI mismatch" error**
- Solution: Make sure your redirect URI in Google Cloud Console exactly matches the one used by Django
- The URI should be: `http://127.0.0.1:8000/accounts/google/callback/`

**Problem: "Client ID not valid" error**
- Solution: Make sure you copied the correct Client ID from Google Cloud Console
- Double-check there are no extra spaces

**Problem: Login page still shows "Setup Required"**
- Solution: Make sure you updated the credentials in the database (they don't auto-load from Google Cloud)
- Try refreshing the page (hard refresh: Ctrl+Shift+R)

**Problem: Placeholder credentials still showing**
- Solution: You need to replace them with real credentials from Google Cloud Console
- The placeholder credentials won't work for actual login, only to remove the setup warning

## For Production

When deploying to production:
1. Update the redirect URI to your actual domain: `https://your-domain.com/accounts/google/callback/`
2. Use environment variables for credentials (optional but recommended):
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=your_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
   ```
3. Update Django settings to read from environment (if using env vars)

## Current Status

- ✅ Django-allauth installed and configured
- ✅ Google OAuth app created in database
- ⏳ **Waiting for:** Real Google OAuth credentials
- ⏳ **Optional:** Update production redirect URIs

That's it! Once you add your real credentials, Google OAuth will be fully functional.
