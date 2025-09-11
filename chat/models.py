"""
Chat Models

Real-time communication models for WebTPM.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    """
    Chat room model for research collaboration.
    
    Allows researchers to communicate in real-time about
    TPM experiments and neural cryptography topics.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Chat room name"
    )
    description = models.TextField(
        blank=True,
        help_text="Room description"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_rooms',
        help_text="User who created the room"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(
        default=50,
        help_text="Maximum number of participants"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"
    
    def __str__(self):
        return f"Room: {self.name}"


class ChatMessage(models.Model):
    """
    Chat message model for real-time communication.
    
    Stores messages sent in chat rooms with optional
    encryption using TPM session keys.
    """
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Chat room this message belongs to"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        help_text="User who sent the message"
    )
    content = models.TextField(
        help_text="Message content"
    )
    encrypted_content = models.TextField(
        blank=True,
        help_text="Encrypted message content"
    )
    is_encrypted = models.BooleanField(
        default=False,
        help_text="Whether the message is encrypted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"Message from {self.user.username} in {self.room.name}"
    
    def can_be_encrypted(self):
        """Check if message can be encrypted with user's session."""
        return self.user.has_active_session()