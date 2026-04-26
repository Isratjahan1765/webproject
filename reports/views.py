"""Report views — template-based."""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .services import ReportService


class MonthlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/monthly_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        year = int(self.request.GET.get('year', now.year))
        month = int(self.request.GET.get('month', now.month))

        report_data = ReportService.get_monthly_summary(year, month)

        # Historical data for Area Chart (last 6 months)
        from dateutil.relativedelta import relativedelta
        from django.db.models import Sum
        from .models import MonthlyReport
        import json
        from django.core.serializers.json import DjangoJSONEncoder

        historical_data = []
        for i in range(5, -1, -1):
            d = now - relativedelta(months=i)
            # Ensure reports exist for these months
            ReportService.generate_monthly_report(d.year, d.month)
            m_summary = MonthlyReport.objects.filter(
                year=d.year, month=d.month
            ).aggregate(
                arrived=Sum('total_arrived'),
                dispatched=Sum('total_dispatched')
            )
            historical_data.append({
                'month': d.strftime('%b'),
                'arrived': float(m_summary['arrived'] or 0),
                'dispatched': float(m_summary['dispatched'] or 0),
            })
        
        ctx['historical_json'] = json.dumps(historical_data, cls=DjangoJSONEncoder)

        ctx['page_title'] = _('Monthly Reports')
        ctx['year'] = year
        ctx['month'] = month
        ctx['summary'] = report_data['summary']
        ctx['reports'] = report_data['reports']
        
        # Overlapping Circles Data (Current Month)
        ctx['circle_data'] = json.dumps({
            'arrival_val': float(report_data['summary']['total_arrival_value'] or 0),
            'dispatch_val': float(report_data['summary']['total_dispatch_value'] or 0),
        }, cls=DjangoJSONEncoder)

        ctx['years'] = range(now.year - 2, now.year + 1)
        ctx['months'] = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
        ]
        return ctx
