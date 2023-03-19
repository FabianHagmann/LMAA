from django.urls import path

from .views import AssignmentsView, AssignmentsDelete
from . import views

urlpatterns = [
    path('assignments', AssignmentsView.as_view(), name='assignments'),
    path('assignments/create', views.create_assignment, name='assignments-create'),
    path('assignments/<int:pk>/delete/', AssignmentsDelete.as_view(), name='assignments-delete'),
    path('assignments/<int:pk>/details', views.assignment_details, name='assignments-details'),
    path('assignments/<int:pk>/edit', views.edit_assignment, name='assignments-edit'),
]
