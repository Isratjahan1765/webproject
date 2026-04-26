"""Driver views — template-based."""

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Driver


class DriverListView(LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'drivers/driver_list.html'
    context_object_name = 'drivers'
    paginate_by = 15

    def get_queryset(self):
        qs = Driver.objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(vehicle_number__icontains=q))
        avail = self.request.GET.get('available', '')
        if avail == '1':
            qs = qs.filter(is_available=True)
        elif avail == '0':
            qs = qs.filter(is_available=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Driver Registry')
        ctx['search_query'] = self.request.GET.get('q', '')

        # Summary Stats
        all_drivers = Driver.objects.all()
        ctx['total_drivers'] = all_drivers.count()
        ctx['available_drivers'] = all_drivers.filter(is_available=True).count()
        ctx['unique_vehicle_types'] = all_drivers.values('vehicle_type').distinct().count()

        return ctx


class DriverDetailView(LoginRequiredMixin, DetailView):
    model = Driver
    template_name = 'drivers/driver_detail.html'
    context_object_name = 'driver'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.name
        return ctx


class DriverCreateView(LoginRequiredMixin, CreateView):
    model = Driver
    template_name = 'drivers/driver_form.html'
    fields = ['name', 'name_bn', 'phone', 'alt_phone', 'nid_number', 'license_number',
              'vehicle_type', 'vehicle_number', 'address', 'photo']
    success_url = reverse_lazy('drivers:driver-list')

    def form_valid(self, form):
        messages.success(self.request, _('Driver registered successfully!'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Register Driver')
        ctx['form_action'] = 'create'
        return ctx


class DriverUpdateView(LoginRequiredMixin, UpdateView):
    model = Driver
    template_name = 'drivers/driver_form.html'
    fields = ['name', 'name_bn', 'phone', 'alt_phone', 'nid_number', 'license_number',
              'vehicle_type', 'vehicle_number', 'address', 'photo', 'is_available']
    success_url = reverse_lazy('drivers:driver-list')

    def form_valid(self, form):
        messages.success(self.request, _('Driver updated successfully!'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Edit Driver')
        ctx['form_action'] = 'update'
        return ctx

from django.views.generic import DeleteView
from django.db.models import ProtectedError
from django.shortcuts import redirect

class DriverDeleteView(LoginRequiredMixin, DeleteView):
    model = Driver
    success_url = reverse_lazy('drivers:driver-list')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Cannot delete this driver because they are already tied to existing arrivals or pickups. Please mark them as Unavailable instead.'))
            return redirect('drivers:driver-list')

    def form_valid(self, form):
        messages.success(self.request, _('Driver deleted successfully!'))
        return super().form_valid(form)
