import json
from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Post
from recommend.models import Interaction


class Command(BaseCommand):
    help = "Build a lightweight index for the creator chatbot (top posts, top tags)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=365, help="Days of history to consider"
        )

    def handle(self, *args, **options):
        days = options["days"]
        since = timezone.now() - timezone.timedelta(days=days)

        # Simpler approach: pick most recent 200 posts and compute views from Interaction
        post_ct = ContentType.objects.get_for_model(Post)
        candidates = Post.objects.order_by("-created")[:200]
        scored = []
        for p in candidates:
            views = Interaction.objects.filter(
                content_type=post_ct,
                object_id=p.id,
                action__iexact="view",
                created_at__gte=since,
            ).count()
            scored.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "views": views,
                    "tags": (
                        [t[0] for t in getattr(p, "tags", [])]
                        if hasattr(p, "tags")
                        else []
                    ),
                }
            )

        scored.sort(key=lambda x: x["views"], reverse=True)

        # Top tags heuristics
        tag_counts = {}
        for p in scored:
            for t in p.get("tags", []):
                tag_counts[t] = tag_counts.get(t, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        top_tags = [t for t, c in top_tags][:10]

        index = {
            "generated_at": timezone.now().isoformat(),
            "top_posts": scored[:50],
            "top_tags": top_tags,
        }

        out_dir = Path("data/creator_bot")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.json"
        out_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        self.stdout.write(self.style.SUCCESS(f"Wrote creator bot index to {out_path}"))
