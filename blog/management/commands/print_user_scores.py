from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Post

try:
    from communities.models import Community, CommunityPost
except Exception:
    CommunityPost = None
    Community = None

try:
    from recommend.models import UserInterests
except Exception:
    UserInterests = None


class Command(BaseCommand):
    help = "Print recommendation scores for posts for a given user (blog and/or community)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", type=str, default="Turbo", help="Username to evaluate"
        )
        parser.add_argument(
            "--type", type=str, choices=["blog", "community", "both"], default="both"
        )
        parser.add_argument(
            "--limit", type=int, default=50, help="Maximum items to print per type"
        )
        parser.add_argument(
            "--json", type=str, help="Optional path to write JSON output"
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        utype = options["type"]
        limit = options["limit"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User '{username}' not found."))
            return

        # fetch user's saved interests if available
        user_blog_tags = []
        user_community_tags = []
        if UserInterests:
            try:
                ui = UserInterests.objects.filter(user=user).first()
                if ui:
                    user_blog_tags = ui.blog_tags or []
                    user_community_tags = ui.community_tags or []
            except Exception:
                pass

        now = timezone.now()
        results = {"blog": [], "community": []}

        if utype in ("blog", "both"):
            posts = Post.objects.all()
            for p in posts:
                # tag matching
                post_tags = [t.name for t in p.tags.all()]
                tag_matches = len([t for t in post_tags if t in user_blog_tags])
                tag_score = tag_matches * 2.0

                # recency boost
                days = (now - p.created).days if p.created else 0
                recency_score = max(0.0, 5.0 - 0.1 * days)

                score = tag_score + recency_score

                results["blog"].append(
                    {
                        "id": p.id,
                        "title": p.title,
                        "score": round(score, 3),
                        "tag_matches": tag_matches,
                        "post_tags": post_tags,
                        "excerpt": (p.description or "")[:200],
                    }
                )

            results["blog"].sort(key=lambda x: x["score"], reverse=True)
            for r in results["blog"][:limit]:
                self.stdout.write(
                    f"[BLOG] ({r['score']}) id={r['id']} - {r['title']} - tags={r['post_tags']} matches={r['tag_matches']}"
                )

        if utype in ("community", "both") and CommunityPost:
            cposts = CommunityPost.objects.select_related("community").all()
            for cp in cposts:
                # match community category and title/content words against user_community_tags
                comm = cp.community
                comm_cat = getattr(comm, "category", "")
                tag_matches = 0
                if comm_cat and comm_cat in user_community_tags:
                    tag_matches += 1
                # simple text match against user tags in title/content
                for t in user_community_tags:
                    if (
                        t.lower() in (cp.title or "").lower()
                        or t.lower() in (cp.content or "").lower()
                    ):
                        tag_matches += 1

                # engagement boost
                likes = cp.likes.count() if hasattr(cp, "likes") else 0
                engagement_score = likes * 0.1

                days = (now - cp.created_at).days if cp.created_at else 0
                recency_score = max(0.0, 5.0 - 0.1 * days)

                score = tag_matches * 2.0 + engagement_score + recency_score

                results["community"].append(
                    {
                        "id": cp.id,
                        "title": cp.title,
                        "community": comm.name if comm else None,
                        "score": round(score, 3),
                        "tag_matches": tag_matches,
                        "likes": likes,
                        "excerpt": (cp.content or "")[:200],
                    }
                )

            results["community"].sort(key=lambda x: x["score"], reverse=True)
            for r in results["community"][:limit]:
                self.stdout.write(
                    f"[COMM] ({r['score']}) id={r['id']} - {r['title']} @ {r['community']} - likes={r['likes']} matches={r['tag_matches']}"
                )

        if options.get("json"):
            import json

            with open(options["json"], "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f"Wrote JSON output to {options['json']}")
            )
