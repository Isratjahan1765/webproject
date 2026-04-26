"""Arrival views — template-based."""

from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View

from .models import Arrival, ArrivalStatus
from .services import ArrivalService


class ArrivalListView(LoginRequiredMixin, ListView):
    model = Arrival
    template_name = 'arrivals/arrival_list.html'
    context_object_name = 'arrivals'
    paginate_by = 15

    def get_queryset(self):
        qs = Arrival.objects.select_related('driver', 'confirmed_by').prefetch_related('items__product')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Confirm New Arrivals')
        ctx['statuses'] = ArrivalStatus.choices
        ctx['selected_status'] = self.request.GET.get('status', '')
        return ctx


class ArrivalDetailView(LoginRequiredMixin, DetailView):
    model = Arrival
    template_name = 'arrivals/arrival_detail.html'
    context_object_name = 'arrival'

    def get_queryset(self):
        return Arrival.objects.select_related('driver', 'confirmed_by').prefetch_related('items__product')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Arrival {self.object.batch_number}'
        return ctx


class ArrivalConfirmView(LoginRequiredMixin, View):
    """POST-only view to confirm an arrival."""

    def post(self, request, pk):
        try:
            ArrivalService.confirm_arrival(pk, request.user)
            messages.success(request, _('Arrival confirmed! Inventory updated.'))
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, _('Error confirming arrival.'))
        return redirect('arrivals:arrival-detail', pk=pk)


class ArrivalRejectView(LoginRequiredMixin, View):
    """POST-only view to reject an arrival."""

    def post(self, request, pk):
        reason = request.POST.get('reason', '')
        try:
            ArrivalService.reject_arrival(pk, request.user, reason)
            messages.warning(request, _('Arrival rejected.'))
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('arrivals:arrival-detail', pk=pk)
