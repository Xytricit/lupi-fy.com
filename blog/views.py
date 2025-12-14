# views.py
import json
import math
from datetime import timedelta
from django.contrib.auth import get_user_model

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import os

from .forms import CommentForm, PostForm
from .models import Comment, ModerationReport, Post, PostImage, Category, Tag

# -------------------- Banned words --------------------
banned_words = [
    "arse",
    "ass",
    "asshole",
    "bastard",
    "bitch",
    "bollocks",
    "bugger",
    "bullshit",
    "cunt",
    "cock",
    "crap",
    "damn",
    "dick",
    "dickhead",
    "dyke",
    "fag",
    "faggot",
    "fuck",
    "fucker",
    "fucking",
    "goddamn",
    "goddammit",
    "homo",
    "jerk",
    "kike",
    "kraut",
    "motherfucker",
    "nigga",
    "nigger",
    "prick",
    "pussy",
    "shit",
    "shithead",
    "slut",
    "twat",
    "wanker",
    "whore",
    "chink",
    "spic",
    "gook",
    "raghead",
    "camel jockey",
    "sand nigger",
    "coon",
    "wetback",
    "cracker",
    "fagg",
    "dago",
    "hebe",
    "jap",
    "nip",
    "paki",
    "slant",
    "beaner",
    "honky",
    "redneck",
    "tranny",
    "tard",
    "idiot",
    "moron",
    "imbecile",
    "retard",
    "loser",
    "scumbag",
    "bimbo",
    "skank",
    "cockhead",
    "piss",
    "shitface",
    "bollock",
    "tosser",
    "wank",
    "twit",
    "dumbass",
    "dumbfuck",
    "fuckface",
    "shitbag",
    "cockmunch",
    "jackass",
    "cum",
    "jizz",
    "blowjob",
    "dildo",
    "tit",
    "tits",
    "boobs",
    "clit",
    "vagina",
    "penis",
    "ejaculate",
    "cumshot",
    "cumslut",
    "anal",
    "anus",
    "fisting",
    "orgasm",
    "masturbate",
    "sex",
    "slutty",
    "whorish",
    "nude",
    "naked",
    "porn",
    "pornography",
    "pornstar",
    "hooker",
    "escort",
    "pimp",
    "stripper",
    "prostitute",
]

# -------------------- VIEWS --------------------


def posts_list_view(request):
    posts = Post.objects.all().order_by("-created")
    return render(request, "blog/blog_list.html", {"posts": posts})


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
        post_content = request.POST.get("content", "").lower()
        banned_found = [w for w in banned_words if w in post_content]
        description_value = request.POST.get("description", "").strip()
        category_input = request.POST.get("category", "").strip()

        # moderation system
        if banned_found:
            user = request.user
            user.warning_count += 1
            if user.warning_count == 2:
                user.suspended_until = timezone.now() + timedelta(hours=24)
            elif user.warning_count == 3:
                user.suspended_until = timezone.now() + timedelta(hours=48)
            elif user.warning_count >= 4:
                user.suspended_until = timezone.now() + timedelta(days=7)
            user.save()

            ModerationReport.objects.create(
                user=user,
                post_content=post_content,
                banned_words_found=", ".join(banned_found),
            )

            messages.error(
                request, f"Your post contains banned words: {', '.join(banned_found)}."
            )
            return redirect("create_post")

        # post saving
        if form.is_valid():
            images = request.FILES.getlist("images")
            if not images:
                messages.error(request, "Please add at least one image to your post.")
                return render(
                    request,
                    "blog/create_post.html",
                    {"form": form, "banned_words": banned_words},
                )

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

    return render(
        request, "blog/create_post.html", {"form": form, "banned_words": banned_words}
    )


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

            if request.is_ajax():  # <-- AJAX request
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
    if sort == 'latest':
        posts_qs = Post.objects.all().order_by('-created')
    elif sort == 'most_liked':
        from django.db.models import Count
        posts_qs = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count', '-created')
    elif sort == 'most_viewed':
        posts_qs = Post.objects.all().order_by('-views', '-created')
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
    elif sort == 'bookmarks':
        # User's bookmarked posts
        posts_qs = request.user.bookmarked_posts.all().order_by('-created')
    else:
        posts_qs = Post.objects.all().order_by('-created')
    
    # Get total count before pagination
    total = posts_qs.count()
    
    # Apply pagination
    posts = posts_qs[offset:offset + limit]
    
    # Serialize posts
    posts_data = []
    for post in posts:
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
    
    return JsonResponse({
        'posts': posts_data,
        'total': total,
        'offset': offset,
        'limit': limit,
        'count': len(posts_data)
    })
