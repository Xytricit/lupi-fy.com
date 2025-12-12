"""Management command to compute recommendations.

This provides a simple, dependency-free baseline:
- Build item co-occurrence from recent interactions
- Score candidate items for each user by similarity to items they've played
- Store top-N recommendations in `Recommendation` table

For production, swap in ALS/Matrix Factorization (implicit) or an online model.
"""

from collections import Counter, defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from recommend.models import Interaction, Recommendation


class Command(BaseCommand):
    help = "Compute simple item-based recommendations from recent interactions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=90, help="Lookback window in days"
        )
        parser.add_argument(
            "--topn",
            type=int,
            default=12,
            help="Top N recommendations to store per user",
        )

    def handle(self, *args, **options):
        days = options["days"]
        topn = options["topn"]
        cutoff = timezone.now() - timedelta(days=days)

        self.stdout.write("Loading interactions...")
        qs = Interaction.objects.filter(created_at__gte=cutoff).select_related(
            "user", "content_type"
        )

        # Build item -> users and user -> items maps
        item_users = defaultdict(set)
        user_items = defaultdict(list)  # list of item keys (content_type_id, object_id)

        for it in qs.iterator():
            key = (it.content_type_id, it.object_id)
            item_users[key].add(it.user_id)
            user_items[it.user_id].append((key, it.value))

        self.stdout.write(f"Found {len(user_items)} users and {len(item_users)} items")

        # Compute simple item-item similarity (Jaccard)
        self.stdout.write("Computing item similarities (approx)...")
        items = list(item_users.keys())
        sim = defaultdict(dict)
        for i, a in enumerate(items):
            users_a = item_users[a]
            if not users_a:
                continue
            for b in items[
                i + 1 : i + 200
            ]:  # limit pairwise to first 200 to avoid explosion
                users_b = item_users[b]
                if not users_b:
                    continue
                inter = len(users_a & users_b)
                union = len(users_a | users_b)
                if union == 0:
                    continue
                score = inter / union
                if score > 0:
                    sim[a][b] = score
                    sim[b][a] = score

        self.stdout.write("Scoring candidates for users...")
        # For each user, score unseen items by similarity to items they've interacted with
        user_recs = {}
        for uid, items_list in user_items.items():
            seen = set(k for k, _ in items_list)
            scores = Counter()
            for k, v in items_list:
                neighbors = sim.get(k, {})
                for cand, s in neighbors.items():
                    if cand in seen:
                        continue
                    scores[cand] += s * v
            # fallback: popularity boost (item user count)
            for cand in list(scores)[:0]:
                pass
            if not scores:
                # recommend by popularity
                pop = Counter({k: len(u) for k, u in item_users.items()})
                for k, sc in pop.most_common(topn):
                    if k not in seen:
                        scores[k] += sc * 0.01

            top = scores.most_common(topn)
            user_recs[uid] = top

        self.stdout.write("Saving recommendations...")
        # bulk save
        created = 0
        with transaction.atomic():
            Recommendation.objects.all().delete()
            for uid, recs in user_recs.items():
                objs = []
                for (ct_id, obj_id), score in recs:
                    objs.append(
                        Recommendation(
                            user_id=uid,
                            content_type_id=ct_id,
                            object_id=obj_id,
                            score=score,
                        )
                    )
                Recommendation.objects.bulk_create(objs)
                created += len(objs)

        self.stdout.write(self.style.SUCCESS(f"Wrote {created} recommendation rows"))
