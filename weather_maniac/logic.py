"""weather_maniac Logic."""


from datetime import datetime
import json
from itertools import chain, groupby
from bs4 import BeautifulSoup
from . import utilities
from . import models


def _create_save_forecast(date, source, max_temps, min_temps):
    """Create and save Forecast model."""
    fcst = models.Forecast(
        date=date,
        source=source,
        max_temps=max_temps,
        min_temps=min_temps
    )
    fcst.save()
    return fcst


def _get_date(date_string):
    """  """
    date_format = '%Y_%m_%d'
    return datetime.strptime(date_string, date_format)


def _get_html_soup(file_name):
    """    """
    with open(file_name) as html_file:
        html_string = html_file.read()
    return BeautifulSoup(html_string, 'html.parser')


def _get_forecasts_from_html(html_soup):
    """  """
    return html_soup.find_all('div', class_='weather-box daily-forecast')


def _get_initialized_dict():
    """Return dict with none values in case forecast lacks particular dates."""
    return {k: None for k in range(8)}


def get_min_max_from_html(file_name):
    predict_date = _get_date(file_name[-24:-14])
    html_soup = _get_html_soup(file_name)
    daily_forecasts = _get_forecasts_from_html(html_soup)

    max_dict = _get_initialized_dict()
    min_dict = _get_initialized_dict()
    for forecast in daily_forecasts:
        forecast_utc = int(forecast.span['data-time'])
        days_in_advance = utilities.calc_days_in_adv(predict_date, forecast_utc//1000)
        if days_in_advance >= 0:
            max_dict[days_in_advance] = forecast.find('td', class_='high').get_text()
            min_dict[days_in_advance] = forecast.find('td', class_='low').get_text()
    forecast_obj = _create_save_forecast(
        predict_date, 'html', max_dict, min_dict)
    return forecast_obj


def temp_f(temp_k):
    return round(9 * (temp_k - 273.15) / 5 + 32)


def _get_json(file_name):
    """ """
    with open(file_name) as data_file:
        json_data = json.load(data_file)
    return json_data


def _get_forecasts_from_json(json_data):
    """ """
    date_temp = {}
    for row in json_data['list']:
        forecast_utc = row['dt']
        days_in_advance = utilities.calc_days_in_adv(predict_date, forecast_utc)
        temp = temp_f(row['main']['temp'])
        date_temp.append([days_in_advance, temp])


def get_min_max_from_json(file_name):
    predict_date = _get_date(file_name[-19:-9])
    json_data = _get_json(file_name)
    date_temp = []
    for row in json_data['list']:
        forecast_utc = row['dt']
        days_in_advance = calc_days_in_adv(predict_date, forecast_utc)
        temp = temp_f(row['main']['temp'])
        date_temp.append([days_in_advance, temp])
    highest_list = {0: None}
    lowest_list = {0: None}
    highest_list.update({k: max([v[1] for v in g])
                        for k, g in groupby(date_temp, lambda x: x[0])})
    lowest_list.update({k: min([v[1] for v in g])
                       for k, g in groupby(date_temp, lambda x: x[0])})
    return lowest_list, highest_list

