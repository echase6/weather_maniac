"""weather_maniac Views."""

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Max, Min
from . import analysis
from . import models
from . import utilities
import datetime


def render_index(request):
    """Render the index (landing) page."""
    return render(request, 'weather_maniac/index.html')


def render_statistics(request):
    """Render the statistics (analysis) page."""
    # template_list = {
    #     'stats': [
    #         {
    #          'source': 'Source 1',
    #          'mtype': 'max',
    #          'start_date': datetime.date(2016, 6, 1),
    #          'end_date': datetime.date(2016, 8, 1),
    #          'stats_by_day': [
    #              {'day': 0, 'mean': 1, 'std': 0.5, 'max': 2},
    #              {'day': 1, 'mean': 1, 'std': 0.5, 'max': 2},
    #              {'day': 2, 'mean': 1, 'std': 0.5, 'max': 2},
    #              {'day': 3, 'mean': 1, 'std': 0.5, 'max': 2},
    #              {'day': 4, 'mean': 1, 'std': 0.5, 'max': 2},
    #          ]},
    #         {
    #             'source': 'Source 2',
    #             'mtype': 'max',
    #             'start_date': datetime.date(2016, 6, 1),
    #             'end_date': datetime.date(2016, 8, 1),
    #             'stats_by_day': [
    #                 {'day': 0, 'mean': 1, 'std': 0.5, 'max': 2},
    #                 {'day': 1, 'mean': 1, 'std': 0.5, 'max': 2},
    #                 {'day': 2, 'mean': 1, 'std': 0.5, 'max': 2},
    #                 {'day': 3, 'mean': 1, 'std': 0.5, 'max': 2},
    #                 {'day': 4, 'mean': 1, 'std': 0.5, 'max': 2},
    #         ]}
    #     ]
    # }
    template_list = {}
    template_stats = []
    for source in models.SOURCES:
        for mytpe in models.TYPES:
            end_date = datetime.date(2016, 5, 1)
            start_date = datetime.date(2116, 6, 1)
            record = {
                'source': models.SOURCE_TO_NAME[source],
                'mtype': mytpe
            }
            stats_by_day = []
            mean, std = analysis.get_statistics(source, 'PDX', mytpe)
            for day in range(models.SOURCE_TO_LENGTH[source]):
                bins = analysis.get_all_bins(source, 'PDX', mytpe, day)
                # mean, std = analysis.get_statistics(source, 'PDX', mtype)
                bin_start = bins.aggregate(Min('start_date'))['start_date__min']
                start_date = min([bin_start, start_date])
                bin_end = bins.aggregate(Max('end_date'))['end_date__max']
                end_date = max([bin_end, end_date])
                max_pos_error = bins.aggregate(Max('error'))['error__max']
                max_neg_error = bins.aggregate(Min('error'))['error__min']
                max_error = utilities.find_abs_largest([max_pos_error,
                                                        max_neg_error])
                record_by_day = {
                    'day': day,
                    'mean': mean[day],
                    'std': std[day],
                    'max': max_error
                }
                stats_by_day.append(record_by_day)
            record['stats_by_day'] = stats_by_day
            record['start_date'] = start_date
            record['end_date'] = end_date
            template_stats.append(record)
    template_list['stats'] = template_stats
    return render(request, 'weather_maniac/statistics.html', template_list)


def render_prediction(request):
    """Render the prediction page."""
    return render(request, 'weather_maniac/prediction.html')


def render_graph(request):
    """Render the prediction page."""
    return render(request, 'weather_maniac/graph.html')


def return_json(request):
    """Return the JSON data for a forecast."""
    fcst_source = request.GET.get('forecaster')
    fcst_type = request.GET.get('mtype')
    # fcst_location = request.GET.get('location')
    json_data = analysis.return_json_of_forecast(fcst_source, fcst_type)
    return JsonResponse(json_data, safe=False)
