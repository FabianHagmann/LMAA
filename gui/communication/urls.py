from django.urls import path

from gui.communication import views
from gui.communication.views import LanguageModelRequestFormView, LanguageModelRequestConfigurationFormView, \
    LanguageModelRequestSolutionEditFormView

urlpatterns = [
    path('communication/new/', LanguageModelRequestFormView.as_view(), name='communication'),
    path('communication/new/<int:req>/configure', LanguageModelRequestConfigurationFormView.as_view(),
         name='communication-configure'),
    path('communication/new/success', views.communication_success_view,
         name='communication-success'),
    path('communication/status', LanguageModelRequestSolutionEditFormView.as_view(), name='communication-status'),
]
