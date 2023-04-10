from django.urls import path

from gui.visualization import views
from gui.visualization.views import VisualizationOverview, VisualizeSingleSolution

urlpatterns = [
    path('visualization/overview', VisualizationOverview.as_view(), name='visualization-overview'),
    path('visualization/solution/<int:pk>', VisualizeSingleSolution.as_view(), name='visualize-solution'),
    path('visualization/assignment/<int:ass>/solutions', views.fetch_solutions_for_assignment,
         name='visualization-assignment-solutions')
]
