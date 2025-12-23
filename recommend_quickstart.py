#!/usr/bin/env python
"""
Quick start script for the AI recommendation module.

Usage:
    python recommend_quickstart.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from recommend.models import Interaction, UserInterests
from recommend.services import get_recommendation_health, get_recommendations


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_dependencies():
    """Check if required dependencies are installed."""
    print_section("1. Checking Dependencies")
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} installed")
    except ImportError:
        print("✗ PyTorch not installed")
        print("  Install with: pip install torch")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__} installed")
    except ImportError:
        print("✗ NumPy not installed")
        print("  Install with: pip install numpy")
        return False
    
    return True


def check_interaction_data():
    """Check if interaction data exists."""
    print_section("2. Checking Interaction Data")
    
    count = Interaction.objects.count()
    print(f"Total interactions: {count}")
    
    if count == 0:
        print("\n⚠ No interaction data found!")
        print("  Users need to interact with content (view, like, bookmark, etc.)")
        print("  Interactions are automatically tracked when users interact with content.")
        return False
    
    # Show breakdown by action
    from django.db.models import Count
    breakdown = Interaction.objects.values('action').annotate(count=Count('action'))
    print("\nBreakdown by action:")
    for item in breakdown:
        print(f"  - {item['action']}: {item['count']}")
    
    return True


def check_model_file():
    """Check if trained model exists."""
    print_section("3. Checking Trained Model")
    
    model_dir = getattr(settings, 'RECOMMEND_MODEL_DIR', 
                       os.path.join(settings.BASE_DIR, 'data', 'recommend'))
    model_path = os.path.join(model_dir, 'torch_recommender_hybrid.pt')
    
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✓ Model found: {model_path}")
        print(f"  Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"✗ Model not found: {model_path}")
        print("\n  To train the model, run:")
        print("  python manage.py train_recommender")
        return False


def check_system_health():
    """Check recommendation system health."""
    print_section("4. System Health")
    
    health = get_recommendation_health()
    
    print("Service Status:")
    for service, status in health.get('services', {}).items():
        healthy = status.get('healthy', False)
        symbol = "✓" if healthy else "✗"
        print(f"  {symbol} {service}: {'Healthy' if healthy else 'Unhealthy'}")
        if not healthy and status.get('error'):
            print(f"    Error: {status['error']}")
    
    if health.get('circuit_breakers'):
        print(f"\n⚠ Circuit breakers active: {health['circuit_breakers']}")
    else:
        print("\n✓ No circuit breakers active")


def test_recommendations():
    """Test getting recommendations for a user."""
    print_section("5. Testing Recommendations")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    users = User.objects.all()[:1]
    if not users:
        print("✗ No users found in database")
        return
    
    user = users[0]
    print(f"Testing recommendations for user: {user.username} (ID: {user.id})")
    
    try:
        recommendations = get_recommendations(
            user_id=user.id,
            content_types=['communities'],
            topn=5
        )
        
        if recommendations:
            print(f"\n✓ Got {len(recommendations)} recommendations:")
            for content_key, score in recommendations[:5]:
                print(f"  - {content_key} (score: {score:.3f})")
        else:
            print("\n⚠ No recommendations returned (may be using fallback)")
            print("  This is normal if the model hasn't been trained yet")
    
    except Exception as e:
        print(f"\n✗ Error getting recommendations: {e}")


def print_next_steps():
    """Print next steps."""
    print_section("Next Steps")
    
    print("1. Ensure users have interactions with content")
    print("   - Users should view, like, bookmark, or play games")
    print("   - Interactions are automatically tracked\n")
    
    print("2. Train the recommendation model")
    print("   python manage.py train_recommender\n")
    
    print("3. Monitor system health")
    print("   python manage.py shell")
    print("   from recommend.services import get_recommendation_health")
    print("   print(get_recommendation_health())\n")
    
    print("4. Retrain periodically")
    print("   - Weekly or after major activity spikes")
    print("   - Use --days flag to train on recent data only\n")
    
    print("5. Check documentation")
    print("   - See recommend/README_RECOMMENDATIONS.md for full details")
    print("   - See RECOMMENDATION_SETUP.md for setup guide")


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("  AI RECOMMENDATION MODULE - QUICK START")
    print("="*60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Interaction Data", check_interaction_data),
        ("Model File", check_model_file),
        ("System Health", check_system_health),
        ("Test Recommendations", test_recommendations),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ Error during {name} check: {e}")
            results[name] = False
    
    print_next_steps()
    
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60 + "\n")
    
    for name, result in results.items():
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
