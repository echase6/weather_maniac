"""weather_maniac Views."""

from django.shortcuts import render
from django.http import JsonResponse
from . import logic
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
    forecast_source = request.GET.get('forecaster')
    json_data = analysis.return_json_of_forecast(forecast_source)
    return JsonResponse(json_data, safe=False)