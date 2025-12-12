from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from blog.models import Category, Post, Tag
from communities.models import Community, CommunityPost


class Command(BaseCommand):
    help = "Seed 20 blog posts (distinct topics) and 20 communities for recommendation testing."

    def handle(self, *args, **options):
        User = get_user_model()
        author = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not author:
            # Create a fallback user
            author = User.objects.create_user(
                username="seeduser", email="seed@local", password="password"
            )

        topics = [
            "AI",
            "Web Development",
            "Productivity",
            "Design",
            "Photography",
            "Gaming",
            "Health",
            "Finance",
            "Travel",
            "Education",
            "Science",
            "Music",
            "Food",
            "Sports",
            "Books",
            "Movies",
            "DIY",
            "Environment",
            "Psychology",
            "Parenting",
        ]

        # Create tags and categories
        tag_objs = []
        for t in topics:
            tag_objs.append(Tag.objects.get_or_create(name=t)[0])

        cat_objs = []
        for t in topics[:6]:
            cat_objs.append(Category.objects.get_or_create(name=t)[0])

        # Create 20 blog posts
        for i, topic in enumerate(topics):
            title = f"{topic} — A Practical Guide ({i+1})"
            content = f"This is a seeded article about {topic}.\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
            description = f"Intro to {topic} and practical tips."
            category = cat_objs[i % len(cat_objs)] if cat_objs else None
            post = Post.objects.create(
                author=author,
                title=title,
                content=content,
                description=description,
                category=category,
            )
            # assign one or two tags
            post.tags.add(tag_objs[i])
            if i % 3 == 0:
                post.tags.add(tag_objs[(i + 3) % len(tag_objs)])

        self.stdout.write(self.style.SUCCESS("Created 20 blog posts"))

        # Create 20 communities and one post each
        categories = [c[0] for c in Community.CATEGORY_CHOICES]
        for i, topic in enumerate(topics):
            name = f"{topic} Community"
            category = categories[i % len(categories)]
            community = Community.objects.create(
                name=name,
                category=category,
                description=f"A community for {topic} enthusiasts.",
                creator=author,
            )
            community.members.add(author)
            # Create a sample community post
            cp_title = f"Welcome to {topic} — Post ({i+1})"
            cp_content = (
                f"This is a seeded community post about {topic}. Share your thoughts!"
            )
            CommunityPost.objects.create(
                community=community, author=author, title=cp_title, content=cp_content
            )

        self.stdout.write(self.style.SUCCESS("Created 20 communities and sample posts"))
