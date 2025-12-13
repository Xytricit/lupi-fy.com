import json
import re
import sys
from datetime import timedelta

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import GameLobbyMessage, GameLobbyChallenge, GameLobbyBan, LetterSetGame


def log_error(msg):
    """Log to both stdout and stderr for visibility."""
    print(msg)
    print(msg, file=sys.stderr)


class GameLobbyConsumer(AsyncJsonWebsocketConsumer):
    """Real-time WebSocket consumer for Try Not To Get Banned game."""

    async def connect(self):
        """Handle new WebSocket connection."""
        try:
            self.group_name = "game_lobby"
            self.user = self.scope.get("user")
            
            log_error(f"[GameLobby] 🔌 Connection attempt - User: {self.user}, Authenticated: {self.user.is_authenticated if self.user else False}")
            
            # Verify user is authenticated
            if not self.user or not self.user.is_authenticated:
                log_error(f"[GameLobby] ❌ Rejecting - user not authenticated")
                await self.close()
                return
            
            # Add to group and accept connection
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            log_error(f"[GameLobby] ✅ {self.user.username} connected and accepted")
            
            # Send chat history
            await self._send_history()
            
            # Notify others
            await self._broadcast_player_joined()
            
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error in connect: {e}")
            try:
                await self.close()
            except:
                pass

    async def _send_history(self):
        """Send recent chat history to connecting user."""
        try:
            messages = await sync_to_async(list)(
                GameLobbyMessage.objects.order_by("-created_at")[:30]
            )
            log_error(f"[GameLobby] 📜 Sending {len(messages)} history messages")
            
            for msg in reversed(messages):
                try:
                    await self.send_json({
                        "type": "history",
                        "username": msg.author_name or (msg.user.username if msg.user else "System"),
                        "message": msg.content,
                        "is_banned": False,
                    })
                except Exception as e:
                    log_error(f"[GameLobby] ⚠️ Error sending history message: {e}")
        except Exception as e:
            log_error(f"[GameLobby] ⚠️ Error loading chat history: {e}")

    async def _broadcast_player_joined(self):
        """Notify group that player joined."""
        try:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "player_joined",
                    "username": self.user.username,
                }
            )
            log_error(f"[GameLobby] 👋 Broadcasted join for {self.user.username}")
        except Exception as e:
            log_error(f"[GameLobby] ⚠️ Error broadcasting join: {e}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        try:
            log_error(f"[GameLobby] 🔌 {self.user.username} disconnected (code: {close_code})")
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception as e:
            log_error(f"[GameLobby] ⚠️ Error during disconnect: {e}")

    async def receive_json(self, content, **kwargs):
        """Handle incoming JSON messages from client."""
        try:
            if not self.user or not self.user.is_authenticated:
                log_error(f"[GameLobby] ⚠️ Received message from unauthenticated user")
                await self.send_json({"type": "error", "message": "Not authenticated"})
                return
            
            action = content.get("action")
            log_error(f"[GameLobby] 📨 Received action: {action}")
            
            if action == "send_message":
                await self.handle_send_message(content)
            else:
                log_error(f"[GameLobby] ⚠️ Unknown action: {action}")
                
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error in receive_json: {e}")
            try:
                await self.send_json({"type": "error", "message": str(e)})
            except:
                pass

    async def handle_send_message(self, content):
        """Process chat message and check for banned words."""
        try:
            message_text = content.get("message", "").strip()
            if not message_text:
                log_error(f"[GameLobby] ⚠️ Empty message from {self.user.username}")
                return
            
            log_error(f"[GameLobby] 💬 {self.user.username}: {message_text}")
            
            # Check if user is banned
            is_user_banned = await sync_to_async(self._check_if_banned)(self.user)
            if is_user_banned:
                log_error(f"[GameLobby] 🚫 {self.user.username} is banned, ignoring message")
                return
            
            # Get banned words
            try:
                from blog.views import banned_words
            except Exception as e:
                log_error(f"[GameLobby] ⚠️ Could not import banned_words: {e}")
                banned_words = []
            
            # Check for banned words
            message_lower = message_text.lower()
            banned_found = [w for w in banned_words if w.lower() in message_lower]
            
            if banned_found:
                log_error(f"[GameLobby] 🚫 {self.user.username} said banned word(s): {banned_found}")
                # Ban the user for 1 minute
                ban_until = timezone.now() + timedelta(minutes=1)
                await sync_to_async(GameLobbyBan.objects.create)(
                    user=self.user,
                    banned_until=ban_until
                )
                
                # Save the message
                await sync_to_async(GameLobbyMessage.objects.create)(
                    user=self.user,
                    author_name=self.user.username,
                    content=message_text,
                    is_system=False
                )
                
                # Broadcast BAN notification
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "user_banned",
                        "username": self.user.username,
                        "message": message_text,
                        "banned_words": banned_found,
                        "ban_duration": 60,
                    }
                )
                log_error(f"[GameLobby] ✅ Ban notification sent for {self.user.username}")
            else:
                log_error(f"[GameLobby] ✅ Message is clean from {self.user.username}")
                # Message is clean - save and broadcast
                await sync_to_async(GameLobbyMessage.objects.create)(
                    user=self.user,
                    author_name=self.user.username,
                    content=message_text,
                    is_system=False
                )
                
                # Broadcast clean message
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_message",
                        "username": self.user.username,
                        "message": message_text,
                        "is_banned": False,
                    }
                )
                log_error(f"[GameLobby] ✅ Message broadcast for {self.user.username}")
                
                # Check for challenge letter usage
                await self.handle_challenge_check(message_text)
                
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error in handle_send_message: {e}")
            import traceback
            log_error(traceback.format_exc())

    async def handle_challenge_check(self, message_text):
        """Check if message contains challenge letters and award points."""
        try:
            # Get the current incomplete challenge for this user
            challenge = await sync_to_async(
                lambda: GameLobbyChallenge.objects.filter(user=self.user, completed=False).order_by("-created_at").first()
            )()
            
            if not challenge:
                log_error(f"[GameLobby] ⚠️ No challenge found for {self.user.username}")
                return
            
            if challenge.completed:
                log_error(f"[GameLobby] ℹ️ Challenge already completed for {self.user.username}")
                return
            
            # Debug: log incoming message and challenge state
            try:
                log_error(f"[GameLobby] 🔎 handle_challenge_check - msg='{message_text}' challenge_letters={challenge.letters} used={challenge.used_letters}")
            except Exception:
                pass

            # Simple check: see if any challenge letters appear in the message
            message_lower = message_text.lower()
            newly_marked = []

            # Normalize letters for comparison
            challenge_letters = [str(x).upper() for x in (challenge.letters or [])]
            current_used = [str(x).upper() for x in (challenge.used_letters or [])]

            for letter in challenge_letters:
                # check single-character occurrence in message
                if letter.lower() in message_lower and letter.upper() not in current_used:
                    newly_marked.append(letter)
            
            if newly_marked:
                log_error(f"[GameLobby] 📝 Found letters {newly_marked} in message from {self.user.username}")
                # Mark letters as used (store as uppercase)
                if not challenge.used_letters:
                    challenge.used_letters = []
                challenge.used_letters.extend([str(x).upper() for x in newly_marked])
                
                # Check if all letters are now used (normalize to uppercase)
                used_set = set([str(x).upper() for x in (challenge.used_letters or [])])
                letters_set = set([str(x).upper() for x in (challenge.letters or [])])
                if used_set >= letters_set:
                    log_error(f"[GameLobby] 🎉 Challenge completed for {self.user.username}!")
                    challenge.completed = True
                    # Award points
                    from accounts.models import WordListGame
                    wgame, _ = await sync_to_async(WordListGame.objects.get_or_create)(user=self.user)
                    wgame.score = (wgame.score or 0) + 20
                    await sync_to_async(wgame.save)()
                
                await sync_to_async(challenge.save)()
                
            # Always broadcast if we have a challenge (even if no new letters found this message)
            # This ensures UI stays in sync
            if challenge and not challenge.completed:
                # Broadcast challenge update
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "challenge_update",
                        "username": self.user.username,
                        "letters": challenge.letters,
                        "used_letters": challenge.used_letters,
                        "completed": challenge.completed,
                        "points_awarded": 0,
                    }
                )
            
            # If completed, create new challenge and broadcast it
            if challenge and challenge.completed:
                new_letters = [chr(ord('A') + (hash(f"{self.user.id}{i}") % 26)) for i in range(12)]
                new_chal = await sync_to_async(
                    lambda: GameLobbyChallenge.objects.create(
                        user=self.user, 
                        letters=new_letters, 
                        used_letters=[], 
                        completed=False
                    )
                )()
                
                # Broadcast completion with points
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "challenge_update",
                        "username": self.user.username,
                        "letters": challenge.letters,
                        "used_letters": challenge.used_letters,
                        "completed": challenge.completed,
                        "points_awarded": 20,
                    }
                )
                
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "new_challenge",
                        "username": self.user.username,
                        "letters": new_chal.letters,
                    }
                )
                log_error(f"[GameLobby] 🆕 New challenge created for {self.user.username}: {new_letters}")
            elif newly_marked:
                log_error(f"[GameLobby] ✅ Challenge update broadcasted")

        except Exception as e:
            log_error(f"[GameLobby] ❌ Error in handle_challenge_check: {e}")
            import traceback
            log_error(traceback.format_exc())

    @staticmethod
    def _check_if_banned(user):
        """Check if user has active ban."""
        try:
            ban = GameLobbyBan.objects.filter(user=user).order_by("-banned_until").first()
            is_banned = ban and ban.is_active() if ban else False
            log_error(f"[GameLobby] 🔍 Check ban for {user.username}: {is_banned}")
            return is_banned
        except Exception as e:
            log_error(f"[GameLobby] ⚠️ Error checking ban: {e}")
            return False

    # ==================== BROADCAST HANDLERS ====================
    # These methods are called by group_send to deliver messages
    
    async def chat_message(self, event):
        """Handler for chat_message events from group."""
        try:
            await self.send_json({
                "type": "chat_message",
                "username": event.get("username"),
                "message": event.get("message"),
                "is_banned": False,
            })
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error sending chat_message to client: {e}")

    async def user_banned(self, event):
        """Handler for user_banned events from group."""
        try:
            await self.send_json({
                "type": "user_banned",
                "username": event.get("username"),
                "message": event.get("message"),
                "banned_words": event.get("banned_words", []),
                "is_banned": True,
                "ban_duration": event.get("ban_duration", 60),
            })
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error sending user_banned to client: {e}")

    async def player_joined(self, event):
        """Handler for player_joined events from group."""
        try:
            await self.send_json({
                "type": "player_joined",
                "username": event.get("username"),
            })
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error sending player_joined to client: {e}")

    async def challenge_update(self, event):
        """Handler for challenge_update events from group."""
        try:
            await self.send_json({
                "type": "challenge_update",
                "username": event.get("username"),
                "letters": event.get("letters"),
                "used_letters": event.get("used_letters"),
                "completed": event.get("completed"),
                "points_awarded": event.get("points_awarded", 0),
            })
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error sending challenge_update to client: {e}")

    async def new_challenge(self, event):
        """Handler for new_challenge events from group."""
        try:
            await self.send_json({
                "type": "new_challenge",
                "username": event.get("username"),
                "letters": event.get("letters"),
            })
        except Exception as e:
            log_error(f"[GameLobby] ❌ Error sending new_challenge to client: {e}")



class LetterSetGameConsumer(AsyncJsonWebsocketConsumer):
    """Real-time WebSocket consumer for the Letter Set game."""

    async def connect(self):
        self.group_name = "letter_set_game"
        self.user = self.scope["user"]
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
            
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        # Get or create game for user
        game = await sync_to_async(
            lambda: LetterSetGame.objects.filter(user=self.user).order_by("-updated_at").first()
        )()
        
        # Send initial game state
        if game:
            await self.send_json({
                "type": "game_state",
                "letters": list(game.letters),
                "score": game.score,
                "completed_words": game.get_completed_words_list(),
            })
        
        # Broadcast player join
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "player_joined",
                "username": self.user.username,
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        if not self.user or not self.user.is_authenticated:
            await self.send_json({"error": "Not authenticated"})
            return

        action = content.get("action")
        
        if action == "submit_word":
            await self.handle_submit_word(content)
        elif action == "send_chat":
            await self.handle_chat(content)
        else:
            pass

    async def handle_submit_word(self, content):
        """Process word submission."""
        try:
            from accounts.views import is_valid_word, is_dictionary_word
            
            word = content.get("word", "").strip()
            if not word or len(word) < 2:
                await self.send_json({"error": "Word must be at least 2 characters"})
                return
            
            # Get game
            game = await sync_to_async(
                lambda: LetterSetGame.objects.filter(user=self.user).order_by("-updated_at").first()
            )()
            
            if not game:
                await self.send_json({"error": "Game not found"})
                return
            
            # Check if word already used
            if word.lower() in [w.lower() for w in game.get_completed_words_list()]:
                await self.send_json({"error": "Word already used", "duplicate": True})
                return
            
            # Check if valid word from letters
            is_valid = await sync_to_async(lambda: is_valid_word(word, game.letters))()
            if not is_valid:
                await self.send_json({"error": "Word cannot be formed from the letters"})
                return
            
            # Check if it's a real dictionary word
            is_real_word, _ = await sync_to_async(is_dictionary_word)(word)
            if not is_real_word:
                await self.send_json({"error": "Not a valid English word"})
                return
            
            # Add word and update score (wrap sync calls)
            async def add_word_sync():
                # Directly update completed_words instead of calling add_word() which also calls save()
                words_list = game.get_completed_words_list()
                if word.lower() not in [w.lower() for w in words_list]:
                    words_list.append(word)
                    game.completed_words = ",".join(words_list)
                game.score = (game.score or 0) + 10
                game.save()
                return game.get_completed_words_list()
            
            completed_words = await sync_to_async(add_word_sync)()

            # Broadcast word submission
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "word_submitted",
                    "username": self.user.username,
                    "word": word,
                    "score": game.score,
                    "completed_words": completed_words,
                }
            )
            
            # Send success response
            await self.send_json({
                "success": True,
                "word": word,
                "score": game.score,
                "completed_words": game.get_completed_words_list(),
            })
        except Exception as e:
            log_error(f"[LetterSet] ❌ Error in handle_submit_word: {e}")
            import traceback
            log_error(traceback.format_exc())
            try:
                await self.send_json({"type": "error", "error": "Internal server error processing word"})
            except:
                pass
        from accounts.views import is_valid_word, is_dictionary_word
        
        word = content.get("word", "").strip()
        if not word or len(word) < 2:
            await self.send_json({"error": "Word must be at least 2 characters"})
            return
        
        # Get game
        game = await sync_to_async(
            lambda: LetterSetGame.objects.filter(user=self.user).order_by("-updated_at").first()
        )()
        
        if not game:
            await self.send_json({"error": "Game not found"})
            return
        
        # Check if word already used
        if word.lower() in [w.lower() for w in game.get_completed_words_list()]:
            await self.send_json({"error": "Word already used", "duplicate": True})
            return
        
        # Check if valid word from letters
        is_valid = await sync_to_async(lambda: is_valid_word(word, game.letters))()
        if not is_valid:
            await self.send_json({"error": "Word cannot be formed from the letters"})
            return
        
        # Check if it's a real dictionary word
        is_real_word, _ = await sync_to_async(is_dictionary_word)(word)
        if not is_real_word:
            await self.send_json({"error": "Not a valid English word"})
            return
        
        # Add word and update score (wrap sync calls)
        async def add_word_sync():
            game.add_word(word)
            game.score = (game.score or 0) + 10
            game.save()
            return game.get_completed_words_list()
        
        completed_words = await sync_to_async(add_word_sync)()

        
        # Broadcast word submission
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "word_submitted",
                "username": self.user.username,
                "word": word,
                "score": game.score,
                "completed_words": completed_words,
            }
        )
        
        # Send success response
        await self.send_json({
            "success": True,
            "word": word,
            "score": game.score,
            "completed_words": game.get_completed_words_list(),
        })

    async def handle_chat(self, content):
        """Process chat message in game."""
        message = content.get("message", "").strip()
        if not message:
            return
        
        # Broadcast message
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "username": self.user.username,
                "message": message,
            }
        )

    # Broadcast handlers
    async def chat_message(self, event):
        """Send chat message to all clients."""
        await self.send_json({
            "type": "chat_message",
            "author": event.get("username"),
            "content": event.get("message"),
            "timestamp": timezone.now().isoformat(),
        })

    async def word_submitted(self, event):
        """Broadcast word submission."""
        await self.send_json({
            "type": "word_submitted",
            "username": event.get("username"),
            "word": event.get("word"),
            "score": event.get("score"),
        })

    async def player_joined(self, event):
        """Notify when a player joins."""
        await self.send_json({
            "type": "player_joined",
            "username": event.get("username"),
        })


class DMConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer to receive direct message notifications for a user."""

    async def connect(self):
        # Accept only if the connecting user matches the URL user_id
        self.user_id = self.scope["url_route"]["kwargs"].get("user_id")
        self.group_name = f"user_{self.user_id}"

        # verify authenticated user matches requested id
        if not self.scope.get("user") or not self.scope["user"].is_authenticated:
            await self.close()
            return

        if str(self.scope["user"].id) != str(self.user_id):
            # Do not allow subscribing to other users' channel
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # This consumer is read-only from client side; ignore incoming messages
        return

    async def dm_message(self, event):
        # Forward DM events to the client
        message = event.get("message")
        await self.send(
            text_data=json.dumps({"type": "dm.message", "message": message})
        )

    async def user_block(self, event):
        """Forward user block/unblock events to connected clients."""
        payload = event.get("payload")
        await self.send(
            text_data=json.dumps({"type": "user.block", "payload": payload})
        )
