"""YouTube-like Recommendation Engine - Per-User Ranking System."""

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Q, Count, Avg, F
from datetime import timedelta
import random

from recommend.models import Interaction, Recommendation, UserInterests


# ============================================================================
# 1. USER PROFILE MANAGEMENT
# ============================================================================

class UserProfile:
    """Manages per-user interest vectors and engagement metrics."""
    
    def __init__(self, user):
        self.user = user
        self.interests, _ = UserInterests.objects.get_or_create(user=user)
        self._init_vectors()
    
    def _init_vectors(self):
        """Initialize interest vectors for all content types."""
        self.interest_vector = {
            'game': self._build_game_vector(),
            'blog': self._build_blog_vector(),
            'community': self._build_community_vector(),
        }
        self.skip_rate = self._calculate_skip_rate()
        self.avg_engagement_time = self._calculate_avg_engagement()
        self.active_hours = self._identify_active_hours()
    
    def _build_game_vector(self):
        """Build interest vector for games from user selections."""
        vector = {}
        for cat in self.interests.game_categories:
            vector[cat] = 1.0
        return vector or {'casual': 0.5}
    
    def _build_blog_vector(self):
        """Build interest vector for blog posts from tags."""
        vector = {}
        for tag in self.interests.blog_tags:
            vector[tag] = 1.0
        return vector or {'technology': 0.3, 'lifestyle': 0.2}
    
    def _build_community_vector(self):
        """Build interest vector for communities from tags."""
        vector = {}
        for tag in self.interests.community_tags:
            vector[tag] = 1.0
        return vector or {'gaming': 0.3}
    
    def _calculate_skip_rate(self):
        """Calculate % of content user skipped in last 30 days."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        interactions = Interaction.objects.filter(
            user=self.user,
            created_at__gte=thirty_days_ago
        )
        total = interactions.count()
        if total == 0:
            return 0.1
        skipped = interactions.filter(action='skip').count()
        return skipped / total if total > 0 else 0.1
    
    def _calculate_avg_engagement(self):
        """Average engagement duration in seconds."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        avg = Interaction.objects.filter(
            user=self.user,
            created_at__gte=thirty_days_ago
        ).aggregate(avg_val=Avg('value'))['avg_val']
        return avg or 120.0
    
    def _identify_active_hours(self):
        """Identify when user is most active (0-23)."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        interactions = Interaction.objects.filter(
            user=self.user,
            created_at__gte=thirty_days_ago
        ).values('created_at__hour').annotate(count=Count('id')).order_by('-count')
        
        if interactions:
            return [h['created_at__hour'] for h in interactions[:3]]
        return [18, 19, 20]


# ============================================================================
# 2. CANDIDATE GENERATION
# ============================================================================

class CandidateGenerator:
    """Generates candidate set for ranking."""
    
    @staticmethod
    def generate_candidates(user, content_type='mixed', limit=200):
        """
        Generate diversified candidate pool.
        Sources: interest-based, collaborative, subscriptions, exploration
        """
        candidates = []
        
        if content_type in ('mixed', 'blog'):
            candidates.extend(CandidateGenerator._interest_based_candidates(user, 'blog', 80))
            candidates.extend(CandidateGenerator._collaborative_candidates(user, 'blog', 40))
            candidates.extend(CandidateGenerator._exploration_candidates(user, 'blog', 10))
        
        if content_type in ('mixed', 'community'):
            candidates.extend(CandidateGenerator._interest_based_candidates(user, 'community', 80))
            candidates.extend(CandidateGenerator._collaborative_candidates(user, 'community', 40))
            candidates.extend(CandidateGenerator._exploration_candidates(user, 'community', 10))
        
        # Deduplicate
        seen = set()
        dedup = []
        for c in candidates:
            key = (c['content_type_id'], c['object_id'])
            if key not in seen:
                seen.add(key)
                dedup.append(c)
        
        return dedup[:limit]
    
    @staticmethod
    def _interest_based_candidates(user, content_type, limit):
        """Fetch content matching user's interests."""
        profile = UserProfile(user)
        
        if content_type == 'blog':
            interests = profile.interests.blog_tags
            if not interests:
                # Return recent posts if no interests
                from blog.models import Post
                posts = Post.objects.all().order_by('-created')[:limit]
                candidates = []
                for p in posts:
                    ct = ContentType.objects.get_for_model(p)
                    candidates.append({
                        'content_type_id': ct.id,
                        'object_id': p.id,
                        'type': 'blog'
                    })
                return candidates
            
            from blog.models import Post
            posts = Post.objects.filter(
                tags__icontains=interests[0] if interests else ''
            ).order_by('-created')[:limit]
            
            candidates = []
            for p in posts:
                ct = ContentType.objects.get_for_model(p)
                candidates.append({
                    'content_type_id': ct.id,
                    'object_id': p.id,
                    'type': 'blog'
                })
            return candidates
        
        elif content_type == 'community':
            interests = profile.interests.community_tags
            if not interests:
                from communities.models import CommunityPost
                posts = CommunityPost.objects.all().order_by('-created_at')[:limit]
                candidates = []
                for p in posts:
                    ct = ContentType.objects.get_for_model(p)
                    candidates.append({
                        'content_type_id': ct.id,
                        'object_id': p.id,
                        'type': 'community'
                    })
                return candidates
            
            from communities.models import CommunityPost
            posts = CommunityPost.objects.all().order_by('-created_at')[:limit]
            
            candidates = []
            for p in posts:
                ct = ContentType.objects.get_for_model(p)
                candidates.append({
                    'content_type_id': ct.id,
                    'object_id': p.id,
                    'type': 'community'
                })
            return candidates
    
    @staticmethod
    def _collaborative_candidates(user, content_type, limit):
        """Find content watched by similar users."""
        # Simplified: get similar users based on interests
        profile = UserProfile(user)
        candidates = []
        
        if content_type == 'blog':
            interests = profile.interests.blog_tags
            if interests:
                from blog.models import Post
                posts = Post.objects.filter(
                    tags__icontains=interests[0]
                ).order_by('-created')[:limit]
                
                for p in posts:
                    ct = ContentType.objects.get_for_model(p)
                    candidates.append({
                        'content_type_id': ct.id,
                        'object_id': p.id,
                        'type': 'blog',
                        'collaborative': True
                    })
        
        return candidates
    
    @staticmethod
    def _exploration_candidates(user, content_type, limit):
        """Exploration pool: random content for testing (5% of feed)."""
        candidates = []
        
        if content_type == 'blog':
            from blog.models import Post
            all_posts = Post.objects.all().order_by('?')[:limit * 2]
            
            for p in all_posts[:limit]:
                ct = ContentType.objects.get_for_model(p)
                candidates.append({
                    'content_type_id': ct.id,
                    'object_id': p.id,
                    'type': 'blog',
                    'exploration': True
                })
        
        elif content_type == 'community':
            from communities.models import CommunityPost
            all_posts = CommunityPost.objects.all().order_by('?')[:limit * 2]
            
            for p in all_posts[:limit]:
                ct = ContentType.objects.get_for_model(p)
                candidates.append({
                    'content_type_id': ct.id,
                    'object_id': p.id,
                    'type': 'community',
                    'exploration': True
                })
        
        return candidates


# ============================================================================
# 3. SCORING ENGINE
# ============================================================================

class ScoringEngine:
    """Personalized scoring for candidates."""
    
    # Weights (must sum to 1.0)
    WEIGHTS = {
        'predicted_watch_time': 0.40,
        'predicted_retention': 0.25,
        'session_extension': 0.15,
        'user_interest_match': 0.15,
        'creator_affinity': 0.05,
    }
    
    @staticmethod
    def score_candidate(candidate, user):
        """
        Compute personalized score for a candidate.
        score = weighted sum of signals
        """
        profile = UserProfile(user)
        
        watch_time = ScoringEngine._predict_watch_time(candidate, profile)
        retention = ScoringEngine._predict_retention(candidate, profile)
        session_ext = ScoringEngine._predict_session_extension(candidate, profile)
        interest_match = ScoringEngine._compute_interest_match(candidate, profile)
        creator_affinity = ScoringEngine._compute_creator_affinity(candidate, user)
        
        score = (
            watch_time * ScoringEngine.WEIGHTS['predicted_watch_time'] +
            retention * ScoringEngine.WEIGHTS['predicted_retention'] +
            session_ext * ScoringEngine.WEIGHTS['session_extension'] +
            interest_match * ScoringEngine.WEIGHTS['user_interest_match'] +
            creator_affinity * ScoringEngine.WEIGHTS['creator_affinity']
        )
        
        # Apply suppression rules
        score = ScoringEngine._apply_suppression(candidate, score)
        
        return max(0, score)
    
    @staticmethod
    def _predict_watch_time(candidate, profile):
        """Predict how long user will watch this content (0-1)."""
        # Simplified: assume 120s average, user's avg engagement / 120
        return min(1.0, profile.avg_engagement_time / 120.0)
    
    @staticmethod
    def _predict_retention(candidate, profile):
        """Predict retention curve (0-1)."""
        # Inverse of skip rate
        return 1.0 - profile.skip_rate
    
    @staticmethod
    def _predict_session_extension(candidate, profile):
        """Predict if this content extends the session (0-1)."""
        # Exploration items: higher session extension
        if candidate.get('exploration'):
            return 0.7
        return 0.5
    
    @staticmethod
    def _compute_interest_match(candidate, profile):
        """Compute match with user interests (0-1)."""
        content_type = candidate.get('type', 'unknown')
        
        if content_type == 'blog':
            vector = profile.interest_vector.get('blog', {})
            if vector:
                return min(1.0, sum(vector.values()) / len(vector))
        elif content_type == 'community':
            vector = profile.interest_vector.get('community', {})
            if vector:
                return min(1.0, sum(vector.values()) / len(vector))
        
        return 0.5
    
    @staticmethod
    def _compute_creator_affinity(candidate, user):
        """Compute affinity with creator (0-1)."""
        # Simplified: count past interactions with this creator
        interactions = Interaction.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return min(1.0, interactions / 50.0)
    
    @staticmethod
    def _apply_suppression(candidate, score):
        """Apply suppression rules to kill low-engagement content."""
        # TODO: fetch engagement metrics for candidate
        # if high CTR but low retention: suppress
        # if high skip rate: suppress
        
        return score


# ============================================================================
# 4. RANKER
# ============================================================================

class Ranker:
    """Rank candidates with diversity and anti-fatigue rules."""
    
    @staticmethod
    def rank(candidates, user, limit=24):
        """
        Rank candidates with:
        - Scoring
        - Diversity rules
        - Anti-fatigue (no creator repetition)
        """
        scored = []
        for c in candidates:
            score = ScoringEngine.score_candidate(c, user)
            scored.append((c, score))
        
        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Apply diversity & anti-fatigue
        ranked = Ranker._apply_diversity_rules(scored, limit)
        
        return ranked
    
    @staticmethod
    def _apply_diversity_rules(scored_candidates, limit):
        """Apply anti-fatigue and diversity rules."""
        result = []
        creator_counts = {}
        
        for candidate, score in scored_candidates:
            if len(result) >= limit:
                break
            
            # Skip if creator has appeared 3x already
            creator_id = candidate.get('creator_id')
            if creator_id:
                count = creator_counts.get(creator_id, 0)
                if count >= 3:
                    continue
                creator_counts[creator_id] = count + 1
            
            result.append(candidate)
        
        return result


# ============================================================================
# 5. RECOMMENDATION ENGINE (MAIN)
# ============================================================================

def compute_recommendations_for_user(user, content_type='mixed', limit=24):
    """
    Main function: compute recommendations for a user.
    
    Flow:
    1. Generate candidates
    2. Score each
    3. Rank with diversity
    4. Store in DB
    5. Return
    """
    # Generate candidates
    candidates = CandidateGenerator.generate_candidates(user, content_type, limit=200)
    
    if not candidates:
        # No candidates: return empty (don't fabricate posts)
        return []
    
    # Rank candidates
    ranked = Ranker.rank(candidates, user, limit)
    
    # Store in Recommendation model
    Recommendation.objects.filter(user=user).delete()
    
    for idx, candidate in enumerate(ranked):
        Recommendation.objects.create(
            user=user,
            content_type_id=candidate['content_type_id'],
            object_id=candidate['object_id'],
            score=idx * -0.1 + 1.0,  # Descending scores
        )
    
    return ranked


# ============================================================================
# 6. FEEDBACK LOOP
# ============================================================================

def record_interaction(user, content_obj, action='view', watch_time=None):
    """
    Record user interaction and update models.
    
    Actions: 'view', 'like', 'share', 'comment', 'skip'
    Signals:
    - Full watch: strong positive
    - Skip <5s: strong negative
    - Like: medium positive
    - Comment: strong positive
    """
    try:
        content_type = ContentType.objects.get_for_model(content_obj)
        
        # Determine signal strength
        signal_strength = {
            'view': 1.0,
            'like': 2.0,
            'comment': 3.0,
            'share': 4.0,
            'skip': -2.0,
        }.get(action, 1.0)
        
        interaction, _ = Interaction.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=content_obj.id,
            action=action,
            defaults={'value': signal_strength}
        )
        
        # Update user profile
        profile = UserProfile(user)
        
        # Trigger re-computation (can be async)
        # compute_recommendations_for_user(user)
        
        return interaction
    except Exception as e:
        print(f"Error recording interaction: {e}")
        return None


# Legacy function for compatibility
def record_game_play(user, game_obj, action="play", value=1.0):
    """Legacy function for recording game plays."""
    return record_interaction(user, game_obj, action, watch_time=value)


def categorize_game(game_obj):
    """Infer game category from game object type."""
    obj_type = type(game_obj).__name__
    if "WordList" in obj_type:
        return "word"
    elif "LetterSet" in obj_type:
        return "word"
    else:
        return "casual"
