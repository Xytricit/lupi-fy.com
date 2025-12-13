import json
import hashlib

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import decorator_from_middleware

from recommend.models import (BLOG_TAGS, COMMUNITY_TAGS, GAME_CATEGORIES,
                              Recommendation, UserInterests)


# ============================================================================
# SMART CACHING & METRICS
# ============================================================================
def smart_cache(cache_key_prefix, ttl=300, user_specific=True):
    """Smart caching decorator with user-specific keys and hit tracking."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Build cache key
            user_hash = hashlib.md5(str(request.user.id).encode()).hexdigest()[:8]
            cache_key = f"{cache_key_prefix}:{user_hash}" if user_specific else cache_key_prefix
            
            # Check cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                try:
                    hits = cache.get(f"{cache_key}:hits", 0)
                    cache.set(f"{cache_key}:hits", hits + 1, ttl * 2)
                except Exception:
                    pass
                return cached_data
            
            # Execute view
            result = view_func(request, *args, **kwargs)
            
            # Store in cache
            try:
                cache.set(cache_key, result, ttl)
                cache.set(f"{cache_key}:hits", 0, ttl * 2)
            except Exception:
                pass
            
            return result
        return wrapper
    return decorator


@login_required
def for_you_recommendations(request):
    """Get top recommendations for logged-in user (cached)."""
    user = request.user
    cache_key = f"for_you:{user.id}"
    data = cache.get(cache_key)
    if data is not None:
        return JsonResponse({"results": data})
    recs = Recommendation.objects.filter(user=user).select_related("content_type")[:24]
    results = []
    for r in recs:
        try:
            ct = ContentType.objects.get_for_id(r.content_type_id)
            app = ct.app_label
            model = ct.model
            # Blog posts
            if app == "blog" and model in ("post", "post"):
                try:
                    from blog.models import Post

                    obj = Post.objects.filter(id=r.object_id).first()
                    if obj:
                        from django.utils.html import strip_tags

                        excerpt = (
                            strip_tags(obj.content)[:220]
                            if hasattr(obj, "content")
                            else ""
                        )
                        img = None
                        if hasattr(obj, "images"):
                            first = obj.images.all().first()
                            if first and hasattr(first, "image"):
                                img = first.image.url
                        results.append(
                            {
                                "type": "blog",
                                "id": obj.id,
                                "title": obj.title,
                                "excerpt": excerpt,
                                "image": img,
                                "score": r.score,
                            }
                        )
                        continue
                except Exception:
                    pass

            # Community posts
            if app == "communities" and model in ("communitypost", "community_post"):
                try:
                    from communities.models import CommunityPost

                    obj = CommunityPost.objects.filter(id=r.object_id).first()
                    if obj:
                        title = getattr(
                            obj,
                            "title",
                            (getattr(obj, "content", "")[:80] or "Community Post"),
                        )
                        excerpt = ""
                        if hasattr(obj, "content"):
                            from django.utils.html import strip_tags

                            excerpt = strip_tags(obj.content)[:220]
                        img = None
                        if hasattr(obj, "image") and obj.image:
                            img = obj.image.url
                        results.append(
                            {
                                "type": "community",
                                "id": obj.id,
                                "title": title,
                                "excerpt": excerpt,
                                "image": img,
                                "score": r.score,
                            }
                        )
                        continue
                except Exception:
                    pass

            # Games or other content types: surface minimal info (frontend will decide where to show)
            if "game" in model or app in ("core", "games"):
                results.append(
                    {"type": "game", "object_id": r.object_id, "score": r.score}
                )
                continue

            # Fallback: include raw content_type and id so frontend can decide
            results.append(
                {
                    "type": "unknown",
                    "content_type": f"{app}.{model}",
                    "object_id": r.object_id,
                    "score": r.score,
                }
            )
        except Exception:
            # on any unexpected error, include minimal data
            results.append(
                {"type": "unknown", "object_id": r.object_id, "score": r.score}
            )

    cache.set(cache_key, results, 60)
    return JsonResponse({"results": results})


@login_required
def get_user_interests(request):
    """Get user's selected interests for all content types."""
    user = request.user
    try:
        interests = UserInterests.objects.get(user=user)
        return JsonResponse(
            {
                "game_categories": interests.game_categories,
                "blog_tags": interests.blog_tags,
                "community_tags": interests.community_tags,
                "completed_game_onboarding": interests.completed_game_onboarding,
                "completed_blog_onboarding": interests.completed_blog_onboarding,
                "completed_community_onboarding": interests.completed_community_onboarding,
                # Backwards-compatible keys
                "categories": interests.categories,
                "completed_onboarding": interests.completed_onboarding,
            }
        )
    except UserInterests.DoesNotExist:
        return JsonResponse(
            {
                "game_categories": [],
                "blog_tags": [],
                "community_tags": [],
                "completed_game_onboarding": False,
                "completed_blog_onboarding": False,
                "completed_community_onboarding": False,
                # Backwards-compatible keys
                "categories": [],
                "completed_onboarding": False,
            }
        )


@login_required
def save_user_interests(request):
    """Save user's selected interests."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        # Support legacy payloads that send {'categories': [...]} as well as newer {type, items}
        if "categories" in data:
            interest_type = "game"
            selected_items = data.get("categories", [])
        else:
            interest_type = data.get("type", "game")  # 'game', 'blog', or 'community'
            selected_items = data.get("items", [])

        interests, _ = UserInterests.objects.get_or_create(user=request.user)

        if interest_type == "game":
            interests.game_categories = selected_items
            interests.completed_game_onboarding = True
            # keep legacy alias in sync
            interests.categories = selected_items
            interests.completed_onboarding = True
        elif interest_type == "blog":
            interests.blog_tags = selected_items
            interests.completed_blog_onboarding = True
        elif interest_type == "community":
            interests.community_tags = selected_items
            interests.completed_community_onboarding = True

        interests.save()
        return JsonResponse(
            {
                "success": True,
                "message": f"{interest_type.capitalize()} interests saved",
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_blog_recommendations(request):
    """Get personalized blog post recommendations based on tags."""
    user = request.user
    # Build cache key safely for anonymous users
    uid = getattr(user, 'id', 'anon') if user and getattr(user, 'is_authenticated', False) else 'anon'
    cache_key = f"blog_recs:{uid}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    # Only attempt to fetch UserInterests when user is authenticated
    if getattr(user, 'is_authenticated', False):
        try:
            interests = UserInterests.objects.get(user=user)
            blog_tags = interests.blog_tags
        except UserInterests.DoesNotExist:
            blog_tags = []
        except Exception:
            blog_tags = []
    else:
        blog_tags = []

    # Import blog models
    from blog.models import Post

    # Get all blog posts with tags (simple scoring by tag match)
    # `Post` model uses `created` datetime field
    all_posts = Post.objects.all().order_by("-created")
    scored_posts = []

    for post in all_posts:
        score = 0
        # Score by tag match (if blog posts have tags)
        if hasattr(post, "tags"):
            post_tags = []
            try:
                if isinstance(post.tags, str):
                    post_tags = [t.strip() for t in post.tags.split(',') if t.strip()]
                else:
                    # ManyToManyField -> get names from related Tag objects
                    try:
                        post_tags = [getattr(t, 'name', str(t)) for t in post.tags.all()]
                    except Exception:
                        # Fallback: try to iterate directly
                        post_tags = [str(t) for t in post.tags]
            except Exception:
                post_tags = []

            for tag in post_tags:
                try:
                    if tag and tag.strip().lower() in [t.lower() for t in blog_tags]:
                        score += 2.0
                except Exception:
                    continue

        # Boost by recency
        from django.utils import timezone

        days_old = (timezone.now() - post.created).days
        recency_boost = max(0, 5 - days_old * 0.1)
        score += recency_boost

        if score > 0 or not blog_tags:  # Show all if no tags selected
            # Provide a short excerpt to the frontend (do not expose score unnecessarily)
            excerpt = ""
            try:
                from django.utils.html import strip_tags

                excerpt = strip_tags(post.content)[:220]
            except Exception:
                excerpt = post.title
            scored_posts.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "excerpt": excerpt,
                    "score": score,
                }
            )

    # Sort by score and take top 12
    scored_posts.sort(key=lambda x: x["score"], reverse=True)
    results = scored_posts[:12]

    cache.set(cache_key, results, 60)
    return JsonResponse({"results": results})


@login_required
def get_community_recommendations(request):
    """Get personalized community post recommendations based on tags."""
    user = request.user
    cache_key = f"community_recs:{user.id}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    try:
        interests = UserInterests.objects.get(user=user)
        community_tags = interests.community_tags
    except UserInterests.DoesNotExist:
        community_tags = []

    # Import community models
    from communities.models import CommunityPost

    # Get all community posts with scoring by tag/category match
    all_posts = CommunityPost.objects.all().order_by("-created_at")
    scored_posts = []

    for post in all_posts:
        score = 0

        # Score by community match (assuming community has category/tags)
        if hasattr(post.community, "category") and post.community.category:
            if post.community.category.lower() in [t.lower() for t in community_tags]:
                score += 2.0

        # Score by post tags if available
        if hasattr(post, "tags") and post.tags:
            post_tags = (
                post.tags.split(",") if isinstance(post.tags, str) else post.tags
            )
            for tag in post_tags:
                if tag.strip().lower() in [t.lower() for t in community_tags]:
                    score += 1.5

        # Boost by engagement (likes)
        if hasattr(post, "likes") and post.likes:
            score += len(post.likes.all()) * 0.1

        # Boost by recency
        from django.utils import timezone

        days_old = (timezone.now() - post.created_at).days
        recency_boost = max(0, 5 - days_old * 0.1)
        score += recency_boost

        if score > 0 or not community_tags:  # Show all if no tags selected
            scored_posts.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:240] if post.content else "",
                    "image": post.image.url if post.image else None,
                    "community_id": post.community.id,
                    "community_name": post.community.name,
                    "community_image": post.community.community_image.url if post.community.community_image else None,
                    "author_id": post.author.id,
                    "author_username": post.author.username,
                    "author_avatar": post.author.avatar.url if post.author.avatar else None,
                    "created_at": post.created_at.isoformat(),
                    "likes_count": post.likes.count(),
                    "dislikes_count": post.dislikes.count(),
                    "comments_count": post.comments.count(),
                    "score": score,
                }
            )

    # Sort by score and take top 12
    scored_posts.sort(key=lambda x: x["score"], reverse=True)
    results = scored_posts[:12]

    cache.set(cache_key, results, 60)
    return JsonResponse({"results": results})


def get_tag_options(request):
    """Get available tag options for selection."""
    content_type = request.GET.get("type", "blog")

    if content_type == "blog":
        tags = [{"slug": slug, "label": label} for slug, label in BLOG_TAGS]
    elif content_type == "community":
        tags = [{"slug": slug, "label": label} for slug, label in COMMUNITY_TAGS]
    elif content_type == "game":
        tags = [{"slug": slug, "label": label} for slug, label in GAME_CATEGORIES]
    else:
        tags = []

    return JsonResponse({"tags": tags})


@login_required
@smart_cache("hybrid_recommendations", ttl=600)
def get_hybrid_recommendations(request):
    """Get hybrid recommendations combining collaborative + content-based filtering.
    
    Features:
    - Collaborative filtering (user embeddings matching)
    - Content-based filtering (tag/category similarity)
    - Diversity penalty (avoid similar items in top-N)
    - Freshness boost (prefer recent items)
    - Cold-start fallback (new users get popular items)
    """
    user = request.user
    topn = int(request.GET.get("topn", 12))
    
    try:
        from recommend.ml.torch_recommender_hybrid import (
            load_model_hybrid,
            recommend_for_user_hybrid,
        )
        
        model = load_model_hybrid()
        if not model:
            # Fallback to basic recommendations if hybrid model unavailable
            recs = Recommendation.objects.filter(user=user)[:topn]
        else:
            recs_raw = recommend_for_user_hybrid(
                user.id, 
                model=model, 
                topn=topn,
                diversity_penalty=0.15,
                freshness_boost=True
            )
            # Convert raw recommendations to database lookups
            recs = []
            for item_key, score in recs_raw:
                try:
                    app_model, oid = item_key.split(":", 1)
                    app_label, model_name = app_model.split(".", 1)
                    ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    rec_obj = Recommendation(
                        user=user,
                        content_type=ct,
                        object_id=int(oid),
                        score=score
                    )
                    recs.append(rec_obj)
                except Exception:
                    pass
    except ImportError:
        # Fallback if hybrid model not available
        recs = Recommendation.objects.filter(user=user)[:topn]
    
    results = []
    for r in recs:
        try:
            ct = ContentType.objects.get_for_id(r.content_type_id)
            app = ct.app_label
            model = ct.model
            
            # Blog posts
            if app == "blog" and model == "post":
                try:
                    from blog.models import Post
                    obj = Post.objects.filter(id=r.object_id).first()
                    if obj:
                        from django.utils.html import strip_tags
                        excerpt = strip_tags(obj.content)[:220] if hasattr(obj, "content") else ""
                        img = None
                        if hasattr(obj, "images"):
                            first = obj.images.all().first()
                            if first and hasattr(first, "image"):
                                img = first.image.url
                        results.append({
                            "type": "blog",
                            "id": obj.id,
                            "title": obj.title,
                            "excerpt": excerpt,
                            "image": img,
                            "score": r.score,
                        })
                        continue
                except Exception:
                    pass
            
            # Community posts
            if app == "communities" and model == "communitypost":
                try:
                    from communities.models import CommunityPost
                    obj = CommunityPost.objects.filter(id=r.object_id).first()
                    if obj:
                        title = getattr(obj, "title", getattr(obj, "content", "Community Post")[:80])
                        excerpt = ""
                        if hasattr(obj, "content"):
                            from django.utils.html import strip_tags
                            excerpt = strip_tags(obj.content)[:220]
                        img = None
                        if hasattr(obj, "image") and obj.image:
                            img = obj.image.url
                        results.append({
                            "type": "community",
                            "id": obj.id,
                            "title": title,
                            "excerpt": excerpt,
                            "image": img,
                            "score": r.score,
                        })
                        continue
                except Exception:
                    pass
        except Exception:
            pass
    
    return JsonResponse({"results": results, "method": "hybrid"})

