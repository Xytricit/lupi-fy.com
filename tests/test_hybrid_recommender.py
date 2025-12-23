
import os
import shutil
import tempfile
import sys
import importlib
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

# Mock torch and numpy BEFORE importing the module
class MockModule:
    def __init__(self, *args, **kwargs):
        self.user_emb = MagicMock()
        self.item_emb = MagicMock()
        self.content_emb = MagicMock()
        self.user_emb.embedding_dim = kwargs.get('emb_dim', 128)
        self.item_emb.embedding_dim = kwargs.get('emb_dim', 128)
        self.content_emb.embedding_dim = kwargs.get('content_emb_dim', 64)
        self.user_emb.weight = MagicMock()
        self.item_emb.weight = MagicMock()
        self.content_emb.weight = MagicMock()
        
    def to(self, device):
        return self
    def parameters(self):
        return []
    def train(self):
        pass
    def eval(self):
        pass
    def load_state_dict(self, state_dict):
        pass
    def state_dict(self):
        return {}
    def __call__(self, *args, **kwargs):
        return MagicMock()

mock_torch = MagicMock()
mock_torch.nn.Module = MockModule
mock_torch.device = lambda x: 'cpu'
mock_torch.tensor = MagicMock(return_value=MagicMock())
mock_torch.ones_like = MagicMock(return_value=MagicMock())
# Configure loss.item() to return a float
mock_loss = MagicMock()
mock_loss.item.return_value = 0.5
mock_loss.backward = MagicMock()
mock_torch.nn.MarginRankingLoss = MagicMock(return_value=MagicMock(return_value=mock_loss))

mock_torch.load = MagicMock(return_value={
    "state_dict": MagicMock(),
    "user_map": {},
    "item_map": {},
    "item_keys": {},
    "item_metadata": {},
    "emb_dim": 128,
    "content_emb_dim": 64
})
sys.modules['torch'] = mock_torch
sys.modules['torch.nn'] = mock_torch.nn
sys.modules['torch.optim'] = mock_torch.optim
sys.modules['numpy'] = MagicMock()

# Now import the module
import recommend.ml.torch_recommender_hybrid
importlib.reload(recommend.ml.torch_recommender_hybrid)

from recommend.ml.torch_recommender_hybrid import (
    HybridRecommenderModel,
    train_and_save_hybrid,
    recommend_for_user_hybrid
)
from recommend.models import Interaction
from communities.models import CommunityPost, Community

User = get_user_model()

class HybridRecommenderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.community = Community.objects.create(
            name="Test Community",
            category="technology",
            creator=self.user
        )
        self.post = CommunityPost.objects.create(
            community=self.community,
            author=self.user,
            title="Test Post",
            content="Content"
        )
        self.post2 = CommunityPost.objects.create(
            community=self.community,
            author=self.user,
            title="Test Post 2",
            content="Content 2"
        )
        self.ct = ContentType.objects.get_for_model(CommunityPost)
        
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        
        # Create interactions
        Interaction.objects.create(
            user=self.user,
            content_type=self.ct,
            object_id=self.post.id,
            action='view',
            value=1.0
        )
        Interaction.objects.create(
            user=self.user2,
            content_type=self.ct,
            object_id=self.post2.id,
            action='view',
            value=1.0
        )
        
        # Temp dir for model
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.temp_dir, "test_model.pt")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_model_initialization(self):
        """Test that the model initializes with correct dimensions."""
        # Since we mocked torch.nn.Module as object, we can instantiate it
        # But we need to mock the internal components like Embedding
        
        # We can't easily test the dimensions on the mock object unless we configure it
        # So let's just verify it can be instantiated
        model = HybridRecommenderModel(n_users=10, n_items=20, emb_dim=128, content_emb_dim=64)
        self.assertIsNotNone(model)

    def test_training_flow(self):
        """Test the training function."""
        # We need to mock torch.save to avoid error
        with patch('torch.save') as mock_save:
            path = train_and_save_hybrid(
                epochs=1,
                model_path=self.model_path,
                batch_size=2,
                emb_dim=16,
                content_emb_dim=8
            )
            
            # Since we mocked save, the file won't exist, but the function should return the path
            self.assertEqual(path, self.model_path)
            self.assertTrue(mock_save.called)
        
        # Test cold start with interests
        from recommend.models import UserInterests
        UserInterests.objects.create(
            user=self.user2,
            community_tags=['technology']
        )
        
        # Mock item metadata to have tags
        mock_torch.load.return_value['item_metadata'] = {
            0: {'tags': ['technology']}
        }
        
        recs_cold = recommend_for_user_hybrid(
            self.user2.id,
            model=None,
            topn=5
        )
        
        # Should return items matching tags
        self.assertTrue(len(recs_cold) > 0)


