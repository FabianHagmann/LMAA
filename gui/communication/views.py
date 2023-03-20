from django.utils import timezone
from django.views.generic import TemplateView

from gui.assignments.models import Assignment


class CommunicationView(TemplateView):
    template_name = 'communication/main.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mytest'] = 'hello'
        context['assignments'] = Assignment.objects.order_by('semester', 'sheet', 'task')
        context['now'] = timezone.now()
        return context
