from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Community, CommunityPost
from .forms import CommunityForm, CommunityPostForm
from accounts.models import Subscription


# -------------------------------
# List all communities
# -------------------------------
def communities_list(request):
    communities = Community.objects.all().order_by('category', '-created_at')
    categories = Community.CATEGORY_CHOICES
    return render(request, 'communities/communities_list.html', {
        'communities': communities,
        'categories': categories
    })


# -------------------------------
# Create a new community
# -------------------------------
@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user
            community.save()
            community.members.add(request.user)  # Auto join

            # Add subscription for this user
            Subscription.objects.get_or_create(user=request.user, community=community)

            return redirect('communities_list')
    else:
        form = CommunityForm()
    return render(request, 'communities/create_community.html', {'form': form})


# -------------------------------
# Toggle join/leave a community
# -------------------------------
@login_required
def toggle_join_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.user in community.members.all():
        community.members.remove(request.user)
        # Remove subscription
        Subscription.objects.filter(user=request.user, community=community).delete()
    else:
        community.members.add(request.user)
        # Add subscription
        Subscription.objects.get_or_create(user=request.user, community=community)

    return redirect('communities_list')


# -------------------------------
# Community detail view
# -------------------------------
def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    posts = community.posts.all()
    members = community.members.all()
    admins = [community.creator]

    # Handle join/leave from detail page
    if request.method == "POST" and request.user.is_authenticated:
        action = request.POST.get("action")
        if action == "join":
            community.members.add(request.user)
            Subscription.objects.get_or_create(user=request.user, community=community)
        elif action == "leave":
            community.members.remove(request.user)
            Subscription.objects.filter(user=request.user, community=community).delete()
        return redirect("community_detail", community_id=community.id)

    return render(request, "communities/community_detail.html", {
        "community": community,
        "posts": posts,
        "members": members,
        "admins": admins,
    })


# -------------------------------
# Save or unsave a community
# -------------------------------
@login_required
def save_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    user = request.user

    if community in user.saved_communities.all():
        user.saved_communities.remove(community)
        messages.success(request, "Removed from saved communities.")
    else:
        user.saved_communities.add(community)
        messages.success(request, "Saved successfully.")

    return redirect('community_detail', community_id=community.id)


# -------------------------------
# Create a community post
# -------------------------------
@login_required
def create_community_post(request, community_id=None):
    all_communities = Community.objects.all().order_by('category', 'name')
    selected_community = get_object_or_404(Community, id=community_id) if community_id else None

    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            community_id_from_form = request.POST.get("community")
            post.community = get_object_or_404(Community, id=community_id_from_form)
            post.author = request.user
            post.save()
            return redirect('community_detail', community_id=post.community.id)
    else:
        form = CommunityPostForm()

    return render(request, 'communities/create_community_post.html', {
        'form': form,
        'communities': all_communities,
        'selected_community': selected_community,
    })


# -------------------------------
# Generic community post creation
# -------------------------------
@login_required
def create_community_post_generic(request):
    all_communities = Community.objects.all().order_by('category', 'name')

    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            community_id_from_form = request.POST.get("community")
            post.community = get_object_or_404(Community, id=community_id_from_form)
            post.author = request.user
            post.save()
            return redirect('community_detail', community_id=post.community.id)
    else:
        form = CommunityPostForm()

    return render(request, 'communities/create_community_post.html', {
        'form': form,
        'communities': all_communities,
        'selected_community': None,
    })


# -------------------------------
# Community post detail
# -------------------------------
def community_post_detail(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    return render(request, 'communities/community_post_detail.html', {
        'post': post,
    })
