from celery import shared_task
from .ml.torch_recommender_hybrid import train_and_save_hybrid

@shared_task
def retrain_recommender():
    """Retrain the hybrid recommender model nightly."""
    try:
        train_and_save_hybrid(
            epochs=10,
            batch_size=1024
        )
        return "Recommender model retrained successfully"
    except Exception as e:
        return f"Failed to retrain recommender: {e}"
