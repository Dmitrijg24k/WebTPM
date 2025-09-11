"""
TPM Models

Django models for neural cryptography implementation.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class Sessions(models.Model):
    """
    TPM synchronization session model.
    
    Stores session keys generated from synchronized Tree-like Parity Machines
    for secure user authentication and data encryption.
    """
    id = models.AutoField(db_column='Id', primary_key=True)
    sessionKey = models.TextField(
        default='none',
        help_text="Generated session key from TPM synchronization"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "TPM Session"
        verbose_name_plural = "TPM Sessions"
    
    def __str__(self):
        return f"Session {self.id}: {self.sessionKey[:20]}..."
    
    def is_expired(self):
        """Check if the session has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Adds TPM session management and research-specific user fields.
    """
    sessionId = models.OneToOneField(
        'Sessions', 
        on_delete=models.CASCADE, 
        verbose_name="TPM Session", 
        null=True,
        blank=True,
        help_text="Active TPM synchronization session"
    )
    research_institution = models.CharField(
        max_length=200,
        blank=True,
        help_text="Research institution or affiliation"
    )
    research_interests = models.TextField(
        blank=True,
        help_text="Research interests in neural cryptography"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_tpm_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = "Research User"
        verbose_name_plural = "Research Users"
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def has_active_session(self):
        """Check if user has an active TPM session."""
        return (self.sessionId and 
                self.sessionId.is_active and 
                not self.sessionId.is_expired())
    
    def get_session_key(self):
        """Get the current session key if available."""
        if self.has_active_session():
            return self.sessionId.sessionKey
        return None


class TPMConfiguration(models.Model):
    """
    Configuration parameters for Tree-like Parity Machines.
    
    This model stores the hyperparameters used in TPM experiments,
    including the number of hidden units (K), input dimension (N),
    and weight range (L).
    """
    name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this TPM configuration"
    )
    k = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Number of hidden units (K)"
    )
    n = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Input dimension per hidden unit (N)"
    )
    l = models.PositiveIntegerField(
        default=6,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Weight range (L)"
    )
    learning_rule = models.CharField(
        max_length=20,
        choices=[
            ('hebbian', 'Hebbian Learning'),
            ('anti_hebbian', 'Anti-Hebbian Learning'),
            ('random_walk', 'Random Walk'),
        ],
        default='hebbian',
        help_text="Learning rule for weight updates"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "TPM Configuration"
        verbose_name_plural = "TPM Configurations"
    
    def __str__(self):
        return f"TPM Config: K={self.k}, N={self.n}, L={self.l} ({self.learning_rule})"


class TPMSession(models.Model):
    """
    TPM synchronization session between two machines.
    
    This model tracks the synchronization process, including
    the number of steps required, success status, and generated keys.
    """
    configuration = models.ForeignKey(
        TPMConfiguration,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    user = models.ForeignKey(
        'todos.User',
        on_delete=models.CASCADE,
        related_name='tpm_sessions'
    )
    session_key = models.TextField(
        blank=True,
        help_text="Generated synchronized key"
    )
    synchronization_steps = models.PositiveIntegerField(
        default=0,
        help_text="Number of steps required for synchronization"
    )
    is_synchronized = models.BooleanField(
        default=False,
        help_text="Whether synchronization was successful"
    )
    weight_matrix = models.JSONField(
        default=dict,
        help_text="Final synchronized weight matrix"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "TPM Session"
        verbose_name_plural = "TPM Sessions"
    
    def __str__(self):
        status = "Synchronized" if self.is_synchronized else "In Progress"
        return f"TPM Session {self.id} - {status} ({self.synchronization_steps} steps)"
    
    @property
    def duration(self):
        """Calculate session duration in seconds."""
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None


class TPMExperiment(models.Model):
    """
    Experimental data for TPM research.
    
    This model stores experimental results for analysis,
    including performance metrics and statistical data.
    """
    name = models.CharField(
        max_length=200,
        help_text="Experiment name or identifier"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed experiment description"
    )
    configuration = models.ForeignKey(
        TPMConfiguration,
        on_delete=models.CASCADE,
        related_name='experiments'
    )
    total_sessions = models.PositiveIntegerField(default=0)
    successful_sessions = models.PositiveIntegerField(default=0)
    average_sync_steps = models.FloatField(default=0.0)
    average_duration = models.FloatField(default=0.0)
    results_data = models.JSONField(
        default=dict,
        help_text="Detailed experimental results"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "TPM Experiment"
        verbose_name_plural = "TPM Experiments"
    
    def __str__(self):
        return f"Experiment: {self.name}"
    
    @property
    def success_rate(self):
        """Calculate synchronization success rate."""
        if self.total_sessions > 0:
            return (self.successful_sessions / self.total_sessions) * 100
        return 0.0