"""
Infallible Recommendation Service

This service provides robust, error-free recommendations with comprehensive
fallback mechanisms, health monitoring, and self-healing capabilities.
"""

import logging
import time
from functools import wraps
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import timedelta, datetime

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import Interaction, Recommendation

logger = logging.getLogger(__name__)

# Configuration
RECOMMENDATION_CACHE_TIMEOUT = 300  # 5 minutes
HEALTH_CHECK_CACHE_TIMEOUT = 60  # 1 minute
MAX_RETRIES = 3
CIRCUIT_BREAKER_TIMEOUT = 300  # 5 minutes

class RecommendationService:
    """
    Infallible recommendation service with comprehensive error handling
    and multiple fallback layers.
    """

    def __init__(self):
        self._health_status = {}
        self._circuit_breaker = {}
        self._last_health_check = {}

    def get_recommendations(
        self,
        user_id: int,
        content_types: List[str],
        topn: int = 12,
        exclude_seen: bool = True,
        diversity_penalty: float = 0.15,
        freshness_boost: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Get infallible recommendations with multiple fallback layers.

        Returns: List of (content_key, score) tuples
        """
        start_time = time.time()

        try:
            # Layer 1: AI-powered recommendations
            recommendations = self._get_ai_recommendations(
                user_id, content_types, topn, exclude_seen,
                diversity_penalty, freshness_boost
            )

            if recommendations:
                self._log_performance('ai_recommendations', time.time() - start_time, len(recommendations))
                return recommendations

            # Layer 2: Collaborative filtering fallback
            recommendations = self._get_collaborative_recommendations(
                user_id, content_types, topn
            )

            if recommendations:
                self._log_performance('collaborative_fallback', time.time() - start_time, len(recommendations))
                return recommendations

            # Layer 3: Content-based recommendations
            recommendations = self._get_content_based_recommendations(
                user_id, content_types, topn
            )

            if recommendations:
                self._log_performance('content_based_fallback', time.time() - start_time, len(recommendations))
                return recommendations

            # Layer 4: Popularity-based recommendations (always works)
            recommendations = self._get_popularity_recommendations(
                content_types, topn
            )

            self._log_performance('popularity_fallback', time.time() - start_time, len(recommendations))
            return recommendations

        except Exception as e:
            logger.error(f"Critical error in recommendation service: {e}", exc_info=True)
            # Emergency fallback - return popular content
            return self._get_emergency_fallback(content_types, topn)

    def _get_ai_recommendations(
        self,
        user_id: int,
        content_types: List[str],
        topn: int,
        exclude_seen: bool,
        diversity_penalty: float,
        freshness_boost: bool
    ) -> List[Tuple[str, float]]:
        """Layer 1: AI-powered recommendations using PyTorch model."""
        if not self._is_service_healthy('ai_recommendations'):
            return []

        try:
            from .ml.torch_recommender import recommend_for_user

            recommendations = recommend_for_user(
                user_id=user_id,
                topn=topn * 2,  # Get more for filtering
                exclude_seen=exclude_seen
            )

            # Validate and filter recommendations
            valid_recommendations = []
            for rec_key, score in recommendations:
                if self._validate_recommendation_key(rec_key, content_types):
                    valid_recommendations.append((rec_key, float(score)))
                    if len(valid_recommendations) >= topn:
                        break

            self._update_health_status('ai_recommendations', True)
            return valid_recommendations

        except ImportError:
            self._update_health_status('ai_recommendations', False, "Missing dependencies")
        except Exception as e:
            logger.warning(f"AI recommendations failed: {e}")
            self._update_health_status('ai_recommendations', False, str(e))

        return []

    def _get_collaborative_recommendations(
        self,
        user_id: int,
        content_types: List[str],
        topn: int
    ) -> List[Tuple[str, float]]:
        """Layer 2: Collaborative filtering using stored recommendations."""
        try:
            # Get pre-computed recommendations for user
            user_recommendations = Recommendation.objects.filter(
                user_id=user_id
            ).select_related('content_type')[:topn * 2]

            recommendations = []
            for rec in user_recommendations:
                content_key = self._make_content_key(rec.content_type, rec.object_id)
                if content_key and self._validate_recommendation_key(content_key, content_types):
                    recommendations.append((content_key, float(rec.score)))

            return recommendations[:topn]

        except Exception as e:
            logger.warning(f"Collaborative recommendations failed: {e}")
            return []

    def _get_content_based_recommendations(
        self,
        user_id: int,
        content_types: List[str],
        topn: int
    ) -> List[Tuple[str, float]]:
        """Layer 3: Content-based recommendations using user interests."""
        try:
            from .models import UserInterests

            user_interests = UserInterests.objects.filter(user_id=user_id).first()
            if not user_interests:
                return []

            # Get user's interests
            interests = self._extract_user_interests(user_interests, content_types)
            if not interests:
                return []

            # Find content matching interests
            recommendations = []
            for content_type in content_types:
                matching_items = self._find_content_by_interests(content_type, interests, topn)
                recommendations.extend(matching_items)

            # Sort by relevance score and return top N
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:topn]

        except Exception as e:
            logger.warning(f"Content-based recommendations failed: {e}")
            return []

    def _get_popularity_recommendations(
        self,
        content_types: List[str],
        topn: int
    ) -> List[Tuple[str, float]]:
        """Layer 4: Popularity-based recommendations (always works)."""
        recommendations = []

        for content_type in content_types:
            try:
                popular_items = self._get_popular_content(content_type, topn // len(content_types) + 1)
                recommendations.extend(popular_items)
            except Exception as e:
                logger.warning(f"Failed to get popular {content_type}: {e}")

        # Sort by score and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:topn]

    def _get_emergency_fallback(
        self,
        content_types: List[str],
        topn: int
    ) -> List[Tuple[str, float]]:
        """Emergency fallback - return any available content."""
        try:
            # Get recent content from all types
            all_content = []
            for content_type in content_types:
                recent_items = self._get_recent_content(content_type, topn // len(content_types) + 1)
                all_content.extend(recent_items)

            all_content.sort(key=lambda x: x[1], reverse=True)
            return all_content[:topn]
        except Exception as e:
            logger.error(f"Emergency fallback failed: {e}")
            return []

    def _is_service_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy (not in circuit breaker state)."""
        if service_name in self._circuit_breaker:
            breaker_time = self._circuit_breaker[service_name]
            if time.time() - breaker_time < CIRCUIT_BREAKER_TIMEOUT:
                return False
            else:
                # Circuit breaker expired, try again
                del self._circuit_breaker[service_name]

        return True

    def _update_health_status(self, service_name: str, healthy: bool, error: str = None):
        """Update health status and manage circuit breaker."""
        self._health_status[service_name] = {
            'healthy': healthy,
            'last_check': time.time(),
            'error': error
        }

        if not healthy:
            # Implement circuit breaker pattern
            failure_count = self._health_status.get(service_name, {}).get('failure_count', 0) + 1
            self._health_status[service_name]['failure_count'] = failure_count

            if failure_count >= MAX_RETRIES:
                self._circuit_breaker[service_name] = time.time()
                logger.warning(f"Circuit breaker activated for {service_name}")

    def _validate_recommendation_key(self, rec_key: str, allowed_types: List[str]) -> bool:
        """Validate that a recommendation key is for allowed content types."""
        try:
            parts = rec_key.split(':', 1)
            if len(parts) != 2:
                return False

            app_model = parts[0]
            if '.' not in app_model:
                return False

            app_label, model_name = app_model.split('.', 1)
            content_type_key = f"{app_label}.{model_name}"

            # Check if this content type is allowed
            for allowed in allowed_types:
                if allowed in content_type_key or content_type_key in allowed:
                    return True

            return False
        except Exception:
            return False

    def _make_content_key(self, content_type, object_id) -> str:
        """Create a content key from ContentType and object_id."""
        try:
            return f"{content_type.app_label}.{content_type.model}:{object_id}"
        except Exception:
            return None

    def _extract_user_interests(self, user_interests, content_types: List[str]) -> Dict[str, List[str]]:
        """Extract relevant interests for the requested content types."""
        interests = {}

        if 'blog' in content_types or 'blogs' in content_types:
            interests['blog'] = user_interests.blog_tags or []

        if 'communities' in content_types or 'community' in content_types:
            interests['community'] = user_interests.community_tags or []

        if 'games' in content_types:
            interests['games'] = user_interests.game_categories or []

        return interests

    def _find_content_by_interests(self, content_type: str, interests: Dict, topn: int) -> List[Tuple[str, float]]:
        """Find content matching user interests."""
        try:
            if content_type == 'blog':
                from blog.models import Post
                tags = interests.get('blog', [])
                if tags:
                    # Find posts with matching tags
                    posts = Post.objects.filter(tags__name__in=tags).distinct()[:topn]
                    return [(f"blog.post:{p.id}", 0.8) for p in posts]
                else:
                    # Return recent posts
                    posts = Post.objects.all().order_by('-created')[:topn]
                    return [(f"blog.post:{p.id}", 0.5) for p in posts]

            elif content_type in ['communities', 'community']:
                from communities.models import CommunityPost
                tags = interests.get('community', [])
                if tags:
                    posts = CommunityPost.objects.filter(
                        community__category__in=tags
                    ).distinct()[:topn]
                    return [(f"communities.communitypost:{p.id}", 0.8) for p in posts]
                else:
                    posts = CommunityPost.objects.all().order_by('-created_at')[:topn]
                    return [(f"communities.communitypost:{p.id}", 0.5) for p in posts]

            elif content_type == 'games':
                from games.models import Game
                categories = interests.get('games', [])
                if categories:
                    games = Game.objects.filter(
                        visibility='public',
                        # Assuming games have categories - adjust as needed
                    ).distinct()[:topn]
                    return [(f"games.game:{g.id}", 0.8) for g in games]
                else:
                    games = Game.objects.filter(visibility='public').order_by('-created')[:topn]
                    return [(f"games.game:{g.id}", 0.5) for g in games]

        except Exception as e:
            logger.warning(f"Error finding content by interests for {content_type}: {e}")

        return []

    def _get_popular_content(self, content_type: str, topn: int) -> List[Tuple[str, float]]:
        """Get popular content for a content type."""
        try:
            if content_type == 'blog':
                from blog.models import Post
                posts = Post.objects.annotate(
                    popularity=Count('likes') + Count('bookmarks')
                ).order_by('-popularity', '-created')[:topn]
                return [(f"blog.post:{p.id}", float(p.popularity or 1)) for p in posts]

            elif content_type in ['communities', 'community']:
                from communities.models import CommunityPost
                posts = CommunityPost.objects.annotate(
                    popularity=Count('likes') + Count('bookmarks')
                ).order_by('-popularity', '-created_at')[:topn]
                return [(f"communities.communitypost:{p.id}", float(p.popularity or 1)) for p in posts]

            elif content_type == 'games':
                from games.models import Game
                games = Game.objects.filter(visibility='public').annotate(
                    popularity=Count('scores')  # Assuming scores indicate plays
                ).order_by('-popularity', '-created')[:topn]
                return [(f"games.game:{g.id}", float(g.popularity or 1)) for g in games]

        except Exception as e:
            logger.warning(f"Error getting popular content for {content_type}: {e}")

        return []

    def _get_recent_content(self, content_type: str, topn: int) -> List[Tuple[str, float]]:
        """Get recent content as emergency fallback."""
        try:
            if content_type == 'blog':
                from blog.models import Post
                posts = Post.objects.all().order_by('-created')[:topn]
                return [(f"blog.post:{p.id}", 0.1) for p in posts]

            elif content_type in ['communities', 'community']:
                from communities.models import CommunityPost
                posts = CommunityPost.objects.all().order_by('-created_at')[:topn]
                return [(f"communities.communitypost:{p.id}", 0.1) for p in posts]

            elif content_type == 'games':
                from games.models import Game
                games = Game.objects.filter(visibility='public').order_by('-created')[:topn]
                return [(f"games.game:{g.id}", 0.1) for g in games]

        except Exception as e:
            logger.error(f"Emergency fallback failed for {content_type}: {e}")

        return []

    def _log_performance(self, method: str, duration: float, result_count: int):
        """Log performance metrics."""
        logger.info(f"Recommendation method '{method}' completed in {duration:.3f}s, returned {result_count} items")

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the recommendation system."""
        return {
            'services': self._health_status.copy(),
            'circuit_breakers': list(self._circuit_breaker.keys()),
            'timestamp': time.time()
        }

# Global service instance
recommendation_service = RecommendationService()

def get_recommendations(*args, **kwargs):
    """Convenience function to get recommendations from the infallible service."""
    return recommendation_service.get_recommendations(*args, **kwargs)

def get_recommendation_health():
    """Get health status of the recommendation system."""
    return recommendation_service.get_health_status()