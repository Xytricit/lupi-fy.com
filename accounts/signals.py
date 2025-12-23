from django.apps import apps
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .badge_services import check_and_award_badges

Post = apps.get_model("blog", "Post")
Game = apps.get_model("games", "Game")
CustomUser = apps.get_model("accounts", "CustomUser")


@receiver(post_save, sender=Post)
def _award_badges_for_post(sender, instance, **kwargs):
    if instance.author:
        check_and_award_badges(instance.author)


@receiver(post_save, sender=Game)
def _award_badges_for_game(sender, instance, **kwargs):
    owner = getattr(instance, "owner", None)
    if owner:
        check_and_award_badges(owner)


@receiver(m2m_changed, sender=CustomUser.followers.through)
def _award_badges_for_followers(sender, instance, action, **kwargs):
    if action in {"post_add", "post_remove", "post_clear"}:
        check_and_award_badges(instance)
