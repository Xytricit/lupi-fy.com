from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Project, Purchase
from decimal import Decimal

User = get_user_model()


class MarketplaceTestCase(TestCase):
    """Test marketplace functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123'
        )
    
    def test_create_project(self):
        """Test project creation"""
        project = Project.objects.create(
            creator=self.creator,
            title='Test Project',
            description='Test description',
            short_description='Test',
            price=Decimal('9.99'),
            category='action',
            status='approved'
        )
        
        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(project.price, Decimal('9.99'))
    
    def test_purchase_flow(self):
        """Test purchase workflow"""
        project = Project.objects.create(
            creator=self.creator,
            title='Test Project',
            description='Test',
            short_description='Test',
            price=Decimal('9.99'),
            category='action',
            status='approved'
        )
        
        purchase = Purchase.objects.create(
            project=project,
            buyer=self.user,
            price_paid=project.price,
            payment_method='free',
            creator_earnings=project.price * Decimal('0.9'),
            platform_fee=project.price * Decimal('0.1')
        )
        
        purchase.complete_purchase()
        
        self.assertEqual(purchase.status, 'completed')
        self.assertTrue(project.can_download(self.user))
    
    def test_free_project_purchase(self):
        """Test purchasing free project"""
        project = Project.objects.create(
            creator=self.creator,
            title='Free Project',
            description='Free test',
            short_description='Free',
            price=Decimal('0.00'),
            is_free=True,
            category='action',
            status='approved'
        )
        
        self.assertTrue(project.can_download(self.user))
