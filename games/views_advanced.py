from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, Avg, Max
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
import json
import re

from .models import Game, GameAsset, GameVersion, Score, Achievement, UserAchievement, Transaction
from accounts.models import UserProfile, UserNotification

# ===== MULTIPLAYER & NETWORKING =====

@login_required
@require_http_methods(["POST"])
def create_multiplayer_session(request):
    """Create a multiplayer game session for real-time gameplay"""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        max_players = data.get('max_players', 4)
        
        game = Game.objects.get(id=game_id)
        
        # Create session (in production would use Django Channels)
        session = {
            'id': f"session_{game_id}_{timezone.now().timestamp()}",
            'game_id': game_id,
            'game_title': game.title,
            'creator': game.owner.username,
            'max_players': max_players,
            'current_players': 1,
            'status': 'waiting',
            'created_at': timezone.now().isoformat(),
            'players': [{'id': request.user.id, 'name': request.user.username, 'joined_at': timezone.now().isoformat()}]
        }
        
        # In production: Store in Redis or database
        return JsonResponse({
            'session_id': session['id'],
            'session': session,
            'ws_url': f"ws://localhost:8000/ws/game/{session['id']}/"
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def join_multiplayer_session(request):
    """Join an existing multiplayer session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        # In production: Fetch from Redis/database
        return JsonResponse({
            'message': 'Joined session',
            'session_id': session_id,
            'player_id': request.user.id,
            'ws_url': f"ws://localhost:8000/ws/game/{session_id}/"
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def list_active_sessions(request):
    """List available multiplayer sessions"""
    try:
        # In production: Query Redis for active sessions
        # For now, return template structure
        sessions = [
            {
                'id': 'session_1',
                'game_title': 'Jump Quest',
                'creator': 'game_dev_1',
                'players_count': 2,
                'max_players': 4,
                'status': 'waiting'
            }
        ]
        return JsonResponse({'sessions': sessions}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ===== AI ASSISTANT ENHANCEMENTS =====

@login_required
@require_http_methods(["POST"])
def ai_suggest_improvements(request):
    """AI suggests code and design improvements"""
    try:
        data = json.loads(request.body)
        logic_json = data.get('logic_json', {})
        game_id = data.get('game_id')
        
        suggestions = []
        events = logic_json.get('events', [])
        
        # Code quality checks
        if len(events) == 0:
            suggestions.append("💡 Add some logic blocks to get started!")
        if len(events) < 3:
            suggestions.append("📌 Consider adding more game mechanics (collisions, timers, etc.)")
        
        # Best practices
        event_types = [e.get('type') for e in events]
        if 'on_collision' not in event_types and len(events) > 2:
            suggestions.append("🎯 Tip: Add collision detection for interactive gameplay")
        if 'on_key_press' not in event_types:
            suggestions.append("⌨️ Tip: Player input (keyboard) makes games more engaging")
        if 'apply_gravity' not in str(events):
            suggestions.append("🌍 Tip: Add gravity to make movement feel realistic")
        
        # Performance hints
        sprite_count = len(set([str(e.get('SPRITE', '')) for e in events]))
        if sprite_count > 10:
            suggestions.append("⚡ Optimization: Many sprites can impact performance. Consider consolidating.")
        
        # Design suggestions
        if 'change_health' not in str(events):
            suggestions.append("💪 Design: Health/score systems make games more challenging")
        if 'destroy_sprite' not in str(events) and 'spawn_sprite' in str(events):
            suggestions.append("🎪 Idea: Combine spawning with destroying for dynamic gameplay")
        
        return JsonResponse({'suggestions': suggestions[:5]}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def ai_generate_starter_code(request):
    """AI generates starter game templates"""
    try:
        data = json.loads(request.body)
        game_type = data.get('game_type', 'platformer')  # platformer, shooter, puzzle, racing
        
        templates = {
            'platformer': {
                'title': 'Platformer Starter',
                'events': [
                    {'type': 'on_start', 'action': 'spawn_sprite', 'sprite': 'player', 'x': 100, 'y': 300},
                    {'type': 'on_key_press', 'key': 'ArrowUp', 'action': 'apply_velocity', 'sprite': 'player', 'vy': -400},
                    {'type': 'on_collision', 'obj1': 'player', 'obj2': 'platform', 'action': 'nothing'},
                ],
                'sprites': ['player', 'platform', 'enemy'],
                'description': 'Player moves left/right and jumps over obstacles'
            },
            'shooter': {
                'title': 'Shooter Starter',
                'events': [
                    {'type': 'on_key_press', 'key': 'Space', 'action': 'spawn_sprite', 'sprite': 'bullet'},
                    {'type': 'on_collision', 'obj1': 'bullet', 'obj2': 'enemy', 'action': 'destroy_sprite'},
                    {'type': 'on_timer', 'interval': 2000, 'action': 'spawn_sprite', 'sprite': 'enemy'},
                ],
                'sprites': ['player', 'bullet', 'enemy'],
                'description': 'Shoot enemies with spacebar'
            },
            'puzzle': {
                'title': 'Puzzle Starter',
                'events': [
                    {'type': 'on_click', 'action': 'move_sprite'},
                    {'type': 'on_collision', 'obj1': 'tile', 'obj2': 'goal', 'action': 'game_complete'},
                ],
                'sprites': ['tile', 'goal'],
                'description': 'Drag tiles to solve puzzle'
            }
        }
        
        template = templates.get(game_type, templates['platformer'])
        return JsonResponse({'template': template}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ===== ADVANCED MODERATION & REVIEW =====

@login_required
@require_http_methods(["POST"])
def report_game(request):
    """Report inappropriate or problematic games"""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        reason = data.get('reason')  # 'inappropriate', 'broken', 'spam', 'copyright'
        details = data.get('details', '')
        
        game = Game.objects.get(id=game_id)
        
        # Create moderation report (in production: use Report model)
        report = {
            'id': f"report_{game_id}_{timezone.now().timestamp()}",
            'game_id': game_id,
            'reporter': request.user.username,
            'reason': reason,
            'details': details,
            'created_at': timezone.now().isoformat(),
            'status': 'pending'
        }
        
        # Send notification to moderators
        moderators = UserProfile.objects.filter(role='moderator')
        for mod_profile in moderators:
            UserNotification.objects.create(
                user=mod_profile.user,
                notification_type='game_reported',
                title=f"Game Report: {game.title}",
                message=f"Reported by {request.user.username}: {reason}",
                related_game=game
            )
        
        return JsonResponse({'report_id': report['id'], 'status': 'submitted'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def get_moderation_queue(request):
    """Get games pending moderation (moderators only)"""
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['moderator', 'admin']:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        pending_games = Game.objects.filter(visibility='pending').select_related('owner').values(
            'id', 'title', 'owner__username', 'created_at', 'visibility'
        )[:20]
        
        return JsonResponse({
            'queue_length': Game.objects.filter(visibility='pending').count(),
            'games': list(pending_games)
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def add_game_tag(request):
    """Add moderation tags to games (abuse, unfinished, needs-review, etc.)"""
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['moderator', 'admin']:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        data = json.loads(request.body)
        game_id = data.get('game_id')
        tags = data.get('tags', [])  # ['abuse', 'unfinished', 'needs-review']
        
        game = Game.objects.get(id=game_id)
        # In production: store in GameTag model
        
        return JsonResponse({'game_id': game_id, 'tags': tags, 'applied': True}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ===== CREATOR ANALYTICS & INSIGHTS =====

@login_required
@require_http_methods(["GET"])
def creator_game_stats(request):
    """Get detailed analytics for creator's games"""
    try:
        game_id = request.GET.get('game_id')
        
        if not game_id:
            # Return stats for all creator's games
            games = Game.objects.filter(owner=request.user).values('id', 'title')
            all_stats = []
            for game in games:
                scores = Score.objects.filter(game_id=game['id'])
                stats = {
                    'game_id': game['id'],
                    'title': game['title'],
                    'total_plays': scores.count(),
                    'avg_score': scores.aggregate(avg=Avg('value'))['avg'] or 0,
                    'high_score': scores.aggregate(max=Max('value'))['max'] or 0,
                    'unique_players': scores.values('player').distinct().count(),
                }
                all_stats.append(stats)
            return JsonResponse({'games_stats': all_stats}, status=200)
        else:
            # Stats for single game
            game = Game.objects.get(id=game_id, owner=request.user)
            scores = Score.objects.filter(game=game)
            
            stats = {
                'game_id': game.id,
                'title': game.title,
                'created_at': game.created_at.isoformat(),
                'visibility': game.visibility,
                'total_plays': scores.count(),
                'avg_score': float(scores.aggregate(avg=Avg('value'))['avg'] or 0),
                'high_score': float(scores.aggregate(max=Max('value'))['max'] or 0),
                'unique_players': scores.values('player').distinct().count(),
                'play_trend': 'up',  # Would be calculated from time-series data
            }
            
            return JsonResponse({'stats': stats}, status=200)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found or unauthorized'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def creator_dashboard_data(request):
    """Complete creator dashboard with all metrics"""
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        # Get all creator's games with stats
        games = Game.objects.filter(owner=user)
        total_plays = Score.objects.filter(game__in=games).count()
        total_revenue = Transaction.objects.filter(related_game__in=games).aggregate(Sum('amount'))['amount__sum'] or 0
        
        dashboard_data = {
            'profile': {
                'username': user.username,
                'bio': profile.bio,
                'followers_count': profile.game_followers.count(),
                'games_created': games.count(),
            },
            'metrics': {
                'total_plays': total_plays,
                'total_revenue': float(total_revenue),
                'avg_game_rating': 4.5,  # Would calculate from ratings
                'completion_rate': '65%'
            },
            'recent_games': list(games.values('id', 'title', 'visibility')[:5]),
            'notifications': list(
                UserNotification.objects.filter(user=user, read=False)
                .values('id', 'title', 'message', 'notification_type')[:5]
            )
        }
        
        return JsonResponse(dashboard_data, status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def user_games_api(request):
    """Return the authenticated user's games (published and drafts) with metrics.

    Response format:
    {
      "games": [ {id,title,thumbnail,visibility,metrics:{plays,likes,shares,avg_session},time_series:[{ts,plays}]}, ... ]
    }
    """
    try:
        user = request.user
        games_qs = Game.objects.filter(owner=user).order_by('-updated_at')
        games = []
        for g in games_qs:
            # Collect simple metrics
            plays = Score.objects.filter(game=g).count()
            likes = getattr(g, 'likes_count', 0) if hasattr(g, 'likes_count') else 0
            shares = getattr(g, 'shares_count', 0) if hasattr(g, 'shares_count') else 0
            avg_session = Score.objects.filter(game=g).aggregate(avg=Avg('value'))['avg'] or 0

            # Build a small time-series of plays per day (last 7 days)
            now = timezone.now()
            series = []
            for i in range(7, 0, -1):
                day = now - timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                day_plays = Score.objects.filter(game=g, created_at__gte=day_start, created_at__lt=day_end).count()
                series.append({'date': day_start.date().isoformat(), 'plays': day_plays})

            games.append({
                'id': str(g.id),
                'title': g.title,
                'thumbnail': g.thumbnail.url if getattr(g, 'thumbnail', None) else None,
                'visibility': g.visibility,
                'metrics': {
                    'plays': plays,
                    'likes': likes,
                    'shares': shares,
                    'avg_session': float(avg_session)
                },
                'time_series': series,
                'updated_at': g.updated_at.isoformat() if getattr(g, 'updated_at', None) else None
            })

        return JsonResponse({'games': games}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_game_api(request):
    """Delete a game owned by the authenticated user. Expects JSON body {game_id: "..."}."""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        game = Game.objects.get(id=game_id, owner=request.user)
        game.delete()
        return JsonResponse({'status': 'deleted', 'game_id': str(game_id)}, status=200)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def share_game_api(request):
    """Generate a shareable link for a game and optionally record the share action."""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        game = Game.objects.get(id=game_id)
        # Generate canonical share URL
        share_url = f"{request.scheme}://{request.get_host()}/games/play/?id={game.id}"
        # Optionally increment a share counter
        if hasattr(game, 'shares_count'):
            try:
                setattr(game, 'shares_count', (getattr(game, 'shares_count') or 0) + 1)
                game.save()
            except Exception:
                pass
        return JsonResponse({'share_url': share_url, 'game_id': str(game.id)}, status=200)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ===== NOTIFICATION SYSTEM =====

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get user notifications"""
    try:
        notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')[:20]
        unread_count = notifications.filter(read=False).count()
        
        notif_data = [{
            'id': n.id,
            'type': n.notification_type,
            'title': n.title,
            'message': n.message,
            'read': n.read,
            'created_at': n.created_at.isoformat(),
            'game_id': n.related_game_id
        } for n in notifications]
        
        return JsonResponse({
            'notifications': notif_data,
            'unread_count': unread_count
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request):
    """Mark notification as read"""
    try:
        data = json.loads(request.body)
        notif_id = data.get('notification_id')
        
        notif = UserNotification.objects.get(id=notif_id, user=request.user)
        notif.read = True
        notif.save()
        
        return JsonResponse({'success': True}, status=200)
    except UserNotification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ===== USER PROFILE & SOCIAL =====

@login_required
@require_http_methods(["GET"])
def get_user_profile(request, username):
    """Get public user profile"""
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        
        if not profile.show_profile_public and user != request.user:
            return JsonResponse({'error': 'Profile is private'}, status=403)
        
        games = Game.objects.filter(owner=user, visibility='public')
        
        profile_data = {
            'username': user.username,
            'bio': profile.bio,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'role': profile.get_role_display(),
            'games_created': profile.games_created,
            'followers_count': profile.game_followers.count(),
            'is_following': request.user in profile.game_followers.all(),
            'games': list(games.values('id', 'title')[:10])
        }
        
        return JsonResponse(profile_data, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def follow_user(request):
    """Follow another user"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        
        user_to_follow = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user_to_follow)
        profile.game_followers.add(request.user)
        
        return JsonResponse({'success': True, 'message': f'Now following {username}'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["PUT"])
def update_user_profile(request):
    """Update own profile"""
    try:
        data = json.loads(request.body)
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        if 'bio' in data:
            profile.bio = data['bio']
        if 'show_profile_public' in data:
            profile.show_profile_public = data['show_profile_public']
        
        profile.save()
        
        return JsonResponse({'success': True, 'message': 'Profile updated'}, status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ===== GAME CREATION =====

@login_required
@require_http_methods(["POST"])
def create_game_api(request):
    """Create a new game with title and optional thumbnail"""
    try:
        title = request.POST.get('title', '').strip()
        visibility = request.POST.get('visibility', 'draft')
        thumbnail = request.FILES.get('thumbnail')
        
        if not title:
            return JsonResponse({'error': 'Game title is required'}, status=400)
        
        if not thumbnail:
            return JsonResponse({'error': 'Thumbnail is required'}, status=400)
        
        # Create the game
        game = Game.objects.create(
            owner=request.user,
            title=title,
            visibility=visibility,
            thumbnail=thumbnail
        )
        
        return JsonResponse({
            'id': str(game.id),
            'title': game.title,
            'thumbnail': game.thumbnail.url if game.thumbnail else None,
            'visibility': game.visibility,
            'created_at': game.created_at.isoformat(),
            'message': 'Game created successfully'
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ===== GAME REMIXING & FORKING =====

@login_required
@require_http_methods(["POST"])
def remix_game(request):
    """Create a remix/fork of an existing game"""
    try:
        data = json.loads(request.body)
        original_game_id = data.get('game_id')
        
        original = Game.objects.get(id=original_game_id, visibility='public')
        
        if not original.allow_remixes:
            return JsonResponse({'error': 'Remixes not allowed for this game'}, status=403)
        
        # Create new game as remix
        remix = Game.objects.create(
            owner=request.user,
            title=f"{original.title} (Remix)",
            slug=f"{original.slug}-remix-{request.user.id}",
            description=f"Remix of {original.title} by {original.owner.username}",
            visibility='draft',
            parent_game=original  # Would need to add this field
        )
        
        # Copy latest version logic
        try:
            latest_version = GameVersion.objects.filter(game=original).latest('version_number')
            GameVersion.objects.create(
                game=remix,
                version_number=1,
                logic_json=latest_version.logic_json
            )
        except GameVersion.DoesNotExist:
            pass
        
        return JsonResponse({
            'remix_id': remix.id,
            'message': 'Game remixed! Start editing in the editor.'
        }, status=201)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Original game not found or not public'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
