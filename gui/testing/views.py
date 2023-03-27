from django.views.generic import TemplateView


class TestcaseListView(TemplateView):
    template_name = 'testing/testcase_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def __build_testcase_list_context__():
    pass