from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from recommend.ml.torch_recommender_hybrid import (
    load_model_hybrid,
    recommend_for_user_hybrid,
    train_and_save_hybrid,
)
from recommend.models import Recommendation


class Command(BaseCommand):
    help = "Train PyTorch hybrid recommender and write top-N Recommendation rows."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument("--epochs", type=int, default=6)
        parser.add_argument("--emb_dim", type=int, default=64)
        parser.add_argument("--content_emb_dim", type=int, default=32)
        parser.add_argument("--topn", type=int, default=50)
        parser.add_argument("--use_content", action="store_true", default=True)

    def handle(self, *args, **options):
        days = options["days"]
        epochs = options["epochs"]
        emb_dim = options["emb_dim"]
        content_emb_dim = options["content_emb_dim"]
        topn = options["topn"]
        use_content = options["use_content"]
        
        self.stdout.write("Training PyTorch hybrid recommender...")
        path = train_and_save_hybrid(
            days=days,
            emb_dim=emb_dim,
            content_emb_dim=content_emb_dim,
            epochs=epochs,
            use_content=use_content,
        )
        if not path:
            self.stdout.write(
                self.style.WARNING("No interactions or nothing to train on.")
            )
            return
        self.stdout.write(self.style.SUCCESS(f"Model saved to {path}"))
        
        model = load_model_hybrid(path)
        if not model:
            self.stdout.write(self.style.ERROR("Failed to load model."))
            return
        
        User = get_user_model()
        users = User.objects.all()
        self.stdout.write(f"Generating top-{topn} recs for {users.count()} users...")
        Recommendation.objects.all().delete()
        
        for user in users:
            recs = recommend_for_user_hybrid(
                user.id, model=model, topn=topn, exclude_seen=True, diversity_penalty=0.15
            )
            for rank, (item_key, score) in enumerate(recs, start=1):
                try:
                    app_model, oid = item_key.split(":", 1)
                    app_label, model_name = app_model.split(".", 1)
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
