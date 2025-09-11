"""
TPM Admin Configuration

Django admin interface for TPM models and data management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import TPMConfiguration, TPMSession, TPMExperiment, User, Sessions
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(Sessions)
class SessionsAdmin(admin.ModelAdmin):
    """Admin interface for TPM Sessions model."""
    
    list_display = [
        'id', 'session_key_preview', 'is_active', 'is_expired_display',
        'created_at', 'expires_at', 'user_count'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['sessionKey', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'is_expired_display', 'user_count']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('sessionKey', 'is_active', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_expired_display', 'user_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def session_key_preview(self, obj):
        """Display a preview of the session key."""
        key = obj.sessionKey
        if len(key) > 30:
            return f"{key[:30]}..."
        return key
    session_key_preview.short_description = 'Session Key'
    
    def is_expired_display(self, obj):
        """Display expiration status with color coding."""
        is_expired = obj.is_expired()
        color = 'red' if is_expired else 'green'
        status = 'Expired' if is_expired else 'Active'
        return format_html('<span style="color: {};">{}</span>', color, status)
    is_expired_display.short_description = 'Status'
    
    def user_count(self, obj):
        """Display number of users with this session."""
        count = obj.user_set.count()
        if count > 0:
            url = reverse('admin:tpm_user_changelist') + f'?sessionId__id__exact={obj.id}'
            return format_html('<a href="{}">{} users</a>', url, count)
        return '0 users'
    user_count.short_description = 'Users'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'research_institution', 'has_active_session_display',
        'last_tpm_sync', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'date_joined',
        'last_tpm_sync', 'research_institution'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'research_institution']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Research Information', {
            'fields': ('research_institution', 'research_interests')
        }),
        ('TPM Session', {
            'fields': ('sessionId', 'last_tpm_sync', 'has_active_session_display'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['has_active_session_display', 'last_tpm_sync']
    
    def has_active_session_display(self, obj):
        """Display active session status with color coding."""
        has_session = obj.has_active_session()
        color = 'green' if has_session else 'red'
        status = 'Active Session' if has_session else 'No Active Session'
        return format_html('<span style="color: {};">{}</span>', color, status)
    has_active_session_display.short_description = 'TPM Session Status'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('sessionId')


@admin.register(TPMConfiguration)
class TPMConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for TPM Configuration model."""
    
    list_display = [
        'name', 'k', 'n', 'l', 'learning_rule', 
        'created_at', 'session_count', 'experiment_count'
    ]
    list_filter = ['learning_rule', 'created_at', 'k', 'n', 'l']
    search_fields = ['name', 'learning_rule']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'learning_rule')
        }),
        ('TPM Parameters', {
            'fields': ('k', 'n', 'l'),
            'description': 'K: Number of hidden units, N: Input dimension, L: Weight range'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def session_count(self, obj):
        """Display number of sessions using this configuration."""
        count = obj.sessions.count()
        if count > 0:
            url = reverse('admin:tpm_tpmsession_changelist') + f'?configuration__id__exact={obj.id}'
            return format_html('<a href="{}">{} sessions</a>', url, count)
        return '0 sessions'
    session_count.short_description = 'Sessions'
    
    def experiment_count(self, obj):
        """Display number of experiments using this configuration."""
        count = obj.experiments.count()
        if count > 0:
            url = reverse('admin:tpm_tpmexperiment_changelist') + f'?configuration__id__exact={obj.id}'
            return format_html('<a href="{}">{} experiments</a>', url, count)
        return '0 experiments'
    experiment_count.short_description = 'Experiments'


@admin.register(TPMSession)
class TPMSessionAdmin(admin.ModelAdmin):
    """Admin interface for TPM Session model."""
    
    list_display = [
        'id', 'user', 'configuration', 'is_synchronized', 
        'synchronization_steps', 'duration_display', 'created_at'
    ]
    list_filter = [
        'is_synchronized', 'created_at', 'configuration__learning_rule',
        'configuration__k', 'configuration__n'
    ]
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['created_at', 'completed_at', 'duration_display']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'configuration', 'session_key')
        }),
        ('Synchronization Status', {
            'fields': ('is_synchronized', 'synchronization_steps')
        }),
        ('Weight Matrix', {
            'fields': ('weight_matrix',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'duration_display'),
            'classes': ('collapse',)
        })
    )
    
    def duration_display(self, obj):
        """Display session duration in a readable format."""
        duration = obj.duration
        if duration is not None:
            if duration < 60:
                return f"{duration:.1f} seconds"
            elif duration < 3600:
                return f"{duration/60:.1f} minutes"
            else:
                return f"{duration/3600:.1f} hours"
        return "N/A"
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'configuration')


@admin.register(TPMExperiment)
class TPMExperimentAdmin(admin.ModelAdmin):
    """Admin interface for TPM Experiment model."""
    
    list_display = [
        'name', 'configuration', 'total_sessions', 'successful_sessions',
        'success_rate_display', 'average_sync_steps', 'created_at'
    ]
    list_filter = [
        'created_at', 'configuration__learning_rule', 
        'configuration__k', 'configuration__n'
    ]
    search_fields = ['name', 'description', 'configuration__name']
    readonly_fields = ['created_at', 'completed_at', 'success_rate_display']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Experiment Information', {
            'fields': ('name', 'description', 'configuration')
        }),
        ('Results', {
            'fields': (
                'total_sessions', 'successful_sessions', 'success_rate_display',
                'average_sync_steps', 'average_duration'
            )
        }),
        ('Detailed Results', {
            'fields': ('results_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def success_rate_display(self, obj):
        """Display success rate as a colored percentage."""
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('configuration')