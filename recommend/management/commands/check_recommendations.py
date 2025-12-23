from django.core.management.base import BaseCommand
from recommend.services import get_recommendation_health, get_recommendations

class Command(BaseCommand):
    help = 'Check the health and functionality of the recommendation system'

    def handle(self, *args, **options):
        self.stdout.write('Checking recommendation system health...')

        # Check health
        health = get_recommendation_health()
        self.stdout.write(f"Health status: {health}")

        # Test recommendations
        try:
            recs = get_recommendations(
                user_id=1,  # Assuming user 1 exists
                content_types=['blog', 'communities', 'games'],
                topn=5
            )
            self.stdout.write(f"Test recommendations: {len(recs)} items")
            for key, score in recs[:3]:
                self.stdout.write(f"  {key}: {score:.3f}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing recommendations: {e}"))

        self.stdout.write(self.style.SUCCESS('Health check complete'))