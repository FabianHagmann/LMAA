from django.urls import path

from gui.testing import views
from gui.testing.views import TestcaseListView, TestcaseDetailsView, TestcaseContainsOverview, TestcaseContainsAddNew, \
    TestcaseContainsDelete

urlpatterns = [
    path('testing/', TestcaseListView.as_view(), name='testing-list'),
    path('testing/<int:ass>', TestcaseDetailsView.as_view(), name='testing-details'),
    path('testing/<int:ass>/contains', TestcaseContainsOverview.as_view(), name='testing-contains-overview'),
    path('testing/<int:ass>/contains/add', TestcaseContainsAddNew.as_view(), name='testing-contains-add'),
    path('testing/<int:ass>/contains/<int:pk>/delete', TestcaseContainsDelete.as_view(), name='testing-contains-delete'),
    path('testing/<int:ass>/execute', views.start_tests_for_assignment, name='testing-execute'),
]
