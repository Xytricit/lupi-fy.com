"""
Management command to train the hybrid recommendation model.

Usage:
    python manage.py train_recommender [--days DAYS] [--epochs EPOCHS] [--emb-dim EMB_DIM]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Train the hybrid recommendation model using interaction data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Only use interactions from the last N days (default: all)",
        )
        parser.add_argument(
            "--epochs",
            type=int,
            default=10,
            help="Number of training epochs (default: 10)",
        )
        parser.add_argument(
            "--emb-dim",
            type=int,
            default=128,
            help="Embedding dimension (default: 128)",
        )
        parser.add_argument(
            "--content-emb-dim",
            type=int,
            default=64,
            help="Content embedding dimension (default: 64)",
        )
        parser.add_argument(
            "--lr",
            type=float,
            default=0.005,
            help="Learning rate (default: 0.005)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1024,
            help="Batch size (default: 1024)",
        )

    def handle(self, *args, **options):
        try:
            from recommend.ml.torch_recommender_hybrid import train_and_save_hybrid
        except ImportError as e:
            raise CommandError(
                f"Failed to import torch recommender: {e}. "
                "Make sure numpy and torch are installed."
            )

        self.stdout.write(self.style.SUCCESS("Starting model training..."))

        try:
            model_path = train_and_save_hybrid(
                days=options["days"],
                emb_dim=options["emb_dim"],
                content_emb_dim=options["content_emb_dim"],
                epochs=options["epochs"],
                lr=options["lr"],
                batch_size=options["batch_size"],
                use_content=True,
            )

            if model_path:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Model trained and saved to {model_path}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠ Model training returned None. "
                        "Check that you have interaction data in the database."
                    )
                )

        except Exception as e:
            raise CommandError(f"Model training failed: {e}")
