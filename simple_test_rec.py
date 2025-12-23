#!/usr/bin/env python
"""Simple test for recommendation system."""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

try:
    from recommend.ml.torch_recommender_hybrid import load_model_hybrid, recommend_for_user_hybrid
    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)

print("Testing hybrid recommendation system...")

try:
    model = load_model_hybrid()
    if model:
        print("Model loaded successfully!")
        print(f"Users: {len(model['user_map'])}")
        print(f"Items: {len(model['item_map'])}")

        # Test with a user ID (assuming user 1 exists)
        try:
            recs = recommend_for_user_hybrid(1, model=model, topn=5)
            print(f"Recommendations for user 1: {len(recs)} items")
            for key, score in recs:
                print(f"  {key}: {score:.3f}")
        except Exception as e:
            print(f"Error getting recommendations: {e}")
    else:
        print("Model not found or failed to load")
except Exception as e:
    print(f"Error loading model: {e}")

print("Test complete.")