from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from accounts.models import Subscription
from communities.models import Community
from django.contrib.auth import get_user_model
from blog.models import Post
from communities.models import CommunityPost
from accounts.models import WordListGame
from django.db.models import Count


def main_home_view(request):
    return render(request, 'index.html')

@login_required
def dashboard_view(request):
    blog_pages = ['blogs', 'view_post', 'create_post', 'moderation_dashboard']
    community_pages = ['communities', 'create_community', 'view_community']
    subscription_pages = ['subscriptions', 'subscription_detail']

    # Recently played (top 5 recent games by updated time, most recent first)
    recent_games = WordListGame.objects.select_related('user').order_by('-updated_at')[:5]

    # Popular communities (for sidebar)
    popular_communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')[:6]

    return render(request, "dashboardhome.html", {
        'blog_pages': blog_pages,
        'community_pages': community_pages,
        'subscription_pages': subscription_pages,
        'recent_games': recent_games,
        'popular_communities': popular_communities,
    })


@login_required
def community_posts_api(request):
    """API endpoint to return community posts paginated and sorted.

    Query params:
      - sort: 'latest' (default), 'engaged', 'popular'
      - offset: integer
      - limit: integer
    Returns JSON list of posts with minimal fields.
    """
    sort = request.GET.get('sort', 'latest')
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0
    try:
        limit = int(request.GET.get('limit', 10))
    except ValueError:
        limit = 10

    qs = CommunityPost.objects.select_related('community', 'author')

    if sort == 'engaged':
        # engagement fallback: order by newest (no comments relation), using created_at
        qs = qs.order_by('-created_at')
    elif sort == 'popular':
        # popular communities first (by member count), then newest
        qs = qs.annotate(community_size=Count('community__members')).order_by('-community_size', '-created_at')
    else:
        qs = qs.order_by('-created_at')

    total = qs.count()
    posts = qs[offset:offset+limit]

    result = []
    for p in posts:
        user_liked = request.user in p.likes.all() if request.user.is_authenticated else False
        user_disliked = request.user in p.dislikes.all() if request.user.is_authenticated else False
        user_bookmarked = request.user in p.bookmarks.all() if request.user.is_authenticated else False

        result.append({
            'id': p.id,
            'title': p.title,
            'content': p.content[:240],
            'image': p.image.url if p.image else None,
            'community_id': p.community.id,
            'community_name': p.community.name,
            'community_image': p.community.community_image.url if p.community.community_image else None,
            'author_username': p.author.username,
            'author_avatar': p.author.avatar.url if p.author.avatar else None,
            'created_at': p.created_at.isoformat(),
            'likes_count': p.likes.count(),
            'dislikes_count': p.dislikes.count(),
            'bookmarks_count': p.bookmarks.count(),
            'user_liked': user_liked,
            'user_disliked': user_disliked,
            'user_bookmarked': user_bookmarked,
        })

    return JsonResponse({'total': total, 'offset': offset, 'limit': limit, 'posts': result})

def communities_view(request):
    # Categories for the bubble scroller
    categories = [
        ('all', 'All'),
        ('technology', 'Technology'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('lifestyle', 'Lifestyle'),
        ('gaming', 'Gaming'),
        ('photography', 'Photography'),
        ('writing', 'Writing'),
        ('music', 'Music'),
    ]

    # Fetch all communities, newest first
    communities = Community.objects.all().order_by('category', 'name')

    return render(request, 'communities/communities_list.html', {
        'categories': categories,
        'communities': communities
    })

@login_required
def toggle_subscription(request, community_id=None, author_id=None):
    from .models import Subscription
    from communities.models import Community
    from blog.models import Post

    user = request.user

    if community_id:
        community = get_object_or_404(Community, id=community_id)
        sub, created = Subscription.objects.get_or_create(user=user, community=community)
        if not created:  # already exists → unsubscribe
            sub.delete()

    elif author_id:
        author = get_object_or_404(get_user_model(), id=author_id)
        sub, created = Subscription.objects.get_or_create(user=user, author=author)
        if not created:
            sub.delete()

    return redirect('subscriptions')
