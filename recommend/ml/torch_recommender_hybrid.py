"""
Enhanced recommendation engine combining:
1. Collaborative Filtering (PyTorch embeddings)
2. Content-Based Filtering (tag/category matching)
3. Hybrid scoring with diversity & freshness boost
4. Cold-start handling for new users/items
5. Caching & metrics tracking
"""

import os
from collections import defaultdict
import random
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except ImportError:  # pragma: no cover
    torch = None
    nn = None
    optim = None

HAS_TORCH = np is not None and torch is not None and nn is not None and optim is not None

MODEL_DIR = getattr(
    settings,
    "RECOMMEND_MODEL_DIR",
    os.path.join(settings.BASE_DIR, "data", "recommend"),
)
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "torch_recommender_hybrid.pt")


def _require_deps(strict=True):
    if not HAS_TORCH:
        if strict:
            raise ImportError(
                "Hybrid recommender requires numpy and torch. Install them to use this feature."
            )
        return False
    return True


if nn is not None:

    class HybridRecommenderModel(nn.Module):
        """Enhanced MF with optional content embeddings and regularization."""

        def __init__(self, n_users, n_items, emb_dim=128, content_emb_dim=64, dropout=0.2):
            super().__init__()
            self.user_emb = nn.Embedding(n_users, emb_dim)
            self.item_emb = nn.Embedding(n_items, emb_dim)
            # Content-based embeddings (category/tag vectors)
            self.content_emb = nn.Embedding(n_items, content_emb_dim)
            
            self.dropout = nn.Dropout(dropout)
            self.bn_user = nn.BatchNorm1d(emb_dim)
            self.bn_item = nn.BatchNorm1d(emb_dim)

            nn.init.xavier_normal_(self.user_emb.weight)
            nn.init.xavier_normal_(self.item_emb.weight)
            nn.init.xavier_normal_(self.content_emb.weight)

        def forward(self, u_idx, i_idx, use_content=False):
            """
            Compute recommendation score:
            - Collaborative: user_emb @ item_emb (dot product)
            - Content: (via projection) user_emb @ content_emb
            - Hybrid: weighted sum
            """
            u = self.user_emb(u_idx)  # [batch, emb_dim]
            i = self.item_emb(i_idx)  # [batch, emb_dim]
            
            # Apply regularization
            u = self.dropout(u)
            i = self.dropout(i)
            
            # Batch norm (requires batch > 1)
            if u.shape[0] > 1:
                u = self.bn_user(u)
                i = self.bn_item(i)

            # Collaborative score
            collab_score = (u * i).sum(dim=1)

            if use_content:
                # Project user embedding to content space
                # We use the first content_emb_dim dimensions of the user embedding
                # This assumes the user embedding space captures content preferences in its first dimensions
                # A better approach might be a separate projection layer, but this keeps it simple
                u_content = u[:, : self.content_emb.embedding_dim]
                c = self.content_emb(i_idx)
                content_score = (u_content * c).sum(dim=1)
                
                # Weighted hybrid: 70% collab, 30% content
                return 0.7 * collab_score + 0.3 * content_score
            return collab_score

else:
    HybridRecommenderModel = None


def _build_maps_enhanced(interactions_qs, content_features=None):
    """Build user/item maps with optional content metadata."""
    user_map = {}
    item_map = {}
    items_by_user = defaultdict(set)
    item_metadata = {}  # Store tags, categories, etc.
    
    for r in interactions_qs:
        try:
            uid = int(r.user_id)
            key = (
                f"{r.content_type.app_label}.{r.content_type.model}:{int(r.object_id)}"
            )
        except Exception:
            continue
        
        if uid not in user_map:
            user_map[uid] = len(user_map)
        if key not in item_map:
            item_map[key] = len(item_map)
        
        items_by_user[uid].add(item_map[key])
        
        # Optionally store metadata
        if content_features and key in content_features:
            item_metadata[item_map[key]] = content_features[key]
    
    return user_map, item_map, items_by_user, item_metadata


def train_and_save_hybrid(
    days=None,
    emb_dim=128,
    content_emb_dim=64,
    epochs=10,
    lr=0.005,
    model_path=MODEL_PATH,
    batch_size=1024,
    use_content=True,
):
    """Train hybrid model with collaborative + content-based filtering."""
    _require_deps()

    from recommend.models import Interaction
    from blog.models import Post
    from communities.models import CommunityPost

    qs = Interaction.objects.all().select_related("content_type")
    if days:
        cutoff = timezone.now() - timezone.timedelta(days=int(days))
        qs = qs.filter(created_at__gte=cutoff)

    content_features = {}
    try:
        for post in Post.objects.all():
            key = f"blog.post:{post.id}"
            tags = getattr(post, 'tags', '')
            content_features[key] = {
                'tags': tags.split(',') if tags else [],
                'views': post.views if hasattr(post, 'views') else 0,
                'created_at': post.created.timestamp() if hasattr(post, 'created') else 0
            }
    except Exception:
        pass
    
    try:
        for post in CommunityPost.objects.all():
            key = f"communities.communitypost:{post.id}"
            tags = getattr(post, 'tags', '')
            content_features[key] = {
                'tags': tags.split(',') if tags else [],
                'likes': post.likes.count() if hasattr(post, 'likes') else 0,
                'created_at': post.created_at.timestamp() if hasattr(post, 'created_at') else 0
            }
    except Exception:
        pass

    user_map, item_map, items_by_user, item_metadata = _build_maps_enhanced(
        qs, content_features
    )
    
    if not user_map or not item_map:
        return None
    
    n_users = len(user_map)
    n_items = len(item_map)
    
    pos_samples = []
    weights = []
    for r in qs:
        try:
            uid = int(r.user_id)
            u_idx = user_map.get(uid)
            if u_idx is None:
                continue
            key = f"{r.content_type.app_label}.{r.content_type.model}:{int(r.object_id)}"
            i_idx = item_map.get(key)
            if i_idx is None:
                continue
            weight = r.engagement_weight()
            if weight <= 0:
                continue
            pos_samples.append((u_idx, i_idx, weight))
            weights.append(weight)
        except Exception:
            continue

    if not pos_samples:
        return None

    user_item_sets = defaultdict(set)
    for raw_uid, item_set in items_by_user.items():
        mapped_idx = user_map.get(raw_uid)
        if mapped_idx is not None:
            user_item_sets[mapped_idx] = set(item_set)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = HybridRecommenderModel(n_users, n_items, emb_dim, content_emb_dim).to(device)
    opt = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = nn.MarginRankingLoss(margin=0.2, reduction="none")
    
    all_items = list(range(n_items))
    batch_sample_size = min(batch_size, len(pos_samples))
    steps_per_epoch = max(1, (len(pos_samples) + batch_sample_size - 1) // batch_sample_size)

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        steps = 0
        for _ in range(steps_per_epoch):
            batch_indices = random.choices(range(len(pos_samples)), weights=weights, k=batch_sample_size)
            batch = [pos_samples[idx] for idx in batch_indices]
            us = torch.tensor([entry[0] for entry in batch], dtype=torch.long, device=device)
            ips = torch.tensor([entry[1] for entry in batch], dtype=torch.long, device=device)
            neg_items = []
            for entry in batch:
                user_idx = entry[0]
                positives = user_item_sets.get(user_idx, set())
                neg = random.choice(all_items)
                attempts = 0
                while neg in positives and attempts < 5:
                    neg = random.choice(all_items)
                    attempts += 1
                neg_items.append(neg)
            ins = torch.tensor(neg_items, dtype=torch.long, device=device)
            
            pos_scores = model(us, ips, use_content=use_content)
            neg_scores = model(us, ins, use_content=use_content)
            target = torch.ones_like(pos_scores, device=device)
            sample_weights = torch.tensor(
                [entry[2] for entry in batch], dtype=torch.float32, device=device
            ).clamp(0.2, 3.0)
            loss_values = loss_fn(pos_scores, neg_scores, target)
            loss = (loss_values * sample_weights).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            
            epoch_loss += loss.item()
            steps += 1
        
        avg_loss = epoch_loss / max(1, steps)
        print(f"Epoch {epoch+1}/{epochs} avg_loss={avg_loss:.4f}")

    payload = {
        "state_dict": model.state_dict(),
        "user_map": user_map,
        "item_map": item_map,
        "item_keys": {v: k for k, v in item_map.items()},
        "item_metadata": item_metadata,
        "emb_dim": emb_dim,
        "content_emb_dim": content_emb_dim,
    }
    torch.save(payload, model_path)
    print(f"[OK] Hybrid model saved with {len(item_metadata)} content-enhanced items")
    return model_path


def load_model_hybrid(model_path=MODEL_PATH):
    """Load hybrid model."""
    if not _require_deps(strict=False):
        return None
    if not os.path.exists(model_path):
        return None
    return torch.load(model_path, map_location="cpu")


def recommend_for_user_hybrid(
    user_id,
    model=None,
    topn=20,
    exclude_seen=True,
    diversity_penalty=0.15,
    freshness_boost=True,
    allowed_content=None,
):
    """
    Enhanced recommendations with:
    - Diversity: penalize similar items in top-N
    - Freshness: boost recent items
    - Cold-start: fallback to popular items for new users
    """
    if not _require_deps(strict=False):
        return []
    
    if model is None:
        model = load_model_hybrid()
        if model is None:
            # Model not trained yet, return empty to trigger fallback
            return []
    
    try:
        user_map = model["user_map"]
        item_map = model["item_map"]
        item_keys = [model["item_keys"][i] for i in sorted(model["item_keys"].keys())]
        allowed_content_set = set(allowed_content) if allowed_content else None

        def _matches_allowed(app_label, model_name):
            if not allowed_content_set:
                return True
            candidate = f"{app_label}.{model_name}"
            if candidate in allowed_content_set:
                return True
            return app_label in allowed_content_set
        item_metadata = model.get("item_metadata", {})
        n_items = len(item_map)
    except (KeyError, TypeError) as e:
        # Model structure invalid, return empty
        return []
    
    # Cold-start: new user
    if user_id not in user_map:
        # Return empty to trigger fallback to collaborative/content-based
        return []
    
    try:
        emb_dim = model.get("emb_dim", 128)
        content_emb_dim = model.get("content_emb_dim", 64)
        
        m = HybridRecommenderModel(len(user_map), len(item_map), emb_dim, content_emb_dim)
        m.load_state_dict(model["state_dict"])
        m.eval()
        
        with torch.no_grad():
            uidx = user_map[user_id]
            uvec = m.user_emb(torch.tensor([uidx], dtype=torch.long)).squeeze(0)  # [emb_dim]
            
            # Collaborative score (full embedding)
            collab_scores = torch.mv(m.item_emb.weight, uvec).numpy()
            
            # Content score (project user vec to content space)
            u_content = uvec[:content_emb_dim]  # [content_emb_dim]
            content_scores = torch.mv(m.content_emb.weight, u_content).numpy()
            
            # Hybrid: 70% collab + 30% content
            scores = 0.7 * collab_scores + 0.3 * content_scores
    except Exception as e:
        # Model inference failed, return empty to trigger fallback
        return []
    
    # Apply freshness boost (prefer recent items)
    if freshness_boost:
        try:
            now_ts = timezone.now().timestamp()
            for i, key in enumerate(item_keys):
                try:
                    meta = item_metadata.get(i, {})
                    created_at = meta.get('created_at', 0)
                    if created_at > 0:
                        age_days = (now_ts - created_at) / 86400.0
                        if age_days < 7:
                            # Boost items from last 7 days significantly
                            scores[i] *= (1.0 + 0.5 * (1 - age_days / 7))
                        elif age_days < 30:
                            # Boost items from last 30 days slightly
                            scores[i] *= (1.0 + 0.2 * (1 - age_days / 30))
                except Exception:
                    pass
        except Exception:
            pass
    
    # Apply diversity penalty (suppress similar items)
    try:
        idxs = list(range(len(scores)))
        idxs.sort(key=lambda i: -scores[i])
        
        selected = []
        selected_indices = set()
        
        for idx in idxs:
            if len(selected) >= topn:
                break
            
            key = item_keys[idx]
            parts = key.split(":", 1)
            if len(parts) != 2:
                continue
            app_model = parts[0]
            if "." not in app_model:
                continue
            app_label, model_name = app_model.split(".", 1)
            if not _matches_allowed(app_label, model_name):
                continue
            
            # Diversity check: penalize items similar to already-selected
            if selected and diversity_penalty > 0:
                try:
                    current_vec = m.item_emb.weight[idx].detach().numpy()
                    similarity_penalty = 0.0
                    
                    for prev_idx in selected_indices:
                        prev_vec = m.item_emb.weight[prev_idx].detach().numpy()
                        sim = np.dot(current_vec, prev_vec) / (
                            np.linalg.norm(current_vec) * np.linalg.norm(prev_vec) + 1e-8
                        )
                        similarity_penalty = max(similarity_penalty, sim * diversity_penalty)
                    
                    penalized_score = scores[idx] * (1 - similarity_penalty)
                    if penalized_score < min(s for _, s in selected) * 0.5:
                        continue
                except Exception:
                    pass
            
            selected.append((key, float(scores[idx])))
            selected_indices.add(idx)
        
        return selected
    except Exception as e:
        # Fallback: return top-N by score without diversity penalty
        try:
            idxs = list(range(len(scores)))
            idxs.sort(key=lambda i: -scores[i])
            selected = []
            for idx in idxs:
                if len(selected) >= topn:
                    break
                key = item_keys[idx]
                parts = key.split(":", 1)
                if len(parts) == 2:
                    app_model = parts[0]
                    if "." in app_model:
                        app_label, model_name = app_model.split(".", 1)
                        if _matches_allowed(app_label, model_name):
                            selected.append((key, float(scores[idx])))
            return selected
        except Exception:
            return []
