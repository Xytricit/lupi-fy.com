import base64
import json
import random
import re
import string
from datetime import timedelta
from pathlib import Path

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import escape as html_escape

try:
    import bleach

    HAS_BLEACH = True
except Exception:
    HAS_BLEACH = False

from blog.models import Post
from communities.models import Community, CommunityPost
from recommend.models import Interaction

from .forms import (CaseSensitiveAuthenticationForm, CustomUserCreationForm,
                    ProfileUpdateForm)
from .models import (Conversation, CustomUser, DirectMessage, GameLobbyBan,
                     GameLobbyChallenge, GameLobbyMessage, LetterSetGame,
                     Notification, Subscription, WordListGame)

User = get_user_model()


# -------------------------------
# EMAIL VERIFICATION
# -------------------------------
def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return "".join([str(random.randint(0, 9)) for _ in range(6)])


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
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request"}, status=400)

    username = request.GET.get("username", "").strip()

    if not username:
        return JsonResponse({"available": False, "message": "Username cannot be empty"})

    if len(username) < 3:
        return JsonResponse(
            {"available": False, "message": "Username must be at least 3 characters"}
        )

    # Case-insensitive check
    exists = CustomUser.objects.filter(username__iexact=username).exists()

    return JsonResponse(
        {
            "available": not exists,
            "message": "Username taken" if exists else "Username available",
        }
    )


def check_email_available(request):
    """Check if email is available (case-insensitive)."""
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request"}, status=400)

    email = request.GET.get("email", "").strip()

    if not email:
        return JsonResponse({"available": False, "message": "Email cannot be empty"})

    # Basic email validation
    if "@" not in email or "." not in email:
        return JsonResponse({"available": False, "message": "Invalid email format"})

    # Case-insensitive check
    exists = CustomUser.objects.filter(email__iexact=email).exists()

    return JsonResponse(
        {
            "available": not exists,
            "message": "Email taken" if exists else "Email available",
        }
    )


# -------------------------------
# REGISTER
# -------------------------------
def register_view(request):
    """Display register page with Google OAuth option and local signup form."""
    from allauth.socialaccount.models import SocialApp

    # Check if Google OAuth app is configured
    try:
        google_app = SocialApp.objects.get(provider="google")
        client_id = (google_app.client_id or "").strip()
        secret = (google_app.secret or "").strip()

        # In development, check for placeholder credentials
        if not client_id or not secret:
            google_configured = False
            google_invalid = True
        elif "PLACEHOLDER" in client_id.upper():
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
            user.is_email_verified = (
                True  # Skip email verification for local signup during dev
            )
            user.save()

            # Log the user in immediately
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(
                request, "Account created successfully! Welcome to Lupify!"
            )
            return redirect("dashboard_home")
        else:
            # Form has errors, render with form data
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    context = {
        "form": form,
        "google_configured": google_configured,
        "google_invalid": google_invalid,
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
                if request.path.endswith("/local/"):
                    messages.info(
                        request,
                        "Email not verified — allowing local sign-in for development.",
                    )
                else:
                    # Try to redirect to the verification flow if present; otherwise show a helpful message
                    try:
                        return redirect("verify_email", user_id=user.id)
                    except Exception:
                        messages.error(
                            request,
                            "Please verify your email before logging in. (verification route not configured)",
                        )
                        return render(
                            request, "accounts/login_backup.html", {"form": form}
                        )

            # Check if account is suspended
            if user.suspended_until and timezone.now() < user.suspended_until:
                remaining = user.suspended_until - timezone.now()
                hours = int(remaining.total_seconds() // 3600)
                messages.error(
                    request, f"Your account is suspended for {hours} more hour(s)."
                )
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
    recent_posts = Post.objects.all().order_by("-created")[:10]
    trending_posts = Post.objects.annotate(like_count=models.Count("likes")).order_by(
        "-like_count"
    )[:6]
    popular_communities = Community.objects.annotate(
        members_count=Count("members")
    ).order_by("-members_count")[:8]

    return render(
        request,
        "dashboardhome.html",
        {
            "recent_posts": recent_posts,
            "trending_posts": trending_posts,
            "popular_communities": popular_communities,
        },
    )


# -------------------------------
# SUBSCRIPTIONS VIEW
# -------------------------------
@login_required
def subscriptions_view(request):
    user = request.user
    # Get all subscriptions linked to this user
    subs = Subscription.objects.filter(user=user)

    # Collect IDs
    community_ids = subs.filter(community__isnull=False).values_list(
        "community_id", flat=True
    )
    author_ids = subs.filter(author__isnull=False).values_list("author_id", flat=True)

    # Joined communities: communities the user is a member of
    joined_communities = Community.objects.filter(members=user)

    # Subscribed communities (explicit subscriptions)
    subscribed_communities = Community.objects.filter(id__in=community_ids)

    # Show posts from communities the user has joined (bring back community posts)
    community_posts = CommunityPost.objects.filter(community__in=joined_communities)

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

    # Provide vars the template expects (subs, subscribed_communities/authors, joined_communities)
    return render(
        request,
        "accounts/subscriptions.html",
        {
            "communities": subscribed_communities,
            "authors": authors,
            "community_posts": community_posts,
            "author_posts": author_posts,
            "subs": subs,
            "subscribed_communities": subscribed_communities,
            "joined_communities": joined_communities,
            "subscribed_authors": authors,
        },
    )


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
                        data = ContentFile(
                            base64.b64decode(imgstr),
                            name=f"{user.username}_avatar.{ext}",
                        )
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
                messages.success(
                    request, f"Your plan has been updated to {selected_plan}!"
                )
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
            # Allow users to opt in/out of receiving direct messages
            user.allow_dms = request.POST.get("allow_dms") == "on"
            user.save()
            messages.success(request, "Your social settings have been updated!")
            return redirect(f"{request.path}?section=social")

    return render(
        request,
        "accounts/account_dashboard.html",
        {
            "section": section,
            "form": form,
            "user": user,
            "plans": membership_plans,
        },
    )


@login_required
def toggle_subscription(request, community_id=None, author_id=None):
    user = request.user

    # COMMUNITY SUBSCRIPTION
    if community_id:
        community = get_object_or_404(Community, id=community_id)
        sub, created = Subscription.objects.get_or_create(
            user=user, community=community
        )

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
        return JsonResponse(
            {
                "username": target_user.username,
                "avatar": target_user.avatar.url if target_user.avatar else None,
                "bio": target_user.bio or "",
                "followers_count": target_user.followers.count(),
                "is_verified": target_user.is_verified,
                "is_premium": target_user.is_premium,
                "is_own_profile": True,
                "allow_dms": getattr(target_user, "allow_dms", True),
                "socials": {
                    "youtube": target_user.social_youtube,
                    "instagram": target_user.social_instagram,
                    "tiktok": target_user.social_tiktok,
                    "twitch": target_user.social_twitch,
                    "github": target_user.social_github,
                },
            }
        )

    # If user has allow_public_socials disabled, return structured privacy info
    # Return a consistent shape so the client can always render Social/Achievements/Chat sections
    if not target_user.allow_public_socials:
        return JsonResponse(
            {
                "username": target_user.username,
                "avatar": target_user.avatar.url if target_user.avatar else None,
                "bio": target_user.bio or "",
                "followers_count": target_user.followers.count(),
                "is_verified": target_user.is_verified,
                "is_premium": target_user.is_premium,
                "is_private": True,
                "allow_public_socials": False,
                "allow_dms": getattr(target_user, "allow_dms", True),
                "is_own_profile": current_user.is_authenticated
                and current_user.id == user_id,
                "socials": {
                    "youtube": None,
                    "instagram": None,
                    "tiktok": None,
                    "twitch": None,
                    "github": None,
                },
                "achievements": [],
                "message": "Account is private",
            }
        )

    # Public profile - return public info
    return JsonResponse(
        {
            "username": target_user.username,
            "avatar": target_user.avatar.url if target_user.avatar else None,
            "bio": target_user.bio or "",
            "followers_count": target_user.followers.count(),
            "is_verified": target_user.is_verified,
            "is_premium": target_user.is_premium,
            "is_private": False,
            "allow_dms": getattr(target_user, "allow_dms", True),
            "socials": {
                "youtube": target_user.social_youtube,
                "instagram": target_user.social_instagram,
                "tiktok": target_user.social_tiktok,
                "twitch": target_user.social_twitch,
                "github": target_user.social_github,
            },
        }
    )


# -------------------------------
# PUBLIC PROFILE PAGE
# -------------------------------
def public_profile_view(request, user_id):
    """Display a read-only public profile page for a user using account dashboard format."""
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    section = request.GET.get("section", "profile")  # default to profile

    # Check if profile is private
    if not target_user.public_profile and (
        not current_user.is_authenticated or current_user.id != user_id
    ):
        # Create form for read-only display
        form = ProfileUpdateForm(instance=target_user)
        return render(
            request,
            "accounts/account_dashboard.html",
            {
                "target_user": target_user,
                "viewing_other_user": True,
                "is_private": True,
                "section": section,
                "user": target_user,
                "form": form,
            },
        )

    # Check if socials are hidden
    show_socials = target_user.allow_public_socials or (
        current_user.is_authenticated and current_user.id == user_id
    )

    # Get user's blog posts if profile is public
    user_posts = (
        Post.objects.filter(author=target_user).order_by("-created")
        if target_user.public_profile
        else Post.objects.none()
    )
    posts_count = user_posts.count()
    followers_count = target_user.followers.count()

    # Check if current user follows this user
    is_following = False
    if current_user.is_authenticated:
        is_following = target_user.followers.filter(id=current_user.id).exists()

    # Create form for read-only display
    form = ProfileUpdateForm(instance=target_user)

    context = {
        "target_user": target_user,
        "viewing_other_user": True,
        "is_private": not target_user.public_profile,
        "user_posts": user_posts[:10],  # Show last 10 posts
        "posts_count": posts_count,
        "followers_count": followers_count,
        "is_following": is_following,
        "is_own_profile": current_user.is_authenticated and current_user.id == user_id,
        "show_socials": show_socials,
        "section": section,
        "user": target_user,
        "form": form,
    }

    return render(request, "accounts/account_dashboard.html", context)


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
        code = request.POST.get("verification_code", "").strip()

        if not code:
            messages.error(request, "Please enter the verification code.")
            return render(request, "accounts/verify_email.html", {"user": user})

        # Check if code is expired
        if (
            user.email_verification_expires_at
            and timezone.now() > user.email_verification_expires_at
        ):
            messages.error(
                request, "Verification code has expired. Please register again."
            )
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
                messages.error(
                    request, f"Invalid code. {remaining_attempts} attempts remaining."
                )
            else:
                messages.error(request, "Too many attempts. Please register again.")
                user.delete()
                return redirect("register")

            return render(
                request,
                "accounts/verify_email.html",
                {"user": user, "attempts_left": remaining_attempts},
            )

    return render(request, "accounts/verify_email.html", {"user": user})


def resend_verification_email(request, user_id):
    """Resend verification email."""
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found"})

    if user.is_email_verified:
        return JsonResponse({"success": False, "message": "Email already verified"})

    if send_verification_email(user):
        return JsonResponse({"success": True, "message": "Verification email sent!"})
    else:
        return JsonResponse({"success": False, "message": "Failed to send email"})


# -------------------------------
# CREATOR DASHBOARD + ANALYTICS
# -------------------------------
@login_required
def creator_dashboard_view(request):
    """Show the current user's authored posts and basic metrics.

    Provides overview metrics (total views, likes, followers), a 30-day
    timeseries for trends (views/likes), and a per-post summary used by
    the template's Content Management table.
    """
    user = request.user
    posts_qs = (
        Post.objects.filter(author=user)
        .annotate(like_count=Count("likes"))
        .order_by("-created")
    )

    post_ids = list(posts_qs.values_list("id", flat=True))
    post_ct = ContentType.objects.get_for_model(Post)

    # Per-post summary
    post_stats = []
    # Use stored Post.views when available. If missing/zero but Interaction rows exist, use Interaction
    # counts and backfill Post.views so dashboard shows correct sums.
    for p in posts_qs:
        stored_views = getattr(p, "views", None)
        if stored_views and stored_views > 0:
            views = stored_views
        else:
            views = Interaction.objects.filter(
                content_type=post_ct, object_id=p.id, action__iexact="view"
            ).count()
            # Backfill into Post.views if we found interactions but stored_views is empty/zero
            if views > 0 and (not stored_views or stored_views == 0):
                try:
                    Post.objects.filter(pk=p.id).update(views=views)
                except Exception:
                    # non-fatal if update fails (DB permission or race)
                    pass

        post_stats.append(
            {
                "id": p.id,
                "title": p.title,
                "created": p.created,
                "like_count": getattr(p, "like_count", 0),
                "views": views,
            }
        )

    # Overview totals: prefer stored Post.views (backfilled above), fallback to Interaction counts
    total_views = sum([ps["views"] for ps in post_stats]) if post_stats else 0
    total_likes = sum([getattr(p, "like_count", 0) for p in posts_qs])
    if total_likes == 0 and post_ids:
        total_likes = Interaction.objects.filter(
            content_type=post_ct, object_id__in=post_ids, action__iexact="like"
        ).count()

    followers_count = 0
    try:
        followers_count = user.followers.count()
    except Exception:
        followers_count = 0

    # Build three timeseries: last 30 days (daily), last 7 days (daily), today (hourly)
    now = timezone.now()

    def build_date_series(days_back):
        since_d = now - timedelta(days=days_back)
        agg_qs_d = Interaction.objects.filter(
            content_type=post_ct,
            object_id__in=post_ids,
            created_at__gte=since_d,
            action__in=["view", "like"],
        )
        agg_d = (
            agg_qs_d.annotate(date=TruncDate("created_at"))
            .values("date", "action")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        labels_d = []
        counts_by_date_d = {}
        for i in range(days_back + 1):
            day = (now - timedelta(days=(days_back - i))).date()
            labels_d.append(day.isoformat())
            counts_by_date_d[day.isoformat()] = {"view": 0, "like": 0}

        for row in agg_d:
            d = row["date"].isoformat()
            a = row["action"].lower()
            counts_by_date_d.setdefault(d, {"view": 0, "like": 0})
            counts_by_date_d[d][a] = row["count"]

        views_d = [counts_by_date_d[d]["view"] for d in labels_d]
        likes_d = [counts_by_date_d[d]["like"] for d in labels_d]

        return labels_d, views_d, likes_d

    # 30-day series
    labels_30, views_30, likes_30 = build_date_series(30)
    # 7-day series
    labels_7, views_7, likes_7 = build_date_series(7)

    # Hourly today series (last 24 hours grouped by hour)
    since_h = now - timedelta(hours=23)
    agg_h = Interaction.objects.filter(
        content_type=post_ct,
        object_id__in=post_ids,
        created_at__gte=since_h,
        action__in=["view", "like"],
    )
    agg_h = (
        agg_h.annotate(hour=TruncHour("created_at"))
        .values("hour", "action")
        .annotate(count=Count("id"))
        .order_by("hour")
    )

    labels_24 = []
    counts_by_hour = {}
    
    # Build 24-hour buckets with consistent timezone handling
    for i in range(24):
        h = (now - timedelta(hours=(23 - i))).replace(minute=0, second=0, microsecond=0)
        labels_24.append(h.strftime("%H:00"))
        # Store by hour start key (use isoformat for consistent matching)
        counts_by_hour[h.isoformat()] = {"view": 0, "like": 0}

    # Populate counts from database aggregation
    for row in agg_h:
        try:
            h_dt = row["hour"]
            # Normalize hour to start of hour for consistent matching
            h_normalized = h_dt.replace(minute=0, second=0, microsecond=0)
            h_iso = h_normalized.isoformat()
        except Exception:
            continue
        a = row["action"].lower()
        counts_by_hour.setdefault(h_iso, {"view": 0, "like": 0})
        counts_by_hour[h_iso][a] = row["count"]

    # Build views/likes arrays in chronological order
    views_24 = []
    likes_24 = []
    for i in range(24):
        h = (now - timedelta(hours=(23 - i))).replace(minute=0, second=0, microsecond=0)
        h_iso = h.isoformat()
        found = counts_by_hour.get(h_iso, {"view": 0, "like": 0})
        views_24.append(found["view"])
        likes_24.append(found["like"])

    # Fallback: if daily/hourly timeseries are empty but totals exist, place totals on last bucket
    if sum(views_30) == 0 and total_views > 0:
        views_30 = [0] * (len(labels_30) - 1) + [total_views]
    if sum(likes_30) == 0 and total_likes > 0:
        likes_30 = [0] * (len(labels_30) - 1) + [total_likes]

    if sum(views_7) == 0 and total_views > 0:
        views_7 = [0] * (len(labels_7) - 1) + [total_views]
    if sum(likes_7) == 0 and total_likes > 0:
        likes_7 = [0] * (len(labels_7) - 1) + [total_likes]

    if sum(views_24) == 0 and total_views > 0:
        views_24 = [0] * (len(labels_24) - 1) + [total_views]
    if sum(likes_24) == 0 and total_likes > 0:
        likes_24 = [0] * (len(labels_24) - 1) + [total_likes]

    # (Old single-series fallbacks removed — we use per-timeframe fallbacks above.)

    # Placeholder revenue data (to be connected to real payments later)
    earnings = {
        "period": "last_30_days",
        "amount": 0.0,
    }

    context = {
        "posts": post_stats,
        "user": user,
        "overview": {
            "total_views": total_views,
            "total_likes": total_likes,
            "followers_count": followers_count,
            "earnings": earnings,
        },
        "trend_labels_30": labels_30,
        "trend_views_30": views_30,
        "trend_likes_30": likes_30,
        "trend_labels_7": labels_7,
        "trend_views_7": views_7,
        "trend_likes_7": likes_7,
        "trend_labels_24": labels_24,
        "trend_views_24": views_24,
        "trend_likes_24": likes_24,
    }

    return render(request, "accounts/creator_dashboard.html", context)


@login_required
def post_analytics_api(request, post_id):
    """Return JSON timeseries for views and likes for the given post (owner-only).

    Query params:
    - days (optional): number of days back to include (default 30)
    """
    # Ensure the post exists and belongs to the requesting user
    post = get_object_or_404(Post, id=post_id, author=request.user)

    try:
        days = int(request.GET.get("days", 30))
    except Exception:
        days = 30

    since = timezone.now() - timedelta(days=days)
    post_ct = ContentType.objects.get_for_model(Post)

    qs = Interaction.objects.filter(
        content_type=post_ct,
        object_id=post.id,
        created_at__gte=since,
        action__in=["view", "like"],
    )
    # Annotate by date and action
    agg = (
        qs.annotate(date=TruncDate("created_at"))
        .values("date", "action")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # Build date range labels
    labels = []
    counts_by_date = {}
    for i in range(days + 1):
        day = (timezone.now() - timedelta(days=(days - i))).date()
        labels.append(day.isoformat())
        counts_by_date[day.isoformat()] = {"view": 0, "like": 0}

    for row in agg:
        d = row["date"].isoformat()
        a = row["action"].lower()
        counts_by_date.setdefault(d, {"view": 0, "like": 0})
        counts_by_date[d][a] = row["count"]

    views = [counts_by_date[d]["view"] for d in labels]
    likes = [counts_by_date[d]["like"] for d in labels]

    # If the timeseries is empty but the Post has stored totals, show those as the last datapoint
    try:
        post_total_views = getattr(post, "views", 0)
    except Exception:
        post_total_views = 0
    try:
        post_total_likes = post.likes.count() if hasattr(post, "likes") else 0
    except Exception:
        post_total_likes = 0

    if sum(views) == 0 and post_total_views > 0:
        views = [0] * (len(labels) - 1) + [post_total_views]
    if sum(likes) == 0 and post_total_likes > 0:
        likes = [0] * (len(labels) - 1) + [post_total_likes]

    return JsonResponse(
        {
            "labels": labels,
            "views": views,
            "likes": likes,
            "post": {"id": post.id, "title": post.title},
        }
    )


@login_required
def appearance_view(request):
    """Allow users to set appearance: light, dark, system."""
    user = request.user
    if request.method == "POST":
        # Accept form-encoded or JSON body or AJAX fetch
        theme = "light"
        accent = None
        font_size = None
        try:
            # form-encoded
            theme = request.POST.get("theme") or theme
            accent = request.POST.get("accent_color") or None
            font_size = request.POST.get("font_size") or None
        except Exception:
            pass
        # try JSON
        try:
            if request.body:
                body = json.loads(request.body)
                theme = body.get("theme", theme)
                accent = body.get("accent_color", accent)
                font_size = body.get("font_size", font_size)
        except Exception:
            pass

        if theme not in ["light", "dark", "system"]:
            theme = "light"

        user.theme_preference = theme
        # validate accent hex-ish (basic) and font_size numeric
        if accent:
            try:
                if isinstance(accent, str) and accent.startswith("#") and 4 <= len(accent) <= 9:
                    user.accent_color = accent
            except Exception:
                pass
        if font_size:
            try:
                fs = int(font_size)
                if 10 <= fs <= 24:
                    user.font_size = fs
            except Exception:
                pass

        user.save()

        # If AJAX request, return JSON to avoid redirecting the client-side fetch
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or request.content_type == "application/json"
        ):
            return JsonResponse({"success": True, "theme": theme, "accent_color": user.accent_color, "font_size": user.font_size})

        return redirect("account_dashboard")

    return render(request, "accounts/appearance.html", {})


@login_required
def creator_chat_api(request):
    """Intelligent creator-facing chatbot API with admin commands, typo tolerance, and analytics.

    POST JSON: {"message": "..."}
    Response: {"reply": "...", "type": "text|metric|command", "action": "optional command data"}
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        message = (data.get("message") or "").strip()
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    user = request.user
    msg_lower = message.lower()
    reply = None
    reply_type = "text"
    action = None  # For dashboard commands

    # Import difflib for fuzzy matching (typo tolerance)
    from difflib import SequenceMatcher

    def similarity_score(a, b):
        """Return similarity score between 0-1"""
        return SequenceMatcher(None, a, b).ratio()

    def fuzzy_match(text, keywords, threshold=0.7):
        """Find keyword match with typo tolerance - handles both single and multi-word"""
        text_lower = text.lower()

        # Exact match first (highest priority)
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True

        # Fuzzy match for multi-word phrases - check if words are close enough
        for keyword in keywords:
            kw_words = keyword.lower().split()
            if len(kw_words) > 1:
                # For multi-word keywords, check if any 2+ words match the phrase
                text_words = text_lower.split()
                for i in range(len(text_words) - len(kw_words) + 1):
                    match_count = 0
                    for j, kw_word in enumerate(kw_words):
                        if similarity_score(text_words[i + j], kw_word) >= threshold:
                            match_count += 1
                    if match_count >= len(kw_words) - 1:  # Allow 1 word difference
                        return True
            else:
                # Single word - do word-by-word fuzzy match
                for word in text_lower.split():
                    if similarity_score(word, keyword.lower()) >= threshold:
                        return True

        return False

    # Helper: compute creator metrics on-the-fly
    def get_creator_metrics():
        posts_qs = (
            Post.objects.filter(author=user)
            .annotate(like_count=Count("likes"))
            .order_by("-created")
        )
        post_ids = list(posts_qs.values_list("id", flat=True))
        post_ct = ContentType.objects.get_for_model(Post)

        total_views = 0
        total_likes = (
            sum([getattr(p, "like_count", 0) for p in posts_qs]) if post_ids else 0
        )
        if post_ids:
            total_views = Interaction.objects.filter(
                content_type=post_ct, object_id__in=post_ids, action__iexact="view"
            ).count()
            if total_likes == 0:
                total_likes = Interaction.objects.filter(
                    content_type=post_ct, object_id__in=post_ids, action__iexact="like"
                ).count()

        followers = user.followers.count() if hasattr(user, "followers") else 0
        return {
            "total_views": total_views,
            "total_likes": total_likes,
            "followers": followers,
            "posts_count": posts_qs.count(),
            "avg_engagement": (
                round((total_likes / max(total_views, 1)) * 100, 1)
                if total_views > 0
                else 0
            ),
        }

    # Intent matching with flexible natural language understanding
    try:
        # ========== ADMIN/DASHBOARD COMMANDS ==========

        # CONFIRM DELETE (explicit confirmation required)
        m = re.search(r"confirm\s+delete\s+(\d+)", msg_lower)
        if m:
            post_id = int(m.group(1))
            try:
                post_to_delete = Post.objects.get(pk=post_id)
                # only allow author or staff to delete
                if post_to_delete.author == user or getattr(user, "is_staff", False):
                    title = post_to_delete.title
                    post_to_delete.delete()
                    reply = f"✅ Deleted post '{title}' (id={post_id}). It has been removed from your account."
                    reply_type = "metric"
                else:
                    reply = "🚫 You don't have permission to delete that post. Only the author or staff can delete posts."
            except Post.DoesNotExist:
                reply = f"❓ I couldn't find a post with id {post_id}. Check the id and try again."
            # stop further processing
            return JsonResponse({"reply": reply, "type": reply_type})

        # CREATE NEW POST COMMAND
        # Make detection stricter: require both a creation verb and the word 'post' (helps avoid
        # false positives when other post-related commands like 'post analytics' or
        # 'delete post' are used). Also raise fuzzy-match threshold for the verb match.
        if "post" in msg_lower and fuzzy_match(
            msg_lower,
            [
                "create",
                "new",
                "write",
                "make",
                "start",
                "compose",
                "composte",
                "crate",
                "creat",
            ],
            threshold=0.75,
        ):
            reply = "✍️ Opening Create Post form for you! Start crafting your next masterpiece 🚀"
            reply_type = "command"
            action = "open_create_post"

        # EDIT/MODIFY POST COMMAND (editing via the bot is disabled)
        elif fuzzy_match(
            msg_lower,
            [
                "edit post",
                "modify post",
                "update post",
                "change post",
                "redit",
                "edti",
                "udpate",
            ],
        ):
            reply = "✏️ I can't modify your posts automatically. You can edit posts yourself in the Content Management area. I can open the Create Post form, or show a post's details for you to edit manually."

        # DELETE POST COMMAND (requires explicit confirmation)
        elif fuzzy_match(
            msg_lower, ["delete post", "remove post", "trash post", "delet", "remov"]
        ):
            # If user supplied an id, prompt for confirmation; otherwise list recent posts and instruct how to confirm
            nums = re.findall(r"\d+", msg_lower)
            if nums:
                post_id = int(nums[0])
                try:
                    p = Post.objects.get(pk=post_id, author=user)
                    reply = f"⚠️ You're about to delete '{p.title}' (id={post_id}). If you're sure, type: 'confirm delete {post_id}' to permanently remove it."
                except Post.DoesNotExist:
                    reply = f"I couldn't find a post with id {post_id} that you own. Check the id and try again."
            else:
                posts_qs = Post.objects.filter(author=user).order_by("-created")[:5]
                if posts_qs:
                    lines = [
                        f"{p.id}: '{p.title}' ({p.views or 0} views)" for p in posts_qs
                    ]
                    reply = (
                        "⚠️ Which post would you like to delete? Reply with the id. Example: 'delete post 123' or once you're sure type: 'confirm delete 123'\n\nYour recent posts:\n"
                        + "\n".join(lines)
                    )
                else:
                    reply = "📝 You don't have any posts to delete. Create one and then you can delete it later if needed."

        # SCHEDULE POST COMMAND
        elif fuzzy_match(
            msg_lower,
            ["schedule post", "publish later", "scheduled post", "shcedule", "publsh"],
        ):
            reply = "📅 Great idea! You can schedule posts from the Create Post form. Set your preferred date and time, and I'll help it go live at the perfect moment! ⏰"

        # VIEW SPECIFIC POST INFO
        elif fuzzy_match(
            msg_lower,
            [
                "show post",
                "tell me about post",
                "post details",
                "post info",
                "which post",
                "what about post",
            ],
        ):
            posts_qs = (
                Post.objects.filter(author=user)
                .annotate(like_count=Count("likes"))
                .order_by("-created")
            )
            if posts_qs.exists():
                # Get top 3 posts for quick selection
                top3 = sorted(
                    posts_qs[:5],
                    key=lambda p: getattr(p, "like_count", 0),
                    reverse=True,
                )[:3]
                lines = [
                    f"• '{p.title}' ({getattr(p, 'like_count', 0)} likes, {p.views or 0} views)"
                    for p in top3
                ]
                reply = (
                    "📌 Your top posts:\n"
                    + "\n".join(lines)
                    + "\n\nWhich one would you like to know more about? Just say its title!"
                )
                reply_type = "metric"
            else:
                reply = "📝 You haven't created any posts yet! Let's change that. Say 'create post' to get started!"

        # BULK UPLOAD COMMAND
        elif fuzzy_match(
            msg_lower,
            [
                "bulk upload",
                "upload multiple",
                "batch upload",
                "upload posts",
                "upoad",
                "bulkupload",
            ],
        ):
            reply = "📤 Bulk Upload is coming soon! For now, you can create posts one at a time. Want to create your next post? Say 'create post'!"

        # PUBLISH/GO LIVE COMMAND
        elif fuzzy_match(
            msg_lower,
            [
                "publish",
                "go live",
                "post now",
                "make live",
                "publish",
                "publsh",
                "go live now",
            ],
        ):
            posts_qs = Post.objects.filter(author=user, published=False).order_by(
                "-created"
            )
            if posts_qs.exists():
                draft = posts_qs.first()
                draft.published = True
                draft.save()
                reply = f"🎉 Published! '{draft.title}' is now live for your audience to see! Go creators go! 🚀"
                reply_type = "metric"
            else:
                reply = "✅ All your posts are already published! Or you don't have any drafts. Want to create a new one? Say 'create post'!"

        # ANALYTICS FOR SPECIFIC POST
        elif fuzzy_match(
            msg_lower,
            [
                "post analytics",
                "post performance",
                "how did post do",
                "post stats",
                "analtyics",
                "perfomance",
            ],
        ):
            posts_qs = (
                Post.objects.filter(author=user)
                .annotate(like_count=Count("likes"))
                .order_by("-created")
            )
            top = sorted(
                posts_qs, key=lambda p: getattr(p, "like_count", 0), reverse=True
            )[:1]
            if top:
                post = top[0]
                reply = f"📊 Your top post analytics:\n📌 Title: '{post.title}'\n👁️ Views: {post.views or 0}\n❤️ Likes: {getattr(post, 'like_count', 0)}\n💬 Comments: {post.comments.count()}\n\nSay 'open analytics' to see detailed graphs!"
                reply_type = "metric"
            else:
                reply = "📊 No posts yet! Create your first post to see analytics. Say 'create post'!"

        # OPEN DASHBOARD/NAVIGATION
        elif fuzzy_match(
            msg_lower,
            [
                "open dashboard",
                "show dashboard",
                "navigate",
                "dashboard",
                "go to",
                "dashbaord",
                "go dashbaord",
            ],
        ):
            reply = "📊 Refreshing your creator dashboard! All your stats, posts, and analytics are right here. Check out your performance summary! 💪"
            reply_type = "command"
            action = "refresh_dashboard"

        # DRAFT MANAGEMENT
        elif fuzzy_match(
            msg_lower,
            [
                "drafts",
                "my drafts",
                "saved drafts",
                "unpublished",
                "show drafts",
                "draftts",
            ],
        ):
            posts_qs = Post.objects.filter(author=user, published=False)
            if posts_qs.exists():
                lines = [
                    f"📝 {i+1}. '{p.title}' (saved {p.created.strftime('%b %d')})"
                    for i, p in enumerate(posts_qs[:5])
                ]
                reply = (
                    "✏️ Your drafts:\n"
                    + "\n".join(lines)
                    + "\n\nSay 'edit post' to continue working on one!"
                )
                reply_type = "metric"
            else:
                reply = "✅ No drafts! All your posts are published. Want to create a new one? Say 'create post'!"

        # BRAINSTORM / IDEA GENERATION
        elif fuzzy_match(
            msg_lower,
            [
                "brainstorm",
                "ideas",
                "brain storm",
                "idea",
                "help me brainstorm",
                "idea for",
                "content ideas",
            ],
        ):
            # Simple idea generator using user's top tags and recent titles
            posts_qs = Post.objects.filter(author=user).order_by("-created")[:20]
            # collect tags
            tag_names = []
            for p in posts_qs:
                for t in getattr(p, "tags", []).all() if hasattr(p, "tags") else []:
                    tag_names.append(t.name)
            tag_counts = {}
            for t in tag_names:
                tag_counts[t] = tag_counts.get(t, 0) + 1
            top_tags = sorted(tag_counts, key=lambda k: tag_counts[k], reverse=True)[:3]

            ideas = []
            if top_tags:
                for tag in top_tags:
                    ideas.append(
                        f"Make a short tutorial about '{tag}' with 3 quick tips and a CTA to follow."
                    )
                    ideas.append(
                        f"Share a 'behind the scenes' post showing how you use {tag} in your workflow."
                    )
            # fallback ideas based on recent titles
            titles = [p.title for p in posts_qs][:5]
            if titles:
                ideas.append(
                    f"Turn '{titles[0]}' into a short series of 3 posts that dive deeper into the topic."
                )
            ideas.extend(
                [
                    "Compile a top-5 lessons learned post from your last 10 creations.",
                    "Ask your audience a question related to your niche and turn responses into content.",
                ]
            )
            reply = "💡 Brainstorm Ideas:\n" + "\n".join([f"- {i}" for i in ideas[:6]])
            reply_type = "text"

        # ========== CONVERSATIONAL GREETINGS & CASUAL TALK ==========

        # CONVERSATIONAL GREETINGS & CASUAL TALK
        elif any(
            w in msg_lower
            for w in [
                "hello",
                "hi",
                "hey",
                "greetings",
                "yo",
                "what's up",
                "sup",
                "howdy",
            ]
        ):
            reply = f"👋 Hey {user.username}! Welcome back! I'm your AI creative assistant. What can I help you with today?"

        # How are you / feeling queries
        elif any(
            w in msg_lower
            for w in [
                "how are you",
                "how's it going",
                "how you doing",
                "you okay",
                "how are things",
            ]
        ):
            reply = "😊 I'm doing great, thanks for asking! More importantly, how's your creator journey going? Want me to check your stats or give you some tips?"

        # Thanks/gratitude
        elif any(
            w in msg_lower
            for w in ["thanks", "thank you", "appreciate", "cheers", "nice one", "cool"]
        ):
            reply = "🙏 You're welcome! I'm here to help you succeed. Keep crushing those creator goals! 💪"

        # What's your name / Who are you
        elif any(
            w in msg_lower
            for w in ["who are you", "what's your name", "your name", "what are you"]
        ):
            reply = "🤖 I'm your AI Creator Assistant, here to help you crush your content goals! I can analyze your stats, suggest growth strategies, and answer any creator questions. What would you like to know?"

        # Good morning / Good night / Time-based greetings
        elif any(
            w in msg_lower
            for w in [
                "good morning",
                "good night",
                "good evening",
                "good afternoon",
                "morning",
                "night",
            ]
        ):
            reply = "☀️ Good vibes! Hope you're having an awesome day. Want to check your dashboard stats or get some content ideas?"

        # Compliments/positive words
        elif any(
            w in msg_lower
            for w in [
                "awesome",
                "great",
                "amazing",
                "cool",
                "love it",
                "nice",
                "excellent",
                "brilliant",
                "wonderful",
            ]
        ):
            reply = "🌟 You're amazing! That positive energy is what creators need. Let's keep that momentum going! Need help with anything?"

        # Sad/negative feelings
        elif any(
            w in msg_lower
            for w in [
                "sad",
                "bad",
                "terrible",
                "hate",
                "frustrated",
                "angry",
                "depressed",
                "bored",
            ]
        ):
            reply = "💙 I sense some frustration. Don't worry! Let's turn this around. Maybe we can find what's working with your content, celebrate small wins, or strategize your next big move. Want to see your stats?"

        # Confused / Need clarification
        elif any(
            w in msg_lower
            for w in ["confused", "don't understand", "huh", "what", "explain", "lost"]
        ):
            reply = "🤔 Let me clarify! I can help you with:\n• 📊 Your views, likes, and engagement stats\n• 🔥 Your top performing posts\n• 💡 Growth strategies & content ideas\n• 📅 Best posting times\n• 🏷️ Hashtag strategies\n• 💰 Monetization info\n\nJust ask me anything about your creator journey!"

        # Jokes / Laughter
        elif any(
            w in msg_lower for w in ["haha", "hehe", "lol", "joke", "funny", "laugh"]
        ):
            replies = [
                "😂 I love the energy! Why did the content creator go to the gym? To get more engagement! 💪",
                "😄 Haha! You're fun. But seriously, let's get your views pumped up instead! 📈",
                "🤣 Good one! You should use that humor in your content—it gets amazing engagement!",
                "😊 You've got a great sense of humor. Keep that energy in your posts—audiences love it!",
            ]
            reply = random.choice(replies)

        # Motivational / Encouragement
        elif any(
            w in msg_lower
            for w in [
                "can i",
                "will i",
                "should i",
                "am i ready",
                "believe",
                "motivat",
                "encourage",
                "support",
            ]
        ):
            reply = "💪 YES! Absolutely! You've got this! Every creator starts somewhere. Success comes from consistency and persistence. Let me help you build momentum:\n• Check your growth metrics\n• Find your trending content\n• Get personalized growth tips\n\nYou're doing amazing! 🌟"

        # Money/earnings query
        elif any(
            w in msg_lower
            for w in [
                "money",
                "earn",
                "revenue",
                "income",
                "money making",
                "how much",
                "make",
                "cash",
                "payment",
            ]
        ):
            if "money" in msg_lower or "earn" in msg_lower or "revenue" in msg_lower:
                reply = "💰 Your earnings dashboard is coming soon! For now, all monetization features are in development. Keep creating great content — you'll be able to earn through ads, subscriptions, and tips.\n\nTip: Focus on engagement metrics (likes, comments) to prepare for monetization."
                reply_type = "metric"

        # Views/performance query
        elif any(
            w in msg_lower
            for w in [
                "views",
                "how many",
                "performance",
                "reach",
                "impressions",
                "traffic",
                "visitors",
            ]
        ):
            metrics = get_creator_metrics()
            reply = f"📊 Your Performance Summary (all-time):\n• Total Views: {metrics['total_views']:,}\n• Total Likes: {metrics['total_likes']:,}\n• Followers: {metrics['followers']:,}\n• Posts: {metrics['posts_count']}\n• Engagement Rate: {metrics['avg_engagement']}%"
            reply_type = "metric"

        # Top posts/best content
        elif any(
            w in msg_lower
            for w in [
                "top post",
                "best post",
                "top content",
                "viral",
                "perform",
                "popular",
                "trending",
                "hot",
            ]
        ):
            posts_qs = (
                Post.objects.filter(author=user)
                .annotate(like_count=Count("likes"))
                .order_by("-created")
            )
            top = sorted(
                posts_qs, key=lambda p: getattr(p, "like_count", 0), reverse=True
            )[:5]
            if top:
                lines = [
                    f"#{i+1} {p.title} ({getattr(p, 'like_count', 0)} likes)"
                    for i, p in enumerate(top)
                ]
                reply = "🔥 Your Top Posts:\n" + "\n".join(lines)
            else:
                reply = "You don't have any posts yet. Start creating to see your top performing content!"
            reply_type = "metric"

        # Suggestions/growth strategies
        elif any(
            w in msg_lower
            for w in [
                "suggest",
                "ideas",
                "what should",
                "grow",
                "help me",
                "tips",
                "strategy",
                "improve",
                "better",
            ]
        ):
            metrics = get_creator_metrics()
            if metrics["posts_count"] == 0:
                reply = "💡 Growth Strategy: Start by creating your first post! Use trending topics and high-quality visuals to attract your first audience."
            elif metrics["avg_engagement"] < 2:
                reply = f"💡 Your engagement is at {metrics['avg_engagement']}%. Try:\n• Use engaging headlines\n• Ask questions in captions\n• Post consistently (3-5x/week)\n• Engage with other creators' content"
            else:
                reply = f"💡 Great engagement ({metrics['avg_engagement']}%)! Next steps:\n• Repurpose top posts into different formats\n• Collaborate with other creators\n• Go live to interact with followers\n• Use trending sounds/hashtags"
            reply_type = "metric"

        # Content calendar/scheduling
        elif any(
            w in msg_lower
            for w in [
                "schedule",
                "calendar",
                "plan",
                "post frequency",
                "when should",
                "best time",
                "timing",
            ]
        ):
            reply = "📅 Content Planning Tips:\n• Best posting times: Tuesday-Thursday, 9am-3pm\n• Frequency: 3-5 posts per week for growth\n• Consistency > perfection — pick a schedule you can maintain\n• Plan 2 weeks ahead to stay consistent"

        # Hashtags/SEO
        elif any(
            w in msg_lower
            for w in [
                "hashtag",
                "seo",
                "discover",
                "trending",
                "tag",
                "keyword",
                "rank",
            ]
        ):
            reply = "🏷️ Hashtag Strategy:\n• Mix popular (1M+) and niche (10K-100K) hashtags\n• Use 10-20 relevant hashtags per post\n• Put best tags in first line\n• Create a branded hashtag for your community\n• Check what trending creators in your niche use"

        # Analytics/insights
        elif any(
            w in msg_lower
            for w in [
                "analytic",
                "insight",
                "stat",
                "data",
                "metric",
                "report",
                "dashboard",
            ]
        ):
            metrics = get_creator_metrics()
            reply = f"📈 Your Creator Stats:\n• Views: {metrics['total_views']:,} (all-time)\n• Engagement: {metrics['avg_engagement']}% avg\n• Audience: {metrics['followers']} followers\n• Content: {metrics['posts_count']} posts\n\nTip: Post during peak times to maximize reach!"
            reply_type = "metric"

        # Explicit 'what can you do' handler (typo-tolerant)
        elif (
            all(x in msg_lower for x in ["what", "can", "do"])
            and any(x in msg_lower for x in ["you", "u", "ya"])
        ) or re.search(r"what\s+cna|what\s+can\s+u|what\s+cn\s+u", msg_lower):
            reply = (
                "🤖 I can help with these things:\n\n"
                "✍️ CONTENT CREATION:\n"
                "• 'Create post' - Start writing new content\n"
                "• 'Edit post' - Open a post for manual editing\n"
                "• 'Show my drafts' - View unsaved posts\n"
                "• 'Publish' - Make a draft live\n\n"
                "📊 ANALYTICS & INSIGHTS:\n"
                "• 'Show my stats' - Full performance overview\n"
                "• 'Top posts' - Your best performing content\n"
                "• 'Post analytics' - Detailed post performance\n"
                "• 'How many views?' - Quick view count\n\n"
                "💡 GROWTH & STRATEGY:\n"
                "• 'How can I grow?' - Personalized tips\n"
                "• 'Best hashtags?' - Hashtag recommendations\n"
                "• 'When should I post?' - Optimal posting times\n\n"
                "🛠 ADMIN TOOLS:\n"
                "• 'Delete post <id>' - Remove a post (you must confirm)\n"
                "• 'Show drafts' - Manage drafts and continue editing\n\n"
                "Tip: If you want this list again, just type: 'what can u do' (I handle typos)."
            )

        # General help/commands
        elif any(
            w in msg_lower
            for w in [
                "help",
                "command",
                "what can",
                "how do i",
                "how to",
                "guide",
                "tutorial",
            ]
        ):
            reply = "🤖 Here's what I can do for you:\n\n✍️ CONTENT CREATION:\n• 'Create post' - Start writing new content\n• 'Edit post' - Modify your latest post\n• 'Show my drafts' - View unsaved posts\n• 'Publish' - Make a draft live\n\n📊 ANALYTICS & INSIGHTS:\n• 'Show my stats' - Full performance overview\n• 'Top posts' - Your best performing content\n• 'Post analytics' - Detailed post performance\n• 'How many views?' - Quick view count\n\n💡 GROWTH & STRATEGY:\n• 'How can I grow?' - Personalized tips\n• 'Best hashtags?' - Hashtag recommendations\n• 'When should I post?' - Optimal posting times\n\n💰 OTHER:\n• 'Am I making money?' - Monetization status\n• 'Dashboard' - Refresh dashboard\n\nJust ask me anything about creating, growing, or analyzing your content! (I forgive typos too 😊)"

        # Bye/Goodbye
        elif any(
            w in msg_lower
            for w in ["bye", "goodbye", "see you", "later", "farewell", "peace", "cya"]
        ):
            reply = "👋 See you later! Keep creating amazing content. I'll be here whenever you need stats, tips, or motivation. Catch you soon! 🚀"

        # Default fallback - but still friendly
        else:
            friendly_replies = [
                "🤖 Interesting! I understand you're asking about '{}'. Here's what I can help with: your creator stats, top posts, growth tips, hashtag strategy, posting schedules, or monetization info. What would help you most?".format(message),
                "💭 I'm not entirely sure about '{}', but I'm learning! Want me to show you your views? Or maybe some growth strategies?".format(message),
                "🤔 That's a creative question! While I'm still learning about that, I'm definitely great at: 📊 stats, 🔥 top posts, 💡 growth tips, 🏷️ hashtags, and 📅 scheduling. Pick one!",
                "😊 I love your curiosity! For now, my superpowers are creator analytics and growth strategies. Want to dive into those, or ask me something else?",
            ]
            reply = random.choice(friendly_replies)

    except Exception as e:
        reply = f"Oops, I hit a snag: {str(e)[:50]}. Try asking about your views or top posts."

    response = {"reply": reply or "I'm here to help!", "type": reply_type}
    if action:
        response["action"] = action

    return JsonResponse(response)


# -------------------------------
# GOOGLE OAUTH LOGIN VIEW
# -------------------------------
def google_login_view(request):
    """Display Google OAuth login page with setup instructions if needed."""
    from allauth.socialaccount.models import SocialApp

    # Check if Google OAuth app is configured
    try:
        google_app = SocialApp.objects.get(provider="google")
        client_id = (google_app.client_id or "").strip()
        secret = (google_app.secret or "").strip()

        # In development, check for placeholder credentials
        if not client_id or not secret:
            google_configured = False
            google_invalid = True
        elif "PLACEHOLDER" in client_id.upper():
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
        "google_configured": google_configured,
        "google_invalid": google_invalid,
    }

    return render(request, "accounts/google_login.html", context)


# --------------------------------
# CHAT VIEWS
# --------------------------------

# moved imports to top to avoid E402 / redefinition issues


@login_required
def send_message_view(request):
    """Send a direct message to another user"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    # message handling
    try:
        data = json.loads(request.body)
        recipient_id = data.get("recipient_id")
        content = data.get("content", "")

        # basic existence checks
        if not recipient_id:
            return JsonResponse({"error": "Missing recipient_id"}, status=400)

        recipient = get_object_or_404(User, id=recipient_id)

        # Respect recipient DM settings and blocking
        if recipient.id != request.user.id:
            if not getattr(recipient, "allow_dms", True):
                return JsonResponse(
                    {"error": "Recipient does not accept direct messages"}, status=403
                )
            try:
                # If recipient has blocked the sender, disallow sending
                if request.user.id in list(
                    recipient.blocked_users.values_list("id", flat=True)
                ):
                    return JsonResponse(
                        {"error": "You are blocked by this user"}, status=403
                    )
            except Exception:
                pass

        # Normalize content and enforce length limits
        if content is None:
            content = ""
        # remove null bytes and trim
        content = content.replace("\x00", "").strip()
        if len(content) == 0:
            return JsonResponse({"error": "Message content is empty"}, status=400)
        if len(content) > 500:
            return JsonResponse({"error": "Message too long (max 500)"}, status=400)

        # Whitelist characters: disallow control characters except newline/tab
        import re

        if re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", content):
            return JsonResponse(
                {"error": "Message contains invalid characters"}, status=400
            )

        # Sanitize content: prefer bleach if available, otherwise escape
        if HAS_BLEACH:
            # allow only basic text, strip tags
            safe_content = bleach.clean(
                content, tags=[], attributes={}, styles=[], strip=True
            )
        else:
            safe_content = html_escape(content)

        # Create or get conversation
        conversation, _ = Conversation.objects.get_or_create(
            user1_id=min(request.user.id, recipient_id),
            user2_id=max(request.user.id, recipient_id),
        )

        # Create message using sanitized content
        message = DirectMessage.objects.create(
            sender=request.user, recipient=recipient, content=safe_content
        )

        # Create notification for recipient
        # Create notification with a sanitized preview (no HTML)
        preview = (
            (safe_content[:100] + ("..." if len(safe_content) > 100 else ""))
            if safe_content
            else ""
        )
        Notification.objects.create(
            user=recipient,
            notification_type="message",
            title=f"{request.user.username} sent you a message",
            message=preview,
            related_user=request.user,
        )

        # Notify recipient via channel layer (if any consumer is listening on group `user_{id}`)
        try:
            channel_layer = get_channel_layer()
            payload = {
                "type": "dm.message",
                "message": {
                    "id": message.id,
                    "sender_id": request.user.id,
                    "sender": request.user.username,
                    "recipient_id": recipient.id,
                    "recipient": recipient.username,
                    # send sanitized content only
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                    "is_read": message.is_read,
                },
            }
            async_to_sync(channel_layer.group_send)(f"user_{recipient.id}", payload)
        except Exception:
            # best-effort: ignore channel errors server-side
            pass

        return JsonResponse(
            {
                "id": message.id,
                "sender": message.sender.username,
                "recipient": message.recipient.username,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "is_read": message.is_read,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        # Print to server console for easier debugging
        print("Error in game_lobby_post_message_view:", str(e))
        print(tb)
        return JsonResponse(
            {"error": "Server error", "details": tb.splitlines()[-10:]}, status=500
        )


@login_required
def get_messages_view(request):
    """Get messages between current user and another user"""
    recipient_id = request.GET.get("recipient_id")

    if not recipient_id:
        return JsonResponse({"error": "Missing recipient_id"}, status=400)

    try:
        recipient_id = int(recipient_id)
        recipient = get_object_or_404(User, id=recipient_id)

        # Get all messages between the two users
        messages = DirectMessage.objects.filter(
            (
                models.Q(sender=request.user, recipient=recipient)
                | models.Q(sender=recipient, recipient=request.user)
            )
        ).order_by("created_at")

        # Hide messages from users the current user has blocked
        try:
            blocked_ids = list(request.user.blocked_users.values_list("id", flat=True))
            if blocked_ids:
                messages = messages.exclude(sender__id__in=blocked_ids)
        except Exception:
            # best-effort: if the relation isn't available, continue
            pass

        # Mark messages as read
        DirectMessage.objects.filter(
            sender=recipient, recipient=request.user, is_read=False
        ).update(is_read=True)

        message_list = [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "sender_id": msg.sender.id,
                "recipient": msg.recipient.username,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "is_read": msg.is_read,
            }
            for msg in messages
        ]

        return JsonResponse({"messages": message_list})
    except ValueError:
        return JsonResponse({"error": "Invalid recipient_id"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_conversations_view(request):
    """Get all conversations for the current user"""
    try:
        conversations = Conversation.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        ).order_by("-updated_at")

        conv_list = []
        for conv in conversations:
            other_user = conv.user2 if conv.user1.id == request.user.id else conv.user1
            conv_list.append(
                {
                    "id": conv.id,
                    "other_user_id": other_user.id,
                    "other_user_username": other_user.username,
                    "updated_at": conv.updated_at.isoformat(),
                }
            )

        return JsonResponse({"conversations": conv_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def notifications_page_view(request):
    """Display all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    unread_count = notifications.filter(is_read=False).count()

    context = {
        "notifications": notifications,
        "unread_count": unread_count,
    }

    return render(request, "accounts/notifications.html", context)


@login_required
def block_user_api(request):
    """API endpoint to block or unblock a user.
    POST JSON: { target_id: int, action: 'block'|'unblock' }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        target_id = int(data.get("target_id"))
        action = data.get("action")
    except Exception:
        return JsonResponse({"error": "Invalid payload"}, status=400)

    if target_id == request.user.id:
        return JsonResponse({"error": "Cannot block yourself"}, status=400)

    target = get_object_or_404(User, id=target_id)

    try:
        if action == "block":
            request.user.blocked_users.add(target)
            request.user.save()
            status = "blocked"
        elif action == "unblock":
            request.user.blocked_users.remove(target)
            request.user.save()
            status = "unblocked"
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)

        # notify both users via channel layer so UI can update instantly
        try:
            channel_layer = get_channel_layer()
            payload = {
                "action": status,
                "by_user_id": request.user.id,
                "target_user_id": target.id,
            }
            async_to_sync(channel_layer.group_send)(
                f"user_{target.id}", {"type": "user.block", "payload": payload}
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}", {"type": "user.block", "payload": payload}
            )
        except Exception:
            pass

        return JsonResponse({"success": True, "status": status})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_notifications_api(request):
    """Get recent notifications for the current user (JSON)"""
    limit = int(request.GET.get("limit", 5))
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:limit]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    notif_list = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "related_user_id": n.related_user.id if n.related_user else None,
            "related_user_username": (
                n.related_user.username if n.related_user else None
            ),
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]

    return JsonResponse(
        {
            "notifications": notif_list,
            "unread_count": unread_count,
        }
    )


@login_required
def mark_notification_read_api(request, notif_id):
    """Mark a specific notification as read"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        notification = get_object_or_404(Notification, id=notif_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def chat_page_view(request, user_id=None):
    """Display the chat page for the current user; optionally open a conversation with a specific user."""
    current_user = request.user

    # Get all conversations for the current user
    conversations = Conversation.objects.filter(
        models.Q(user1=current_user) | models.Q(user2=current_user)
    ).order_by("-updated_at")

    conv_list = []
    for conv in conversations:
        other_user = conv.user2 if conv.user1.id == current_user.id else conv.user1
        conv_list.append(
            {
                "id": conv.id,
                "other_user_id": other_user.id,
                "other_user_username": other_user.username,
                "other_user_avatar": (
                    other_user.avatar.url if other_user.avatar else None
                ),
                "updated_at": conv.updated_at.isoformat(),
            }
        )

    # Get the target user if provided
    selected_user = None
    if user_id:
        try:
            selected_user = get_object_or_404(User, id=user_id)
        except Exception:
            selected_user = None

    # determine block state between current user and selected_user
    is_blocked_by_me = False
    has_blocked_me = False
    if selected_user:
        try:
            is_blocked_by_me = selected_user.id in list(
                request.user.blocked_users.values_list("id", flat=True)
            )
            has_blocked_me = request.user.id in list(
                selected_user.blocked_users.values_list("id", flat=True)
            )
        except Exception:
            is_blocked_by_me = False
            has_blocked_me = False

    context = {
        "conversations": conv_list,
        "selected_user": selected_user,
        "selected_user_id": user_id,
        "is_blocked_by_me": is_blocked_by_me,
        "has_blocked_me": has_blocked_me,
    }

    return render(request, "accounts/chat.html", context)


# --------------------------------
# GAME LOBBY VIEWS
# --------------------------------


@login_required
def game_lobby_view(request):
    """Display the Try Not To Get Banned game lobby with chat"""
    from blog.views import banned_words

    # Check if user has active ban
    ban = (
        GameLobbyBan.objects.filter(user=request.user).order_by("-banned_until").first()
    )
    is_banned = ban and ban.is_active() if ban else False

    if is_banned:
        ban_time_remaining = int((ban.banned_until - timezone.now()).total_seconds())
    else:
        ban_time_remaining = 0

    context = {
        "banned_words": banned_words,
        "is_banned": is_banned,
        "ban_time_remaining": ban_time_remaining,
    }
    # Include Try Not To Get Banned score info (from WordListGame) and a small leaderboard
    try:
        wgame, _ = WordListGame.objects.get_or_create(user=request.user)
        context["lobby_score"] = wgame.score or 0
    except Exception:
        context["lobby_score"] = 0

    # Top 5 leaderboard (descending by score)
    try:
        top = WordListGame.objects.order_by("-score")[:5]
        leaderboard = [
            {"username": t.user.username, "score": t.score or 0} for t in top
        ]
        context["lobby_leaderboard"] = leaderboard
    except Exception:
        context["lobby_leaderboard"] = []

    return render(request, "core/game_lobby.html", context)


@login_required
def game_lobby_post_message_view(request):
    """Post a message in the game lobby and check for banned words"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        from blog.views import banned_words

        # Check if user is banned
        ban = (
            GameLobbyBan.objects.filter(user=request.user)
            .order_by("-banned_until")
            .first()
        )
        is_banned = ban and ban.is_active() if ban else False

        if is_banned:
            return JsonResponse(
                {
                    "error": "banned",
                    "ban_time_remaining": int(
                        (ban.banned_until - timezone.now()).total_seconds()
                    ),
                },
                status=403,
            )

        data = json.loads(request.body)
        # Accept both 'message' and 'content' keys for flexibility
        message_content = (data.get("content") or data.get("message") or "").strip().lower()

        if not message_content:
            return JsonResponse({"error": "Empty message"}, status=400)

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
                GameLobbyMessage.objects.create(
                    user=request.user,
                    author_name=request.user.username,
                    content=data.get("content") or data.get("message"),
                    is_system=False,
                )
                GameLobbyMessage.objects.create(
                    user=None, author_name="System", content=system_msg, is_system=True
                )
            except Exception:
                pass

            # broadcast to group
            channel_layer = get_channel_layer()
            payload_msg = {
                "author": request.user.username,
                "content": data.get("content") or data.get("message"),
                "created_at": timezone.now().isoformat(),
                "is_system": False,
            }
            system_payload = {
                "author": "System",
                "content": system_msg,
                "created_at": timezone.now().isoformat(),
                "is_system": True,
            }
            try:
                async_to_sync(channel_layer.group_send)(
                    "game_lobby", {"type": "lobby_message", "message": payload_msg}
                )
                async_to_sync(channel_layer.group_send)(
                    "game_lobby", {"type": "lobby_message", "message": system_payload}
                )
            except Exception:
                pass

            return JsonResponse(
                {
                    "error": "banned_words",
                    "banned_words_found": banned_found,
                    "ban_time_remaining": 60,
                    "chat_post": payload_msg,
                    "system_message": system_msg,
                },
                status=400,
            )
            # if we had challenge updates, include them as well (not used here)

        # Message is clean, return success
        # persist and broadcast clean message
        try:
            GameLobbyMessage.objects.create(
                user=request.user,
                author_name=request.user.username,
                content=data.get("content") or data.get("message"),
                is_system=False,
            )
        except Exception:
            pass
        try:
            channel_layer = get_channel_layer()
            payload_msg = {
                "author": request.user.username,
                "content": data.get("content") or data.get("message"),
                "created_at": timezone.now().isoformat(),
                "is_system": False,
            }
            async_to_sync(channel_layer.group_send)(
                "game_lobby", {"type": "lobby_message", "message": payload_msg}
            )
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
            challenge = (
                GameLobbyChallenge.objects.filter(user=request.user)
                .order_by("-created_at")
                .first()
            )
            if challenge and not challenge.completed:
                # Parse message into tokens; for each token that is a dictionary word,
                # collect letters present in that token that belong to the challenge.
                tokens = re.findall(r"\b[\w']+\b", data.get("content", "").lower())
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
                        "letters": challenge.letters,
                        "used_letters": challenge.used_letters,
                        "completed": challenge.completed,
                        "user": request.user.username,
                    }
                    # broadcast small system messages
                    if newly:
                        tick_msg = f"{request.user.username} found: {', '.join(newly)}"
                        GameLobbyMessage.objects.create(
                            user=None,
                            author_name="System",
                            content=tick_msg,
                            is_system=True,
                        )
                        try:
                            async_to_sync(channel_layer.group_send)(
                                "game_lobby",
                                {
                                    "type": "lobby_message",
                                    "message": {
                                        "author": "System",
                                        "content": tick_msg,
                                        "created_at": timezone.now().isoformat(),
                                        "is_system": True,
                                    },
                                },
                            )
                        except Exception:
                            pass
                    if challenge.completed:
                        # Award 20 points
                        wgame, _ = WordListGame.objects.get_or_create(user=request.user)
                        wgame.score = (wgame.score or 0) + 20
                        wgame.save()
                        sys_msg = f"{request.user.username} completed the 12-letter challenge and earned 20 points!"
                        GameLobbyMessage.objects.create(
                            user=None,
                            author_name="System",
                            content=sys_msg,
                            is_system=True,
                        )
                        try:
                            async_to_sync(channel_layer.group_send)(
                                "game_lobby",
                                {
                                    "type": "lobby_message",
                                    "message": {
                                        "author": "System",
                                        "content": sys_msg,
                                        "created_at": timezone.now().isoformat(),
                                        "is_system": True,
                                    },
                                },
                            )
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
                            GameLobbyMessage.objects.create(
                                user=None,
                                author_name="System",
                                content=new_chal_msg,
                                is_system=True,
                            )
                            try:
                                async_to_sync(channel_layer.group_send)(
                                    "game_lobby",
                                    {
                                        "type": "lobby_message",
                                        "message": {
                                            "author": "System",
                                            "content": new_chal_msg,
                                            "created_at": timezone.now().isoformat(),
                                            "is_system": True,
                                        },
                                    },
                                )
                            except Exception:
                                pass
                            # prepare challenge_update to send back to client
                            challenge_update = {
                                "letters": challenge.letters,
                                "used_letters": challenge.used_letters,
                                "completed": challenge.completed,
                                "user": request.user.username,
                            }
                        except Exception:
                            # if new challenge creation fails, leave as-is (no crash)
                            pass
        except Exception:
            challenge_update = None

        # Always return a success response for clean messages (challenge_update may be None)
        resp = {
            "success": True,
            "user": request.user.username,
            "content": data.get("content"),
            "created_at": timezone.now().isoformat(),
        }
        if challenge_update:
            resp["challenge_update"] = challenge_update
        return JsonResponse(resp)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --------------------------------
# GAMES HUB
# --------------------------------


@login_required
def games_hub_view(request):
    """Display available games"""
    games = [
        {
            "id": "try-not-to-get-banned",
            "name": "Try Not To Get Banned",
            "emoji": "🎮",
            "description": "Chat freely but watch your words!",
            "url": "game_lobby",
        }
    ]
    # Add Letter Set as a separate game entry
    games.append(
        {
            "id": "letter-set",
            "name": "Letter Set",
            "emoji": "🔤",
            "description": "Form words from a set of letters and earn points.",
            "url": "letter_set_game",
        }
    )

    return render(request, "core/games_hub.html", {"games": games})


# --------------------------------
# LETTER SET GAME
# --------------------------------


def generate_random_letters(count=15):
    """Generate `count` random distinct letters (default 15)."""
    alphabet = list(string.ascii_uppercase)
    return "".join(random.sample(alphabet, count))


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
        wordfile = base / "data" / "words.txt"
        if wordfile.exists():
            with open(wordfile, "r", encoding="utf-8") as fh:
                words = {line.strip().lower() for line in fh}
            return (w in words), True
    except Exception:
        pass

    # 3) try /usr/share/dict/words
    try:
        wf = Path("/usr/share/dict/words")
        if wf.exists():
            with open(wf, "r", encoding="utf-8") as fh:
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
@login_required
def letter_set_game_view(request):
    """Display Letter Set game"""
    # Get or create current game session
    game = (
        LetterSetGame.objects.filter(user=request.user).order_by("-updated_at").first()
    )

    if (
        not game or (timezone.now() - game.updated_at).total_seconds() > 3600
    ):  # Reset after 1 hour
        # Create new game session with random letters
        game = LetterSetGame.objects.create(
            user=request.user,
            letters=generate_random_letters(15),
            score=0,
            completed_words="",
        )

    context = {
        "game": game,
        "completed_words": game.get_completed_words_list(),
        "letters": sorted(game.letters),  # Show sorted for easier reading
    }

    return render(request, "core/letter_set_game.html", context)


@login_required
def letter_set_submit_word_view(request):
    """Submit a word in Letter Set game"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        word = data.get("word", "").strip()

        if not word or len(word) < 2:
            return JsonResponse(
                {"error": "Word must be at least 2 characters"}, status=400
            )

        # Get current game
        game = (
            LetterSetGame.objects.filter(user=request.user)
            .order_by("-updated_at")
            .first()
        )
        if not game:
            return JsonResponse({"error": "No active game session"}, status=400)

        # Check if word can be formed from available letters
        if not is_valid_word(word, game.letters):
            return JsonResponse(
                {
                    "error": "invalid_letters",
                    "message": f'The word "{word}" cannot be formed from your letters: {game.letters}',
                },
                status=400,
            )

        # Check dictionary membership
        is_dict_word, dict_available = is_dictionary_word(word)
        if not is_dict_word:
            return JsonResponse(
                {
                    "error": "not_dictionary",
                    "message": f'"{word}" is not recognized as a dictionary word.',
                    "dictionary_available": dict_available,
                },
                status=400,
            )

        # Check if word already completed
        completed = game.get_completed_words_list()
        if any(w.lower() == word.lower() for w in completed):
            return JsonResponse(
                {"error": "duplicate", "message": f'You already completed "{word}"!'},
                status=400,
            )

        # Add word
        added = game.add_word(word)
        if not added:
            return JsonResponse(
                {"error": "duplicate", "message": "Duplicate word."}, status=400
            )

        # Increment score for the submitted word
        game.score = (game.score or 0) + 1
        game.save()

        # Compute used letters based on completed words
        used_letters = set("".join(game.get_completed_words_list()).upper())
        all_letters = set(game.letters.upper())
        all_greened = used_letters >= all_letters

        response = {
            "success": True,
            "word": word,
            "score": game.score,
            "total_words": len(game.get_completed_words_list()),
            "used_letters": sorted(list(used_letters)),
            "all_greened": all_greened,
            "dictionary_available": dict_available,
            "message": f"Great! +1 point! Your score: {game.score}",
        }

        # If all letters have been used, award bonus (20 points) and generate new letters
        if all_greened:
            bonus = 20
            game.score = game.score + bonus
            new_letters = generate_random_letters(15)
            game.letters = new_letters
            game.completed_words = ""
            game.save()
            response["bonus_awarded"] = True
            response["bonus_amount"] = bonus
            response["new_letters"] = new_letters
            response["message"] = (
                f"All letters used! Bonus +{bonus} points awarded. Your score: {game.score}"
            )

        return JsonResponse(response)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def letter_set_chat_view(request):
    """Chat interface for Letter Set game"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        message_content = data.get("content", "").strip()

        if not message_content:
            return JsonResponse({"error": "Empty message"}, status=400)

        # Just return success - message is handled client-side
        return JsonResponse(
            {
                "success": True,
                "user": request.user.username,
                "content": message_content,
                "created_at": timezone.now().isoformat(),
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def letter_set_start_view(request):
    """API to start or get the current Letter Set session for the user (JSON)."""
    try:
        game = (
            LetterSetGame.objects.filter(user=request.user)
            .order_by("-updated_at")
            .first()
        )
        if not game or (timezone.now() - game.updated_at).total_seconds() > 3600:
            game = LetterSetGame.objects.create(
                user=request.user,
                letters=generate_random_letters(15),
                score=0,
                completed_words="",
            )

        return JsonResponse(
            {
                "letters": game.letters,
                "score": game.score,
                "completed_words": game.get_completed_words_list(),
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def game_lobby_challenge_start_view(request):
    """Return the user's active 12-letter lobby challenge (JSON).

    If the user has an existing not-completed challenge, return it. Otherwise
    create a new challenge and return that. This preserves progress across
    reloads.
    """
    try:
        # Try to find the most recent incomplete challenge for this user
        chal = (
            GameLobbyChallenge.objects.filter(user=request.user, completed=False)
            .order_by("-created_at")
            .first()
        )

        if not chal:
            letters = generate_random_letter_list(12)
            chal = GameLobbyChallenge.objects.create(
                user=request.user, letters=letters, used_letters=[], completed=False
            )

        return JsonResponse(
            {
                "challenge": {
                    "letters": chal.letters,
                    "used_letters": chal.used_letters,
                    "completed": chal.completed,
                }
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def game_lobby_challenge_save_view(request):
    """Save the user's current challenge progress (POST JSON).

    Expects JSON payload: {"used_letters": [...], "completed": true|false}
    Updates the user's most recent challenge (or creates one if missing).
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    used = data.get("used_letters")
    completed = data.get("completed")

    try:
        chal = (
            GameLobbyChallenge.objects.filter(user=request.user).order_by("-created_at").first()
        )
        if not chal:
            # create a fresh one if none exists
            letters = generate_random_letter_list(12)
            chal = GameLobbyChallenge.objects.create(
                user=request.user, letters=letters, used_letters=[], completed=False
            )

        if isinstance(used, list):
            chal.used_letters = used
        if isinstance(completed, bool):
            chal.completed = completed

        chal.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def generate_random_word_list(count=12):
    """Generate `count` random unique words from available dictionary sources."""
    import random
    from pathlib import Path

    # Prefer a large data/words.txt if present
    base = Path(__file__).resolve().parent.parent
    wordfile = base / "data" / "words.txt"
    words = []
    try:
        if wordfile.exists():
            with open(wordfile, "r", encoding="utf-8") as fh:
                words = [w.strip().lower() for w in fh if w.strip()]
    except Exception:
        words = []

    # fallback to small built-in wordlist if none available
    if not words:
        words = [
            "apple",
            "banana",
            "orange",
            "table",
            "chair",
            "window",
            "river",
            "mountain",
            "guitar",
            "python",
            "coffee",
            "bottle",
            "keyboard",
            "mouse",
            "monitor",
            "paper",
            "pencil",
            "flower",
            "pillow",
            "garden",
            "butter",
            "silver",
            "planet",
            "rocket",
            "ocean",
            "forest",
            "island",
            "isotope",
            "button",
            "candle",
            "painter",
            "castle",
            "driver",
            "engine",
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
