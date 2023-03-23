from django.urls import path

from gui.communication.views import LanguageModelRequestFormView, LanguageModelRequestConfigurationFormView, \
    LanguageModelRequestSolutionEditFormView

urlpatterns = [
    path('communication/', LanguageModelRequestFormView.as_view(), name='communication'),
    path('communication/configure', LanguageModelRequestConfigurationFormView.as_view(),
         name='communication-configure'),
    path('communication/edit', LanguageModelRequestSolutionEditFormView.as_view(), name='communication-edit'),
]
