from django.urls import path

from . import views
from .views import AssignmentsView, AssignmentsDelete, TagView, TagsDelete

urlpatterns = [
    path('assignments', AssignmentsView.as_view(), name='assignments'),
    path('assignments/create', views.create_assignment, name='assignments-create'),
    path('assignments/<int:pk>/delete', AssignmentsDelete.as_view(), name='assignments-delete'),
    path('assignments/<int:pk>/details', views.assignment_details, name='assignments-details'),
    path('assignments/<int:pk>/edit', views.edit_assignment, name='assignments-edit'),
    path('assignments/tags', TagView.as_view(), name='tags'),
    path('assignments/tags/create', views.create_tag, name='tags-create'),
    path('assignments/tags/<int:pk>/edit', views.edit_tag, name='tags-edit'),
    path('assignments/tags/<int:pk>/delete', TagsDelete.as_view(), name='tags-delete'),
]
