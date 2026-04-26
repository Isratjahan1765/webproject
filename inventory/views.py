"""Inventory views — template-based."""

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import F

from .models import InventoryRecord, InventoryLog


class InventoryListView(LoginRequiredMixin, ListView):
    model = InventoryRecord
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        qs = InventoryRecord.objects.select_related('product').filter(product__is_active=True)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(product__name__icontains=q)
        stock_filter = self.request.GET.get('stock', '')
        if stock_filter == 'low':
            qs = qs.filter(
                total_quantity__gt=0,
                total_quantity__lt=F('product__minimum_stock') + F('reserved_quantity')
            )
        elif stock_filter == 'out':
            qs = qs.filter(total_quantity__lte=F('reserved_quantity'))
        return qs.order_by('product__name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Inventory Management')
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['stock_filter'] = self.request.GET.get('stock', '')

        import json
        from django.core.serializers.json import DjangoJSONEncoder
        from core.services import DashboardService
        
        ctx['inventory_distribution'] = json.dumps(
            list(DashboardService.get_inventory_distribution()),
            cls=DjangoJSONEncoder
        )

        top_products = DashboardService.get_top_products(limit=15)
        line_data = [
            {'name': p.product.name, 'qty': p.total_quantity}
            for p in top_products
        ]
        ctx['inventory_line_data'] = json.dumps(line_data, cls=DjangoJSONEncoder)
        
        return ctx


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = InventoryRecord
    template_name = 'inventory/inventory_detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        return InventoryRecord.objects.select_related('product')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Inventory: {self.object.product.name}'
        ctx['logs'] = InventoryLog.objects.filter(
            product=self.object.product
        ).order_by('-created_at')[:20]
        return ctx
