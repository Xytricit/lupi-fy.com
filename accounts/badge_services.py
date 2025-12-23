from django.apps import apps
from django.db.models import Count

from .models import Badge, UserBadge, UserStats


def _get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def refresh_user_stats(user):
    if not user:
        return None

    Post = _get_model("blog", "Post")
    Game = _get_model("games", "Game")

    stats, _ = UserStats.objects.get_or_create(user=user)
    stats.games_created = Game.objects.filter(owner=user).count() if Game else 0
    stats.posts_created = Post.objects.filter(author=user).count() if Post else 0
    stats.followers = user.followers.count()

    if Post:
        stats.likes_received = (
            Post.objects.filter(author=user)
            .aggregate(likes=Count("likes"))
            .get("likes")
            or 0
        )
    else:
        stats.likes_received = 0

    stats.save()
    return stats


def check_and_award_badges(user):
    if not user:
        return []

    stats = refresh_user_stats(user)
    if not stats:
        return []

    earned = set(
        UserBadge.objects.filter(user=user).values_list("badge_id", flat=True)
    )

    awarded = []
    for badge in Badge.objects.exclude(id__in=earned):
        current_value = stats.get_stat(badge.requirement_type)
        if current_value >= badge.requirement_value:
            awarded.append(UserBadge.objects.create(user=user, badge=badge))

    return awarded


def get_user_badge_context(user):
    if not user:
        return {"cards": [], "earned_count": 0, "total": 0, "stats": None}

    stats = refresh_user_stats(user)
    earned_ids = set(
        UserBadge.objects.filter(user=user).values_list("badge_id", flat=True)
    )

    cards = []
    for badge in Badge.objects.all():
        progress_value = stats.get_stat(badge.requirement_type) if stats else 0
        cards.append(
            {
                "name": badge.name,
                "description": badge.description,
                "icon_url": badge.icon.url if badge.icon else None,
                "requirement_text": badge.requirement_summary(),
                "unlocked": badge.id in earned_ids,
                "tier": badge.tier,
                "progress_value": min(progress_value, badge.requirement_value),
                "goal_value": badge.requirement_value,
            }
        )

    return {
        "cards": cards,
        "earned_count": len(earned_ids),
        "total": len(cards),
        "stats": stats,
    }
