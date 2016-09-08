"""weather_maniac Views."""

from django.shortcuts import render
from . import logic

def render_index(request):
    """Render the index (landing) page."""
    return render(request, 'weather_maniac/index.html')



def render_statistics(request):
    """Render the statistics (analysis) page."""
    return render(request, 'weather_maniac/statistics.html')



def render_prediction(request):
    """Render the prediction page."""
    return render(request, 'weather_maniac/prediction.html')



def render_graph(request):
    """Render the prediction page."""
    return render(request, 'weather_maniac/graph.html')