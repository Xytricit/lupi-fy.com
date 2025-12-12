from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from recommend.ml.torch_recommender import (load_model, recommend_for_user,
                                            train_and_save)
from recommend.models import Recommendation


class Command(BaseCommand):
    help = "Train PyTorch recommender and write top-N Recommendation rows."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument("--epochs", type=int, default=6)
        parser.add_argument("--emb_dim", type=int, default=64)
        parser.add_argument("--topn", type=int, default=50)

    def handle(self, *args, **options):
        days = options["days"]
        epochs = options["epochs"]
        emb_dim = options["emb_dim"]
        topn = options["topn"]
        self.stdout.write("Training PyTorch recommender...")
        path = train_and_save(days=days, emb_dim=emb_dim, epochs=epochs)
        if not path:
            self.stdout.write(
                self.style.WARNING("No interactions or nothing to train on.")
            )
            return
        self.stdout.write(self.style.SUCCESS(f"Model saved to {path}"))
        model = load_model(path)
        if not model:
            self.stdout.write(self.style.ERROR("Failed to load model."))
            return
        User = get_user_model()
        users = User.objects.all()
        self.stdout.write(f"Generating top-{topn} recs for {users.count()} users...")
        Recommendation.objects.all().delete()
        for user in users:
            recs = recommend_for_user(user.id, model=model, topn=topn)
            for rank, (item_key, score) in enumerate(recs, start=1):
                try:
                    app_model, oid = item_key.split(":", 1)
                    app_label, model_name = app_model.split(".", 1)
                    # Resolve ContentType and create Recommendation using content_type
                    ct = ContentType.objects.get(app_label=app_label, model=model_name)
                    Recommendation.objects.create(
                        user=user,
                        content_type=ct,
                        object_id=int(oid),
                        score=score,
                    )
                except Exception as e:
                    self.stderr.write(f"Skipping {item_key}: {e}")
        self.stdout.write(self.style.SUCCESS("Recommendations stored."))
