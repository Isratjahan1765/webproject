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

        ctx['page_title'] = _('Monthly Reports')
        ctx['year'] = year
        ctx['month'] = month
        ctx['summary'] = report_data['summary']
        ctx['reports'] = report_data['reports']
        ctx['years'] = range(now.year - 2, now.year + 1)
        ctx['months'] = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
        ]
        return ctx
