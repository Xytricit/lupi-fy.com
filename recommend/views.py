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


def _parse_recommendation_key(rec_key):
    parts = rec_key.split(":", 1)
    if len(parts) != 2:
        return None, None, None
    app_model, object_id = parts
    if "." not in app_model:
        return None, None, None
    return app_model.split(".", 1) + [object_id]


def _serialize_recommendation_entry(rec_key, score):
    app_label, model_name, object_id = _parse_recommendation_key(rec_key)
    if not app_label:
        return None
    if app_label == "blog" and "post" in model_name:
        try:
            from blog.models import Post
            from django.utils.html import strip_tags
        except Exception:
            return None
        try:
            obj = Post.objects.filter(id=int(object_id)).first()
        except (TypeError, ValueError):
            return None
        if not obj:
            return None
        excerpt = strip_tags(obj.content)[:220] if hasattr(obj, "content") else ""
        image = None
        if hasattr(obj, "images"):
            first = obj.images.all().first()
            if first and hasattr(first, "image"):
                image = first.image.url
        return {
            "type": "blog",
            "id": obj.id,
            "title": obj.title,
            "excerpt": excerpt,
            "image": image,
            "score": float(score),
        }
    if app_label == "communities" and "post" in model_name:
        try:
            from communities.models import CommunityPost
            from django.utils.html import strip_tags
        except Exception:
            return None
        try:
            obj = CommunityPost.objects.filter(id=int(object_id)).first()
        except (TypeError, ValueError):
            return None
        if not obj:
            return None
        title = obj.title or (obj.content[:80] if obj.content else "Community Post")
        excerpt = strip_tags(obj.content)[:220] if obj.content else ""
        return {
            "type": "community",
            "id": obj.id,
            "title": title,
            "excerpt": excerpt,
            "image": obj.image.url if obj.image else None,
            "community_id": obj.community.id,
            "community_name": obj.community.name,
            "author_username": obj.author.username,
            "score": float(score),
        }
    if app_label == "games" and "game" in model_name:
        try:
            from games.models import Game
            import uuid
        except Exception:
            return None
        game_id = object_id
        try:
            game_id = uuid.UUID(object_id)
        except (ValueError, TypeError):
            pass
        obj = Game.objects.filter(id=game_id).first()
        if not obj:
            return None
        return {
            "type": "game",
            "id": str(obj.id),
            "title": obj.title,
            "description": getattr(obj, "description", ""),
            "thumbnail": obj.thumbnail.url if obj.thumbnail else None,
            "score": float(score),
        }
    if app_label == "marketplace" and "project" in model_name:
        try:
            from marketplace.models import Project
            import uuid
        except Exception:
            return None
        project_id = object_id
        try:
            project_id = uuid.UUID(object_id)
        except (ValueError, TypeError):
            pass
        proj = Project.objects.filter(id=project_id).first()
        if not proj:
            return None
        return {
            "type": "marketplace",
            "id": str(proj.id),
            "title": proj.title,
            "short_description": getattr(proj, "short_description", ""),
            "thumbnail": proj.thumbnail.url if proj.thumbnail else None,
            "price": float(proj.price) if hasattr(proj, "price") else None,
            "is_free": getattr(proj, "is_free", False),
            "score": float(score),
        }
    return None


def _hydrate_hybrid_recommendations(raw_recs):
    if not raw_recs:
        return []
    results = []
    for rec_key, score in raw_recs:
        entry = _serialize_recommendation_entry(rec_key, score)
        if entry:
            results.append(entry)
    return results


def _run_hybrid_recommendation(user_id, allowed_content, topn=12, exclude_seen=True):
    try:
        from recommend.ml.torch_recommender_hybrid import load_model_hybrid, recommend_for_user_hybrid
    except Exception:
        return []
    model = load_model_hybrid()
    if not model:
        return []
    try:
        recommendations = recommend_for_user_hybrid(
            user_id,
            model=model,
            topn=topn,
            exclude_seen=exclude_seen,
            diversity_penalty=0.15,
            freshness_boost=True,
            allowed_content=allowed_content,
        )
    except Exception:
        return []
    return _hydrate_hybrid_recommendations(recommendations)


@login_required
def for_you_recommendations(request):
    """Get PyTorch hybrid recommendations for logged-in user."""
    user = request.user
    cache_key = f"for_you_pytorch:{user.id}"
    
    # Check cache first
    data = cache.get(cache_key)
    if data is not None:
        return JsonResponse({"results": data})
    
    results = _run_hybrid_recommendation(
        user.id,
        {"blog", "communities", "games", "marketplace"},
        topn=24,
    )

    # Fallback: if no recommendations, show recent posts
    if not results:
        try:
            from blog.models import Post
            from communities.models import CommunityPost
            from django.utils.html import strip_tags
            
            recent_posts = list(Post.objects.all().order_by('-created')[:12])
            recent_community = list(CommunityPost.objects.all().order_by('-created_at')[:12])
            
            for post in recent_posts:
                try:
                    excerpt = strip_tags(post.content)[:220] if hasattr(post, "content") else ""
                    img = None
                    if hasattr(post, "images"):
                        first = post.images.all().first()
                        if first and hasattr(first, "image"):
                            img = first.image.url
                    results.append({
                        "type": "blog",
                        "id": post.id,
                        "title": post.title,
                        "excerpt": excerpt,
                        "image": img,
                        "score": 0.5,
                    })
                except Exception:
                    pass
            
            for post in recent_community:
                try:
                    excerpt = strip_tags(post.content)[:220] if post.content else ""
                    results.append({
                        "type": "community",
                        "id": post.id,
                        "title": post.title or "Community Post",
                        "excerpt": excerpt,
                        "image": post.image.url if post.image else None,
                        "score": 0.5,
                    })
                except Exception:
                    pass
        except Exception as e:
            print(f"Error generating fallback: {e}")

    cache.set(cache_key, results, 300)  # Cache for 5 minutes
    return JsonResponse({"results": results, "method": "pytorch_hybrid"})


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
def onboarding_view(request):
    """Render the onboarding page for new users to select interests."""
    from django.shortcuts import render, redirect
    
    # If already completed, redirect to dashboard
    try:
        interests = UserInterests.objects.get(user=request.user)
        if interests.completed_community_onboarding:
            return redirect('dashboard_home')
    except UserInterests.DoesNotExist:
        pass
        
    return render(request, 'onboarding.html', {
        'categories': GAME_CATEGORIES, # Using game categories as general interest categories for now
        'tags': COMMUNITY_TAGS
    })

@login_required
def log_interaction_api(request):
    """API to log client-side interactions like clicks."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
        action = data.get('action')
        object_id = data.get('object_id')
        content_type_str = data.get('content_type', 'communities.communitypost')
        
        if not action or not object_id:
            return JsonResponse({"error": "Missing parameters"}, status=400)
            
        # Parse content type
        try:
            app_label, model = content_type_str.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except (ValueError, ContentType.DoesNotExist):
            return JsonResponse({"error": "Invalid content type"}, status=400)
            
        from recommend.models import Interaction
        
        Interaction.objects.create(
            user=request.user,
            content_type=ct,
            object_id=object_id,
            action=action,
            value=1.0
        )
        
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

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

    user_id = getattr(user, "id", None)
    hybrid_results = _run_hybrid_recommendation(user_id, {"blog"}, topn=12)
    if hybrid_results:
        cache.set(cache_key, hybrid_results, 60)
        return JsonResponse({"results": hybrid_results, "method": "hybrid"})

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

    normalized_blog_tags = {tag.strip().lower() for tag in blog_tags if tag}

    # Import blog models
    from blog.models import Post

    # Get all blog posts with tags (simple scoring by tag match)
    # `Post` model uses `created` datetime field
    all_posts = Post.objects.all().order_by("-created")
    scored_posts = []

    for post in all_posts:
        score = 0
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
                if not tag:
                    continue
                normalized_tag = tag.strip().lower()
                if normalized_tag in normalized_blog_tags:
                    score += 2.0

        category_name = getattr(post.category, "name", "")
        if category_name and category_name.strip().lower() in normalized_blog_tags:
            score += 1.5

        # Boost by recency
        from django.utils import timezone

        days_old = (timezone.now() - post.created).days
        recency_boost = max(0, 5 - days_old * 0.1)
        score += recency_boost

        if score > 0 or not normalized_blog_tags:  # Show all if no tags selected
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

    hybrid_results = _run_hybrid_recommendation(user.id, {"communities"}, topn=12)
    if hybrid_results:
        cache.set(cache_key, hybrid_results, 60)
        return JsonResponse({"results": hybrid_results, "method": "hybrid"})

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
            from django.utils.html import strip_tags
            excerpt = strip_tags(post.content)[:220] if post.content else ""
            scored_posts.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:240] if post.content else "",
                    "excerpt": excerpt,
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


@login_required
def get_game_recommendations(request):
    cache_key = f"game_recs:{request.user.id}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    results = _run_hybrid_recommendation(request.user.id, {"games"}, topn=12)
    if not results:
        try:
            from games.models import Game
        except Exception:
            Game = None
        if Game:
            fallback_games = Game.objects.filter(visibility="public").order_by("-created_at")[:12]
            for game in fallback_games:
                results.append({
                    "type": "game",
                    "id": str(game.id),
                    "title": game.title,
                    "description": getattr(game, "description", ""),
                    "thumbnail": game.thumbnail.url if game.thumbnail else None,
                    "score": 0.5,
                })
    cache.set(cache_key, results, 60)
    return JsonResponse({"results": results})


@login_required
def get_marketplace_recommendations(request):
    cache_key = f"marketplace_recs:{request.user.id}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({"results": cached})

    results = _run_hybrid_recommendation(request.user.id, {"marketplace"}, topn=12)
    if not results:
        try:
            from marketplace.models import Project
        except Exception:
            Project = None
        if Project:
            fallback_projects = Project.objects.filter(status="approved").order_by("-published_at", "-created_at")[:12]
            for proj in fallback_projects:
                results.append({
                    "type": "marketplace",
                    "id": str(proj.id),
                    "title": proj.title,
                    "short_description": getattr(proj, "short_description", ""),
                    "thumbnail": proj.thumbnail.url if proj.thumbnail else None,
                    "price": float(proj.price) if hasattr(proj, "price") else None,
                    "is_free": getattr(proj, "is_free", False),
                    "score": 0.5,
                })
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
    content_filter_arg = request.GET.get("content_type")
    if content_filter_arg:
        allowed_content = {
            part.strip() for part in content_filter_arg.split(",") if part.strip()
        }
    else:
        allowed_content = {"blog", "communities", "games", "marketplace"}
    
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
                freshness_boost=True,
                allowed_content=allowed_content
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


@login_required
def track_interaction(request):
    """Track user interactions for recommendation engine."""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        content_type_str = data.get('content_type')  # e.g., 'blog.post' or 'communities.communitypost'
        object_id = int(data.get('object_id'))
        action = data.get('action', 'view')  # 'view', 'like', 'dislike', 'complete', 'skip'
        metadata = data.get('metadata') or {}
        if not isinstance(metadata, dict):
            metadata = {}
        for field in (
            'duration',
            'duration_seconds',
            'scroll_depth',
            'scroll_fraction',
            'bookmarked',
            'saved',
            'wishlisted',
            'liked',
            'disliked',
        ):
            if field in data:
                metadata[field] = data[field]
        raw_value = data.get('value')
        if raw_value is not None:
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                value = 1.0
        else:
            duration_guess = metadata.get('duration_seconds') or metadata.get('duration')
            try:
                value = float(duration_guess)
            except (TypeError, ValueError):
                value = 1.0
        value = max(value, 0.1)
        
        # Parse content_type
        if '.' in content_type_str:
            app_label, model_name = content_type_str.split('.', 1)
            ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        else:
            return JsonResponse({"error": "Invalid content_type format"}, status=400)
        
        # Create or update interaction
        interaction, created = Interaction.objects.get_or_create(
            user=request.user,
            content_type=ct,
            object_id=object_id,
            action=action,
            defaults={'value': value, 'metadata': metadata}
        )
        
        if not created:
            current_meta = interaction.metadata or {}
            current_meta.update(metadata)
            interaction.metadata = current_meta
            interaction.value = max(interaction.value, value)
            interaction.save()
        
        return JsonResponse({
            "success": True,
            "created": created,
            "interaction_id": interaction.id
        })
    except Exception as e:
        print(f"Error tracking interaction: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=400)

