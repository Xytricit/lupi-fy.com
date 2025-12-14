from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import json


def editor_debug_view(request):
    """Debug-only: serve the enhanced editor without requiring authentication.

    This is a temporary helper to verify frontend assets (Blockly/Phaser)
    during local development when authentication would otherwise redirect.
    """
    return render(request, "games/editor_enhanced.html", {})


def editor_public_view(request):
    """Serve the enhanced editor without requiring authentication (guest/public)."""
    # Allow guest/editor to accept a `game_id` GET param so the editor
    # can load a specific game for viewing/editing when the link includes it.
    game_id = request.GET.get('game_id')
    context = {}
    if game_id:
        context['game_id'] = game_id
    # If a user is authenticated, provide minimal profile info to the editor
    if request.user.is_authenticated:
        user = request.user
        context['current_user'] = {
            'id': user.id,
            'username': user.username,
            'avatar_url': getattr(user, 'avatar.url', None) if getattr(user, 'avatar', None) else None,
        }
    return render(request, "games/editor_enhanced.html", context)


@login_required
def editor_dashboard_view(request):
    """Render the LupiForge Game Editor Dashboard at /games/dashboard.

    The frontend will fetch the authenticated user's games via an API
    (`/games/api/user/games/`) and render published/draft lists, analytics,
    and quick actions. We intentionally keep server-side rendering minimal
    and let the client obtain real user-specific data.
    """
    return render(request, "games/dashboard.html", {})


@login_required
def dashboard_home_view(request):
    """Alias for editor_dashboard_view; allows /games/dashboard/home/ to work."""
    return render(request, "games/dashboard.html", {})


@login_required
def recently_played_api(request):
    """Return the current user's recently played game sessions ordered by last_played desc."""
    from accounts.models import UserGameSession

    sessions = (
        UserGameSession.objects.filter(user=request.user)
        .order_by("-last_played")[:12]
    )
    games = []
    for s in sessions:
        games.append(
            {
                "id": s.id,
                "title": s.game or "Game",
                "image": None,
                "last_played": s.last_played.isoformat(),
            }
        )

    return JsonResponse({"games": games})

@login_required
def editor_view(request, version=None):
    """Serve the in-browser Phaser editor. Accepts optional `version` kwarg or GET param.

    - If `version` == 'enhanced' (either via kwarg or ?version=enhanced) renders enhanced editor.
    - Otherwise renders the basic editor.
    """
    # Priority: explicit kwarg passed by URLconf, then GET param, then default
    v = version or request.GET.get('version', 'basic')
    # Provide current user information to the editor so the frontend can
    # integrate with the authenticated user's profile (avatar, username, id).
    user = request.user
    current_user = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_authenticated': user.is_authenticated,
        'avatar_url': getattr(user, 'avatar.url', None) if getattr(user, 'avatar', None) else None,
    }
    # Try to include role if available (profile may be optional)
    try:
        current_user['role'] = getattr(user.profile, 'role', None)
    except Exception:
        current_user['role'] = None

    context = {'current_user': current_user}

    if v == 'enhanced':
        return render(request, "games/editor_enhanced.html", context)
    return render(request, "games/editor.html", context)


@login_required
def creator_dashboard_view(request):
    """Creator dashboard with stats and analytics."""
    return render(request, "games/creator_dashboard.html", {})


@login_required
def multiplayer_view(request):
    """Multiplayer lobby and game sessions."""
    return render(request, "games/multiplayer.html", {})


@login_required
@require_http_methods(["POST"])
def save_game_api(request):
    """Save or update a game version."""
    from .models import Game, GameVersion
    try:
        data = json.loads(request.body)
        title = data.get('title', 'Untitled Game')
        description = data.get('description', '')
        logic_json = data.get('logic_json', {})
        bundle_url = data.get('bundle_url', 'local://bundle')
        visibility = data.get('visibility', 'draft')
        
        # Create or update game
        game, created = Game.objects.get_or_create(
            owner=request.user,
            title=title,
            defaults={'description': description, 'visibility': visibility}
        )
        
        if not created:
            game.description = description
            game.visibility = visibility
            game.save()
        
        # Create version
        latest_version = game.versions.order_by('-version_number').first()
        version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = GameVersion.objects.create(
            game=game,
            version_number=version_number,
            bundle_url=bundle_url,
            logic_json=logic_json,
            is_published=False
        )
        
        return JsonResponse({'game_id': str(game.id), 'version': version_number, 'status': 'saved'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def publish_game_api(request):
    """Submit game for review (moderator approval)."""
    from .models import Game
    try:
        game_id = request.GET.get('game_id')
        game = Game.objects.get(id=game_id, owner=request.user)
        game.visibility = 'pending'
        game.save()
        return JsonResponse({'status': 'pending_review', 'game_id': str(game.id)})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def approve_game_api(request):
    """Admin/Moderator: Approve a game (make public)."""
    from .models import Game
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ('admin', 'moderator'):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    try:
        game_id = request.GET.get('game_id')
        game = Game.objects.get(id=game_id)
        game.visibility = 'public'
        game.save()
        return JsonResponse({'status': 'approved', 'game_id': str(game.id)})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def reject_game_api(request):
    """Admin/Moderator: Reject a game (keep as draft)."""
    from .models import Game
    if not hasattr(request.user, 'profile') or request.user.profile.role not in ('admin', 'moderator'):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    try:
        game_id = request.GET.get('game_id')
        game = Game.objects.get(id=game_id)
        game.visibility = 'draft'
        game.save()
        return JsonResponse({'status': 'rejected', 'game_id': str(game.id)})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def moderation_view(request):
    """Serve the moderation panel for admins/moderators."""
    if request.user.profile.role not in ('admin', 'moderator'):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    return render(request, "games/moderation.html", {})


@login_required
@require_http_methods(["GET"])
def games_list_api(request):
    """List all games for moderation."""
    from .models import Game
    if request.user.profile.role not in ('admin', 'moderator'):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    games = Game.objects.all().values('id', 'title', 'description', 'visibility', 'owner__username')
    return JsonResponse({
        'games': [
            {
                'id': str(g['id']),
                'title': g['title'],
                'description': g['description'],
                'visibility': g['visibility'],
                'owner': g['owner__username']
            }
            for g in games
        ]
    })


@login_required
@require_http_methods(["POST"])
def reject_game_api(request):
    """Admin/Moderator: Reject a game (keep as draft)."""
    from .models import Game
    if request.user.profile.role not in ('admin', 'moderator'):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    try:
        game_id = request.GET.get('game_id')
        game = Game.objects.get(id=game_id)
        game.visibility = 'draft'
        game.save()
        return JsonResponse({'status': 'rejected', 'game_id': str(game.id)})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def upload_asset_api(request):
    """Upload an asset (sprite, sound, bg) for a game."""
    from .models import Game, GameAsset
    try:
        game_id = request.GET.get('game_id')
        game = Game.objects.get(id=game_id, owner=request.user)
        
        asset_name = request.POST.get('name', 'asset')
        asset_type = request.POST.get('type', 'sprite')
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        asset = GameAsset.objects.create(
            game=game,
            name=asset_name,
            asset_type=asset_type,
            file=file,
            metadata={'filename': file.name, 'size': file.size}
        )
        
        return JsonResponse({
            'asset_id': asset.id,
            'name': asset.name,
            'url': asset.file.url,
            'type': asset.asset_type
        })
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def list_assets_api(request):
    """List all assets for a game."""
    from .models import Game, GameAsset
    try:
        game_id = request.GET.get('game_id')
        game = Game.objects.get(id=game_id)
        
        # Check if user is owner or game is public
        if game.owner_id != request.user.id and game.visibility != 'public':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        assets = GameAsset.objects.filter(game=game).values('id', 'name', 'asset_type', 'file', 'metadata')
        return JsonResponse({
            'assets': list(assets)
        })
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def submit_score_api(request):
    """Submit a score for a game."""
    from .models import Game, Score, UserAchievement, Achievement
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        value = data.get('value', 0)
        
        game = Game.objects.get(id=game_id)
        
        # Create score
        score = Score.objects.create(
            game=game,
            player=request.user,
            value=value,
            metadata=data.get('metadata', {})
        )
        
        # Check achievements
        if value >= 1000:
            ach, created = Achievement.objects.get_or_create(
                name="Score Warrior",
                defaults={
                    'description': 'Score over 1000 points',
                    'condition': 'score_over_1000'
                }
            )
            UserAchievement.objects.get_or_create(
                user=request.user,
                achievement=ach,
                game=game
            )
        
        # Get leaderboard rank
        rank = Score.objects.filter(game=game, value__gt=value).count() + 1
        
        return JsonResponse({
            'score_id': score.id,
            'rank': rank,
            'value': value
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def leaderboard_api(request):
    """Get leaderboard for a game (daily/weekly/all-time)."""
    from .models import Game, Score
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        game_id = request.GET.get('game_id')
        period = request.GET.get('period', 'all')  # daily, weekly, all
        limit = int(request.GET.get('limit', 50))
        
        game = Game.objects.get(id=game_id)
        
        # Filter by period
        if period == 'daily':
            since = timezone.now() - timedelta(days=1)
            scores = Score.objects.filter(game=game, created_at__gte=since).order_by('-value')[:limit]
        elif period == 'weekly':
            since = timezone.now() - timedelta(weeks=1)
            scores = Score.objects.filter(game=game, created_at__gte=since).order_by('-value')[:limit]
        else:  # all-time
            scores = Score.objects.filter(game=game).order_by('-value')[:limit]
        
        # Build leaderboard with ranks
        leaderboard = [
            {
                'rank': i+1,
                'player': s.player.username if s.player else 'Anonymous',
                'score': s.value,
                'date': s.created_at.isoformat()
            }
            for i, s in enumerate(scores)
        ]
        
        return JsonResponse({'leaderboard': leaderboard, 'period': period})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def user_achievements_api(request):
    """Get achievements for logged-in user."""
    from .models import UserAchievement
    achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement').values(
        'achievement__name', 'achievement__description', 'earned_at', 'game__title'
    )
    return JsonResponse({'achievements': list(achievements)})


@login_required
@require_http_methods(["POST"])
def analyze_logic_api(request):
    """AI Assistant: Analyze game logic for errors/suggestions."""
    try:
        data = json.loads(request.body)
        logic_json = data.get('logic_json', {})
        game_meta = data.get('meta', {})
        
        # Simple validation logic
        suggestions = []
        errors = []
        
        events = logic_json.get('events', [])
        
        # Check for missing event handlers
        if len(events) == 0:
            suggestions.append("No logic blocks detected. Try adding an 'On Start' event to initialize your game.")
        
        # Check for common issues
        sprite_names = set()
        for event in events:
            if event.get('type') == 'move_sprite':
                sprite_names.add(event.get('SPRITE', 'sprite'))
            elif event.get('type') == 'destroy_sprite':
                sprite_names.add(event.get('SPRITE', 'sprite'))
        
        if 'player' not in sprite_names and len(events) > 0:
            suggestions.append("💡 Tip: Consider having a 'player' sprite. Most games need a controllable character.")
        
        # Check for collisions without consequences
        collision_events = [e for e in events if e.get('type') == 'on_collision']
        if collision_events and len(events) < 3:
            suggestions.append("Collision detected but limited logic. Add damage/score changes to make it impactful.")
        
        # AI suggestion
        suggestions.append("✨ AI Suggestion: Add health/damage mechanics for engaging gameplay.")
        
        return JsonResponse({
            'status': 'ok',
            'errors': errors,
            'suggestions': suggestions
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def creator_revenue_api(request):
    """Get revenue stats for a creator's games."""
    from .models import Game, Transaction
    try:
        games = Game.objects.filter(owner=request.user)
        total_revenue = 0
        game_stats = []
        
        for game in games:
            transactions = Transaction.objects.filter(game=game, status='completed')
            game_revenue = sum(t.amount for t in transactions)
            total_revenue += game_revenue
            
            game_stats.append({
                'game_id': str(game.id),
                'title': game.title,
                'revenue': float(game_revenue),
                'transaction_count': transactions.count()
            })
        
        return JsonResponse({
            'total_revenue': float(total_revenue),
            'games': game_stats
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def tutorial_view(request):
    """Serve the interactive tutorial page."""
    return render(request, "games/tutorial.html", {})


@login_required
def moderation_view(request):
    """Serve the moderation panel (admin/moderator only)."""
    try:
        if hasattr(request.user, 'profile') and request.user.profile.role not in ('moderator', 'admin'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except:
        pass
    return render(request, "games/moderation.html", {})


def games_catalog_view(request):
    """Serve the games catalog page showing all released & approved games."""
    return render(request, "games/games_catalog.html", {})


def block_burst_view(request):
    """Serve the Block Burst game."""
    return render(request, "games/block_burst.html", {})


@require_http_methods(["GET"])
def games_api_view(request):
    """API endpoint: return released & approved games created via Lupiforge.
    
    Returns JSON array of game objects with id, title, description, thumbnail, url, released, approved.
    Only includes games that:
    - Have visibility='public' (approved by admin)
    - Have at least one GameVersion with logic_json (created via Lupiforge)
    """
    # #region agent log
    import json
    import os
    from datetime import datetime
    log_path = r'c:\Users\turbo\OneDrive\Documents\GitHub\lupi-fy.com\.cursor\debug.log'
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            json.dump({'location':'games/views.py:529','message':'games_api_view called','data':{'method':request.method},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
            f.write('\n')
    except: pass
    # #endregion
    from .models import Game, GameVersion
    try:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                json.dump({'location':'games/views.py:540','message':'Querying games_with_versions','data':{},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                f.write('\n')
        except: pass
        # #endregion
        # Fetch only public games that have versions (created via Lupiforge)
        # A game is created via Lupiforge if it has at least one GameVersion
        # We check for games with public visibility that have GameVersions
        # (logic_json default is {}, so we just check that GameVersion exists)
        games_with_versions = GameVersion.objects.filter(
            game__visibility='public'
        ).values_list('game_id', flat=True).distinct()
        
        # Get the actual games - convert to list first
        games_with_versions_list = list(games_with_versions)
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                json.dump({'location':'games/views.py:567','message':'games_with_versions result','data':{'count':len(games_with_versions_list),'ids':[str(x) for x in games_with_versions_list]},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                f.write('\n')
        except: pass
        # #endregion
        
        # If no games with versions, return empty list
        if not games_with_versions_list:
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    json.dump({'location':'games/views.py:573','message':'No games with versions found','data':{},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                    f.write('\n')
            except: pass
            # #endregion
            return JsonResponse([], safe=False)
        
        games = Game.objects.filter(
            id__in=games_with_versions_list,
            visibility='public'
        ).values(
            'id', 'title', 'description', 'created_at', 'thumbnail'
        )
        
        # #region agent log
        try:
            games_list = list(games)
            with open(log_path, 'a', encoding='utf-8') as f:
                json.dump({'location':'games/views.py:552','message':'Games queried','data':{'count':len(games_list)},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                f.write('\n')
        except: pass
        # #endregion
        
        # Format for frontend consumption
        result = []
        for g in games:
            try:
                thumbnail_url = ''
                # Check if thumbnail field exists and has a value
                thumbnail_field = g.get('thumbnail')
                if thumbnail_field:
                    try:
                        game_obj = Game.objects.get(id=g['id'])
                        if game_obj.thumbnail:
                            thumbnail_url = game_obj.thumbnail.url
                    except Exception as thumb_err:
                        # #region agent log
                        try:
                            with open(log_path, 'a', encoding='utf-8') as f:
                                json.dump({'location':'games/views.py:610','message':'Thumbnail error','data':{'game_id':str(g['id']),'error':str(thumb_err)},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                                f.write('\n')
                        except: pass
                        # #endregion
                        pass
                
                result.append({
                    'id': str(g['id']),
                    'title': g.get('title', 'Untitled Game'),
                    'description': g.get('description', ''),
                    'thumbnail': thumbnail_url,
                    'url': f"/games/{g['id']}/",
                    'released': True,
                    'approved': True
                })
            except Exception as game_err:
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        json.dump({'location':'games/views.py:625','message':'Error formatting game','data':{'game':str(g),'error':str(game_err)},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                        f.write('\n')
                except: pass
                # #endregion
                continue
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                json.dump({'location':'games/views.py:575','message':'Returning result','data':{'result_count':len(result),'titles':[r['title'] for r in result]},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                f.write('\n')
        except: pass
        # #endregion
        
        return JsonResponse(result, safe=False)
    except Exception as e:
        # #region agent log
        try:
            import traceback
            with open(log_path, 'a', encoding='utf-8') as f:
                json.dump({'location':'games/views.py:580','message':'Exception in games_api_view','data':{'error':str(e),'traceback':traceback.format_exc()},'timestamp':int(datetime.now().timestamp()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'}, f)
                f.write('\n')
        except: pass
        # #endregion
        return JsonResponse({'error': str(e)}, status=400)






