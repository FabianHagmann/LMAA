from django.urls import path

from .views import AssignmentsView
from . import views

urlpatterns = [
    path('assignments', AssignmentsView.as_view(), name='assignments'),
    path('assignments/create', views.create_assignment, name='assignments-create'),
]
