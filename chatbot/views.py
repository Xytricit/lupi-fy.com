from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
import json
import requests
from django.core.cache import cache
import os
import re
from datetime import timedelta
from django.utils import timezone

# ============================================================================
# ANALYTICS & USER CONTEXT
# ============================================================================

def get_user_analytics(user):
    """Fetch comprehensive user engagement metrics for AI context."""
    from blog.models import Post as BlogPost
    # communities defines CommunityPost (not Post). Import the correct model.
    from communities.models import CommunityPost, Community
    
    try:
        # Blog post metrics
        blog_posts = BlogPost.objects.filter(author=user)
        blog_post_count = blog_posts.count()
        blog_views = sum(p.views for p in blog_posts) if blog_posts.exists() else 0
        blog_likes = sum(p.likes.count() for p in blog_posts) if blog_posts.exists() else 0
        
        # Community metrics
        # CommunityPost uses `author` as the FK to the user
        community_posts = CommunityPost.objects.filter(author=user)
        community_post_count = community_posts.count()
        community_likes = sum(p.likes.count() for p in community_posts) if community_posts.exists() else 0
        
        # Community membership
        communities = Community.objects.filter(members=user).count()
        
        # Follower metrics (if you have a follow system)
        followers = getattr(user, 'followers', type('obj', (object,), {'count': lambda: 0})()).count()
        following = getattr(user, 'following', type('obj', (object,), {'count': lambda: 0})()).count()
        
        # Recent activity
        days_active = (timezone.now() - user.date_joined).days
        
        # Engagement score
        engagement_score = (blog_views * 0.3) + (blog_likes * 0.5) + (community_likes * 0.4) + (communities * 0.2)
        
        return {
            'blog_posts': blog_post_count,
            'blog_views': blog_views,
            'blog_likes': blog_likes,
            'community_posts': community_post_count,
            'community_likes': community_likes,
            'communities_joined': communities,
            'followers': followers,
            'following': following,
            'days_active': days_active,
            'engagement_score': round(engagement_score, 1),
            'total_posts': blog_post_count + community_post_count,
            'total_engagement': blog_views + blog_likes + community_likes
        }
    except Exception as e:
        return {
            'blog_posts': 0,
            'blog_views': 0,
            'blog_likes': 0,
            'community_posts': 0,
            'community_likes': 0,
            'communities_joined': 0,
            'followers': 0,
            'following': 0,
            'days_active': 0,
            'engagement_score': 0,
            'total_posts': 0,
            'total_engagement': 0
        }

def calculate_user_level(analytics):
    """Calculate creator level based on engagement metrics."""
    engagement = analytics.get('engagement_score', 0)
    posts = analytics.get('total_posts', 0)
    
    if posts == 0:
        return 'Emerging Creator', 1
    elif engagement < 10 and posts < 5:
        return 'Emerging Creator', 1
    elif engagement < 50 and posts < 15:
        return 'Creator', 2
    elif engagement < 200 and posts < 40:
        return 'Creator Plus', 3
    else:
        return 'Creator Pro', 4

def build_lightweight_prompt(user):
    """Build a minimal system prompt for faster models like TinyLlama."""
    return f"You are Lupify AI, a friendly content coach helping creators like {user.username}. Be helpful, concise, and encouraging."

def build_enhanced_prompt(user, analytics, conversation_history):
    """Build an AI system prompt with rich user context."""
    level, level_num = calculate_user_level(analytics)
    
    # Recent conversation context
    recent_messages = conversation_history[-4:] if len(conversation_history) > 0 else []
    recent_context = "\n".join([f"{msg['role'].title()}: {msg['content'][:100]}..." for msg in recent_messages])
    
    prompt = f"""You are Lupify AI, an advanced content coach and creative assistant for the Lupify creator community.
You help creators succeed by providing personalized guidance, insights, and direct action support.

=== USER PROFILE ===
Name: {user.username}
Creator Level: {level} (Tier {level_num}/4)
Member Since: {(timezone.now() - user.date_joined).days} days ago

=== ENGAGEMENT METRICS ===
Blog Posts: {analytics['blog_posts']}
Community Posts: {analytics['community_posts']}
Total Views: {analytics['blog_views']}
Total Engagement: {analytics['total_engagement']} (likes + views)
Communities Joined: {analytics['communities_joined']}
Followers: {analytics['followers']}

=== YOUR ROLE ===
You are a sophisticated AI that combines:
1. **Content Coaching**: Provide specific, actionable feedback on content strategy
2. **Analytics Insights**: Explain what's working, what isn't, and why
3. **Task Execution**: When appropriate, suggest or execute actions using #TASK: commands
4. **Mentorship**: Guide creators from one level to the next with clear milestones
5. **Motivation**: Be encouraging and celebrate wins, no matter how small

=== INTERACTION GUIDELINES ===
- Analyze patterns in their engagement and suggest improvements
- Offer specific content ideas tailored to their niche
- Help them understand what types of posts perform best
- When they ask for help, offer #TASK: commands they can accept
- Be warm, enthusiastic, and genuinely invested in their success
- Keep responses focused (200 words max, unless detailed explanation needed)
- Use their name occasionally to build connection

=== TASK EXECUTION ===
You can suggest tasks using this format: #TASK: [action_name] [parameters]
Available actions:
- #TASK: create_post type:blog|community
- #TASK: open_modal create|settings|analytics
- #TASK: navigate dashboard|profile|communities
- #TASK: view_insights
- #TASK: suggest_community [name/category]

Example: "Want to get started? #TASK: create_post type:blog"

Current Conversation Context:
{recent_context if recent_context else 'New conversation'}

Respond naturally to their message while considering their profile, level, and engagement patterns.
Focus on growth, actionable insights, and making them feel supported in their creative journey."""
    
    return prompt

# ============================================================================
# TASK EXECUTION SYSTEM
# ============================================================================

def extract_tasks(ai_response):
    """Extract task commands from AI response text."""
    task_pattern = r'#TASK:\s*(\w+)\s*([^\n#]*)'
    matches = re.findall(task_pattern, ai_response)
    tasks = []
    for match in matches:
        action, params = match
        param_dict = {}
        # Parse parameters like "type:blog" into dict
        for param in params.split():
            if ':' in param:
                key, val = param.split(':', 1)
                param_dict[key.strip()] = val.strip()
        tasks.append({
            'action': action.strip().lower(),
            'params': param_dict
        })
    return tasks

def validate_task_permission(user, task_action):
    """Validate that user has permission to execute this task."""
    # Basic validation - can be extended
    allowed_actions = [
        'create_post', 'open_modal', 'navigate', 'view_insights', 'suggest_community'
    ]
    return task_action in allowed_actions

def get_task_metadata(task):
    """Generate metadata about a task for frontend execution."""
    action = task['action']
    params = task['params']
    
    task_map = {
        'create_post': {
            'label': 'Create Post',
            'icon': 'pencil',
            'data': {
                'type': params.get('type', 'blog'),
                'url': f"/posts/create/" if params.get('type') == 'blog' else "/communities/post/create/"
            }
        },
        'open_modal': {
            'label': 'Open Settings',
            'icon': 'settings',
            'data': {
                'modal': params.get('modal', 'create'),
                'target': f"#{params.get('modal', 'create')}Modal"
            }
        },
        'navigate': {
            'label': f"Go to {params.get('page', 'dashboard').title()}",
            'icon': 'arrow-right',
            'data': {
                'page': params.get('page', 'dashboard'),
                'urls': {
                    'dashboard': '/dashboard/',
                    'profile': '/accounts/dashboard/',
                    'communities': '/communities/'
                }
            }
        },
        'view_insights': {
            'label': 'View Analytics',
            'icon': 'chart',
            'data': {'url': '/analytics/'}
        },
        'suggest_community': {
            'label': f"Join {params.get('name', 'Community')}",
            'icon': 'users',
            'data': {'community': params.get('name', '')}
        }
    }
    
    return task_map.get(action, {
        'label': action.title(),
        'icon': 'check',
        'data': params
    })

# ============================================================================
# CHATBOT VIEWS
# ============================================================================

@login_required
def chatbot_page(request):
    """Render main chatbot interface with user analytics."""
    analytics = get_user_analytics(request.user)
    level, level_num = calculate_user_level(analytics)
    
    return render(request, 'chatbot/index.html', {
        'username': request.user.username,
        'user_id': request.user.id,
        'analytics': analytics,
        'creator_level': level,
        'level_num': level_num,
    })

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def chat_api(request):
    """Process chat messages with analytics context and task execution."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        user_id = request.user.id
        session_key = f'chatbot_session_{user_id}'
        conversation_history = cache.get(session_key, [])
        
        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Get user context
        analytics = get_user_analytics(request.user)
        
        # Use lightweight prompt for faster models (tinyllama), full prompt for slower ones (mistral)
        model = os.environ.get('OLLAMA_MODEL', 'mistral:latest').lower()
        if 'tinyllama' in model:
            system_prompt = build_lightweight_prompt(request.user)
        else:
            system_prompt = build_enhanced_prompt(request.user, analytics, conversation_history)
        
        # Query AI
        response_text = query_local_ai(user_message, conversation_history, system_prompt)
        
        # Extract any tasks from response
        tasks = extract_tasks(response_text)
        task_metadata = []
        
        for task in tasks:
            if validate_task_permission(request.user, task['action']):
                task_metadata.append(get_task_metadata(task))
        
        # Add response to history
        conversation_history.append({
            'role': 'assistant',
            'content': response_text
        })
        
        # Keep last 30 messages in cache (3-day expiry)
        cache.set(session_key, conversation_history[-30:], 259200)
        
        return JsonResponse({
            'response': response_text,
            'tasks': task_metadata,
            'success': True
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def query_local_ai(user_message, history, system_prompt):
    """Send message to local Ollama AI and get response."""
    try:
        messages = [{'role': 'system', 'content': system_prompt}]
        for msg in history:
            messages.append(msg)
        # Allow overriding the Ollama model via OLLAMA_MODEL env var (e.g. 'tinyllama' or 'tinyllama:latest')
        model = os.environ.get('OLLAMA_MODEL', 'mistral:latest')

        response = requests.post(
            'http://localhost:11434/api/chat',
            json={
                'model': model,
                'messages': messages,
                'stream': False,
                'temperature': 0.7
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get('message', {}).get('content', 'I encountered an error processing your request.')
        else:
            return 'Chatbot service is unavailable. Make sure Ollama is running: `ollama serve`'
    
    except requests.exceptions.ConnectionError:
        return 'Chatbot service is offline. Make sure Ollama is running and the mistral model is downloaded. Run: `ollama pull mistral`'
    except requests.exceptions.Timeout:
        return 'The AI is taking longer than expected. This may happen if the model is still downloading or under heavy load. Please try again in a moment.'
    except Exception as e:
        return f'Chatbot error: {str(e)}'

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def clear_chat(request):
    """Clear conversation history for user."""
    user_id = request.user.id
    session_key = f'chatbot_session_{user_id}'
    cache.delete(session_key)
    return JsonResponse({'success': True})

@login_required
def chat_history(request):
    """Get conversation history for user."""
    user_id = request.user.id
    session_key = f'chatbot_session_{user_id}'
    history = cache.get(session_key, [])
    return JsonResponse({'history': history})

@login_required
def user_analytics(request):
    """Get user analytics endpoint for dashboard integration."""
    analytics = get_user_analytics(request.user)
    level, level_num = calculate_user_level(analytics)
    return JsonResponse({
        'analytics': analytics,
        'level': level,
        'level_num': level_num
    })


@login_required
def dashboard_insights(request):
    """Return AI-generated prioritized, actionable insights for creators only.

    Uses the existing `get_user_analytics`, `calculate_user_level`,
    `build_enhanced_prompt` and `query_local_ai` helpers to compose a prompt
    and query the local Ollama service. Returns JSON with `insights` list
    and raw AI response.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = request.user
    try:
        from blog.models import Post as BlogPost
        from communities.models import CommunityPost

        is_creator = (
            BlogPost.objects.filter(author=user).exists()
            or CommunityPost.objects.filter(author=user).exists()
        )
    except Exception:
        is_creator = False

    if not is_creator:
        return JsonResponse({'error': 'Insights available to creators only'}, status=403)

    # Build analytics and prompt
    analytics = get_user_analytics(user)
    level, level_num = calculate_user_level(analytics)
    system_prompt = build_enhanced_prompt(user, analytics, [])

    user_message = (
        "Provide 3 prioritized, actionable improvements this creator can make to "
        "increase engagement. For each item give a short action and one-sentence rationale. "
        "Return numbered items."
    )

    ai_response = query_local_ai(user_message, [], system_prompt)

    # Simple parse: split into numbered or bullet items
    items = []
    try:
        parts = [p.strip() for p in re.split(r"\r?\n", ai_response) if p.strip()]
        cur = ''
        for line in parts:
            if re.match(r'^\d+[\)\.]', line) or re.match(r'^\d+\s', line):
                if cur:
                    items.append(cur.strip())
                cur = re.sub(r'^\d+[\)\.\s]*', '', line)
            elif re.match(r'^[-•]\s+', line):
                if cur:
                    items.append(cur.strip())
                    cur = ''
                items.append(re.sub(r'^[-•]\s+', '', line).strip())
            else:
                if cur:
                    cur += ' ' + line
                else:
                    cur = line
        if cur:
            items.append(cur.strip())
    except Exception:
        items = []

    # Fallback: if parsing failed, return entire response as single insight
    if not items:
        items = [ai_response.strip()]

    # Limit to 5 insights max
    items = items[:5]

    return JsonResponse({'insights': items, 'raw': ai_response})
