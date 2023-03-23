from django.urls import path

from gui.communication.views import LanguageModelRequestFormView, LanguageModelRequestConfigurationFormView, \
    LanguageModelRequestSolutionEditFormView

urlpatterns = [
    path('communication/new/', LanguageModelRequestFormView.as_view(), name='communication'),
    path('communication/new/configure', LanguageModelRequestConfigurationFormView.as_view(),
         name='communication-configure'),
    path('communication/new/edit', LanguageModelRequestSolutionEditFormView.as_view(), name='communication-edit'),
]
