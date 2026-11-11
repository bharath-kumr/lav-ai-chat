from rest_framework import generics, permissions

from .models import Conversation
from .serializers import ConversationSerializer, ConversationDetailSerializer


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/chat/conversations/      -> list this user's chat threads (sidebar)
    POST /api/chat/conversations/      -> start a new conversation, returns its id
                                           (frontend then opens a WebSocket to it)
    """

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/chat/conversations/<id>/   -> full thread incl. all messages
    DELETE /api/chat/conversations/<id>/   -> delete a conversation
    """

    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
