"""Utilities for recording interactions and managing recommendations."""

from django.contrib.contenttypes.models import ContentType

from recommend.models import Interaction


def record_game_play(user, game_obj, action="play", value=1.0):
    """Record that a user played/completed/liked a game.

    Args:
        user: CustomUser instance
        game_obj: Game object (WordListGame, LetterSetGame, etc.)
        action: 'play', 'like', 'view', 'complete'
        value: weight for the interaction (default 1.0)
    """
    try:
        content_type = ContentType.objects.get_for_model(game_obj)
        interaction, created = Interaction.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=game_obj.id,
            action=action,
            defaults={"value": value},
        )
        if not created:
            interaction.value = value
            interaction.save()
        return interaction
    except Exception as e:
        print(f"Error recording interaction: {e}")
        return None


def categorize_game(game_obj):
    """Infer game category from game object type."""
    obj_type = type(game_obj).__name__
    if "WordList" in obj_type:
        return "word"
    elif "LetterSet" in obj_type:
        return "word"
    else:
        return "casual"
