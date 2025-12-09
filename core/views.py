from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from accounts.models import Subscription
from communities.models import Community
from django.contrib.auth import get_user_model


def main_home_view(request):
    return render(request, 'index.html')

@login_required
def dashboard_view(request):
    blog_pages = ['blogs', 'view_post', 'create_post', 'moderation_dashboard']
    community_pages = ['communities', 'create_community', 'view_community']
    subscription_pages = ['subscriptions', 'subscription_detail']

    return render(request, "dashboardhome.html", {
        'blog_pages': blog_pages,
        'community_pages': community_pages,
        'subscription_pages': subscription_pages,
    })

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
