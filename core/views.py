import json
import logging
from datetime import timedelta
import os
from types import SimpleNamespace

logger = logging.getLogger(__name__)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import Subscription, WordListGame
from blog.models import Post
from communities.models import Community, CommunityPost
from games.models import Game
from marketplace.models import Project


def _dashboard_home_context(request):
    """Build context used by the dashboard-style home page.

    Kept in a helper so both the public home page and the authenticated dashboard
    can render consistently.
    """
    from accounts.models import UserGameSession, WordListGame
    from django.db import DatabaseError

    def _recent_game_entry(label, played_at):
        title = (label or "Word Game").strip() or "Word Game"
        return SimpleNamespace(game_type=title, last_played=played_at)

    # Recently played (current user's last 8 game sessions by last_played)
    if request.user.is_authenticated:
        try:
            recent_games_qs = (
                UserGameSession.objects.filter(user=request.user)
                .order_by("-last_played")[:8]
            )
            recent_games = [
                _recent_game_entry(session.game, session.last_played)
                for session in recent_games_qs
            ]
        except DatabaseError:
            fallback_games = WordListGame.objects.select_related("user").order_by("-updated_at")[:8]
            recent_games = [
                _recent_game_entry(
                    f"{game.user.username}'s Word Challenge",
                    game.updated_at,
                )
                for game in fallback_games
            ]
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
      - sort: 'latest' (default), 'engaged', 'popular', 'foryou'
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
    # - foryou: AI-powered recommendations using PyTorch model
    # - latest: newest first
    # - most_liked: order by likes count desc
    # - engaged: order by comments count desc then likes
    # - trending: lightweight recency-weighted likes score (recent posts weighted higher)
    # - popular: communities with more members first (legacy fallback)

    result = []

    if sort == "foryou":
        if request.user.is_authenticated:
            try:
                from recommend.services import get_recommendations
                recommendations = get_recommendations(
                    user_id=request.user.id,
                    content_types=["communities"],
                    topn=limit * 3,
                    exclude_seen=True,
                    diversity_penalty=0.15,
                    freshness_boost=True
                )
    
                post_ids = []
                for rec_key, score in recommendations:
                    try:
                        parts = rec_key.split(':')
                        if len(parts) == 2 and 'communitypost' in parts[0].lower():
                            post_ids.append(int(parts[1]))
                    except Exception:
                        continue
    
                if post_ids:
                    posts_dict = {p.id: p for p in qs.filter(id__in=post_ids[:limit])}
                    posts = [posts_dict[pid] for pid in post_ids if pid in posts_dict]
                else:
                    posts = list(qs.order_by('-created_at')[:limit])
    
                total = len(posts)
            except Exception as e:
                logger.warning(f"Community recommendations failed, using fallback: {e}")
                qs = qs.order_by('-created_at')
                total = qs.count()
                posts = qs[offset:offset + limit]
        else:
            qs = qs.order_by('-created_at')
            total = qs.count()
            posts = qs[offset:offset + limit]
    elif sort == "most_liked":
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
    from recommend.models import Interaction
    from django.contrib.contenttypes.models import ContentType
    
    ct_community = ContentType.objects.get_for_model(CommunityPost)
    
    for p in posts:
        # Log impression if user is authenticated
        if request.user.is_authenticated:
            try:
                Interaction.objects.get_or_create(
                    user=request.user,
                    content_type=ct_community,
                    object_id=p.id,
                    action='impression',
                    defaults={'value': 1.0}
                )
            except Exception:
                pass

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

        try:
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
        except Exception as e:
            logger.warning(f"Error serializing community post {p.id}: {e}")
            continue

    return JsonResponse(
        {"total": total, "offset": offset, "limit": limit, "posts": result}
    )


def search_suggestions(request):
    """Return up to 10 mixed-type suggestions for the given query term.
    Types: user, blog, community_post, game
    Always returns results - falls back to popular content if no matches.
    """
    q_raw = request.GET.get("q", "").strip()
    
    # Normalize query: remove extra spaces, lowercase
    q = " ".join(q_raw.split()).lower() if q_raw else ""
    
    # Build grouped suggestions
    include_users = getattr(settings, "SEARCH_INCLUDE_USERS", False)
    grouped = {"users": [], "blogs": [], "community_posts": [], "games": []}
    User = get_user_model()
    
    has_results = False

    # users (max 4) - only if allowed
    if include_users and q:
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
            has_results = True

    # blog posts (max 5)
    if q:
        blog_posts = Post.objects.filter(title__icontains=q).order_by("-created")[:5]
    else:
        blog_posts = Post.objects.all().order_by("-created")[:5]
    
    for p in blog_posts:
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
        has_results = True

    # community posts (max 5)
    if q:
        cposts = CommunityPost.objects.filter(title__icontains=q).order_by("-created_at")[:5]
    else:
        cposts = CommunityPost.objects.all().order_by("-created_at")[:5]
    
    for cp in cposts:
        grouped["community_posts"].append(
            {
                "id": cp.id,
                "title": cp.title,
                "subtitle": cp.community.name if cp.community else "",
                "url": f"/communities/post/{cp.id}/",
                "image": cp.image.url if getattr(cp, "image", None) else None,
            }
        )
        has_results = True

    # games (max 3)
    if q:
        games = WordListGame.objects.select_related("user").filter(
            user__username__icontains=q
        )[:3]
    else:
        games = WordListGame.objects.select_related("user").all().order_by("-updated_at")[:3]
    
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
        has_results = True

    # If no results at all (very specific nonsense query), show popular content
    if not has_results:
        # Show popular posts
        popular_posts = Post.objects.all().order_by("-created")[:3]
        for p in popular_posts:
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
                    "subtitle": "Popular post",
                    "url": reverse("post_detail", args=[p.id]),
                    "image": img,
                }
            )

    return JsonResponse({"groups": grouped, "include_users": include_users, "query": q_raw})


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
    Query params: q, offset, limit, sort
    """
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "relevance")
    # protect against extremely long queries
    if len(q) > 300:
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

        # allow 10 search API requests per 60 seconds per client (higher in DEBUG/staff)
        LIMIT = 10
        WINDOW = 60
        try:
            if getattr(settings, 'DEBUG', False) or (
                request.user.is_authenticated and getattr(request.user, 'is_staff', False)
            ):
                LIMIT = 120
                WINDOW = 30
        except Exception:
            pass
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
        cache_key = f"search_cache_v2:{qlow}"
        cached = cache.get(cache_key)
        if cached is not None:
            # cached contains the precomputed 'scored' list and optional include_users
            scored = cached.get("scored", [])
            include_users = cached.get("include_users", False)
            # If cache has empty results for a non-empty query, provide fallback feed
            if (not scored) and qlow:
                try:
                    recent_blogs = list(Post.objects.order_by("-created")[:50])
                    recent_cposts = list(CommunityPost.objects.order_by("-created_at")[:50])
                    recent_games = list(WordListGame.objects.select_related("user").order_by("-updated_at")[:50])
                    users_fb = list(get_user_model().objects.filter(public_profile=True)[:20]) if include_users else []
                    for p in recent_blogs:
                        scored.append({
                            "type": "blog",
                            "id": p.id,
                            "title": p.title,
                            "subtitle": p.content[:120] if p.content else "",
                            "url": reverse("post_detail", args=[p.id]),
                            "score": 50 + p.likes.count() * 2 + p.bookmarks.count() * 3,
                            "created_at": p.created.isoformat(),
                            "popularity": (p.bookmarks.count() * 3 + p.likes.count() * 2 + getattr(p, "views", 0) * 0.1),
                        })
                    for cp in recent_cposts:
                        scored.append({
                            "type": "community_post",
                            "id": cp.id,
                            "title": cp.title,
                            "subtitle": cp.community.name if cp.community else "",
                            "url": f"/communities/post/{cp.id}/",
                            "score": 50 + cp.likes.count() * 2 + cp.bookmarks.count() * 3 + cp.comments.count(),
                            "created_at": cp.created_at.isoformat(),
                            "popularity": (cp.bookmarks.count() * 3 + cp.likes.count() * 2 + cp.comments.count()),
                        })
                    for g in recent_games:
                        scored.append({
                            "type": "game",
                            "id": g.id,
                            "title": f"Game by {g.user.username}",
                            "subtitle": f"Score: {getattr(g,'score','')}",
                            "url": reverse("games_hub"),
                            "score": 40 + (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                            "created_at": g.updated_at.isoformat(),
                            "popularity": (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                        })
                    for u in users_fb:
                        scored.append({
                            "type": "user",
                            "id": u.id,
                            "title": u.username,
                            "subtitle": "",
                            "url": reverse("public_profile_view", args=[u.id]),
                            "score": 30 + (u.followers.count() if hasattr(u, "followers") else 0),
                            "created_at": getattr(u, "date_joined", None).isoformat() if getattr(u, "date_joined", None) else "",
                            "popularity": (u.followers.count() if hasattr(u, "followers") else 0),
                        })
                except Exception:
                    pass
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
        # Handle special category searches and empty query fallback
        qlow = q.lower()
        if qlow == "":
            # Default feed when no query: latest/popular mixed content
            recent_blogs = list(Post.objects.order_by("-created")[:50])
            recent_cposts = list(CommunityPost.objects.order_by("-created_at")[:50])
            recent_games = list(WordListGame.objects.select_related("user").order_by("-updated_at")[:50])
            users = list(get_user_model().objects.filter(public_profile=True)[:20]) if include_users else []

            for p in recent_blogs:
                scored.append({
                    "type": "blog",
                    "id": p.id,
                    "title": p.title,
                    "subtitle": p.content[:120] if p.content else "",
                    "url": reverse("post_detail", args=[p.id]),
                    "score": 50 + p.likes.count() * 2 + p.bookmarks.count() * 3,
                    "created_at": p.created.isoformat(),
                    "popularity": (p.bookmarks.count() * 3 + p.likes.count() * 2 + getattr(p, "views", 0) * 0.1),
                })
            for cp in recent_cposts:
                scored.append({
                    "type": "community_post",
                    "id": cp.id,
                    "title": cp.title,
                    "subtitle": cp.community.name if cp.community else "",
                    "url": f"/communities/post/{cp.id}/",
                    "score": 50 + cp.likes.count() * 2 + cp.bookmarks.count() * 3 + cp.comments.count(),
                    "created_at": cp.created_at.isoformat(),
                    "popularity": (cp.bookmarks.count() * 3 + cp.likes.count() * 2 + cp.comments.count()),
                })
            for g in recent_games:
                scored.append({
                    "type": "game",
                    "id": g.id,
                    "title": f"Game by {g.user.username}",
                    "subtitle": f"Score: {getattr(g,'score','')}",
                    "url": reverse("games_hub"),
                    "score": 40 + (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                    "created_at": g.updated_at.isoformat(),
                    "popularity": (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                })
            for u in users:
                scored.append({
                    "type": "user",
                    "id": u.id,
                    "title": u.username,
                    "subtitle": "",
                    "url": reverse("public_profile_view", args=[u.id]),
                    "score": 30 + (u.followers.count() if hasattr(u, "followers") else 0),
                    "created_at": getattr(u, "date_joined", None).isoformat() if getattr(u, "date_joined", None) else "",
                    "popularity": (u.followers.count() if hasattr(u, "followers") else 0),
                })
        elif qlow == "games":
            # Return all games
            games = list(WordListGame.objects.select_related("user").order_by("-updated_at")[:200])
            for g in games:
                scored.append(
                    {
                        "type": "game",
                        "id": g.id,
                        "title": f"Game by {g.user.username}",
                        "subtitle": f"Score: {getattr(g,'score','')}",
                        "url": reverse("games_hub"),
                        "score": 100,
                        "created_at": g.updated_at.isoformat(),
                        "popularity": (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                    }
                )
        elif qlow == "blogs":
            # Return all blog posts
            blogs = list(Post.objects.order_by("-created")[:200])
            for p in blogs:
                scored.append(
                    {
                        "type": "blog",
                        "id": p.id,
                        "title": p.title,
                        "subtitle": p.content[:120] if p.content else "",
                        "url": reverse("post_detail", args=[p.id]),
                        "score": 100,
                        "created_at": p.created.isoformat(),
                        "popularity": (p.bookmarks.count() * 3 + p.likes.count() * 2 + getattr(p, "views", 0) * 0.1),
                    }
                )
        elif qlow == "communities":
            # Return all community posts
            cposts = list(CommunityPost.objects.order_by("-created_at")[:200])
            for cp in cposts:
                scored.append(
                    {
                        "type": "community_post",
                        "id": cp.id,
                        "title": cp.title,
                        "subtitle": cp.community.name if cp.community else "",
                        "url": f"/communities/post/{cp.id}/",
                        "score": 100,
                        "created_at": cp.created_at.isoformat(),
                        "popularity": (cp.bookmarks.count() * 3 + cp.likes.count() * 2 + cp.comments.count()),
                    }
                )
        elif qlow == "users":
            # Return all users with public profiles
            if include_users:
                users = list(User.objects.filter(public_profile=True)[:200])
                for u in users:
                    scored.append(
                        {
                            "type": "user",
                            "id": u.id,
                            "title": u.username,
                            "subtitle": "",
                            "url": reverse("public_profile_view", args=[u.id]),
                            "score": 100,
                            "created_at": u.date_joined.isoformat(),
                            "popularity": (u.followers.count() if hasattr(u, "followers") else 0),
                            }
                            )
        else:
            # Normal search logic for queries that are at least 1 character
            if len(q) < 1:
                scored = []
            else:
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

                for u in users:
                    scored.append(
                        {
                            "type": "user",
                            "id": u.id,
                            "title": u.username,
                            "subtitle": "",
                            "url": reverse("public_profile_view", args=[u.id]),
                            "score": 120 if u.username.lower().startswith(qlow) else 80,
                            "created_at": getattr(u, "date_joined", None).isoformat() if getattr(u, "date_joined", None) else "",
                            "popularity": (u.followers.count() if hasattr(u, "followers") else 0),
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
                            "created_at": p.created.isoformat(),
                            "popularity": (p.bookmarks.count() * 3 + p.likes.count() * 2 + getattr(p, "views", 0) * 0.1),
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
                            "created_at": cp.created_at.isoformat(),
                            "popularity": (cp.bookmarks.count() * 3 + cp.likes.count() * 2 + cp.comments.count()),
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
                            "created_at": g.updated_at.isoformat(),
                            "popularity": (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                        }
                    )

        # If query produced no results, fall back to default feed (popular/recent mix)
        if (not scored) and qlow != "":
            try:
                recent_blogs = list(Post.objects.order_by("-created")[:50])
                recent_cposts = list(CommunityPost.objects.order_by("-created_at")[:50])
                recent_games = list(WordListGame.objects.select_related("user").order_by("-updated_at")[:50])
                users_fb = list(get_user_model().objects.filter(public_profile=True)[:20]) if include_users else []
                for p in recent_blogs:
                    scored.append({
                        "type": "blog",
                        "id": p.id,
                        "title": p.title,
                        "subtitle": p.content[:120] if p.content else "",
                        "url": reverse("post_detail", args=[p.id]),
                        "score": 50 + p.likes.count() * 2 + p.bookmarks.count() * 3,
                        "created_at": p.created.isoformat(),
                        "popularity": (p.bookmarks.count() * 3 + p.likes.count() * 2 + getattr(p, "views", 0) * 0.1),
                    })
                for cp in recent_cposts:
                    scored.append({
                        "type": "community_post",
                        "id": cp.id,
                        "title": cp.title,
                        "subtitle": cp.community.name if cp.community else "",
                        "url": f"/communities/post/{cp.id}/",
                        "score": 50 + cp.likes.count() * 2 + cp.bookmarks.count() * 3 + cp.comments.count(),
                        "created_at": cp.created_at.isoformat(),
                        "popularity": (cp.bookmarks.count() * 3 + cp.likes.count() * 2 + cp.comments.count()),
                    })
                for g in recent_games:
                    scored.append({
                        "type": "game",
                        "id": g.id,
                        "title": f"Game by {g.user.username}",
                        "subtitle": f"Score: {getattr(g,'score','')}",
                        "url": reverse("games_hub"),
                        "score": 40 + (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                        "created_at": g.updated_at.isoformat(),
                        "popularity": (g.user.followers.count() if hasattr(g.user, "followers") else 0),
                    })
                for u in users_fb:
                    scored.append({
                        "type": "user",
                        "id": u.id,
                        "title": u.username,
                        "subtitle": "",
                        "url": reverse("public_profile_view", args=[u.id]),
                        "score": 30 + (u.followers.count() if hasattr(u, "followers") else 0),
                        "created_at": getattr(u, "date_joined", None).isoformat() if getattr(u, "date_joined", None) else "",
                        "popularity": (u.followers.count() if hasattr(u, "followers") else 0),
                    })
            except Exception:
                pass

        # cache the computed scored list for this query to reduce DB load
        try:
            cache.set(
                cache_key,
                {"scored": scored, "include_users": include_users},
                timeout=60,
            )
        except Exception:
            pass

    # sort based on sort param
    try:
        if sort == "relevance":
            scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        elif sort == "title_asc":
            scored.sort(key=lambda x: x["title"].lower())
        elif sort == "title_desc":
            scored.sort(key=lambda x: x["title"].lower(), reverse=True)
        elif sort == "recent":
            scored.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        elif sort == "popular":
            scored.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        else:
            scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    except Exception as e:
        logger.warning(f"Error sorting search results: {e}")
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
    """Render the search results page."""
    q = request.GET.get("q", "").strip()

    context = {
        "q": q,
    }
    return render(request, "search_results.html", context)


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
