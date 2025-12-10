from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db import models
import base64
import random
from datetime import timedelta

from .forms import CustomUserCreationForm, CaseSensitiveAuthenticationForm, ProfileUpdateForm
from .models import Subscription, CustomUser, GameLobbyBan, GameLobbyMessage, LetterSetGame, GameLobbyChallenge, WordListGame
import json
from pathlib import Path
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import re
from blog.models import Post
from communities.models import Community, CommunityPost
from django.db.models import Count

User = get_user_model()


# -------------------------------
# EMAIL VERIFICATION
# -------------------------------
def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_verification_email(user):
    """Send verification email to user."""
    code = generate_verification_code()
    user.email_verification_code = code
    user.email_verification_expires_at = timezone.now() + timedelta(hours=24)
    user.email_verification_attempts = 0
    user.save()
    
    subject = "Verify Your Lupify Account"
    message = f"""
    Hello {user.username},
    
    Your verification code is: {code}
    
    This code will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    Lupify Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


# -------------------------------
# REAL-TIME VALIDATION ENDPOINTS
# -------------------------------
def check_username_available(request):
    """Check if username is available (case-insensitive)."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({'available': False, 'message': 'Username cannot be empty'})
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username must be at least 3 characters'})
    
    # Case-insensitive check
    exists = CustomUser.objects.filter(username__iexact=username).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Username taken' if exists else 'Username available'
    })


def check_email_available(request):
    """Check if email is available (case-insensitive)."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    email = request.GET.get('email', '').strip()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email cannot be empty'})
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        return JsonResponse({'available': False, 'message': 'Invalid email format'})
    
    # Case-insensitive check
    exists = CustomUser.objects.filter(email__iexact=email).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Email taken' if exists else 'Email available'
    })


# -------------------------------
# REGISTER
# -------------------------------
def register_view(request):
    """Display register page with Google OAuth option and local signup form."""
    from allauth.socialaccount.models import SocialApp
    import os
    
    # Check if Google OAuth app is configured
    try:
        google_app = SocialApp.objects.get(provider='google')
        client_id = (google_app.client_id or '').strip()
        secret = (google_app.secret or '').strip()
        
        # In development, check for placeholder credentials
        if not client_id or not secret:
            google_configured = False
            google_invalid = True
        elif 'PLACEHOLDER' in client_id.upper():
            # In development, show error about placeholder credentials
            # (actual OAuth requires real Google credentials)
            google_configured = False
            google_invalid = True
        else:
            google_configured = True
            google_invalid = False
    except SocialApp.DoesNotExist:
        google_configured = False
        google_invalid = False
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Allow immediate login for local signup
            user.is_email_verified = True  # Skip email verification for local signup during dev
            user.save()
            
            # Log the user in immediately
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Account created successfully! Welcome to Lupify!")
            return redirect("dashboard_home")
        else:
            # Form has errors, render with form data
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'google_configured': google_configured,
        'google_invalid': google_invalid,
    }
    return render(request, "accounts/register.html", context)


# -------------------------------
# LOGIN
# -------------------------------
def login_view(request):
    if request.method == "POST":
        form = CaseSensitiveAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            # Check if email is verified
            if not user.is_email_verified:
                # Allow local fallback login even if email is not verified so developers can sign in during setup.
                if request.path.endswith('/local/'):
                    messages.info(request, "Email not verified — allowing local sign-in for development.")
                else:
                    # Try to redirect to the verification flow if present; otherwise show a helpful message
                    try:
                        return redirect("verify_email", user_id=user.id)
                    except Exception:
                        messages.error(request, "Please verify your email before logging in. (verification route not configured)")
                        return render(request, "accounts/login_backup.html", {"form": form})

            # Check if account is suspended
            if user.suspended_until and timezone.now() < user.suspended_until:
                remaining = user.suspended_until - timezone.now()
                hours = int(remaining.total_seconds() // 3600)
                messages.error(request, f"Your account is suspended for {hours} more hour(s).")
                return redirect("login")

            login(request, user)
            return redirect("dashboard_home")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = CaseSensitiveAuthenticationForm()

    # Render the styled backup login template which provides the local username/password form
    return render(request, "accounts/login_backup.html", {"form": form})


# -------------------------------
# LOGOUT
# -------------------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------------------
# PROFILE VIEW / UPDATE
# -------------------------------
@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})


# -------------------------------
# DASHBOARD VIEW
# -------------------------------
@login_required
def dashboard_view(request):
    # Show recent posts, trending posts (by likes), and popular communities
    recent_posts = Post.objects.all().order_by('-created')[:10]
    trending_posts = Post.objects.annotate(like_count=models.Count('likes')).order_by('-like_count')[:6]
    popular_communities = Community.objects.annotate(members_count=Count('members')).order_by('-members_count')[:8]

    return render(request, "dashboardhome.html", {
        "recent_posts": recent_posts,
        "trending_posts": trending_posts,
        "popular_communities": popular_communities,
    })


# -------------------------------
# SUBSCRIPTIONS VIEW
# -------------------------------
@login_required
def subscriptions_view(request):
    user = request.user

    # Get all subscriptions linked to this user
    subs = Subscription.objects.filter(user=user)

    # Collect IDs
    community_ids = subs.filter(community__isnull=False).values_list("community_id", flat=True)
    author_ids = subs.filter(author__isnull=False).values_list("author_id", flat=True)

    # Fetch subscribed communities + subscribed authors
    communities = Community.objects.filter(id__in=community_ids)
    authors = get_user_model().objects.filter(id__in=author_ids)

    # Fetch posts
    community_posts = CommunityPost.objects.filter(community_id__in=community_ids)

    # Also include authors the user follows (via User.following)
    try:
        followed_author_ids = list(user.following.values_list("id", flat=True))
    except Exception:
        followed_author_ids = []

    # Merge subscription author IDs with followed author IDs and deduplicate
    all_author_ids = list(set(list(author_ids) + list(followed_author_ids)))

    # Query author objects for both subscribed and followed authors
    authors = get_user_model().objects.filter(id__in=all_author_ids)

    author_posts = Post.objects.filter(author_id__in=all_author_ids)

    # Provide vars the template expects (subs, subscribed_communities/authors)
    return render(request, "accounts/subscriptions.html", {
        "communities": communities,
        "authors": authors,
        "community_posts": community_posts,
        "author_posts": author_posts,
        "subs": subs,
        "subscribed_communities": communities,
        "subscribed_authors": authors,
    })





# -------------------------------
# ACCOUNT DASHBOARD (PROFILE + MEMBERSHIPS)
# -------------------------------
@login_required
def account_dashboard_view(request):
    user = request.user
    section = request.GET.get("section", "profile")  # default to profile
    form = None
    membership_plans = ["Free", "Basic", "Premium"]

    # Ensure default membership
    if not hasattr(user, "membership") or not user.membership:
        user.membership = "Free"
        user.save()

    if section == "profile":
        if request.method == "POST":
            form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()

                # Handle cropped avatar
                avatar_data = request.POST.get("avatar_cropped")
                if avatar_data:
                    try:
                        format, imgstr = avatar_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f"{user.username}_avatar.{ext}")
                        user.avatar.save(data.name, data, save=True)
                        user.refresh_from_db()
                    except Exception as e:
                        messages.error(request, f"Failed to upload avatar: {e}")

                messages.success(request, "Your profile has been updated!")
                return redirect(f"{request.path}?section=profile")
        else:
            form = ProfileUpdateForm(instance=user)

    elif section == "memberships":
        if request.method == "POST":
            selected_plan = request.POST.get("membership")
            if selected_plan in membership_plans:
                user.membership = selected_plan
                user.save()
                messages.success(request, f"Your plan has been updated to {selected_plan}!")
                return redirect(f"{request.path}?section=memberships")

    elif section == "social":
        if request.method == "POST":
            user.social_youtube = request.POST.get("youtube", "")
            user.social_instagram = request.POST.get("instagram", "")
            user.social_tiktok = request.POST.get("tiktok", "")
            user.social_twitch = request.POST.get("twitch", "")
            user.social_github = request.POST.get("github", "")
            user.public_profile = request.POST.get("public_profile") == "on"
            user.allow_public_socials = request.POST.get("allow_public_socials") == "on"
            user.save()
            messages.success(request, "Your social settings have been updated!")
            return redirect(f"{request.path}?section=social")

    return render(request, "accounts/account_dashboard.html", {
        "section": section,
        "form": form,
        "user": user,
        "plans": membership_plans,
    })
@login_required
def toggle_subscription(request, community_id=None, author_id=None):
    user = request.user

    # COMMUNITY SUBSCRIPTION
    if community_id:
        community = get_object_or_404(Community, id=community_id)
        sub, created = Subscription.objects.get_or_create(user=user, community=community)

        if not created:
            sub.delete()

        return redirect("subscriptions")

    # AUTHOR SUBSCRIPTION
    if author_id:
        author = get_object_or_404(User, id=author_id)
        sub, created = Subscription.objects.get_or_create(user=user, author=author)

        if not created:
            sub.delete()

        return redirect("subscriptions")

    return redirect("subscriptions")


# -------------------------------
# USER PROFILE POPUP / VIEW
# -------------------------------
def user_profile_view(request, user_id):
    """Returns user profile data for popup display or privacy message."""
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user

    # If viewing own profile, return all info
    if current_user.is_authenticated and current_user.id == user_id:
        return JsonResponse({
            "username": target_user.username,
            "avatar": target_user.avatar.url if target_user.avatar else None,
            "bio": target_user.bio or "",
            "followers_count": target_user.followers.count(),
            "is_verified": target_user.is_verified,
            "is_premium": target_user.is_premium,
            "is_own_profile": True,
            "socials": {
                "youtube": target_user.social_youtube,
                "instagram": target_user.social_instagram,
                "tiktok": target_user.social_tiktok,
                "twitch": target_user.social_twitch,
                "github": target_user.social_github,
            }
        })

    # If user has allow_public_socials disabled, return privacy message
    if not target_user.allow_public_socials:
        return JsonResponse({
            "username": target_user.username,
            "is_private": True,
            "message": "Account is private"
        })

    # Public profile - return public info
    return JsonResponse({
        "username": target_user.username,
        "avatar": target_user.avatar.url if target_user.avatar else None,
        "bio": target_user.bio or "",
        "followers_count": target_user.followers.count(),
        "is_verified": target_user.is_verified,
        "is_premium": target_user.is_premium,
        "is_private": False,
        "socials": {
            "youtube": target_user.social_youtube,
            "instagram": target_user.social_instagram,
            "tiktok": target_user.social_tiktok,
            "twitch": target_user.social_twitch,
            "github": target_user.social_github,
        }
    })


# -------------------------------
# PUBLIC PROFILE PAGE
# -------------------------------
def public_profile_view(request, user_id):
    """Display a read-only public profile page for a user using account dashboard format."""
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    section = request.GET.get("section", "profile")  # default to profile
    
    # Check if profile is private
    if not target_user.public_profile and (not current_user.is_authenticated or current_user.id != user_id):
        # Create form for read-only display
        form = ProfileUpdateForm(instance=target_user)
        return render(request, 'accounts/account_dashboard.html', {
            'target_user': target_user,
            'viewing_other_user': True,
            'is_private': True,
            'section': section,
            'user': target_user,
            'form': form,
        })
    
    # Check if socials are hidden
    show_socials = target_user.allow_public_socials or (current_user.is_authenticated and current_user.id == user_id)
    
    # Get user's blog posts if profile is public
    user_posts = Post.objects.filter(author=target_user).order_by('-created') if target_user.public_profile else Post.objects.none()
    posts_count = user_posts.count()
    followers_count = target_user.followers.count()
    
    # Check if current user follows this user
    is_following = False
    if current_user.is_authenticated:
        is_following = target_user.followers.filter(id=current_user.id).exists()
    
    # Create form for read-only display
    form = ProfileUpdateForm(instance=target_user)
    
    context = {
        'target_user': target_user,
        'viewing_other_user': True,
        'is_private': not target_user.public_profile,
        'user_posts': user_posts[:10],  # Show last 10 posts
        'posts_count': posts_count,
        'followers_count': followers_count,
        'is_following': is_following,
        'is_own_profile': current_user.is_authenticated and current_user.id == user_id,
        'show_socials': show_socials,
        'section': section,
        'user': target_user,
        'form': form,
    }
    
    return render(request, 'accounts/account_dashboard.html', context)


# -------------------------------
# EMAIL VERIFICATION
# -------------------------------
def verify_email(request, user_id):
    """Display email verification page."""
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("register")
    
    if user.is_email_verified:
        messages.info(request, "Your email is already verified. Please log in.")
        return redirect("login")
    
    if request.method == "POST":
        code = request.POST.get('verification_code', '').strip()
        
        if not code:
            messages.error(request, "Please enter the verification code.")
            return render(request, "accounts/verify_email.html", {'user': user})
        
        # Check if code is expired
        if user.email_verification_expires_at and timezone.now() > user.email_verification_expires_at:
            messages.error(request, "Verification code has expired. Please register again.")
            user.delete()
            return redirect("register")
        
        # Check attempts
        if user.email_verification_attempts >= 5:
            messages.error(request, "Too many attempts. Please register again.")
            user.delete()
            return redirect("register")
        
        # Verify code
        if code == user.email_verification_code:
            user.is_email_verified = True
            user.email_verification_code = None
            user.email_verification_expires_at = None
            user.save()
            
            messages.success(request, "Email verified! You can now log in.")
            return redirect("login")
        else:
            user.email_verification_attempts += 1
            user.save()
            
            remaining_attempts = 5 - user.email_verification_attempts
            if remaining_attempts > 0:
                messages.error(request, f"Invalid code. {remaining_attempts} attempts remaining.")
            else:
                messages.error(request, "Too many attempts. Please register again.")
                user.delete()
                return redirect("register")
            
            return render(request, "accounts/verify_email.html", {'user': user, 'attempts_left': remaining_attempts})
    
    return render(request, "accounts/verify_email.html", {'user': user})


def resend_verification_email(request, user_id):
    """Resend verification email."""
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})
    
    if user.is_email_verified:
        return JsonResponse({'success': False, 'message': 'Email already verified'})
    
    if send_verification_email(user):
        return JsonResponse({'success': True, 'message': 'Verification email sent!'})
    else:
        return JsonResponse({'success': False, 'message': 'Failed to send email'})


# -------------------------------
# GOOGLE OAUTH LOGIN VIEW
# -------------------------------
def google_login_view(request):
    """Display Google OAuth login page with setup instructions if needed."""
    from allauth.socialaccount.models import SocialApp
    import os
    
    # Check if Google OAuth app is configured
    try:
        google_app = SocialApp.objects.get(provider='google')
        client_id = (google_app.client_id or '').strip()
        secret = (google_app.secret or '').strip()
        
        # In development, check for placeholder credentials
        if not client_id or not secret:
            google_configured = False
            google_invalid = True
        elif 'PLACEHOLDER' in client_id.upper():
            # In development, show error about placeholder credentials
            # (actual OAuth requires real Google credentials)
            google_configured = False
            google_invalid = True
        else:
            google_configured = True
            google_invalid = False
    except SocialApp.DoesNotExist:
        google_configured = False
        google_invalid = False
    
    context = {
        'google_configured': google_configured,
        'google_invalid': google_invalid,
    }
    
    return render(request, 'accounts/google_login.html', context)


# --------------------------------
# CHAT VIEWS
# --------------------------------

from .models import DirectMessage, Conversation, GameLobbyBan
import json

@login_required
def send_message_view(request):
    """Send a direct message to another user"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        content = data.get('content', '').strip()
        
        if not recipient_id or not content:
            return JsonResponse({'error': 'Missing fields'}, status=400)
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Create or get conversation
        conversation, _ = Conversation.objects.get_or_create(
            user1_id=min(request.user.id, recipient_id),
            user2_id=max(request.user.id, recipient_id)
        )
        
        # Create message
        message = DirectMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
        return JsonResponse({
            'id': message.id,
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        # Print to server console for easier debugging
        print('Error in game_lobby_post_message_view:', str(e))
        print(tb)
        return JsonResponse({'error': 'Server error', 'details': tb.splitlines()[-10:]}, status=500)


@login_required
def get_messages_view(request):
    """Get messages between current user and another user"""
    recipient_id = request.GET.get('recipient_id')
    
    if not recipient_id:
        return JsonResponse({'error': 'Missing recipient_id'}, status=400)
    
    try:
        recipient_id = int(recipient_id)
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Get all messages between the two users
        messages = DirectMessage.objects.filter(
            (models.Q(sender=request.user, recipient=recipient) |
             models.Q(sender=recipient, recipient=request.user))
        ).order_by('created_at')
        
        # Mark messages as read
        DirectMessage.objects.filter(
            sender=recipient,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        message_list = [{
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'recipient': msg.recipient.username,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read
        } for msg in messages]
        
        return JsonResponse({'messages': message_list})
    except ValueError:
        return JsonResponse({'error': 'Invalid recipient_id'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_conversations_view(request):
    """Get all conversations for the current user"""
    try:
        conversations = Conversation.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        ).order_by('-updated_at')
        
        conv_list = []
        for conv in conversations:
            other_user = conv.user2 if conv.user1.id == request.user.id else conv.user1
            conv_list.append({
                'id': conv.id,
                'other_user_id': other_user.id,
                'other_user_username': other_user.username,
                'updated_at': conv.updated_at.isoformat()
            })
        
        return JsonResponse({'conversations': conv_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --------------------------------
# GAME LOBBY VIEWS
# --------------------------------

@login_required
def game_lobby_view(request):
    """Display the Try Not To Get Banned game lobby with chat"""
    from blog.views import banned_words
    
    # Check if user has active ban
    ban = GameLobbyBan.objects.filter(user=request.user).order_by('-banned_until').first()
    is_banned = ban and ban.is_active() if ban else False
    
    if is_banned:
        ban_time_remaining = int((ban.banned_until - timezone.now()).total_seconds())
    else:
        ban_time_remaining = 0
    
    context = {
        'banned_words': banned_words,
        'is_banned': is_banned,
        'ban_time_remaining': ban_time_remaining,
    }
    # Include Try Not To Get Banned score info (from WordListGame) and a small leaderboard
    try:
        wgame, _ = WordListGame.objects.get_or_create(user=request.user)
        context['lobby_score'] = wgame.score or 0
    except Exception:
        context['lobby_score'] = 0

    # Top 5 leaderboard (descending by score)
    try:
        top = WordListGame.objects.order_by('-score')[:5]
        leaderboard = [{'username': t.user.username, 'score': t.score or 0} for t in top]
        context['lobby_leaderboard'] = leaderboard
    except Exception:
        context['lobby_leaderboard'] = []
    
    return render(request, 'core/game_lobby.html', context)


@login_required
def game_lobby_post_message_view(request):
    """Post a message in the game lobby and check for banned words"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from blog.views import banned_words
        
        # Check if user is banned
        ban = GameLobbyBan.objects.filter(user=request.user).order_by('-banned_until').first()
        is_banned = ban and ban.is_active() if ban else False
        
        if is_banned:
            return JsonResponse({
                'error': 'banned',
                'ban_time_remaining': int((ban.banned_until - timezone.now()).total_seconds())
            }, status=403)
        
        data = json.loads(request.body)
        message_content = data.get('content', '').strip().lower()
        
        if not message_content:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Check for banned words
        banned_found = [word for word in banned_words if word in message_content]
        
        if banned_found:
            # Ban the user for 1 minute
            ban_until = timezone.now() + timedelta(minutes=1)
            GameLobbyBan.objects.create(user=request.user, banned_until=ban_until)
            # Return chat-friendly payload: include original message and a system message
            system_msg = f"{request.user.username} was banned for 1 minute for using: {', '.join(banned_found)}"
            # persist offending message and system announcement, then broadcast
            try:
                GameLobbyMessage.objects.create(user=request.user, author_name=request.user.username, content=data.get('content'), is_system=False)
                GameLobbyMessage.objects.create(user=None, author_name='System', content=system_msg, is_system=True)
            except Exception:
                pass

            # broadcast to group
            channel_layer = get_channel_layer()
            payload_msg = {
                'author': request.user.username,
                'content': data.get('content'),
                'created_at': timezone.now().isoformat(),
                'is_system': False,
            }
            system_payload = {
                'author': 'System',
                'content': system_msg,
                'created_at': timezone.now().isoformat(),
                'is_system': True,
            }
            try:
                async_to_sync(channel_layer.group_send)('game_lobby', {'type': 'lobby_message', 'message': payload_msg})
                async_to_sync(channel_layer.group_send)('game_lobby', {'type': 'lobby_message', 'message': system_payload})
            except Exception:
                pass

            return JsonResponse({
                'error': 'banned_words',
                'banned_words_found': banned_found,
                'ban_time_remaining': 60,
                'chat_post': payload_msg,
                'system_message': system_msg,
            }, status=400)
            # if we had challenge updates, include them as well
            try:
                if 'challenge_update' in locals() and challenge_update:
                    return JsonResponse({
                        'error': 'banned_words',
                        'banned_words_found': banned_found,
                        'ban_time_remaining': 60,
                        'chat_post': payload_msg,
                        'system_message': system_msg,
                        'challenge_update': challenge_update,
                    }, status=400)
            except Exception:
                pass
        
        # Message is clean, return success
        # persist and broadcast clean message
        try:
            GameLobbyMessage.objects.create(user=request.user, author_name=request.user.username, content=data.get('content'), is_system=False)
        except Exception:
            pass
        try:
            channel_layer = get_channel_layer()
            payload_msg = {
                'author': request.user.username,
                'content': data.get('content'),
                'created_at': timezone.now().isoformat(),
                'is_system': False,
            }
            async_to_sync(channel_layer.group_send)('game_lobby', {'type': 'lobby_message', 'message': payload_msg})
        except Exception:
            pass

        # --- Lobby 12-letter challenge handling ---
        challenge_update = None
        try:
            # Ensure channel_layer is available for broadcasts in this scope
            try:
                channel_layer = get_channel_layer()
            except Exception:
                channel_layer = None
            challenge = GameLobbyChallenge.objects.filter(user=request.user).order_by('-created_at').first()
            if challenge and not challenge.completed:
                # Parse message into tokens; for each token that is a dictionary word,
                # collect letters present in that token that belong to the challenge.
                tokens = re.findall(r"\b[\w']+\b", data.get('content', '').lower())
                letters_found = set()
                for token in tokens:
                    is_word, dict_avail = is_dictionary_word(token)
                    if is_word:
                        # find letters from challenge present in token
                        for ch in challenge.letters:
                            if ch.lower() in token:
                                letters_found.add(ch.upper())
                if letters_found:
                    newly = challenge.mark_letters(list(letters_found))
                    # prepare update payload
                    challenge_update = {
                        'letters': challenge.letters,
                        'used_letters': challenge.used_letters,
                        'completed': challenge.completed,
                        'user': request.user.username,
                    }
                    # broadcast small system messages
                    if newly:
                        tick_msg = f"{request.user.username} found: {', '.join(newly)}"
                        GameLobbyMessage.objects.create(user=None, author_name='System', content=tick_msg, is_system=True)
                        try:
                            async_to_sync(channel_layer.group_send)('game_lobby', {'type': 'lobby_message', 'message': {'author': 'System', 'content': tick_msg, 'created_at': timezone.now().isoformat(), 'is_system': True}})
                        except Exception:
                            pass
                    if challenge.completed:
                        # Award 20 points
                        wgame, _ = WordListGame.objects.get_or_create(user=request.user)
                        wgame.score = (wgame.score or 0) + 20
                        wgame.save()
                        sys_msg = f"{request.user.username} completed the 12-letter challenge and earned 20 points!"
                        GameLobbyMessage.objects.create(user=None, author_name='System', content=sys_msg, is_system=True)
                        try:
                            async_to_sync(channel_layer.group_send)('game_lobby', {'type': 'lobby_message', 'message': {'author': 'System', 'content': sys_msg, 'created_at': timezone.now().isoformat(), 'is_system': True}})
                        except Exception:
                            pass
                        # Generate a new 12-letter challenge for the user and reset used letters
                        try:
                            new_letters = generate_random_letter_list(12)
                            challenge.letters = new_letters
                            challenge.used_letters = []
                            challenge.completed = False
                            challenge.save()
                            # announce new challenge to lobby
                            new_chal_msg = f"A new 12-letter challenge has been generated for {request.user.username}."
                            GameLobbyMessage.objects.create(user=None, author_name='System', content=new_chal_msg, is_system=True)
                            try:
                                async_to_sync(channel_layer.group_send)('game_lobby', {'type': 'lobby_message', 'message': {'author': 'System', 'content': new_chal_msg, 'created_at': timezone.now().isoformat(), 'is_system': True}})
                            except Exception:
                                pass
                            # prepare challenge_update to send back to client
                            challenge_update = {
                                'letters': challenge.letters,
                                'used_letters': challenge.used_letters,
                                'completed': challenge.completed,
                                'user': request.user.username,
                            }
                        except Exception:
                            # if new challenge creation fails, leave as-is (no crash)
                            pass
        except Exception:
            challenge_update = None

        # Always return a success response for clean messages (challenge_update may be None)
        resp = {
            'success': True,
            'user': request.user.username,
            'content': data.get('content'),
            'created_at': timezone.now().isoformat()
        }
        if challenge_update:
            resp['challenge_update'] = challenge_update
        return JsonResponse(resp)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --------------------------------
# GAMES HUB
# --------------------------------

@login_required
def games_hub_view(request):
    """Display available games"""
    games = [
        {
            'id': 'try-not-to-get-banned',
            'name': 'Try Not To Get Banned',
            'emoji': '🎮',
            'description': 'Chat freely but watch your words!',
            'url': 'game_lobby'
        }
    ]
    # Add Letter Set as a separate game entry
    games.append({
        'id': 'letter-set',
        'name': 'Letter Set',
        'emoji': '🔤',
        'description': 'Form words from a set of letters and earn points.',
        'url': 'letter_set_game'
    })

    return render(request, 'core/games_hub.html', {'games': games})


# --------------------------------
# LETTER SET GAME
# --------------------------------

import random
import string

def generate_random_letters(count=15):
    """Generate `count` random distinct letters (default 15)."""
    alphabet = list(string.ascii_uppercase)
    return ''.join(random.sample(alphabet, count))


def is_dictionary_word(word):
    """Try multiple strategies to verify if `word` is an English word.

    Priority:
    1. python-enchant (if installed)
    2. local wordlist at data/words.txt (one word per line)
    3. /usr/share/dict/words (Unix systems)
    4. fallback: return True (dictionary unavailable)
    """
    w = word.strip().lower()
    if not w:
        return False, False
    # 1) try pyenchant
    try:
        import enchant
        d = enchant.Dict("en_US")
        return d.check(w), True
    except Exception:
        pass

    # 2) try local data/words.txt
    try:
        base = Path(__file__).resolve().parent.parent
        wordfile = base / 'data' / 'words.txt'
        if wordfile.exists():
            with open(wordfile, 'r', encoding='utf-8') as fh:
                words = {line.strip().lower() for line in fh}
            return (w in words), True
    except Exception:
        pass

    # 3) try /usr/share/dict/words
    try:
        wf = Path('/usr/share/dict/words')
        if wf.exists():
            with open(wf, 'r', encoding='utf-8') as fh:
                words = {line.strip().lower() for line in fh}
            return (w in words), True
    except Exception:
        pass

    # 4) dictionary not available, fallback (treat as unknown)
    return True, False


def is_valid_word(word, allowed_letters):
    """Check if word can be formed from allowed letters (case-insensitive)"""
    word_lower = word.lower()
    allowed_lower = allowed_letters.lower()
    
    for char in word_lower:
        if char not in allowed_lower:
            return False
        # Check if letter is available (can't use more than what's in the set)
        if allowed_lower.count(char) < word_lower.count(char):
            return False
    return True


@login_required
def letter_set_game_view(request):
    """Display Letter Set game"""
    # Get or create current game session
    game = LetterSetGame.objects.filter(user=request.user).order_by('-updated_at').first()
    
    if not game or (timezone.now() - game.updated_at).total_seconds() > 3600:  # Reset after 1 hour
        # Create new game session with random letters
        game = LetterSetGame.objects.create(
            user=request.user,
            letters=generate_random_letters(15),
            score=0,
            completed_words=''
        )
    
    context = {
        'game': game,
        'completed_words': game.get_completed_words_list(),
        'letters': sorted(game.letters),  # Show sorted for easier reading
    }
    
    return render(request, 'core/letter_set_game.html', context)


@login_required
def letter_set_submit_word_view(request):
    """Submit a word in Letter Set game"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        word = data.get('word', '').strip()
        
        if not word or len(word) < 2:
            return JsonResponse({'error': 'Word must be at least 2 characters'}, status=400)
        
        # Get current game
        game = LetterSetGame.objects.filter(user=request.user).order_by('-updated_at').first()
        if not game:
            return JsonResponse({'error': 'No active game session'}, status=400)
        
        # Check if word can be formed from available letters
        if not is_valid_word(word, game.letters):
            return JsonResponse({
                'error': 'invalid_letters',
                'message': f'The word "{word}" cannot be formed from your letters: {game.letters}'
            }, status=400)

        # Check dictionary membership
        is_dict_word, dict_available = is_dictionary_word(word)
        if not is_dict_word:
            return JsonResponse({
                'error': 'not_dictionary',
                'message': f'"{word}" is not recognized as a dictionary word.',
                'dictionary_available': dict_available
            }, status=400)

        # Check if word already completed
        completed = game.get_completed_words_list()
        if any(w.lower() == word.lower() for w in completed):
            return JsonResponse({
                'error': 'duplicate',
                'message': f'You already completed "{word}"!'
            }, status=400)

        # Add word
        added = game.add_word(word)
        if not added:
            return JsonResponse({'error': 'duplicate', 'message': 'Duplicate word.'}, status=400)

        # Increment score for the submitted word
        game.score = (game.score or 0) + 1
        game.save()

        # Compute used letters based on completed words
        used_letters = set(''.join(game.get_completed_words_list()).upper())
        all_letters = set(game.letters.upper())
        all_greened = used_letters >= all_letters

        response = {
            'success': True,
            'word': word,
            'score': game.score,
            'total_words': len(game.get_completed_words_list()),
            'used_letters': sorted(list(used_letters)),
            'all_greened': all_greened,
            'dictionary_available': dict_available,
            'message': f'Great! +1 point! Your score: {game.score}'
        }

        # If all letters have been used, award bonus (20 points) and generate new letters
        if all_greened:
            bonus = 20
            game.score = game.score + bonus
            new_letters = generate_random_letters(15)
            game.letters = new_letters
            game.completed_words = ''
            game.save()
            response['bonus_awarded'] = True
            response['bonus_amount'] = bonus
            response['new_letters'] = new_letters
            response['message'] = f'All letters used! Bonus +{bonus} points awarded. Your score: {game.score}'

        return JsonResponse(response)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def letter_set_chat_view(request):
    """Chat interface for Letter Set game"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        message_content = data.get('content', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Just return success - message is handled client-side
        return JsonResponse({
            'success': True,
            'user': request.user.username,
            'content': message_content,
            'created_at': timezone.now().isoformat()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def letter_set_start_view(request):
    """API to start or get the current Letter Set session for the user (JSON)."""
    try:
        game = LetterSetGame.objects.filter(user=request.user).order_by('-updated_at').first()
        if not game or (timezone.now() - game.updated_at).total_seconds() > 3600:
            game = LetterSetGame.objects.create(
                user=request.user,
                letters=generate_random_letters(15),
                score=0,
                completed_words=''
            )

        return JsonResponse({
            'letters': game.letters,
            'score': game.score,
            'completed_words': game.get_completed_words_list(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def game_lobby_challenge_start_view(request):
    """Start or return the user's 12-word lobby challenge (JSON)."""
    try:
        # Always generate a fresh 12-letter challenge when this endpoint is called.
        # This creates a new per-user challenge each time the client requests start.
        letters = generate_random_letter_list(12)
        chal = GameLobbyChallenge.objects.create(user=request.user, letters=letters, used_letters=[], completed=False)

        return JsonResponse({
            'letters': chal.letters,
            'used_letters': chal.used_letters,
            'completed': chal.completed,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def generate_random_word_list(count=12):
    """Generate `count` random unique words from available dictionary sources."""
    import random
    from pathlib import Path

    # Prefer a large data/words.txt if present
    base = Path(__file__).resolve().parent.parent
    wordfile = base / 'data' / 'words.txt'
    words = []
    try:
        if wordfile.exists():
            with open(wordfile, 'r', encoding='utf-8') as fh:
                words = [w.strip().lower() for w in fh if w.strip()]
    except Exception:
        words = []

    # fallback to small built-in wordlist if none available
    if not words:
        words = [
            'apple','banana','orange','table','chair','window','river','mountain','guitar','python','coffee','bottle',
            'keyboard','mouse','monitor','paper','pencil','flower','pillow','garden','butter','silver','planet','rocket',
            'ocean','forest','island','isotope','button','candle','painter','castle','driver','engine'
        ]

    # choose unique words
    words = list(set(words))
    if len(words) <= count:
        return words[:count]
    return random.sample(words, count)


def generate_random_letter_list(count=12):
    import random
    import string
    # allow duplicates (letters may repeat)
    alphabet = list(string.ascii_uppercase)
    if count <= 0:
        return []
    # Use random.choices to allow repeated letters per user request
    return random.choices(alphabet, k=count)

