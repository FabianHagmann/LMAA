from django.urls import path

from gui.testing.views import TestcaseListView, TestcaseDetailsView

urlpatterns = [
    path('testing/', TestcaseListView.as_view(), name='testing-list'),
    path('testing/<int:pk>', TestcaseDetailsView.as_view(), name='testing-details'),
]
