# Machine Learning Recommendation System

## Overview

The Lupify recommendation engine provides personalized "For You" recommendations based on user gameplay behavior and interests. The system uses a lightweight, dependency-free collaborative filtering approach with optional advanced ML support.

## Architecture

### 1. **Onboarding Modal**
When users first visit the dashboard, they see an interests selection modal allowing them to choose from:
- Word Games
- Puzzle Games
- Strategy Games
- Casual Games
- Trivia
- Educational

This provides the ML system with a warm-start signal for initial recommendations.

### 2. **Data Models**

#### `UserInterests`
Stores user's selected game interests and onboarding completion status:
```python
user               # OneToOne to CustomUser
categories         # JSONField: ['word', 'puzzle', ...]
completed_onboarding  # Boolean flag
```

#### `Interaction`
Records every user action with games:
```python
user               # ForeignKey to CustomUser
content_type       # ContentType (points to WordListGame, LetterSetGame, etc.)
object_id          # ID of the game object
action             # 'play', 'like', 'view', 'complete'
value              # Float weight (importance of action, default 1.0)
created_at         # Timestamp
```

#### `Recommendation`
Pre-computed recommendations for each user (refreshed periodically):
```python
user               # ForeignKey to CustomUser
content_type       # ContentType (points to recommended game)
object_id          # ID of recommended game
score              # Float score (higher = more relevant)
created_at         # Timestamp
```

### 3. **Recommendation Algorithm**

The baseline uses **item-based collaborative filtering**:

1. **Interaction Aggregation**: Build user-item and item-user matrices from recent interactions (default: 90 days)
2. **Similarity Computation**: Calculate Jaccard similarity between items based on shared users
3. **Scoring**: For each user, score unseen items by similarity to items they've already played
4. **Popularity Fallback**: If no similarity data exists, recommend by item popularity

**Example**:
- User A played games [1, 2, 3]
- User B played games [2, 3, 4]
- Similarity(1, 4) is computed from co-players
- When recommending to User A, game 4 gets scored based on similarity to games 1, 2, 3

### 4. **Offline Computation Pipeline**

```bash
python manage.py compute_recommendations --days 90 --topn 12
```

This command:
- Loads interactions from the last N days
- Computes item-item similarities
- Generates top-N recommendations per user
- Clears old recommendations and inserts new ones atomically

**Output**: 
```
Loading interactions...
Found 42 users and 156 items
Computing item similarities (approx)...
Scoring candidates for users...
Saving recommendations...
Wrote 504 recommendation rows
```

### 5. **API Endpoints**

#### GET `/recommend/for-you/`
Returns cached recommendations for the logged-in user.
```json
{
  "results": [
    {
      "content_type_id": 15,
      "object_id": 42,
      "score": 0.85
    },
    ...
  ]
}
```

#### GET `/recommend/interests/`
Fetch user's selected interests and onboarding status.
```json
{
  "categories": ["word", "puzzle"],
  "completed_onboarding": true
}
```

#### POST `/recommend/interests/save/`
Save user's interest selections and mark onboarding complete.
```json
{
  "categories": ["word", "puzzle", "casual"]
}
```

### 6. **Frontend Integration**

**Dashboard ("For You" Section)**:
- Displayed after interests modal if recommendations exist
- Shows top-12 games with scores
- "Refresh" button to reload recommendations (cached for 60 seconds)

**Interests Modal**:
- Shown on first dashboard visit (if `completed_onboarding` is false)
- User selects interests and clicks "Save" to onboard
- "Skip" button allows bypassing onboarding

### 7. **Recording Interactions**

To record a game play, use the utility function:

```python
from recommend.utils import record_game_play

game = WordListGame.objects.get(id=123)
record_game_play(user=request.user, game_obj=game, action='play', value=1.0)
```

### 8. **Production Improvements**

#### A. Advanced ML Models
- **ALS (Alternating Least Squares)**: Install `implicit` library for matrix factorization
- **Embeddings**: Use word2vec-like embeddings to find semantic game similarity
- **Deep Learning**: Implement a neural collaborative filtering model using PyTorch/TensorFlow

#### B. Real-time Updates
- Use Celery + Redis for async recommendation computation
- Schedule `compute_recommendations` with Celery Beat (e.g., hourly or nightly)
- Implement incremental updates instead of full recompute

#### C. Serving & Caching
- Cache recommendations in Redis for sub-100ms response times
- Implement A/B testing to measure recommendation quality
- Track CTR (click-through rate) on recommended games

#### D. Personalization Signals
- Weight recent plays more heavily (time decay)
- Track game abandonment and completion rates
- Incorporate user's success rate (score earned per game)
- Consider social signals (which games friends play)

#### E. Evaluation Metrics
- **Precision@K**: % of top-K recommendations user actually plays
- **Recall@K**: % of games user plays that appear in top-K
- **NDCG**: Normalized Discounted Cumulative Gain (ranking quality)
- **Diversity**: Ensure recommendations span multiple categories

### 9. **Testing**

Run the recommendation tests:
```bash
python manage.py test recommend --verbosity=2
```

Tests cover:
- Interest onboarding (save/load)
- For You API responses
- Interaction recording
- Game categorization

## Usage Workflow

### For Users:
1. First dashboard visit → Interests modal appears
2. Select interests → Click "Save"
3. "For You" section loads with personalized recommendations
4. Click "Refresh" to reload recommendations
5. Play recommended games → Interactions recorded automatically

### For Developers:
1. Ensure games record interactions when played (use `record_game_play()`)
2. Periodically run `compute_recommendations` (via Celery Beat or cron)
3. Monitor recommendation quality via logs and user metrics

## Configuration

### settings.py
```python
INSTALLED_APPS = [
    ...
    'recommend',
    ...
]

# Caching for "For You" recommendations (60 seconds)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### Customization
Edit `recommend/models.py` `GAME_CATEGORIES` to add/remove interest types:
```python
GAME_CATEGORIES = [
    ('word', 'Word Games'),
    ('puzzle', 'Puzzle Games'),
    # Add new categories here
]
```

## Future Enhancements

- [ ] Support for user-provided ratings (explicit feedback)
- [ ] Trending recommendations (what's popular this week)
- [ ] Category-specific recommendations
- [ ] "People like you also played" social recommendations
- [ ] Seasonal/event-based recommendations
- [ ] Recommendation explanations ("You liked Word Games, so...")

