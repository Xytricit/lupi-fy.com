from datetime import timedelta
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import WordListGame
from blog.models import Post
from communities.models import Community, CommunityPost


def _dashboard_home_context(request):
    """Build context used by the dashboard-style home page.

    Kept in a helper so both the public home page and the authenticated dashboard
    can render consistently.
    """
    from accounts.models import UserGameSession, WordListGame
    from django.db import DatabaseError

    # Recently played (current user's last 8 game sessions by last_played)
    if request.user.is_authenticated:
        try:
            recent_games_qs = (
                UserGameSession.objects.filter(user=request.user)
                .order_by("-last_played")[:8]
            )
            recent_games = list(recent_games_qs)
        except DatabaseError:
            recent_games = list(
                WordListGame.objects.select_related("user").order_by("-updated_at")[:8]
            )
    else:
        recent_games = []

    # Popular communities (for sidebar)
    popular_communities = Community.objects.annotate(
        member_count=Count("members")
    ).order_by("-member_count")[:6]

    return {
        "blog_pages": ["blogs", "view_post", "create_post", "moderation_dashboard"],
        "community_pages": ["communities", "create_community", "view_community"],
        "subscription_pages": ["subscriptions", "subscription_detail"],
        "recent_games": recent_games,
        "popular_communities": popular_communities,
    }


def main_home_view(request):
    # The product experience lives on the feed-style dashboard.
    # Keep it available for both guests and logged-in users.
    return render(request, "index.html", _dashboard_home_context(request))


@login_required
def dashboard_view(request):
    return render(request, "dashboardhome.html", _dashboard_home_context(request))


def community_posts_api(request):
    """API endpoint to return community posts paginated and sorted.

    Query params:
      - sort: 'latest' (default), 'engaged', 'popular'
      - offset: integer
      - limit: integer
    Returns JSON list of posts with minimal fields.
    """
    sort = request.GET.get("sort", "latest")
    try:
        offset = int(request.GET.get("offset", 0))
    except ValueError:
        offset = 0
    try:
        limit = int(request.GET.get("limit", 10))
    except ValueError:
        limit = 10

    qs = CommunityPost.objects.select_related("community", "author")

    # Enhanced sorting strategies
    # - latest: newest first
    # - most_liked: order by likes count desc
    # - engaged: order by comments count desc then likes
    # - trending: lightweight recency-weighted likes score (recent posts weighted higher)
    # - popular: communities with more members first (legacy fallback)

    result = []

    if sort == "most_liked":
        qs = qs.annotate(likes_count=Count("likes")).order_by(
            "-likes_count", "-created_at"
        )
        total = qs.count()
        posts = qs[offset : offset + limit]
    elif sort == "engaged":
        qs = qs.annotate(
            comments_count=Count("comments"), likes_count=Count("likes")
        ).order_by("-comments_count", "-likes_count", "-created_at")
        total = qs.count()
        posts = qs[offset : offset + limit]
    elif sort == "trending":
        # Consider posts from the last week and score them by likes / age_hours
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        recent_qs = qs.filter(created_at__gte=week_ago).annotate(
            likes_count=Count("likes"), comments_count=Count("comments")
        )
        # Materialize and score in Python to allow more flexible math without DB-specific functions
        scored = []
        for p in recent_qs:
            likes = p.likes.count()
            # age in hours (at least 1)
            age_hours = max(1.0, (now - p.created_at).total_seconds() / 3600.0)
            # score: likes weighted by recency, slight weight for comments
            score = (likes + 0.5 * p.comments.count()) / (age_hours**0.8)
            scored.append((p, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        total = recent_qs.count()
        posts = [s[0] for s in scored][offset : offset + limit]
        # If trending window is empty, fall back to most_liked overall
        if total == 0:
            qs = qs.annotate(likes_count=Count("likes")).order_by(
                "-likes_count", "-created_at"
            )
            total = qs.count()
            posts = qs[offset : offset + limit]
    elif sort == "popular":
        qs = qs.annotate(community_size=Count("community__members")).order_by(
            "-community_size", "-created_at"
        )
        total = qs.count()
        posts = qs[offset : offset + limit]
    elif sort == "most_viewed":
        # No per-post view counter available; fall back to bookmarks and likes as proxy for view/popularity
        qs = qs.annotate(
            bookmarks_count=Count("bookmarks"), likes_count=Count("likes")
        ).order_by("-bookmarks_count", "-likes_count", "-created_at")
        total = qs.count()
        posts = qs[offset : offset + limit]
    elif sort == "bookmarks":
        # Return posts the current user has bookmarked (most recent first)
        if request.user.is_authenticated:
            qs = qs.filter(bookmarks=request.user).order_by("-created_at")
        else:
            qs = qs.none()
        total = qs.count()
        posts = qs[offset : offset + limit]
    else:
        qs = qs.order_by("-created_at")
        total = qs.count()
        posts = qs[offset : offset + limit]

    # Build JSON result list
    for p in posts:
        user_liked = (
            request.user in p.likes.all() if request.user.is_authenticated else False
        )
        user_disliked = (
            request.user in p.dislikes.all() if request.user.is_authenticated else False
        )
        user_bookmarked = (
            request.user in p.bookmarks.all()
            if request.user.is_authenticated
            else False
        )

        result.append(
            {
                "id": p.id,
                "title": p.title,
                "content": p.content[:240],
                "image": p.image.url if p.image else None,
                "community_id": p.community.id,
                "community_name": p.community.name,
                "community_image": (
                    p.community.community_image.url
                    if p.community.community_image
                    else None
                ),
                "author_id": p.author.id,
                "author_username": p.author.username,
                "author_avatar": p.author.avatar.url if p.author.avatar else None,
                "created_at": p.created_at.isoformat(),
                "likes_count": p.likes.count(),
                "dislikes_count": p.dislikes.count(),
                "comments_count": p.comments.count(),
                "bookmarks_count": p.bookmarks.count(),
                "user_liked": user_liked,
                "user_disliked": user_disliked,
                "user_bookmarked": user_bookmarked,
            }
        )

    return JsonResponse(
        {"total": total, "offset": offset, "limit": limit, "posts": result}
    )


def search_suggestions(request):
    """Return up to 10 mixed-type suggestions for the given query term.
    Types: user, blog, community_post, game
    """
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})

    # Build grouped suggestions. We intentionally support opting out of user suggestions
    include_users = getattr(settings, "SEARCH_INCLUDE_USERS", False)
    grouped = {"users": [], "blogs": [], "community_posts": [], "games": []}
    User = get_user_model()

    # users (max 4) - only if allowed
    if include_users:
        users = User.objects.filter(username__icontains=q, public_profile=True)[:4]
        for u in users:
            grouped["users"].append(
                {
                    "id": u.id,
                    "title": u.username,
                    "subtitle": "",
                    "url": reverse("public_profile_view", args=[u.id]),
                    "image": u.avatar.url if getattr(u, "avatar", None) else None,
                }
            )

    # blog posts (max 4) - try exact/prefix first by ordering
    blog_posts = Post.objects.filter(title__icontains=q).order_by("-created")[:6]
    for p in blog_posts[:4]:
        img = None
        try:
            first = p.images.first()
            img = first.image.url if first else None
        except Exception:
            img = None
        grouped["blogs"].append(
            {
                "id": p.id,
                "title": p.title,
                "subtitle": (p.content[:120] + "...") if p.content else "",
                "url": reverse("post_detail", args=[p.id]),
                "image": img,
            }
        )

    # community posts (max 4)
    cposts = CommunityPost.objects.filter(title__icontains=q).order_by("-created_at")[
        :6
    ]
    for cp in cposts[:4]:
        grouped["community_posts"].append(
            {
                "id": cp.id,
                "title": cp.title,
                "subtitle": cp.community.name if cp.community else "",
                "url": f"/communities/post/{cp.id}/",
                "image": cp.image.url if getattr(cp, "image", None) else None,
            }
        )

    # games (max 2)
    games = WordListGame.objects.select_related("user").filter(
        user__username__icontains=q
    )[:2]
    for g in games:
        grouped["games"].append(
            {
                "id": g.id,
                "title": f"Game by {g.user.username}",
                "subtitle": f"Score: {getattr(g, 'score', '')}",
                "url": reverse("games_hub"),
                "image": None,
            }
        )

    return JsonResponse({"groups": grouped, "include_users": include_users})


def lupiforge_guide_view(request):
    """Render the LupiForge user guide markdown file into a readable page.

    The markdown is read from the repository root `LUPIFORGE_USER_GUIDE.md`
    and passed to the template where client-side `marked.js` converts it to
    HTML. This avoids adding a server-side markdown dependency.
    """
    guide_path = os.path.join(getattr(settings, 'BASE_DIR', ''), 'LUPIFORGE_USER_GUIDE.md')
    markdown_text = ''
    try:
        with open(guide_path, 'r', encoding='utf-8') as fh:
            markdown_text = fh.read()
    except Exception:
        markdown_text = '# LupiForge Guide\n\nGuide not found. Please contact the site administrator.'

    return render(request, 'lupiforge_guide.html', {'markdown': markdown_text})


def search_api(request):
    """Return paginated mixed search results for the search page.
    Query params: q, offset, limit
    """
    q = request.GET.get("q", "").strip()
    # protect against extremely short or long queries
    if not q or len(q) < 2 or len(q) > 300:
        return JsonResponse({"total": 0, "results": []})

    # -----------------------
    # Rate limiting (per-IP or per-user)
    # -----------------------
    try:
        from django.core.cache import cache

        # identify client: logged-in users get per-user limit, otherwise per-IP
        if request.user.is_authenticated:
            client_key = f"search_rl_user:{request.user.id}"
        else:
            # try X-Forwarded-For first
            xff = request.META.get("HTTP_X_FORWARDED_FOR")
            if xff:
                ip = xff.split(",")[0].strip()
            else:
                ip = request.META.get("REMOTE_ADDR", "anon")
            client_key = f"search_rl_ip:{ip}"

        # allow 10 search API requests per 60 seconds per client
        LIMIT = 10
        WINDOW = 60
        cur = cache.get(client_key) or 0
        if cur >= LIMIT:
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)
        # increment counter (non-atomic fallback)
        cache.set(client_key, cur + 1, timeout=WINDOW)
    except Exception:
        # best-effort: if cache not available, continue (avoid blocking)
        pass

    # -----------------------
    # Query-level caching
    # -----------------------
    try:
        from django.core.cache import cache

        qlow = q.lower()
        cache_key = f"search_cache:{qlow}"
        cached = cache.get(cache_key)
        if cached is not None:
            # cached contains the precomputed 'scored' list and optional include_users
            scored = cached.get("scored", [])
            include_users = cached.get("include_users", False)
        else:
            cached = None
            qlow = q.lower()
    except Exception:
        cache = None
        cached = None

    try:
        offset = int(request.GET.get("offset", 0))
    except ValueError:
        offset = 0
    try:
        limit = int(request.GET.get("limit", 20))
    except ValueError:
        limit = 20

    User = get_user_model()
    # We'll compute a simple relevance score and then return sorted mixed results.
    scored = []

    include_users = getattr(settings, "SEARCH_INCLUDE_USERS", False)

    if cached is None:
        # not cached: perform DB queries and scoring
        if include_users:
            users = list(
                User.objects.filter(username__icontains=q, public_profile=True)[:50]
            )
        else:
            users = []

        blogs = list(Post.objects.filter(title__icontains=q)[:200])
        cposts = list(CommunityPost.objects.filter(title__icontains=q)[:200])
        games = list(
            WordListGame.objects.select_related("user").filter(
                user__username__icontains=q
            )[:200]
        )

        qlow = q.lower()

        def score_text(text):
            if not text:
                return 0
            t = text.lower()
            if t == qlow:
                return 200
            if t.startswith(qlow):
                return 150
            if qlow in t:
                return 100
            return 0

        scored = []
        for u in users:
            scored.append(
                {
                    "type": "user",
                    "id": u.id,
                    "title": u.username,
                    "subtitle": "",
                    "url": reverse("public_profile_view", args=[u.id]),
                    "score": 120 if u.username.lower().startswith(qlow) else 80,
                }
            )

        for p in blogs:
            s = score_text(p.title) + (
                50 if p.content and qlow in p.content.lower() else 0
            )
            scored.append(
                {
                    "type": "blog",
                    "id": p.id,
                    "title": p.title,
                    "subtitle": p.content[:120] if p.content else "",
                    "url": reverse("post_detail", args=[p.id]),
                    "score": s,
                }
            )

        for cp in cposts:
            s = score_text(cp.title)
            scored.append(
                {
                    "type": "community_post",
                    "id": cp.id,
                    "title": cp.title,
                    "subtitle": cp.community.name if cp.community else "",
                    "url": f"/communities/post/{cp.id}/",
                    "score": s,
                }
            )

        for g in games:
            s = 90 if g.user.username.lower().startswith(qlow) else 60
            scored.append(
                {
                    "type": "game",
                    "id": g.id,
                    "title": f"Game by {g.user.username}",
                    "subtitle": f"Score: {getattr(g,'score','')}",
                    "url": reverse("games_hub"),
                    "score": s,
                }
            )

        # cache the computed scored list for this query to reduce DB load
        try:
            cache.set(
                cache_key,
                {"scored": scored, "include_users": include_users},
                timeout=60,
            )
        except Exception:
            pass

    # sort by score desc, then (for posts) by recency where possible
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)

    total = len(scored)
    slice_results = scored[offset : offset + limit]

    # group results by type for nicer rendering on frontend
    grouped = {"users": [], "blogs": [], "community_posts": [], "games": []}
    for r in slice_results:
        if r["type"] == "user":
            grouped["users"].append(r)
        elif r["type"] == "blog":
            grouped["blogs"].append(r)
        elif r["type"] == "community_post":
            grouped["community_posts"].append(r)
        elif r["type"] == "game":
            grouped["games"].append(r)

    return JsonResponse(
        {
            "total": total,
            "offset": offset,
            "limit": limit,
            "results": slice_results,
            "groups": grouped,
        }
    )


def search_page(request):
    """Render the full search results page. The frontend will call `search_api` to get results and implement infinite scroll."""
    q = request.GET.get("q", "").strip()
    return render(request, "search_results.html", {"q": q})


def communities_view(request):
    # Categories for the bubble scroller
    categories = [
        ("all", "All"),
        ("technology", "Technology"),
        ("design", "Design"),
        ("business", "Business"),
        ("lifestyle", "Lifestyle"),
        ("gaming", "Gaming"),
        ("photography", "Photography"),
        ("writing", "Writing"),
        ("music", "Music"),
    ]

    # Fetch all communities, newest first
    communities = Community.objects.all().order_by("category", "name")

    return render(
        request,
        "communities/communities_list.html",
        {"categories": categories, "communities": communities},
    )


def terms_of_service_view(request):
    """Render the Terms & Conditions / Terms of Service page."""
    return render(request, "terms.html")


@login_required
def toggle_subscription(request, community_id=None, author_id=None):
    from communities.models import Community

    from .models import Subscription

    user = request.user

    if community_id:
        community = get_object_or_404(Community, id=community_id)
        sub, created = Subscription.objects.get_or_create(
            user=user, community=community
        )
        if not created:  # already exists → unsubscribe
            sub.delete()

    elif author_id:
        author = get_object_or_404(get_user_model(), id=author_id)
        sub, created = Subscription.objects.get_or_create(user=user, author=author)
        if not created:
            sub.delete()

    return redirect("subscriptions")


def about_view(request):
    """Display the about page"""
    return render(request, "core/about.html")


def contact_view(request):
    """Display the contact page"""
    return render(request, "core/contact.html")
