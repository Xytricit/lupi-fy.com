from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from urllib.parse import urlencode
import json

from .models import (
    Project, ProjectMedia, Purchase, DownloadAccess, 
    ProjectReview, Wishlist, ProjectAnalytics, CreatorPayout
)


# ============================================================================
# MARKETPLACE HOME - Browse projects
# ============================================================================
def marketplace_home(request):
    """Main marketplace listing page"""
    
    # Filters
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')
    search = request.GET.get('q', '')
    
    # Base queryset - only approved projects
    projects = Project.objects.filter(status='approved')
    
    # Apply filters
    if category:
        projects = projects.filter(category=category)
    
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    # Sorting
    if sort == 'newest':
        projects = projects.order_by('-created_at')
    elif sort == 'popular':
        projects = projects.order_by('-sales_count')
    elif sort == 'top_rated':
        projects = projects.order_by('-rating_average')
    elif sort == 'price_low':
        projects = projects.order_by('price')
    elif sort == 'price_high':
        projects = projects.order_by('-price')
    
    # Featured projects
    featured = Project.objects.filter(
        status='approved',
        is_featured=True,
        featured_until__gte=timezone.now()
    ).order_by('-created_at')[:6]
    
    # Pagination
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    show_pagination = paginator.count > paginator.per_page

    filter_params = {}
    if category:
        filter_params['category'] = category
    if sort and sort != 'newest':
        filter_params['sort'] = sort
    if search:
        filter_params['q'] = search
    filter_query = urlencode(filter_params)
    
    context = {
        'projects': page_obj,
        'featured': featured,
        'category': category,
        'sort': sort,
        'search': search,
        'categories': Project._meta.get_field('category').choices,
        'project_count': paginator.count,
        'page_size': paginator.per_page,
        'show_pagination': show_pagination,
        'filter_query': filter_query,
    }
    
    return render(request, 'marketplace/home.html', context)


# ============================================================================
# PROJECT DETAIL - Individual project page
# ============================================================================
def project_detail(request, slug):
    """Single project detail page with purchase button"""
    
    project = get_object_or_404(Project, slug=slug, status='approved')
    
    # Increment view count (use cache to prevent spam)
    cache_key = f"project_view_{project.id}_{request.session.session_key}"
    from django.core.cache import cache
    if not cache.get(cache_key):
        project.increment_view()
        cache.set(cache_key, True, 3600)
    
    # Check if user owns/purchased this
    user_has_access = False
    user_purchase = None
    if request.user.is_authenticated:
        user_has_access = project.can_download(request.user)
        user_purchase = Purchase.objects.filter(
            project=project,
            buyer=request.user
        ).first()
    
    # Get reviews
    reviews = ProjectReview.objects.filter(
        project=project,
        is_approved=True
    ).select_related('reviewer').order_by('-created_at')[:10]
    
    # Related projects
    related = Project.objects.filter(
        category=project.category,
        status='approved'
    ).exclude(id=project.id).order_by('-sales_count')[:4]
    
    context = {
        'project': project,
        'user_has_access': user_has_access,
        'user_purchase': user_purchase,
        'reviews': reviews,
        'related': related,
    }
    
    return render(request, 'marketplace/project_detail.html', context)


# ============================================================================
# UPLOAD PROJECT - Creator uploads new project
# ============================================================================
@login_required
def upload_project(request):
    """Upload new project for sale"""
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        short_description = request.POST.get('short_description')
        price = request.POST.get('price', 0)
        category = request.POST.get('category')
        game_id = request.POST.get('project_id', '')
        
        # File uploads
        thumbnail = request.FILES.get('thumbnail')
        project_file = request.FILES.get('project_file')
        
        # Create project
        project = Project.objects.create(
            creator=request.user,
            title=title,
            description=description,
            short_description=short_description,
            price=Decimal(price),
            is_free=(Decimal(price) == 0),
            category=category,
            thumbnail=thumbnail,
            project_file=project_file,
            file_size=project_file.size if project_file else 0,
            project_id=game_id if game_id else None,
            status='pending_review'
        )
        
        return JsonResponse({
            'success': True,
            'project_id': str(project.id),
            'message': 'Project submitted for review!',
            'redirect': f'/marketplace/{project.slug}/'
        })
    
    # GET request - show upload form
    game_id = request.GET.get('project_id')
    project_data = {}
    
    context = {
        'project_data': project_data,
        'categories': Project._meta.get_field('category').choices,
    }
    
    return render(request, 'marketplace/upload.html', context)


# ============================================================================
# PURCHASE PROJECT - Handle payment and purchase
# ============================================================================
@login_required
@require_http_methods(['POST'])
def purchase_project(request, project_id):
    """Initiate purchase flow"""
    
    project = get_object_or_404(Project, id=project_id, status='approved')
    
    # Check if already purchased
    existing = Purchase.objects.filter(
        project=project,
        buyer=request.user,
        status='completed'
    ).first()
    
    if existing:
        return JsonResponse({
            'success': False,
            'error': 'You already own this project'
        }, status=400)
    
    # Calculate platform fee (10%)
    platform_fee = project.price * Decimal('0.10')
    creator_earnings = project.price - platform_fee
    
    # Create purchase record
    purchase = Purchase.objects.create(
        project=project,
        buyer=request.user,
        price_paid=project.price,
        payment_method='free' if project.is_free else 'paypal',
        platform_fee=platform_fee,
        creator_earnings=creator_earnings,
        status='pending'
    )
    
    if project.is_free:
        # Complete immediately for free projects
        purchase.complete_purchase()
        
        return JsonResponse({
            'success': True,
            'message': 'Project added to your library!',
            'redirect': f'/marketplace/{project.slug}/'
        })
    else:
        # For paid projects - would integrate with PayPal/Stripe
        payment_url = f"/marketplace/payment/{purchase.id}/"
        
        return JsonResponse({
            'success': True,
            'payment_url': payment_url,
            'purchase_id': str(purchase.id)
        })


# ============================================================================
# DOWNLOAD PROJECT - Secure file download
# ============================================================================
@login_required
def download_project(request, project_id):
    """Generate secure download link and serve file"""
    
    project = get_object_or_404(Project, id=project_id)
    
    # Verify access
    if not project.can_download(request.user):
        return HttpResponseForbidden("You don't have access to this project")
    
    # Get download access record
    access = get_object_or_404(DownloadAccess, project=project, user=request.user)
    
    # Check rate limiting
    from django.core.cache import cache
    cache_key = f"download_limit_{request.user.id}_{project.id}"
    download_count = cache.get(cache_key, 0)
    
    if download_count >= 5:
        return JsonResponse({
            'error': 'Download limit exceeded. Try again in 1 hour.'
        }, status=429)
    
    # Increment download count
    access.download_count += 1
    access.last_download_at = timezone.now()
    access.save()
    
    project.downloads_count += 1
    project.save(update_fields=['downloads_count'])
    
    cache.set(cache_key, download_count + 1, 3600)
    
    # Serve file
    file_path = project.project_file.path
    response = FileResponse(open(file_path, 'rb'), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{project.slug}.zip"'
    
    return response


# ============================================================================
# USER LIBRARY - Show purchased projects
# ============================================================================
@login_required
def user_library(request):
    """User's purchased/owned projects library"""
    
    purchases = Purchase.objects.filter(
        buyer=request.user,
        status='completed'
    ).select_related('project').order_by('-completed_at')
    
    context = {
        'purchases': purchases,
    }
    
    return render(request, 'marketplace/library.html', context)


# ============================================================================
# CREATOR DASHBOARD - Analytics and earnings
# ============================================================================
@login_required
def creator_dashboard(request):
    """Creator analytics dashboard showing sales, revenue, and stats"""
    
    # Get creator's projects
    projects = Project.objects.filter(creator=request.user).annotate(
        total_sales=Count('purchases', filter=Q(purchases__status='completed')),
        total_revenue=Sum('purchases__creator_earnings', filter=Q(purchases__status='completed'))
    )
    
    # Overall stats
    total_revenue = Purchase.objects.filter(
        project__creator=request.user,
        status='completed'
    ).aggregate(total=Sum('creator_earnings'))['total'] or 0
    
    total_sales = Purchase.objects.filter(
        project__creator=request.user,
        status='completed'
    ).count()
    
    # Recent sales
    recent_sales = Purchase.objects.filter(
        project__creator=request.user,
        status='completed'
    ).select_related('project', 'buyer').order_by('-completed_at')[:10]
    
    context = {
        'projects': projects,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'recent_sales': recent_sales,
    }
    
    return render(request, 'marketplace/creator_dashboard.html', context)


# ============================================================================
# REQUEST PAYOUT - Creator requests earnings payout
# ============================================================================
@login_required
@require_http_methods(['POST'])
def request_payout(request):
    """Creator requests payout of earnings"""
    
    amount = Decimal(request.POST.get('amount', 0))
    payout_method = request.POST.get('method', 'paypal')
    payout_email = request.POST.get('email')
    
    # Minimum payout amount
    if amount < 10:
        return JsonResponse({
            'error': 'Minimum payout amount is $10'
        }, status=400)
    
    # Check available balance
    total_earnings = Purchase.objects.filter(
        project__creator=request.user,
        status='completed'
    ).aggregate(total=Sum('creator_earnings'))['total'] or 0
    
    available = total_earnings
    
    if amount > available:
        return JsonResponse({
            'error': f'Insufficient balance. Available: ${available}'
        }, status=400)
    
    # Create payout request
    payout = CreatorPayout.objects.create(
        creator=request.user,
        amount=amount,
        payout_method=payout_method,
        payout_email=payout_email,
        status='pending'
    )
    
    return JsonResponse({
        'success': True,
        'payout_id': str(payout.id),
        'message': 'Payout request submitted. Processing within 3-5 business days.'
    })


# ============================================================================
# ADMIN: APPROVE PROJECT
# ============================================================================
@login_required
def admin_approve_project(request, project_id):
    """Admin approves pending project"""
    
    if not request.user.is_staff:
        return HttpResponseForbidden("Admin access required")
    
    project = get_object_or_404(Project, id=project_id)
    project.status = 'approved'
    project.published_at = timezone.now()
    project.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Project "{project.title}" approved'
    })


# ============================================================================
# ADMIN: REJECT PROJECT
# ============================================================================
@login_required
@require_http_methods(['POST'])
def admin_reject_project(request, project_id):
    """Admin rejects pending project with reason"""
    
    if not request.user.is_staff:
        return HttpResponseForbidden("Admin access required")
    
    project = get_object_or_404(Project, id=project_id)
    reason = request.POST.get('reason', '')
    
    project.status = 'rejected'
    project.rejection_reason = reason
    project.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Project "{project.title}" rejected'
    })


# ============================================================================
# API: ADD TO WISHLIST
# ============================================================================
@login_required
@require_http_methods(['POST'])
def add_to_wishlist(request, project_id):
    """Add project to user's wishlist"""
    
    project = get_object_or_404(Project, id=project_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        project=project
    )
    
    return JsonResponse({
        'success': True,
        'added': created,
        'message': 'Added to wishlist' if created else 'Already in wishlist'
    })


# ============================================================================
# API: REMOVE FROM WISHLIST
# ============================================================================
@login_required
@require_http_methods(['POST'])
def remove_from_wishlist(request, project_id):
    """Remove project from wishlist"""
    
    Wishlist.objects.filter(
        user=request.user,
        project_id=project_id
    ).delete()
    
    return JsonResponse({'success': True})


# ============================================================================
# API: SUBMIT REVIEW
# ============================================================================
@login_required
@require_http_methods(['POST'])
def submit_review(request, project_id):
    """Submit review for purchased project"""
    
    project = get_object_or_404(Project, id=project_id)
    
    # Verify user purchased this
    purchase = get_object_or_404(
        Purchase,
        project=project,
        buyer=request.user,
        status='completed'
    )
    
    rating = int(request.POST.get('rating', 5))
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    
    review, created = ProjectReview.objects.update_or_create(
        project=project,
        reviewer=request.user,
        defaults={
            'rating': rating,
            'title': title,
            'content': content,
            'purchase': purchase
        }
    )
    
    return JsonResponse({
        'success': True,
        'created': created,
        'message': 'Review submitted!' if created else 'Review updated!'
    })


# ============================================================================
# SEARCH API - Advanced search with filters
# ============================================================================
def search_projects(request):
    """API endpoint for advanced search"""
    
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 999999)
    min_rating = request.GET.get('min_rating', 0)
    
    projects = Project.objects.filter(status='approved')
    
    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query)
        )
    
    if category:
        projects = projects.filter(category=category)
    
    projects = projects.filter(
        price__gte=Decimal(min_price),
        price__lte=Decimal(max_price),
        rating_average__gte=Decimal(min_rating)
    )
    
    # Serialize results
    results = []
    for p in projects[:50]:
        results.append({
            'id': str(p.id),
            'slug': p.slug,
            'title': p.title,
            'price': float(p.price),
            'thumbnail': p.thumbnail.url if p.thumbnail else None,
            'rating': float(p.rating_average),
            'sales': p.sales_count,
        })
    
    return JsonResponse({'results': results})
