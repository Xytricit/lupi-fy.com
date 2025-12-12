from .models import ModerationReport


def check_post_for_banned_words(user, content, banned_words):
    """
    Returns list of banned words OR None.
    Also creates ModerationReport and updates user strikes.
    """

    banned_found = []

    lower = content.lower()

    for word in banned_words:
        if word in lower:
            banned_found.append(word)

    if banned_found:
        # Add a strike
        user.warning_count += 1
        user.save()

        # Create moderation log record
        ModerationReport.objects.create(
            user=user, post_content=content, banned_words_found=", ".join(banned_found)
        )

        return banned_found  # signals violation

    return None  # no banned words
