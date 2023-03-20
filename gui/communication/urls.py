from django.urls import path

from .views import CommunicationView

urlpatterns = [
    path('communication/', CommunicationView.as_view(), name='communication')
]
