from django.urls import path

from gui.testing.views import TestcaseListView

urlpatterns = [
    path('testing/', TestcaseListView.as_view(), name='testing-list'),
]