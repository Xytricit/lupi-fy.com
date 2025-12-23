# views.py
import json
import math
import os
from datetime import timedelta
from io import BytesIO

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.views.decorators.http import require_POST
from PIL import Image, ImageOps

from .forms import CommentForm, PostForm
from .models import Comment, ModerationReport, Post, PostImage, Category, Tag

# -------------------- VIEWS --------------------


def posts_list_view(request):
    posts_qs = (
        Post.objects.select_related("author", "category")
        .prefetch_related("images", "tags")
        .order_by("-created")
    )
    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    blog_posts = list(page_obj.object_list)
    for post in blog_posts:
        text = strip_tags(post.content or "")
        post.excerpt = Truncator(text).chars(220)
        word_count = len(text.split())
        post.read_time = max(1, math.ceil(word_count / 200)) if word_count else 1
        post.created_at = post.created
        first_image = post.images.first()
        post.primary_image_url = (
            first_image.image.url
            if first_image and getattr(first_image, "image", None)
            else None
        )
        primary_tag = post.tags.first()
        category_name = getattr(post.category, "name", None)
        post.primary_tag_name = primary_tag.name if primary_tag else category_name

    context = {
        "blog_posts": blog_posts,
        "has_more": page_obj.has_next(),
    }
    return render(request, "blog/blog_list.html", context)


@login_required
def create_post_view(request):

    # suspension check
    if (
        getattr(request.user, "suspended_until", None)
        and timezone.now() < request.user.suspended_until
    ):
        messages.error(request, "You are suspended and cannot post right now.")
        return redirect("blogs")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        description_value = request.POST.get("description", "").strip()
        category_input = request.POST.get("category", "").strip()

        # post saving
        if form.is_valid():
            images = request.FILES.getlist("images")
            if not images:
                message = "Please add at least one image to your post."
                form.add_error(None, message)
                messages.error(request, message)
            else:
                post = form.save(commit=False)
                post.author = request.user
                if description_value:
                    post.description = description_value
                if category_input:
                    cat_name = category_input.lstrip("#").strip()
                    if cat_name:
                        cat_obj, _ = Category.objects.get_or_create(name=cat_name.title())
                        post.category = cat_obj
                post.save()
                form.save_m2m()

                max_w, max_h = 1600, 900
                target_ratio = 16 / 9
                for img in images:
                    try:
                        im = Image.open(img)
                        im = ImageOps.exif_transpose(im)
                        im = im.convert("RGB")
                        w, h = im.size
                        current_ratio = w / h if h else 1
                        if current_ratio > target_ratio:
                            new_w = int(h * target_ratio)
                            left = (w - new_w) // 2
                            box = (left, 0, left + new_w, h)
                        else:
                            new_h = int(w / target_ratio)
                            top = (h - new_h) // 2
                            box = (0, top, w, top + new_h)
                        im = im.crop(box)
                        im.thumbnail((max_w, max_h), Image.LANCZOS)
                        out = BytesIO()
                        im.save(out, format="JPEG", quality=85)
                        out.seek(0)
                        base = os.path.splitext(getattr(img, "name", "image"))[0]
                        filename = f"{base}_cropped.jpg"
                        content = ContentFile(out.read())
                        post_image = PostImage()
                        post_image.image.save(filename, content, save=True)
                        post.images.add(post_image)
                    except Exception:
                        post_image = PostImage.objects.create(image=img)
                        post.images.add(post_image)

            source_texts = [
                request.POST.get("title", ""),
                request.POST.get("content", ""),
                description_value or "",
            ]
            tags_seen = set()
            for txt in source_texts:
                for token in txt.split():
                    if token.startswith("#") and len(token) > 1:
                        slug = token[1:].strip().lower().rstrip(".,!?;:")
                        if slug and slug not in tags_seen:
                            tags_seen.add(slug)
                            t_obj, _ = Tag.objects.get_or_create(name=slug.title())
                            post.tags.add(t_obj)

            messages.success(request, f"Post '{post.title}' created successfully!")
            return redirect("blogs")

        messages.error(request, "There was an error with your post.")

    else:
        form = PostForm()

    return render(request, "blog/create_post.html", {"form": form})


# -------------------- STAFF MODERATION --------------------


@staff_member_required
def moderation_dashboard(request):
    reports = ModerationReport.objects.filter(resolved=False).order_by("-timestamp")
    return render(request, "blog/moderation_dashboard.html", {"reports": reports})


@staff_member_required
def resolve_report(request, report_id):
    report = get_object_or_404(ModerationReport, id=report_id)
    report.resolved = True
    report.save()
    return redirect("moderation_dashboard")


# -------------------- POST DETAIL + COMMENTS --------------------


@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    # top-level comments (no parent) for display; replies available via comment.replies
    comments = Comment.objects.filter(post=post, parent__isnull=True).order_by(
        "-created_at"
    )

    # Increment view count atomically when the detail page is accessed (GET)
    try:
        if request.method == "GET":
            from django.db.models import F

            Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
            # refresh the local instance so templates see the updated value
            post.refresh_from_db(fields=["views"])
    except Exception:
        # Don't block page render on view-counter failure
        pass

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()

            is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
            if is_ajax:
                return JsonResponse(
                    {
                        "id": new_comment.id,
                        "user": new_comment.user.username,
                        "text": new_comment.text,
                        "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )

            return redirect("post_detail", pk=post.id)
    else:
        form = CommentForm()

    # estimate reading time (200 wpm)
    content_text = post.content or ""
    word_count = len(content_text.split())
    minutes = max(1, math.ceil(word_count / 200))

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "form": form,
            "comments": comments,
            "reading_minutes": minutes,
            "word_count": word_count,
        },
    )


@login_required
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(Post, id=post_id)
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


@login_required
def toggle_dislike(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(Post, id=post_id)
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
            "dislikes_count": post.dislikes.count(),
            "likes_count": post.likes.count(),
        }
    )


@login_required
def toggle_bookmark(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.bookmarks.all():
        post.bookmarks.remove(user)
        bookmarked = False
    else:
        post.bookmarks.add(user)
        bookmarked = True

    return JsonResponse({"bookmarked": bookmarked})


@login_required
def like_comment(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        comment.dislikes.remove(user)  # optional: remove dislike if previously disliked
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "likes_count": comment.likes.count(),
            "dislikes_count": comment.dislikes.count(),
        }
    )


@login_required
def dislike_comment(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
        disliked = False
    else:
        comment.dislikes.add(user)
        comment.likes.remove(user)  # optional: remove like if previously liked
        disliked = True

    return JsonResponse(
        {
            "disliked": disliked,
            "dislikes_count": comment.dislikes.count(),
            "likes_count": comment.likes.count(),
        }
    )


User = get_user_model()


@login_required
@require_POST
def follow_user(request, author_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    author = get_object_or_404(User, id=author_id)
    user = request.user

    if user == author:
        return JsonResponse({"error": "You can't follow yourself."}, status=400)

    if user in author.followers.all():
        author.followers.remove(user)
        status = "Follow"
    else:
        author.followers.add(user)
        status = "Following"
    return JsonResponse({"status": status, "followers_count": author.followers.count()})


@require_POST
def post_comment(request, post_id):
    # Allow AJAX clients to receive JSON errors rather than redirects when not authenticated
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get("text", "").strip()
    parent_id = request.POST.get("parent_id")

    if not text:
        return JsonResponse({"error": "Comment cannot be empty."}, status=400)

    # create comment; allow optional parent to support replies
    if parent_id:
        try:
            parent = Comment.objects.get(id=int(parent_id))
        except Comment.DoesNotExist:
            parent = None
    else:
        parent = None

    comment = Comment.objects.create(
        post=post, user=request.user, text=text, parent=parent
    )

    return JsonResponse(
        {
            "id": comment.id,
            "user": comment.user.username,
            "text": comment.text,
            "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
        }
    )


@require_POST
def report_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    post = get_object_or_404(Post, id=post_id)

    # Parse JSON body
    try:
        data = json.loads(request.body)
        reason = data.get("reason", "")
        details = data.get("details", "")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Create moderation report with reason and details
    report_message = f"Reason: {reason}\n\nDetails: {details}"
    ModerationReport.objects.create(
        user=request.user,
        post=post,
        post_content=post.content,
        banned_words_found=report_message,
    )

    return JsonResponse({"success": True, "message": "Report submitted successfully"})


@login_required
@require_POST
def delete_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user
    # only author or staff can delete
    if post.author != user and not getattr(user, "is_staff", False):
        return JsonResponse({"error": "Permission denied."}, status=403)

    title = post.title
    post.delete()
    return JsonResponse({"success": True, "message": f"Deleted post '{title}'"})

# -------------------- BLOG API --------------------

def blog_posts_api(request):
    """API endpoint for fetching blog posts with sorting."""
    # Get query parameters
    sort = request.GET.get('sort', 'latest')
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 12))

    # Build queryset based on sort parameter
    if sort == 'foryou':
        if request.user.is_authenticated:
            try:
                from recommend.services import get_recommendations

                recommendations = get_recommendations(
                    user_id=request.user.id,
                    content_types=["blog"],
                    topn=limit * 3,
                    exclude_seen=True,
                    diversity_penalty=0.15,
                    freshness_boost=True
                )

                post_ids = []
                for rec_key, score in recommendations:
                    try:
                        parts = rec_key.split(':')
                        if len(parts) == 2 and 'post' in parts[0].lower():
                            post_ids.append(int(parts[1]))
                    except Exception:
                        continue

                if post_ids:
                    posts_dict = {p.id: p for p in Post.objects.filter(id__in=post_ids[:limit])}
                    posts = [posts_dict[pid] for pid in post_ids if pid in posts_dict]
                else:
                    # Fallback to recent posts if no recommendations
                    posts = list(Post.objects.order_by('-created')[:limit])

                total = len(posts)
            except Exception as e:
                logger.warning(f"Blog recommendations failed, using fallback: {e}")
                posts_qs = Post.objects.all().order_by('-created')
                total = posts_qs.count()
                posts = posts_qs[offset:offset + limit]
        else:
            posts_qs = Post.objects.all().order_by('-created')
            total = posts_qs.count()
            posts = posts_qs[offset:offset + limit]
    elif sort == 'latest':
        posts_qs = Post.objects.all().order_by('-created')
        total = posts_qs.count()
        posts = posts_qs[offset:offset + limit]
    elif sort == 'most_liked':
        from django.db.models import Count
        posts_qs = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count', '-created')
        total = posts_qs.count()
        posts = posts_qs[offset:offset + limit]
    elif sort == 'most_viewed':
        posts_qs = Post.objects.all().order_by('-views', '-created')
        total = posts_qs.count()
        posts = posts_qs[offset:offset + limit]
    elif sort == 'trending':
        # Trending: posts with high engagement recently
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        posts_qs = Post.objects.filter(
            Q(likes__isnull=False) | Q(comments__isnull=False)
        ).annotate(
            engagement=Count('likes') + Count('comments')
        ).filter(created__gte=week_ago).order_by('-engagement', '-created')
        total = posts_qs.count()
        posts = posts_qs[offset:offset + limit]
    elif sort == 'bookmarks':
        # User's bookmarked posts
        posts_qs = request.user.bookmarked_posts.all().order_by('-created')
        total = posts_qs.count()
        posts = posts_qs[offset:offset + limit]
    else:
        posts_qs = Post.objects.all().order_by('-created')
        total = posts_qs.count()
        posts = posts_qs[offset:offset + limit]
    
    # Serialize posts
    posts_data = []
    for post in posts:
        try:
            # Get first image
            img = None
            if hasattr(post, 'images') and post.images.exists():
                first_img = post.images.first()
                if first_img and hasattr(first_img, 'image'):
                    img = first_img.image.url

            posts_data.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:200] if post.content else '',
                'image': img,
                'author_id': post.author.id,
                'author_username': post.author.username,
                'author_avatar': post.author.avatar.url if post.author.avatar else None,
                'created': post.created.isoformat(),
                'likes_count': post.likes.count(),
                'dislikes_count': post.dislikes.count(),
                'comments_count': post.comments.count(),
                'user_liked': request.user in post.likes.all(),
                'user_disliked': request.user in post.dislikes.all(),
                'user_bookmarked': request.user in post.bookmarks.all(),
            })
        except Exception as e:
            logger.warning(f"Error serializing blog post {post.id}: {e}")
            continue
    
    return JsonResponse({
        'posts': posts_data,
        'total': total,
        'offset': offset,
        'limit': limit,
        'count': len(posts_data)
    })
