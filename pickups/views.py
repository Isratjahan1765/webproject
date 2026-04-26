"""Pickup views."""

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views import View

from .models import Pickup, PickupStatus
from .services import PickupService


class PickupListView(LoginRequiredMixin, ListView):
    model = Pickup
    template_name = 'pickups/pickup_list.html'
    context_object_name = 'pickups'
    paginate_by = 15

    def get_queryset(self):
        qs = Pickup.objects.select_related('driver', 'confirmed_by').prefetch_related('items__product')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('destination', '-pickup_date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Confirm Delivery Pickup')
        ctx['statuses'] = PickupStatus.choices
        ctx['selected_status'] = self.request.GET.get('status', '')
        return ctx


class PickupDetailView(LoginRequiredMixin, DetailView):
    model = Pickup
    template_name = 'pickups/pickup_detail.html'
    context_object_name = 'pickup'

    def get_queryset(self):
        return Pickup.objects.select_related('driver', 'confirmed_by').prefetch_related('items__product')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Pickup {self.object.pickup_number}'
        return ctx


class PickupConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            PickupService.confirm_pickup(pk, request.user)
            messages.success(request, _('Pickup confirmed! Inventory & revenue updated.'))
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('pickups:pickup-detail', pk=pk)


class PickupCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reason = request.POST.get('reason', '')
        try:
            PickupService.cancel_pickup(pk, request.user, reason)
            messages.warning(request, _('Pickup cancelled.'))
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('pickups:pickup-detail', pk=pk)
