"""Notification views."""

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.utils.translation import gettext_lazy as _

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Notifications')
        ctx['unread_count'] = Notification.objects.filter(user=self.request.user, is_read=False).count()
        return ctx


class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.mark_as_read()
        return redirect(notif.link or 'notifications:notification-list')


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications:notification-list')
