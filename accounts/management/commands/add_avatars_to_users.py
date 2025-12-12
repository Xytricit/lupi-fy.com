import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Add sample avatars to users who do not have avatars"

    def handle(self, *args, **options):
        avatars_dir = os.path.join(settings.MEDIA_ROOT, "avatars")

        # Get list of available avatar files
        available_avatars = [
            f for f in os.listdir(avatars_dir) if f.endswith((".png", ".jpg", ".jpeg"))
        ]

        if not available_avatars:
            self.stdout.write(self.style.WARNING("No avatar files found!"))
            return

        users_without_avatars = User.objects.filter(avatar="").distinct()

        if not users_without_avatars.exists():
            self.stdout.write(self.style.SUCCESS("All users already have avatars!"))
            return

        avatar_index = 0
        for user in users_without_avatars:
            avatar_name = available_avatars[avatar_index % len(available_avatars)]
            avatar_path = os.path.join(avatars_dir, avatar_name)

            if os.path.exists(avatar_path):
                with open(avatar_path, "rb") as f:
                    avatar_content = f.read()

                user.avatar.save(
                    f"{user.username}_avatar_{avatar_index}.png",
                    ContentFile(avatar_content),
                    save=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Assigned avatar to {user.username}")
                )

            avatar_index += 1

        self.stdout.write(self.style.SUCCESS("\nDone! All users now have avatars."))
