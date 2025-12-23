import os
import random
from collections import defaultdict

from django.conf import settings

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except ImportError:  # pragma: no cover
    torch = None
    nn = None
    optim = None

MODEL_DIR = getattr(
    settings,
    "RECOMMEND_MODEL_DIR",
    os.path.join(settings.BASE_DIR, "data", "recommend"),
)
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "torch_recommender.pt")


if nn is not None:

    class MFModel(nn.Module):
        def __init__(self, n_users, n_items, emb_dim=64):
            super().__init__()
            self.user_emb = nn.Embedding(n_users, emb_dim)
            self.item_emb = nn.Embedding(n_items, emb_dim)
            nn.init.normal_(self.user_emb.weight, 0, 0.01)
            nn.init.normal_(self.item_emb.weight, 0, 0.01)

        def forward(self, u_idx, i_idx):
            u = self.user_emb(u_idx)
            v = self.item_emb(i_idx)
            return (u * v).sum(dim=1)

else:
    MFModel = None


def _build_maps(interactions_qs):
    user_map = {}
    item_map = {}
    items_by_user = defaultdict(set)
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
    return user_map, item_map, items_by_user


def _require_torch():
    if torch is None or nn is None or optim is None or MFModel is None:
        raise ImportError(
            "PyTorch is required for the torch recommender. Install torch to use this feature."
        )


def train_and_save(
    days=None, emb_dim=64, epochs=6, lr=0.01, model_path=MODEL_PATH, batch_size=1024
):
    _require_torch()

    # lazy import to avoid requiring Django models at module import time
    from recommend.models import Interaction

    qs = Interaction.objects.all().select_related("content_type")
    if days:
        from django.utils import timezone

        cutoff = timezone.now() - timezone.timedelta(days=int(days))
        # Interaction model uses 'created_at' as the timestamp field
        qs = qs.filter(created_at__gte=cutoff)

    user_map, item_map, items_by_user = _build_maps(qs)
    if not user_map or not item_map:
        return None
    n_users = len(user_map)
    n_items = len(item_map)
    # Prepare positive pairs
    pos_pairs = []
    for r in qs:
        try:
            u = user_map[int(r.user_id)]
            k = f"{r.content_type.app_label}.{r.content_type.model}:{int(r.object_id)}"
            i = item_map.get(k)
            if i is None:
                continue
            pos_pairs.append((u, i))
        except Exception:
            continue

    if not pos_pairs:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MFModel(n_users, n_items, emb_dim).to(device)
    opt = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    user_pos = defaultdict(list)
    for u, i in pos_pairs:
        user_pos[u].append(i)
    users = list(user_pos.keys())
    all_items = list(range(n_items))
    loss_fn = nn.MarginRankingLoss(margin=0.1)
    model.train()
    for epoch in range(epochs):
        random.shuffle(users)
        epoch_loss = 0.0
        steps = 0
        batch = []
        for u in users:
            pos_list = user_pos[u]
            if not pos_list:
                continue
            for pos in pos_list:
                neg = random.choice(all_items)
                # simple negative sampling
                while neg in pos_list:
                    neg = random.choice(all_items)
                batch.append((u, pos, neg))
                if len(batch) >= batch_size:
                    us = torch.tensor(
                        [b[0] for b in batch], dtype=torch.long, device=device
                    )
                    ips = torch.tensor(
                        [b[1] for b in batch], dtype=torch.long, device=device
                    )
                    ins = torch.tensor(
                        [b[2] for b in batch], dtype=torch.long, device=device
                    )
                    pos_scores = model(us, ips)
                    neg_scores = model(us, ins)
                    target = torch.ones_like(pos_scores, device=device)
                    loss = loss_fn(pos_scores, neg_scores, target)
                    opt.zero_grad()
                    loss.backward()
                    opt.step()
                    epoch_loss += loss.item()
                    steps += 1
                    batch = []
        if batch:
            us = torch.tensor([b[0] for b in batch], dtype=torch.long, device=device)
            ips = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device)
            ins = torch.tensor([b[2] for b in batch], dtype=torch.long, device=device)
            pos_scores = model(us, ips)
            neg_scores = model(us, ins)
            target = torch.ones_like(pos_scores, device=device)
            loss = loss_fn(pos_scores, neg_scores, target)
            opt.zero_grad()
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
            steps += 1
        avg_loss = epoch_loss / max(1, steps)
        print(f"Epoch {epoch+1}/{epochs} avg_loss={avg_loss:.4f}")

    # save model + maps
    payload = {
        "state_dict": model.state_dict(),
        "user_map": user_map,
        "item_map": item_map,
        "item_keys": {v: k for k, v in item_map.items()},
        "emb_dim": emb_dim,
    }
    torch.save(payload, model_path)
    return model_path


def load_model(model_path=MODEL_PATH):
    _require_torch()
    if not os.path.exists(model_path):
        return None
    return torch.load(model_path, map_location="cpu")


def recommend_for_user(user_id, model=None, topn=20, exclude_seen=True):
    """Get recommendations for a user using the trained model."""
    try:
        _require_torch()
    except ImportError:
        return []
    
    if model is None:
        model = load_model()
        if model is None:
            return []
    
    try:
        user_map = model["user_map"]
        item_map = model["item_map"]
        item_keys = [model["item_keys"][i] for i in sorted(model["item_keys"].keys())]
        n_items = len(item_map)
    except (KeyError, TypeError):
        return []
    
    # Cold-start: new user, return popular items
    if user_id not in user_map:
        return [(item_keys[i], 0.5) for i in range(min(topn, n_items))]
    
    try:
        emb_dim = model.get("emb_dim", 64)
        m = MFModel(len(user_map), len(item_map), emb_dim)
        m.load_state_dict(model["state_dict"])
        m.eval()
        
        with torch.no_grad():
            uidx = user_map[user_id]
            uvec = m.user_emb(torch.tensor([uidx], dtype=torch.long)).squeeze(0)
            item_embs = m.item_emb.weight
            scores = torch.mv(item_embs, uvec).numpy()
        
        idxs = list(range(len(scores)))
        idxs.sort(key=lambda i: -scores[i])
        
        out = []
        for i in idxs[:topn]:
            out.append((item_keys[i], float(scores[i])))
        return out
    except Exception as e:
        # Fallback on error
        return [(item_keys[i], 0.5) for i in range(min(topn, n_items))]
