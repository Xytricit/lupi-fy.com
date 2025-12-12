import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from blog.models import Post, PostImage


class Command(BaseCommand):
    help = "Add sample images to posts that do not have images"

    def handle(self, *args, **options):
        # Get the posts directory
        posts_dir = os.path.join(settings.MEDIA_ROOT, "posts")
        sample_images = [
            "dog.jpeg",
            "trojan.jpg",
            "chosostunned.jpg",
            "resized_lupify_image_600px.jpg",
        ]

        posts_without_images = Post.objects.filter(images__isnull=True).distinct()

        if not posts_without_images.exists():
            self.stdout.write(self.style.SUCCESS("All posts already have images!"))
            return

        image_index = 0
        for post in posts_without_images:
            # Get a sample image
            img_name = sample_images[image_index % len(sample_images)]
            img_path = os.path.join(posts_dir, img_name)

            if os.path.exists(img_path):
                # Read the image file
                with open(img_path, "rb") as f:
                    img_content = f.read()

                # Create a PostImage
                post_image = PostImage.objects.create(
                    image=ContentFile(img_content, name=img_name)
                )
                post.images.add(post_image)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Added image to "{post.title}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"✗ Image file not found: {img_path}")
                )

            image_index += 1

        self.stdout.write(self.style.SUCCESS("\nDone! All posts now have images."))
