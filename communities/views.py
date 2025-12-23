import base64
import base64
import hashlib
from collections import OrderedDict, namedtuple

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import Subscription

from .forms import CommunityForm, CommunityPostForm
from .models import (Community, CommunityPost, CommunityPostComment,
                     ModerationReport)


def _youtube_style_id(value: str) -> str:
    digest = hashlib.blake2b(value.encode("utf-8"), digest_size=6).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


# -------------------------------
# List all communities
# -------------------------------
def communities_list(request):
    communities_qs = (
        Community.objects.all()
        .annotate(member_count=Count("members", distinct=True))
        .order_by("category", "name")
    )

    membership_ids = set()
    if request.user.is_authenticated:
        membership_ids = set(
            request.user.joined_communities.values_list("id", flat=True)
        )

    CategoryMeta = namedtuple("CategoryMeta", ["slug", "name"])
    category_lookup = {}
    communities_by_category = OrderedDict()
    for slug, label in Community.CATEGORY_CHOICES:
        meta = CategoryMeta(slug=slug, name=label)
        category_lookup[slug] = meta
        communities_by_category[meta] = []

    for community in communities_qs:
        community.is_member = community.id in membership_ids
        community.image = community.community_image or community.banner_image
        meta = category_lookup.get(community.category)
        if meta:
            communities_by_category[meta].append(community)

    category_filters = [
        {"slug": meta.slug, "name": meta.name}
        for meta, entries in communities_by_category.items()
        if entries
    ]

    return render(
        request,
        "communities/communities_list.html",
        {
            "communities_by_category": communities_by_category,
            "category_filters": category_filters,
        },
    )


# -------------------------------
# Join / Leave helpers for AJAX
# -------------------------------
@login_required
@require_http_methods(["POST"])
def join_community_ajax(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    community.members.add(request.user)
    Subscription.objects.get_or_create(user=request.user, community=community)
    return JsonResponse(
        {
            "status": "success",
            "member_count": community.members.count(),
            "is_member": True,
        }
    )


@login_required
@require_http_methods(["POST"])
def leave_community_ajax(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user in community.members.all():
        community.members.remove(request.user)
        Subscription.objects.filter(user=request.user, community=community).delete()
    return JsonResponse(
        {
            "status": "success",
            "member_count": community.members.count(),
            "is_member": False,
        }
    )


# -------------------------------
# Create a new community
# -------------------------------
@login_required
def create_community(request):
    if request.method == "POST":
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user

            # Handle cropped banner/logo data if provided (base64 dataURLs)
            banner_data = request.POST.get("cropped_banner")
            logo_data = request.POST.get("cropped_logo")
            try:
                if banner_data:
                    format, imgstr = banner_data.split(";base64,")
                    ext = format.split("/")[-1]
                    data = ContentFile(
                        base64.b64decode(imgstr), name=f"{community.name}_banner.{ext}"
                    )
                    community.banner_image = data
                # if no cropped banner but file uploaded via form, form.save will handle it
                if logo_data:
                    format, imgstr = logo_data.split(";base64,")
                    ext = format.split("/")[-1]
                    data = ContentFile(
                        base64.b64decode(imgstr), name=f"{community.name}_logo.{ext}"
                    )
                    community.community_image = data
            except Exception as e:
                messages.error(request, f"Failed to process uploaded images: {e}")

            community.save()
            community.members.add(request.user)  # Auto join

            # Add subscription for this user
            Subscription.objects.get_or_create(user=request.user, community=community)

            messages.success(request, "Community created successfully.")
            return redirect("communities_list")
    else:
        form = CommunityForm()
    return render(request, "communities/create_community.html", {"form": form})


# -------------------------------
# Toggle join/leave a community
# -------------------------------
@login_required
def toggle_join_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.user in community.members.all():
        community.members.remove(request.user)
        # Remove subscription
        Subscription.objects.filter(user=request.user, community=community).delete()
    else:
        community.members.add(request.user)
        # Add subscription
        Subscription.objects.get_or_create(user=request.user, community=community)

    return redirect("communities_list")


# -------------------------------
# Community detail view
# -------------------------------
def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    posts = community.posts.all()
    members = community.members.all()
    admins = [community.creator]

    # Handle join/leave from detail page
    if request.method == "POST" and request.user.is_authenticated:
        action = request.POST.get("action")
        if action == "join":
            community.members.add(request.user)
            Subscription.objects.get_or_create(user=request.user, community=community)
        elif action == "leave":
            community.members.remove(request.user)
            Subscription.objects.filter(user=request.user, community=community).delete()
        return redirect("community_detail", community_id=community.id)

    return render(
        request,
        "communities/community_detail.html",
        {
            "community": community,
            "posts": posts,
            "members": members,
            "admins": admins,
        },
    )


# -------------------------------
# Save or unsave a community
# -------------------------------
@login_required
def save_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    user = request.user

    if community in user.saved_communities.all():
        user.saved_communities.remove(community)
        messages.success(request, "Removed from saved communities.")
    else:
        user.saved_communities.add(community)
        messages.success(request, "Saved successfully.")

    return redirect("community_detail", community_id=community.id)


# -------------------------------
# Create a community post
# -------------------------------
@login_required
def create_community_post(request, community_id=None):
    all_communities = Community.objects.all().order_by("category", "name")
    selected_community = (
        get_object_or_404(Community, id=community_id) if community_id else None
    )

    if request.method == "POST":
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            community_id_from_form = request.POST.get("community")
            post.community = get_object_or_404(Community, id=community_id_from_form)
            post.author = request.user
            post.save()
            return redirect("community_detail", community_id=post.community.id)
    else:
        form = CommunityPostForm()

    return render(
        request,
        "communities/create_community_post.html",
        {
            "form": form,
            "communities": all_communities,
            "selected_community": selected_community,
        },
    )


# -------------------------------
# Generic community post creation
# -------------------------------
@login_required
def create_community_post_generic(request):
    all_communities = Community.objects.all().order_by("category", "name")

    if request.method == "POST":
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            community_id_from_form = request.POST.get("community")
            post.community = get_object_or_404(Community, id=community_id_from_form)
            post.author = request.user
            post.save()
            return redirect("community_detail", community_id=post.community.id)
    else:
        form = CommunityPostForm()

    return render(
        request,
        "communities/create_community_post.html",
        {
            "form": form,
            "communities": all_communities,
            "selected_community": None,
        },
    )


# -------------------------------
# Community post detail
# -------------------------------
def community_post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    comments = post.comments.filter(parent__isnull=True).prefetch_related("replies")
    user_liked = request.user.is_authenticated and request.user in post.likes.all()
    user_disliked = (
        request.user.is_authenticated and request.user in post.dislikes.all()
    )
    user_following_author = False
    if request.user.is_authenticated:
        user_following_author = Subscription.objects.filter(
            user=request.user, author=post.author
        ).exists()
    return render(
        request,
        "communities/community_post_detail.html",
        {
            "post": post,
            "comments": comments,
            "likes_count": post.likes.count(),
            "dislikes_count": post.dislikes.count(),
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "user_following_author": user_following_author,
        },
    )


# -------------------------------
# Toggle like on community post
# -------------------------------
@login_required
def toggle_community_post_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(CommunityPost, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        post.dislikes.remove(user)  # Remove dislike if present
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "likes_count": post.likes.count(),
            "dislikes_count": post.dislikes.count(),
        }
    )


# -------------------------------
# Toggle dislike on community post
# -------------------------------
@login_required
def toggle_community_post_dislike(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(CommunityPost, id=post_id)
    user = request.user

    if user in post.dislikes.all():
        post.dislikes.remove(user)
        disliked = False
    else:
        post.dislikes.add(user)
        post.likes.remove(user)  # Remove like if present
        disliked = True

    return JsonResponse(
        {
            "disliked": disliked,
            "likes_count": post.likes.count(),
            "dislikes_count": post.dislikes.count(),
        }
    )


# -------------------------------
# Toggle bookmark on community post
# -------------------------------
@login_required
def toggle_community_post_bookmark(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(CommunityPost, id=post_id)
    user = request.user

    if user in post.bookmarks.all():
        post.bookmarks.remove(user)
        bookmarked = False
    else:
        post.bookmarks.add(user)
        bookmarked = True

    return JsonResponse(
        {"bookmarked": bookmarked, "bookmarks_count": post.bookmarks.count()}
    )


# -------------------------------
# Add comment to post
# -------------------------------
@login_required
def add_community_post_comment(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(CommunityPost, id=post_id)
    text = request.POST.get("text", "").strip()
    parent_id = request.POST.get("parent_id")

    if not text:
        return JsonResponse({"error": "Comment text required."}, status=400)

    parent = None
    if parent_id:
        parent = get_object_or_404(CommunityPostComment, id=parent_id)

    comment = CommunityPostComment.objects.create(
        post=post, author=request.user, text=text, parent=parent
    )

    return JsonResponse(
        {
            "id": comment.id,
            "user": comment.author.username,
            "text": comment.text,
            "created_at": comment.created_at.strftime("%b %d, %Y %I:%M %p"),
            "likes_count": 0,
            "dislikes_count": 0,
        }
    )


# -------------------------------
# Toggle like on comment
# -------------------------------
@login_required
def toggle_community_comment_like(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    comment = get_object_or_404(CommunityPostComment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        comment.dislikes.remove(user)
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "likes_count": comment.likes.count(),
            "dislikes_count": comment.dislikes.count(),
        }
    )


# -------------------------------
# Toggle dislike on comment
# -------------------------------
@login_required
def toggle_community_comment_dislike(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    comment = get_object_or_404(CommunityPostComment, id=comment_id)
    user = request.user

    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
        disliked = False
    else:
        comment.dislikes.add(user)
        comment.likes.remove(user)
        disliked = True

    return JsonResponse(
        {
            "disliked": disliked,
            "likes_count": comment.likes.count(),
            "dislikes_count": comment.dislikes.count(),
        }
    )


# -------------------------------
# Report post/comment
# -------------------------------
@login_required
def report_community_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(CommunityPost, id=post_id)
    report_type = request.POST.get("type", "other")
    description = request.POST.get("description", "").strip()

    ModerationReport.objects.create(
        post=post,
        reported_by=request.user,
        report_type=report_type,
        description=description,
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Report submitted. Thank you for keeping our community safe.",
        }
    )
