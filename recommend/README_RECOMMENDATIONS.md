# AI Recommendation Module - Setup & Usage Guide

## Overview

The recommendation system uses a **multi-layer fallback architecture** to ensure recommendations are always available:

1. **Layer 1: AI-Powered (PyTorch Hybrid Model)** - Collaborative + Content-Based Filtering
2. **Layer 2: Collaborative Filtering** - Pre-computed recommendations from stored data
3. **Layer 3: Content-Based** - Tag/category matching
4. **Layer 4: Popularity-Based** - Most popular/recent content (always works)

## Prerequisites

Install required dependencies:

```bash
pip install torch numpy
```

Or add to your `requirements.txt`:
```
torch>=2.0.0
numpy>=1.21.0
```

## Quick Start

### 1. Generate Interaction Data

The recommendation system learns from user interactions. Make sure users are:
- Viewing content (blog posts, community posts, games)
- Liking/disliking content
- Bookmarking content
- Playing games

These interactions are automatically tracked when users interact with content.

### 2. Train the Model

Once you have interaction data, train the hybrid model:

```bash
python manage.py train_recommender
```

**Options:**
```bash
# Train using only recent interactions (last 30 days)
python manage.py train_recommender --days 30

# Customize training parameters
python manage.py train_recommender --epochs 20 --emb-dim 256 --lr 0.01

# Full options
python manage.py train_recommender --help
```

**Output:**
- Model saved to: `data/recommend/torch_recommender_hybrid.pt`
- Console output shows training progress and loss

### 3. Use Recommendations

The system automatically uses recommendations in:
- **Dashboard feed** - "For you" filter uses AI recommendations
- **Search results** - Fallback recommendations when no matches found
- **API endpoints** - `/dashboard/community-posts-api/?sort=foryou`

## How It Works

### Recommendation Flow

```
User requests recommendations
    ↓
Layer 1: AI Model (if trained)
    ├─ Success → Return AI recommendations
    └─ Fail → Try Layer 2
    ↓
Layer 2: Collaborative Filtering
    ├─ Success → Return stored recommendations
    └─ Fail → Try Layer 3
    ↓
Layer 3: Content-Based
    ├─ Success → Return tag-matched recommendations
    └─ Fail → Try Layer 4
    ↓
Layer 4: Popularity-Based (always works)
    └─ Return popular/recent content
```

### Model Architecture

The hybrid model combines:

1. **Collaborative Filtering**
   - User embeddings (128-dim by default)
   - Item embeddings (128-dim)
   - Learns from user-item interactions

2. **Content-Based Filtering**
   - Content embeddings (64-dim by default)
   - Learns from tags, categories, metadata
   - Helps with cold-start items

3. **Hybrid Scoring**
   - 70% collaborative score
   - 30% content-based score
   - Weighted combination for balanced recommendations

4. **Post-Processing**
   - **Freshness Boost**: Recent items (< 7 days) get +50% boost
   - **Diversity Penalty**: Suppress similar items in top-N
   - **Content Filtering**: Only return allowed content types

## Monitoring & Health

Check recommendation system health:

```python
from recommend.services import get_recommendation_health

health = get_recommendation_health()
print(health)
# Output:
# {
#     'services': {
#         'ai_recommendations': {'healthy': True, 'last_check': 1234567890},
#         'collaborative_fallback': {'healthy': False, 'error': '...'},
#         ...
#     },
#     'circuit_breakers': [],
#     'timestamp': 1234567890
# }
```

## Troubleshooting

### Model Not Training

**Problem:** `train_recommender` command fails

**Solutions:**
1. Check torch/numpy are installed: `python -c "import torch; import numpy"`
2. Ensure you have interaction data: `python manage.py shell`
   ```python
   from recommend.models import Interaction
   print(Interaction.objects.count())  # Should be > 0
   ```
3. Check disk space in `data/recommend/` directory

### Recommendations Not Showing

**Problem:** Users see empty recommendations or fallback content

**Solutions:**
1. Model may not be trained yet - run `python manage.py train_recommender`
2. Check if model file exists: `ls data/recommend/torch_recommender_hybrid.pt`
3. Verify interaction data exists: `python manage.py shell`
   ```python
   from recommend.models import Interaction
   print(Interaction.objects.count())
   ```
4. Check logs for errors: `tail -f logs/django.log`

### Slow Recommendations

**Problem:** Recommendations take too long to load

**Solutions:**
1. Model is too large - reduce embedding dimensions:
   ```bash
   python manage.py train_recommender --emb-dim 64 --content-emb-dim 32
   ```
2. Too many interactions - train on recent data only:
   ```bash
   python manage.py train_recommender --days 30
   ```
3. Enable caching in Django settings:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

## API Reference

### Get Recommendations

```python
from recommend.services import get_recommendations

recommendations = get_recommendations(
    user_id=1,
    content_types=['communities'],  # or ['blog'], ['games'], etc.
    topn=12,
    exclude_seen=True,
    diversity_penalty=0.15,
    freshness_boost=True
)

# Returns: List of (content_key, score) tuples
# Example: [('communities.communitypost:123', 0.95), ...]
```

### Track Interactions

```python
from recommend.models import Interaction
from django.contrib.contenttypes.models import ContentType
from communities.models import CommunityPost

post = CommunityPost.objects.get(id=123)
ct = ContentType.objects.get_for_model(CommunityPost)

Interaction.objects.create(
    user_id=1,
    content_type=ct,
    object_id=post.id,
    action='like',  # or 'view', 'click', 'complete', etc.
    value=1.0,
    metadata={'duration_seconds': 30, 'scroll_depth': 0.8}
)
```

## Configuration

Add to `settings.py`:

```python
# Recommendation model directory
RECOMMEND_MODEL_DIR = os.path.join(BASE_DIR, 'data', 'recommend')

# Cache timeout for recommendations (seconds)
RECOMMENDATION_CACHE_TIMEOUT = 300  # 5 minutes

# Enable/disable search include users in recommendations
SEARCH_INCLUDE_USERS = False
```

## Performance Tips

1. **Train regularly** - Retrain model weekly or after major user activity
2. **Use caching** - Redis cache significantly speeds up recommendations
3. **Batch interactions** - Collect interactions before training
4. **Monitor health** - Check `get_recommendation_health()` regularly
5. **Adjust parameters** - Tune embedding dimensions based on your data size

## Advanced Usage

### Custom Training

```python
from recommend.ml.torch_recommender_hybrid import train_and_save_hybrid

model_path = train_and_save_hybrid(
    days=30,
    emb_dim=256,
    content_emb_dim=128,
    epochs=20,
    lr=0.01,
    batch_size=2048,
    use_content=True
)
```

### Manual Inference

```python
from recommend.ml.torch_recommender_hybrid import recommend_for_user_hybrid

recommendations = recommend_for_user_hybrid(
    user_id=1,
    topn=20,
    exclude_seen=True,
    diversity_penalty=0.15,
    freshness_boost=True,
    allowed_content={'communities', 'blog'}
)
```

## Support

For issues or questions:
1. Check logs: `tail -f logs/django.log`
2. Run health check: `python manage.py shell` → `from recommend.services import get_recommendation_health; print(get_recommendation_health())`
3. Verify data: `python manage.py shell` → `from recommend.models import Interaction; print(Interaction.objects.count())`
