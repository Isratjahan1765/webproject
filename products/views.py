"""
Product views — both template-based and utility views.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Product, ProductCategory, ProductUnit
from .services import ProductService


class ProductListView(LoginRequiredMixin, ListView):
    """List all active products with search and filter."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        # Search
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = ProductService.search_products(query)
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(category=category)
        return qs.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Product Catalogue')
        context['categories'] = ProductCategory.choices
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')

        import json
        from django.core.serializers.json import DjangoJSONEncoder
        from core.services import DashboardService
        
        context['inventory_distribution'] = json.dumps(
            list(DashboardService.get_inventory_distribution()),
            cls=DjangoJSONEncoder
        )
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """View full product details."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['page_title'] = product.name

        # Fetch related inventory
        try:
            from inventory.models import InventoryRecord
            context['inventory'] = InventoryRecord.objects.get(product=product)
        except Exception:
            context['inventory'] = None

        # Recent arrivals for this product
        try:
            from arrivals.models import ArrivalItem
            context['recent_arrivals'] = ArrivalItem.objects.select_related(
                'arrival', 'arrival__driver'
            ).filter(product=product).order_by('-arrival__arrival_date')[:5]
        except Exception:
            context['recent_arrivals'] = []

        # Recent pickups
        try:
            from pickups.models import PickupItem
            context['recent_pickups'] = PickupItem.objects.select_related(
                'pickup', 'pickup__driver'
            ).filter(product=product).order_by('-pickup__pickup_date')[:5]
        except Exception:
            context['recent_pickups'] = []

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Create a new product (Manager only)."""
    model = Product
    template_name = 'products/product_form.html'
    fields = [
        'name', 'name_bn', 'sku', 'category', 'unit',
        'unit_price', 'minimum_stock', 'description',
        'description_bn', 'image',
    ]
    success_url = reverse_lazy('products:product-list')

    def form_valid(self, form):
        messages.success(self.request, _('Product created successfully!'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Add New Product')
        context['form_action'] = 'create'
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing product (Manager only)."""
    model = Product
    template_name = 'products/product_form.html'
    fields = [
        'name', 'name_bn', 'sku', 'category', 'unit',
        'unit_price', 'minimum_stock', 'description',
        'description_bn', 'image', 'is_active',
    ]
    success_url = reverse_lazy('products:product-list')

    def form_valid(self, form):
        messages.success(self.request, _('Product updated successfully! Changes propagated.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Edit Product')
        context['form_action'] = 'update'
        return context


from django.views.generic import DeleteView
from django.db.models import ProtectedError
from django.shortcuts import redirect

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a product."""
    model = Product
    success_url = reverse_lazy('products:product-list')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Cannot delete this product because it is already tied to existing inventory, arrivals, or pickups. Please deactivate it instead.'))
            return redirect('products:product-list')

    def form_valid(self, form):
        messages.success(self.request, _('Product deleted successfully!'))
        return super().form_valid(form)
