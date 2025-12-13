# 🔌 Backend Integration Guide

## Overview

The LupiForge editor is currently **frontend-only with localStorage**. This guide explains how to integrate it with a Django backend.

**Current State**: All features work with mock data and localStorage  
**Next Step**: Replace localStorage with API calls  
**Effort**: Medium (2-3 days per feature)

---

## Architecture Overview

### Current Data Flow
```
User Action → Manager Object → localStorage → UI Update
```

### Target Data Flow
```
User Action → Manager Object → API Call → Django Backend → Database → Response → UI Update
```

---

## Step-by-Step Integration

### Step 1: Authentication

Every API call needs user authentication.

**Frontend** (add to all managers):
```javascript
// Add to all fetch calls
const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
};
```

**Backend** (Django):
```python
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class GameViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
```

---

## API Endpoints Checklist

### 1️⃣ Games API

#### Save Project
**Endpoint**: `POST /games/api/save/`

**Frontend** (LeaderboardManager):
```javascript
// Old (localStorage):
localStorage.setItem('lupiforge_project', JSON.stringify({blocks, name}));

// New (API):
fetch('/games/api/save/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
    body: JSON.stringify({
        name: projectName,
        blocks: workspace.getAllBlocks(),
        code: generatedCode
    })
}).then(r => r.json()).then(data => console.log('Saved:', data.id));
```

**Backend** (Django):
```python
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'blocks', 'code', 'created_at', 'updated_at']

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Game.objects.filter(creator=self.request.user)
    
    def create(self, request):
        game = Game.objects.create(
            creator=request.user,
            name=request.data['name'],
            blocks=request.data['blocks'],
            code=request.data['code']
        )
        return Response(GameSerializer(game).data)
```

#### Publish Game
**Endpoint**: `POST /games/api/publish/`

**Frontend**:
```javascript
function publishGame() {
    const gameData = {
        name: document.getElementById('projectName').value,
        blocks: Blockly.Xml.workspaceToDom(workspace),
        code: generateCode()
    };
    
    fetch('/games/api/publish/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(gameData)
    }).then(r => r.json()).then(data => {
        NotificationManager.add('Submitted', 'Game queued for review');
        console.log('Published as:', data.id);
    });
}
```

**Backend**:
```python
class GamePublishView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        game = Game.objects.create(
            creator=request.user,
            name=request.data['name'],
            status='pending',
            blocks=request.data['blocks']
        )
        # Trigger email to moderators
        notify_moderators(game)
        return Response({'id': game.id, 'status': 'pending'})
```

---

### 2️⃣ Leaderboard API

**Endpoint**: `GET /games/api/leaderboard/?period=daily`

**Frontend** (LeaderboardManager.loadLeaderboard):
```javascript
loadLeaderboard() {
    fetch(`/games/api/leaderboard/?period=${this.currentPeriod}`, {
        headers: getHeaders()
    })
    .then(r => r.json())
    .then(data => {
        this.scores = data.scores;
        this.render();
    });
}
```

**Backend**:
```python
from django.utils import timezone
from datetime import timedelta

class LeaderboardView(APIView):
    def get(self, request):
        period = request.query_params.get('period', 'daily')
        
        if period == 'daily':
            start_date = timezone.now() - timedelta(days=1)
        elif period == 'weekly':
            start_date = timezone.now() - timedelta(weeks=1)
        elif period == 'monthly':
            start_date = timezone.now() - timedelta(days=30)
        else:  # alltime
            start_date = timezone.now() - timedelta(days=3650)
        
        scores = Score.objects.filter(
            created_at__gte=start_date
        ).select_related('player', 'game').order_by('-score')[:100]
        
        return Response({
            'scores': ScoreSerializer(scores, many=True).data
        })
```

---

### 3️⃣ Social API

#### Follow User
**Endpoint**: `POST /games/api/follow/`

**Frontend**:
```javascript
follow(userId) {
    const user = this.users.find(u => u.id === userId);
    
    fetch('/games/api/follow/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
            user_id: userId,
            action: user.isFollowing ? 'unfollow' : 'follow'
        })
    }).then(r => r.json()).then(data => {
        user.isFollowing = data.is_following;
        this.render();
    });
}
```

**Backend**:
```python
class FollowView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = request.data['user_id']
        action = request.data['action']
        
        target_user = User.objects.get(id=user_id)
        
        if action == 'follow':
            request.user.following.add(target_user)
        else:
            request.user.following.remove(target_user)
        
        return Response({
            'is_following': request.user.following.filter(id=user_id).exists()
        })
```

#### Remix Game
**Endpoint**: `POST /games/api/remix/`

**Frontend**:
```javascript
remixGame() {
    fetch('/games/api/remix/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({game_id: this.selectedGameId})
    }).then(r => r.json()).then(data => {
        const remixedGame = data;
        loadProjectIntoWorkspace(remixedGame);
        showToast('Game remixed! Editing your copy...');
    });
}
```

**Backend**:
```python
class RemixView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        original_game = Game.objects.get(id=request.data['game_id'])
        
        # Create copy
        remixed_game = Game.objects.create(
            creator=request.user,
            name=f"{original_game.name} (Remixed)",
            blocks=original_game.blocks,
            code=original_game.code,
            based_on=original_game
        )
        
        return Response(GameSerializer(remixed_game).data)
```

---

### 4️⃣ Dashboard API

**Endpoint**: `GET /games/api/creator/dashboard/`

**Frontend**:
```javascript
loadDashboard() {
    fetch('/games/api/creator/dashboard/', {
        headers: getHeaders()
    })
    .then(r => r.json())
    .then(data => {
        this.stats = data.stats;
        this.games = data.games;
        this.revenue = data.revenue;
        this.renderStats();
        this.renderGames();
        this.renderRevenue();
    });
}
```

**Backend**:
```python
class CreatorDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        games = Game.objects.filter(creator=user)
        
        return Response({
            'stats': {
                'total_games': games.count(),
                'total_plays': GamePlay.objects.filter(game__creator=user).count(),
                'total_followers': user.followers.count(),
                'total_revenue': calculate_revenue(user)
            },
            'games': GameSerializer(games, many=True).data,
            'revenue': Revenue.objects.filter(game__creator=user).values('game__name', 'amount')
        })
```

---

### 5️⃣ Moderation API

#### Get Queue
**Endpoint**: `GET /games/api/moderation/queue/`

**Frontend**:
```javascript
loadQueue() {
    fetch('/games/api/moderation/queue/', {
        headers: getHeaders()
    })
    .then(r => r.json())
    .then(data => {
        this.queue = data.games;
        this.renderQueue();
    });
}
```

**Backend**:
```python
class ModerationQueueView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        pending = Game.objects.filter(status='pending').order_by('created_at')
        approved_today = Game.objects.filter(
            status='approved',
            approved_at__date=timezone.now().date()
        ).count()
        rejected_today = Game.objects.filter(
            status='rejected',
            rejected_at__date=timezone.now().date()
        ).count()
        
        return Response({
            'games': GameSerializer(pending, many=True).data,
            'approved_today': approved_today,
            'rejected_today': rejected_today
        })
```

#### Approve/Reject
**Endpoints**: `POST /games/api/approve/` and `POST /games/api/reject/`

**Frontend**:
```javascript
performApproval(gameId, feedback) {
    fetch('/games/api/approve/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({game_id: gameId, feedback})
    }).then(r => r.json()).then(data => {
        NotificationManager.add('Game Approved!', `${data.name} is now live`);
        this.loadQueue();
    });
}
```

**Backend**:
```python
class ApproveGameView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        game = Game.objects.get(id=request.data['game_id'])
        game.status = 'approved'
        game.approved_at = timezone.now()
        game.moderator_feedback = request.data.get('feedback', '')
        game.save()
        
        # Notify creator
        Notification.objects.create(
            user=game.creator,
            type='game_approved',
            game=game
        )
        
        return Response(GameSerializer(game).data)
```

---

### 6️⃣ Multiplayer API

**Endpoints**:
- `GET /games/api/multiplayer/rooms/`
- `POST /games/api/multiplayer/create/`
- `POST /games/api/multiplayer/join/`
- `POST /games/api/multiplayer/leave/`

**WebSocket**: `wss://yourserver.com/ws/multiplayer/`

**Frontend**:
```javascript
// Load rooms
loadRooms() {
    fetch('/games/api/multiplayer/rooms/', {headers: getHeaders()})
        .then(r => r.json())
        .then(data => {this.renderRooms()});
}

// Create room
createRoom() {
    fetch('/games/api/multiplayer/create/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({...roomData})
    }).then(r => r.json()).then(room => {
        this.joinRoom(room.id);
    });
}

// WebSocket connection
const ws = new WebSocket(`wss://yourserver.com/ws/multiplayer/?room=${roomId}`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'player_joined') {
        this.players.push(data.player);
        this.renderPlayers();
    }
};
```

**Backend** (Django Channels):
```python
# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MultiplayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_action',
                'player': self.scope['user'].username,
                'action': data['action']
            }
        )
    
    async def player_action(self, event):
        await self.send(text_data=json.dumps(event))
```

---

### 7️⃣ Settings API

**Endpoint**: `POST /games/api/settings/`

**Frontend**:
```javascript
saveSettings(section) {
    const data = {
        [section]: getFormData(section)
    };
    
    fetch('/games/api/settings/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data)
    }).then(r => r.json()).then(response => {
        showToast('Settings saved!');
    });
}
```

**Backend**:
```python
class SettingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if 'profile' in request.data:
            profile = user.profile
            profile.bio = request.data['profile'].get('bio')
            profile.save()
        
        if 'preferences' in request.data:
            prefs = request.data['preferences']
            user.preferences = prefs
            user.save()
        
        return Response({'status': 'saved'})
```

---

### 8️⃣ Score Submission API

**Endpoint**: `POST /games/api/submit-score/`

**Frontend** (ScoreManager):
```javascript
submitScore() {
    const playerName = document.getElementById('playerName').value;
    const currentScore = PreviewManager.score;
    const gameId = workspace.id;
    
    fetch('/games/api/submit-score/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
            game_id: gameId,
            player_name: playerName,
            score: currentScore
        })
    }).then(r => r.json()).then(data => {
        showToast(`Score submitted! Rank: #${data.rank}`);
    });
}
```

**Backend**:
```python
class SubmitScoreView(APIView):
    def post(self, request):
        game = Game.objects.get(id=request.data['game_id'])
        
        score = Score.objects.create(
            game=game,
            player_name=request.data['player_name'],
            score=request.data['score'],
            player=request.user if request.user.is_authenticated else None
        )
        
        rank = Score.objects.filter(
            game=game,
            score__gt=score.score
        ).count() + 1
        
        return Response({'score_id': score.id, 'rank': rank})
```

---

## Database Models

```python
from django.contrib.auth.models import User
from django.db import models

class Game(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    blocks = models.JSONField()
    code = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    moderator_feedback = models.TextField(blank=True)
    plays_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} by {self.creator.username}"

class Asset(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='assets/')
    file_type = models.CharField(max_length=50)  # sprite, sound, background
    created_at = models.DateTimeField(auto_now_add=True)

class Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.CharField(max_length=10, default='👤')
    role = models.CharField(max_length=20, default='player')
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    TYPES = [
        ('game_approved', 'Game Approved'),
        ('game_rejected', 'Game Rejected'),
        ('new_follower', 'New Follower'),
        ('score_submitted', 'Score Submitted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class MultiplayerRoom(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    max_players = models.IntegerField()
    is_private = models.BooleanField(default=False)
    players = models.ManyToManyField(User, related_name='multiplayer_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
```

---

## URL Routing

```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'games', views.GameViewSet, basename='game')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/leaderboard/', views.LeaderboardView.as_view()),
    path('api/follow/', views.FollowView.as_view()),
    path('api/remix/', views.RemixView.as_view()),
    path('api/creator/dashboard/', views.CreatorDashboardView.as_view()),
    path('api/moderation/queue/', views.ModerationQueueView.as_view()),
    path('api/approve/', views.ApproveGameView.as_view()),
    path('api/reject/', views.RejectGameView.as_view()),
    path('api/multiplayer/rooms/', views.MultiplayerRoomsView.as_view()),
    path('api/multiplayer/create/', views.CreateRoomView.as_view()),
    path('api/multiplayer/join/', views.JoinRoomView.as_view()),
    path('api/settings/', views.SettingsView.as_view()),
    path('api/submit-score/', views.SubmitScoreView.as_view()),
]
```

---

## Implementation Priority

1. **Phase 1** (Critical): Games API (Save, Load, Publish)
2. **Phase 2** (High): Authentication, User Profiles
3. **Phase 3** (High): Leaderboard, Scores
4. **Phase 4** (Medium): Social (Follow, Remix)
5. **Phase 5** (Medium): Dashboard, Moderation
6. **Phase 6** (Lower): Multiplayer WebSocket
7. **Phase 7** (Polish): Settings, Notifications

---

## Testing Checklist

- [ ] All localStorage calls replaced with API calls
- [ ] Authentication headers on all requests
- [ ] Error handling for failed requests
- [ ] Loading states during async operations
- [ ] Data validation on both frontend & backend
- [ ] Rate limiting on sensitive endpoints
- [ ] CORS configured properly
- [ ] Database migrations created
- [ ] Tests written for all models
- [ ] API documentation generated

---

## Deployment Notes

1. **Environment Variables**:
   ```
   API_BASE_URL=https://api.yoursite.com
   WS_URL=wss://api.yoursite.com/ws/
   ```

2. **Security**:
   - Use HTTPS only
   - CSRF protection enabled
   - Rate limiting per user
   - Input validation
   - SQL injection protection

3. **Performance**:
   - Database indexes on frequently queried fields
   - Caching for leaderboard
   - CDN for asset storage
   - Pagination for large result sets

4. **Monitoring**:
   - Log all API calls
   - Track error rates
   - Monitor database performance
   - Alert on failures

---

## Support & Troubleshooting

**API Not Responding**:
- Check network tab in DevTools
- Verify headers (Authorization, Content-Type)
- Check backend logs
- Verify CORS configuration

**Data Not Persisting**:
- Confirm POST requests completing
- Check database for entries
- Verify migrations ran
- Check user permissions

**Authentication Issues**:
- Verify token in localStorage
- Check token expiration
- Confirm auth headers
- Test with curl first

---

This guide provides a complete roadmap for integrating the LupiForge editor with a production Django backend. Start with Phase 1 (Games API) and work through systematically.
