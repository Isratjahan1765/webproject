"""
Global context processors for SPHWMS templates.
Injects data available in every template render.
"""

from django.conf import settings


def global_context(request):
    """Inject global variables into all templates."""
    return {
        'SYSTEM_NAME': 'SPHWMS',
        'SYSTEM_FULL_NAME': 'Smart Post-Harvest Warehouse Management System',
        'SYSTEM_NAME_BN': 'স্মার্ট পোস্ট-হার্ভেস্ট গুদাম ব্যবস্থাপনা সিস্টেম',
        'CURRENT_LANGUAGE': getattr(request, 'LANGUAGE_CODE', 'en'),
        'AVAILABLE_LANGUAGES': settings.LANGUAGES,
        'DEBUG_MODE': settings.DEBUG,
        'unread_notifications_count': _get_unread_count(request),
    }


def _get_unread_count(request):
    """Get unread notification count for authenticated users."""
    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            return Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            return 0
    return 0
