import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from . import ai_service
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    ws://host/ws/chat/<conversation_id>/?token=<jwt_access_token>
    Client sends : {"message": "text"}
    Server sends : {"type":"chunk","text":"..."} ... then {"type":"done","full_text":"..."}
                   or {"type":"error","detail":"..."}
    """

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        if not await self.conversation_exists(self.conversation_id, self.user):
            await self.close(code=4004)
            return

        await self.accept()

    async def receive(self, text_data):
        try:
            user_text = json.loads(text_data).get("message", "").strip()
        except (ValueError, AttributeError):
            return
        if not user_text:
            return

        # Load history BEFORE saving the new message (Gemini gets the new one separately)
        history = await self.get_history(self.conversation_id)
        await self.save_message(self.conversation_id, "user", user_text)
        await self.set_title_if_new(self.conversation_id, user_text)

        full_reply = ""
        try:
            async for chunk in ai_service.stream_lav_response(history, user_text):
                full_reply += chunk
                await self.send(text_data=json.dumps({"type": "chunk", "text": chunk}))
        except Exception as exc:  # show API/key errors in the UI instead of dying silently
            await self.send(text_data=json.dumps({"type": "error", "detail": str(exc)[:500]}))
            return

        if not full_reply:
            await self.send(text_data=json.dumps({"type": "error", "detail": "Gemini returned an empty reply (maybe blocked). Try rephrasing."}))
            return

        is_clarifying = full_reply.strip().endswith("?") and len(full_reply) < 300
        await self.save_message(self.conversation_id, "bot", full_reply, is_clarifying)
        await self.send(text_data=json.dumps({"type": "done", "full_text": full_reply, "is_clarifying": is_clarifying}))

    # ---------- DB helpers ----------
    @database_sync_to_async
    def conversation_exists(self, conversation_id, user):
        return Conversation.objects.filter(id=conversation_id, user=user).exists()

    @database_sync_to_async
    def save_message(self, conversation_id, role, content, is_clarifying=False):
        msg = Message.objects.create(
            conversation_id=conversation_id, role=role, content=content, is_clarifying=is_clarifying
        )
        Conversation.objects.get(id=conversation_id).save()  # bumps updated_at
        return msg

    @database_sync_to_async
    def get_history(self, conversation_id):
        latest = Message.objects.filter(conversation_id=conversation_id).order_by("-created_at")[:20]
        return list(latest)[::-1]  # last 20, oldest first

    @database_sync_to_async
    def set_title_if_new(self, conversation_id, text):
        conv = Conversation.objects.get(id=conversation_id)
        if conv.title == "New chat":
            conv.title = text[:50]
            conv.save()
