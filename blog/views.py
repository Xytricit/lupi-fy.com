# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Post, PostImage, Comment, ModerationReport
from .forms import PostForm, CommentForm
from django.http import JsonResponse
# -------------------- Banned words --------------------
banned_words = [
    "arse","ass","asshole","bastard","bitch","bollocks","bugger","bullshit","cunt","cock","crap","damn",
    "dick","dickhead","dyke","fag","faggot","fuck","fucker","fucking","goddamn","goddammit","homo",
    "jerk","kike","kraut","motherfucker","nigga","nigger","prick","pussy","shit","shithead","slut",
    "twat","wanker","whore","chink","spic","gook","raghead","camel jockey","sand nigger","coon",
    "wetback","cracker","fagg","dago","hebe","jap","nip","paki","slant","beaner","honky",
    "redneck","tranny","tard","idiot","moron","imbecile","retard","loser","scumbag","bimbo","skank",
    "cockhead","piss","shitface","bollock","tosser","wank","twit","dumbass","dumbfuck","fuckface",
    "shitbag","cockmunch","jackass","cum","jizz","blowjob","dildo","tit","tits","boobs","clit","vagina",
    "penis","ejaculate","cumshot","cumslut","anal","anus","fisting","orgasm","masturbate","sex","slutty",
    "whorish","nude","naked","porn","pornography","pornstar","hooker","escort","pimp","stripper","prostitute"
]

# -------------------- VIEWS --------------------

def posts_list_view(request):
    posts = Post.objects.all().order_by('-created')
    return render(request, "blog/blog_list.html", {"posts": posts})

@login_required
def create_post_view(request):

    # suspension check
    if getattr(request.user, "suspended_until", None) and timezone.now() < request.user.suspended_until:
        messages.error(request, "You are suspended and cannot post right now.")
        return redirect("blogs")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        post_content = request.POST.get("content", "").lower()
        banned_found = [w for w in banned_words if w in post_content]

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

            messages.error(request, f"Your post contains banned words: {', '.join(banned_found)}.")
            return redirect("create_post")

        # post saving
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()

            images = request.FILES.getlist('images')
            for img in images:
                post_image = PostImage.objects.create(image=img)
                post.images.add(post_image)

            messages.success(request, f"Post '{post.title}' created successfully!")
            return redirect("blogs")

        messages.error(request, "There was an error with your post.")

    else:
        form = PostForm()

    return render(request, "blog/create_post.html", {"form": form, "banned_words": banned_words})


# -------------------- STAFF MODERATION --------------------

@staff_member_required
def moderation_dashboard(request):
    reports = ModerationReport.objects.filter(resolved=False).order_by('-timestamp')
    return render(request, "blog/moderation_dashboard.html", {"reports": reports})

@staff_member_required
def resolve_report(request, report_id):
    report = get_object_or_404(ModerationReport, id=report_id)
    report.resolved = True
    report.save()
    return redirect('moderation_dashboard')


# -------------------- POST DETAIL + COMMENTS --------------------

@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    # top-level comments (no parent) for display; replies available via comment.replies
    comments = Comment.objects.filter(post=post, parent__isnull=True).order_by('-created_at')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()

            if request.is_ajax():  # <-- AJAX request
                return JsonResponse({
                    "id": new_comment.id,
                    "user": new_comment.user.username,
                    "text": new_comment.text,
                    "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M"),
                })

            return redirect("post_detail", pk=post.id)
    else:
        form = CommentForm()

    return render(request, "blog/post_detail.html", {
        "post": post,
        "form": form,
        "comments": comments,
    })



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Post

@login_required
def toggle_like(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        post.dislikes.remove(user)  # Remove dislike if present
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
        'dislikes_count': post.dislikes.count()
    })


@login_required
def toggle_dislike(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.dislikes.all():
        post.dislikes.remove(user)
        disliked = False
    else:
        post.dislikes.add(user)
        post.likes.remove(user)  # Remove like if present
        disliked = True

    return JsonResponse({
        'disliked': disliked,
        'dislikes_count': post.dislikes.count(),
        'likes_count': post.likes.count()
    })


@login_required
def toggle_bookmark(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.bookmarks.all():
        post.bookmarks.remove(user)
        bookmarked = False
    else:
        post.bookmarks.add(user)
        bookmarked = True

    return JsonResponse({
        'bookmarked': bookmarked
    })
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Comment

@login_required
def like_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        comment.dislikes.remove(user)  # optional: remove dislike if previously disliked
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes.count(),
        'dislikes_count': comment.dislikes.count()
    })


@login_required
def dislike_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.dislikes.all():
        comment.dislikes.remove(user)
        disliked = False
    else:
        comment.dislikes.add(user)
        comment.likes.remove(user)  # optional: remove like if previously liked
        disliked = True

    return JsonResponse({
        'disliked': disliked,
        'dislikes_count': comment.dislikes.count(),
        'likes_count': comment.likes.count()
    })
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def follow_user(request, author_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    author = get_object_or_404(User, id=author_id)
    user = request.user

    if user == author:
        return JsonResponse({'error': "You can't follow yourself."}, status=400)

    if user in author.followers.all():
        author.followers.remove(user)
        status = 'Follow'
    else:
        author.followers.add(user)
        status = 'Following'
    return JsonResponse({'status': status, 'followers_count': author.followers.count()})
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Post, Comment

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

    comment = Comment.objects.create(post=post, user=request.user, text=text, parent=parent)

    return JsonResponse({
        "id": comment.id,
        "user": comment.user.username,
        "text": comment.text,
        "created_at": comment.created_at.strftime("%b %d, %Y %H:%M")
    })


def report_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    post = get_object_or_404(Post, id=post_id)
    # create a moderation report for staff to review
    ModerationReport.objects.create(
        user=request.user,
        post_content=post.content,
        banned_words_found='',
    )

    return JsonResponse({'status': 'reported'})

