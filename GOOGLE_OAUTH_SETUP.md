# Google OAuth Setup Guide

This application now uses **Google OAuth only** for authentication. No traditional username/password login is available.

## Setting Up Google OAuth

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Google+ API" for your project:
   - Go to APIs & Services > Library
   - Search for "Google+ API"
   - Click on it and press "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Choose "Web application"
4. Fill in the application name (e.g., "Lupify")
5. Add authorized redirect URIs:
   - For **development**: `http://localhost:8000/accounts/google/callback/`
   - For **development**: `http://127.0.0.1:8000/accounts/google/callback/`
   - For **production**: `https://your-domain.com/accounts/google/callback/`
6. Click "Create"
7. Copy your **Client ID** and **Client Secret**

### Step 3: Add Google OAuth Credentials to Django

Once you have the credentials, you need to add them to your Django admin:

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Go to [Django Admin](http://127.0.0.1:8000/admin/)

3. Navigate to **Socialaccount > Social applications**

4. Click "Add Social Application"

5. Fill in the form:
   - **Provider**: Google
   - **Name**: Google (or any name you prefer)
   - **Client id**: Paste your Google Client ID
   - **Secret key**: Paste your Google Client Secret
   - **Sites**: Select your site(s) from the list (should be 127.0.0.1:8000 for development)

6. Click "Save"

### Step 4: Test the Login

1. Go to [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/)
2. Click "Continue with Google"
3. You'll be redirected to Google's login page
4. After successful authentication, you'll be redirected back and logged in

## Important Notes

- **No Email Verification**: Google OAuth handles email verification, so users don't need to verify their email in the app
- **Auto User Creation**: New users are automatically created when they sign in with Google for the first time
- **Profile Data**: User information (name, email, avatar) is populated from their Google account
- **Email Verification Fields**: The old email verification fields in the database are no longer used but are kept for backward compatibility

## Environment Variables

For production deployment, ensure these environment variables are set:
- `EMAIL_HOST_USER` (if using SMTP)
- `EMAIL_HOST_PASSWORD` (if using SMTP)
- `DEFAULT_FROM_EMAIL`

The Google OAuth credentials are stored in the database, not environment variables.

## Troubleshooting

### "The redirect URI doesn't match"
- Make sure the redirect URI in your Google OAuth settings exactly matches the one being used by Django
- Check both the domain and the path: `http://127.0.0.1:8000/accounts/google/callback/`

### "Client ID not found"
- Make sure you've added the Google OAuth credentials in Django Admin under Socialaccount > Social applications
- Ensure you selected the correct site(s)

### Users can't log in
- Check that the Google OAuth app is configured in Django Admin
- Verify your Google Client ID and Client Secret are correct
- Check browser console for any JavaScript errors

## Files Changed

- `mysite/urls.py`: Added `allauth.urls` path
- `mysite/settings.py`: Added allauth configuration and middleware
- `accounts/urls.py`: Replaced old login/register views with Google OAuth login page
- `accounts/templates/accounts/google_login.html`: New Google OAuth login page

## Old Files (Deprecated)

The following are no longer used but kept for reference:
- `accounts/templates/accounts/login.html` (old login form)
- `accounts/templates/accounts/register.html` (old registration form)
- `accounts/templates/accounts/verify_email.html` (old email verification)
- `accounts/views.py`: Old `register_view`, `login_view`, `verify_email` functions are commented out

These can be deleted if you prefer, but they're kept in case you need to revert in the future.
