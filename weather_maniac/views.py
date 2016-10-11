"""weather_maniac Views."""

from django.shortcuts import render
from django.http import JsonResponse
from . import statistics
from . import models


def render_index(request):
    """Render the index (landing) page."""
    return render(request, 'weather_maniac/index.html')


def render_faq(request):
    """Render the faq page."""
    return render(request, 'weather_maniac/faq.html')


def render_statistics(request):
    """Render the statistics (analysis) page."""
    template_stats = []
    for source in ['html', 'api', 'jpeg']:  # TODO: Expand to cover other JPEG's
        for mtype in models.TYPES:
            record = statistics.make_stats_json(source, mtype)
            template_stats.append(record)
    template_list = {'stats': template_stats}
    return render(request, 'weather_maniac/statistics.html', template_list)


def render_prediction(request):
    """Render the prediction page."""
    return render(request, 'weather_maniac/prediction.html')


def render_graph(request):
    """Render the comparison page."""
    return render(request, 'weather_maniac/graph.html')


def return_graph_json(request):
    mtype = request.GET.get('mtype')
    template_json = statistics.make_graph_json(mtype)
    return JsonResponse(template_json, safe=False)


def return_json(request):
    """Return the JSON data for a forecast."""
    fcst_source = request.GET.get('forecaster')
    fcst_type = request.GET.get('mtype')
    json_data = statistics.return_json_of_forecast(fcst_source, fcst_type)
    return JsonResponse(json_data, safe=False)
