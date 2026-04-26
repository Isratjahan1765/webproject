"""Revenue views."""

from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import json

from .models import RevenueEntry
from .services import RevenueService


class RevenueListView(LoginRequiredMixin, ListView):
    model = RevenueEntry
    template_name = 'revenue/revenue_list.html'
    context_object_name = 'entries'
    paginate_by = 20

    def get_queryset(self):
        qs = RevenueEntry.objects.select_related('product')
        tx_type = self.request.GET.get('type', '')
        if tx_type:
            qs = qs.filter(transaction_type=tx_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx['page_title'] = _('Total Revenue')
        ctx['summary'] = RevenueService.get_revenue_summary(year=now.year)
        ctx['monthly_summary'] = RevenueService.get_revenue_summary(year=now.year, month=now.month)
        ctx['selected_type'] = self.request.GET.get('type', '')

        from django.core.serializers.json import DjangoJSONEncoder
        from django.db.models import Sum
        from .models import TransactionType

        # Expense by product
        expense_qs = RevenueEntry.objects.filter(transaction_type=TransactionType.ARRIVAL).values(
            'product__name'
        ).annotate(total_expense=Sum('total_amount')).order_by('-total_expense')[:15]
        
        expense_by_product = [
            {'product': e['product__name'], 'total': float(e['total_expense'] or 0)} 
            for e in expense_qs
        ]
        ctx['expense_by_product'] = json.dumps(expense_by_product, cls=DjangoJSONEncoder)

        # Revenue vs Expense (Doughnut data)
        rev_vs_exp = [
            {'label': str(_('Revenue')), 'amount': float(ctx['summary']['total_income'] or 0)},
            {'label': str(_('Expense')), 'amount': float(ctx['summary']['total_expense'] or 0)}
        ]
        ctx['rev_vs_exp_data'] = json.dumps(rev_vs_exp, cls=DjangoJSONEncoder)

        return ctx
