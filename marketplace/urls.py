from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # ========================================================================
    # PUBLIC PAGES
    # ========================================================================
    
    # Main marketplace home/browse
    path('', views.marketplace_home, name='home'),
    
    
    # ========================================================================
    # CREATOR ACTIONS - Require login
    # ========================================================================
    
    # Upload new project for sale
    path('upload/', views.upload_project, name='upload'),
    
    # Creator dashboard with analytics
    path('creator/', views.creator_dashboard, name='creator_dashboard'),
    
    
    # ========================================================================
    # USER LIBRARY
    # ========================================================================
    
    # User's purchased projects library
    path('library/', views.user_library, name='library'),
    
    
    # ========================================================================
    # API ENDPOINTS - AJAX calls from frontend
    # ========================================================================
    
    # Purchase/buy a project
    path('api/purchase/<uuid:project_id>/', views.purchase_project, name='api_purchase'),
    
    # Download purchased project
    path('download/<uuid:project_id>/', views.download_project, name='download'),
    
    # Add to wishlist
    path('api/wishlist/add/<uuid:project_id>/', views.add_to_wishlist, name='api_wishlist_add'),
    
    # Remove from wishlist
    path('api/wishlist/remove/<uuid:project_id>/', views.remove_from_wishlist, name='api_wishlist_remove'),
    
    # Submit review
    path('api/review/<uuid:project_id>/', views.submit_review, name='api_review'),
    
    # Search projects
    path('api/search/', views.search_projects, name='api_search'),
    
    # Request payout (for creators)
    path('api/request-payout/', views.request_payout, name='api_request_payout'),
    
    
    # ========================================================================
    # ADMIN MODERATION - Staff only
    # ========================================================================
    
    # Approve pending project
    path('admin/approve/<uuid:project_id>/', views.admin_approve_project, name='admin_approve'),
    
    # Reject pending project
    path('admin/reject/<uuid:project_id>/', views.admin_reject_project, name='admin_reject'),
    
    
    # ========================================================================
    # CATCH-ALL - Must come LAST
    # ========================================================================
    
    # Individual project detail page
    path('<slug:slug>/', views.project_detail, name='project_detail'),
]
