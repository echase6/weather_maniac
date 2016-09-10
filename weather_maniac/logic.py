"""weather_maniac Logic."""


from datetime import datetime, timedelta
import json
from itertools import chain, groupby
from bs4 import BeautifulSoup
from . import utilities
from . import models


def _create_forecast(date, day_in_advance, source, max_temp, min_temp):
    """Create and save Forecast model."""
    return models.DayRecord(
        date_reference=date,
        day_in_advance=day_in_advance,
        source=source,
        max_temp=max_temp,
        min_temp=min_temp
    )


def _qualify_date(date):
    """Date qualifier.

    >>> _qualify_date(datetime(2016, 8, 1, 0, 0))
    True
    >>> _qualify_date(datetime(2006, 6, 1, 0, 0))
    False
    >>> _qualify_date(datetime(2200, 6, 1, 0, 0))
    False
    >>> _qualify_date(datetime(2016, 6, 1, 1, 1))
    False
    """
    return all([
        date > datetime(2016, 6, 1, 0, 0),
        date < datetime(2116, 6, 1, 0, 0),
        date == date.replace(hour=0, minute=0, second=0, microsecond=0)
    ])


def _qualify_fields(date, day_in_advance, source, max_temp, min_temp):
    """Field qualifiers, prior to saving record."""
    if not _qualify_date(date):
        raise ValueError('Date not as expected.  Got {}'.format(date))
    if source not in models.SOURCES:
        raise ValueError('Soucre not correct.  Got {}'.format(source))
    if day_in_advance < 0 or day_in_advance > 7:
        raise ValueError('Day in advance not correct.  Got {}'.format(day_in_advance))
    if max_temp < -99 or max_temp > 199:
        raise ValueError('Max temp not correct.  Got {}'.format(str(max_temp)))
    if min_temp < -99 or min_temp > 199:
        raise ValueError('Min temp not correct.  Got {}'.format(str(min_temp)))


def _update_forecast(date, day_in_advance, source, max_temp, min_temp):
    """Update the forecast point, creating a new one if needed."""
    _qualify_fields(date, day_in_advance, source, max_temp, min_temp)
    try:
        fcst = models.DayRecord.objects.get(
            date_reference=date,
            day_in_advance=day_in_advance,
            source=source
        )
    except models.DayRecord.DoesNotExist:
        fcst = _create_forecast(date, day_in_advance, source, max_temp, min_temp)
    fcst.max_temp = max(max_temp, fcst.max_temp)
    fcst.min_temp = min(min_temp, fcst.min_temp)
    fcst.save()
    return fcst


def _get_date(date_string):
    """Convert date string into date object.

    >>> _get_date('2016_06_01')
    datetime.datetime(2016, 6, 1, 0, 0)
    """
    date_format = '%Y_%m_%d'
    return datetime.strptime(date_string, date_format)


def _get_html_soup(file_name):
    """HTML file loader."""
    with open(file_name) as html_file:
        html_string = html_file.read()
    return BeautifulSoup(html_string, 'html.parser')


def _get_forecasts_from_html(html_soup):
    """HTML file content loader."""
    return html_soup.find_all('div', class_='weather-box daily-forecast')


def _get_retimed_fcsts_from_html(daily_forecasts, predict_date):
    """Harvests temperature points from html file. """
    days_to_max_min = {}
    for forecast in daily_forecasts:
        forecast_utc = int(forecast.span['data-time'])
        max_temp = int(forecast.find('td', class_='high').get_text())
        min_temp = int(forecast.find('td', class_='low').get_text())
        days_in_advance = utilities.calc_days_in_adv(predict_date, forecast_utc//1000)
        if days_in_advance >= 0:
            days_to_max_min[days_in_advance] = (max_temp, min_temp)
    return days_to_max_min


def process_html_file(file_name):
    """Main function to extract max and min temperatures from one HTML file
        and save the contents to a DayRecord.


    The prediction date comes from when the file was read, and is encoded in
       the filename.  The html file contains a forecast time, but this is ignored.
    The date the forecast applies to is normalized to PDT, and max/min temps
       are found for the time from midnight to midnight.
    """
    predict_date = _get_date(file_name[-24:-14])
    html_soup = _get_html_soup(file_name)
    daily_forecasts = _get_forecasts_from_html(html_soup)
    days_to_max_min = _get_retimed_fcsts_from_html(daily_forecasts, predict_date)
    for day_in_advance, (max_temp, min_temp) in days_to_max_min.items():
        date_reference = predict_date + timedelta(day_in_advance)
        try:
            _update_forecast(date_reference, day_in_advance, 'html', max_temp, min_temp)
        except ValueError as error:
            print(error)


def temp_f(temp_k):
    """Kelvin to Fahrenheit converter.

    >>> temp_f(240)
    -28
    """
    return round(9 * (temp_k - 273.15) / 5 + 32)


def _get_json(file_name):
    """JSON file content loader. """
    with open(file_name) as data_file:
        json_data = json.load(data_file)
    return json_data


def _get_retimed_fcsts_from_json(json_data, predict_date):
    """Harvests temperature points from json file. """
    date_temp = {}
    for row in json_data['list']:
        forecast_utc = row['dt']
        days_in_advance = utilities.calc_days_in_adv(predict_date, forecast_utc)
        temp = int(temp_f(row['main']['temp']))
        if days_in_advance in date_temp:
            date_temp[days_in_advance] += [temp]
        else:
            date_temp[days_in_advance] = [temp]
    return date_temp


def process_json_file(file_name):
    """Main function to extract max and min temperatures from one API(json) file
        and save the contents to a DayRecord.

    The file contains temperature predictions every hour (not max/min) so the
       process is to find the max and min for a given day.
    The prediction date comes from when the file was read, and is encoded in
       the filename.  The json file does not contain prediction time.
    The date the forecast applies to is normalized to PDT, and max/min temps
       are found for the time from midnight to midnight.
    """
    predict_date = _get_date(file_name[-19:-9])
    json_data = _get_json(file_name)
    date_temp = _get_retimed_fcsts_from_json(json_data, predict_date)
    days_to_max_min = {}
    for item in date_temp.items():
        days_to_max_min[item[0]] = (max(item[1]), min(item[1]))
    for day_in_advance, (max_temp, min_temp) in days_to_max_min.items():
        date_reference = predict_date + timedelta(day_in_advance)
        try:
            _update_forecast(date_reference, day_in_advance, 'api', max_temp, min_temp)
        except ValueError as error:
            print(error)

