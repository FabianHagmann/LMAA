from django.urls import path

from gui.visualization import views
from gui.visualization.views import VisualizationOverview, VisualizeSingleSolution, AssignmentSimilarity, \
    EditSingleSolution, TestMetricVisualizationView, VisualizationCompareView

urlpatterns = [
    path('visualization/overview', VisualizationOverview.as_view(), name='visualization-overview'),
    path('visualization/solution/<int:pk>', VisualizeSingleSolution.as_view(), name='visualize-solution'),
    path('visaulization/solution/<int:pk>/edit', EditSingleSolution.as_view(), name='edit-solution'),
    path('visualization/assignment/<int:ass>/solutions', views.fetch_solutions_for_assignment,
         name='visualization-assignment-solutions'),
    path('visualization/assignment/<int:ass>/similarity', AssignmentSimilarity.as_view(),
         name='visualization-assignment-similarity'),
    path('visualization/assignment/<int:ass>/similarity/communicator/<str:com>',
         views.fetch_assignment_similarity_for_communicator, name='visualization-assignment-similarity-communicator'),
    path('visualization/successmetrics', TestMetricVisualizationView.as_view(), name='visualization-test-metrics-overview'),
    path('visualization/compare/<str:sol1>/<str:sol2>', VisualizationCompareView.as_view(), name='visualization-compare'),
    path('visualization/export/similarity', views.export_similarity_report, name='visualization-export-similarity'),
    path('visualization/export/success', views.export_success_report, name='visualization-export-success'),
]
