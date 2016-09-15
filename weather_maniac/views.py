"""weather_maniac Views."""

from django.shortcuts import render
from django.http import JsonResponse
from . import analysis


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


def return_json(request):
    """Return the JSON data for a forecast."""
    fcst_source = request.GET.get('forecaster')
    fcst_type = request.GET.get('type')
    # fcst_location = request.GET.get('location')
    json_data = analysis.return_json_of_forecast(fcst_source, fcst_type)
    return JsonResponse(json_data, safe=False)
