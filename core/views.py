"""
Core views — Dashboard and utility views.
"""

import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from .services import DashboardService


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard with real-time analytics and charts."""
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = DashboardService.get_overview_stats()
        context['top_products'] = DashboardService.get_top_products()
        context['recent_arrivals'] = DashboardService.get_recent_arrivals()
        context['recent_pickups'] = DashboardService.get_recent_pickups()
        context['revenue_chart_data'] = json.dumps(
            DashboardService.get_revenue_chart_data(),
            cls=DjangoJSONEncoder
        )
        context['inventory_distribution'] = json.dumps(
            list(DashboardService.get_inventory_distribution()),
            cls=DjangoJSONEncoder
        )
        context['page_title'] = 'Dashboard'
        return context


class DashboardAPIView(LoginRequiredMixin, TemplateView):
    """JSON endpoint for AJAX dashboard refresh."""

    def get(self, request, *args, **kwargs):
        data = {
            'stats': DashboardService.get_overview_stats(),
            'revenue_chart': DashboardService.get_revenue_chart_data(),
        }
        # Convert Decimal to float for JSON serialization
        for key, val in data['stats'].items():
            if hasattr(val, 'quantize'):
                data['stats'][key] = float(val)

        return JsonResponse(data, safe=False)
