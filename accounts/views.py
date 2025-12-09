from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.core.files.base import ContentFile
import base64

from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import Subscription, CustomUser
from blog.models import Post
from communities.models import Community, CommunityPost
from django.db.models import Count

User = get_user_model()


# -------------------------------
# REGISTER
# -------------------------------
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to Lupify!")
            return redirect("dashboard_home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


# -------------------------------
# LOGIN
# -------------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

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
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


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
    author_posts = Post.objects.filter(author_id__in=author_ids)

    return render(request, "accounts/subscriptions.html", {
        "communities": communities,
        "authors": authors,
        "community_posts": community_posts,
        "author_posts": author_posts,
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

