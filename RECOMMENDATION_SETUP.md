# AI Recommendation Module - Implementation Summary

## What Was Fixed

### 1. **Robust Error Handling**
   - Added comprehensive try-catch blocks throughout the recommendation pipeline
   - Model inference failures now gracefully fall back to next layer instead of crashing
   - Cold-start users (new users with no interactions) now trigger fallback instead of returning empty

### 2. **Dependency Management**
   - Added `_require_deps()` checks to verify torch/numpy are installed
   - System works without PyTorch (falls back to collaborative/content-based)
   - Clear error messages when dependencies are missing

### 3. **Model Training**
   - Created `train_recommender` management command
   - Supports customizable parameters (epochs, embedding dims, learning rate, batch size)
   - Can train on recent data only (--days flag)
   - Saves model to `data/recommend/torch_recommender_hybrid.pt`

### 4. **Multi-Layer Fallback**
   - Layer 1: AI-Powered (PyTorch hybrid model)
   - Layer 2: Collaborative Filtering (stored recommendations)
   - Layer 3: Content-Based (tag/category matching)
   - Layer 4: Popularity-Based (always works)
   - Each layer automatically triggers if previous fails

### 5. **Freshness & Diversity**
   - Recent items (< 7 days) get +50% score boost
   - Similar items penalized to ensure diverse recommendations
   - Configurable diversity penalty (default 0.15)

## How to Use

### Step 1: Install Dependencies
```bash
pip install torch numpy
```

### Step 2: Generate Interaction Data
Users interact with content naturally:
- View blog posts, community posts, games
- Like/dislike content
- Bookmark content
- Play games

These are automatically tracked.

### Step 3: Train the Model
```bash
python manage.py train_recommender
```

Optional parameters:
```bash
python manage.py train_recommender --days 30 --epochs 20 --emb-dim 256
```

### Step 4: Use Recommendations
Automatically used in:
- Dashboard "For you" feed
- Search results fallback
- API endpoints with `sort=foryou`

## Architecture

```
Recommendation Request
    ↓
[Layer 1: AI Model] → Success? Return
    ↓ Fail
[Layer 2: Collaborative] → Success? Return
    ↓ Fail
[Layer 3: Content-Based] → Success? Return
    ↓ Fail
[Layer 4: Popularity] → Always returns results
```

## Key Features

✅ **Hybrid Approach**: Combines collaborative + content-based filtering
✅ **Cold-Start Handling**: Works for new users and items
✅ **Freshness Boost**: Recent content gets higher scores
✅ **Diversity**: Prevents similar items from dominating results
✅ **Fallback Layers**: Always returns recommendations
✅ **Health Monitoring**: Track system status and failures
✅ **Circuit Breaker**: Prevents cascading failures
✅ **Caching**: Reduces computation overhead

## Files Modified/Created

### Modified:
- `recommend/ml/torch_recommender_hybrid.py` - Added error handling and fallbacks

### Created:
- `recommend/management/commands/train_recommender.py` - Training command
- `recommend/management/__init__.py` - Package marker
- `recommend/management/commands/__init__.py` - Package marker
- `recommend/README_RECOMMENDATIONS.md` - Complete documentation

## Testing

### Check if model is trained:
```bash
ls data/recommend/torch_recommender_hybrid.pt
```

### Check interaction data:
```bash
python manage.py shell
from recommend.models import Interaction
print(f"Total interactions: {Interaction.objects.count()}")
```

### Check recommendation health:
```bash
python manage.py shell
from recommend.services import get_recommendation_health
print(get_recommendation_health())
```

### Get recommendations for a user:
```bash
python manage.py shell
from recommend.services import get_recommendations
recs = get_recommendations(user_id=1, content_types=['communities'], topn=10)
print(recs)
```

## Next Steps

1. **Ensure users have interactions** - They should naturally interact with content
2. **Train the model** - Run `python manage.py train_recommender`
3. **Monitor performance** - Check health status and logs
4. **Retrain periodically** - Weekly or after major activity spikes
5. **Tune parameters** - Adjust embedding dimensions based on performance

## Troubleshooting

**Model not training?**
- Check torch/numpy installed: `python -c "import torch; import numpy"`
- Verify interaction data exists: `python manage.py shell` → `from recommend.models import Interaction; print(Interaction.objects.count())`

**Recommendations not showing?**
- Model may not be trained - run `python manage.py train_recommender`
- Check model file exists: `ls data/recommend/torch_recommender_hybrid.pt`
- Check logs for errors

**Slow recommendations?**
- Reduce embedding dimensions: `python manage.py train_recommender --emb-dim 64`
- Train on recent data only: `python manage.py train_recommender --days 30`
- Enable Redis caching in Django settings

## Support

See `recommend/README_RECOMMENDATIONS.md` for detailed documentation and API reference.
