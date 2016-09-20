"""weather_maniac Logic."""

from datetime import datetime, timedelta

from . import models
from . import utilities


def _create_forecast(date, day_in_advance, source, max_temp, min_temp):
    """Create Forecast model."""
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
        date > datetime(2016, 5, 1, 0, 0),
        date < datetime(2116, 6, 1, 0, 0),
        date == date.replace(hour=0, minute=0, second=0, microsecond=0)
    ])


def _qualify_fields(date, day_in_advance, source, max_temp, min_temp):
    """Field qualifiers, prior to saving record."""
    if not _qualify_date(date):
        raise ValueError('Date not as expected.  Got {}'.format(date))
    if source not in models.SOURCES:
        raise ValueError('Source not correct.  Got {}'.format(source))
    if day_in_advance < 0 or day_in_advance > 7:
        raise ValueError('Day in advance not correct.  Got {}'
                         .format(day_in_advance))
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
        fcst = _create_forecast(date, day_in_advance,
                                source, max_temp, min_temp)
    fcst.max_temp = max(max_temp, fcst.max_temp)
    fcst.min_temp = min(min_temp, fcst.min_temp)
    fcst.save()
    return fcst


def get_date(date_string):
    """Convert date string into date object.

    >>> get_date('2016_06_01')
    datetime.datetime(2016, 6, 1, 0, 0)
    """
    date_format = '%Y_%m_%d'
    return datetime.strptime(date_string, date_format)


def get_retimed_fcsts_from_html(daily_forecasts, predict_date):
    """Harvests temperature points from html file.

    Returns a dict with keys as day in advance, values as (max_temp, min_temp).
    """
    days_to_max_min = {}
    for forecast in daily_forecasts:
        forecast_utc = int(forecast.span['data-time'])
        max_temp = int(forecast.find('div', class_='wx-high').get_text())
        min_temp = int(forecast.find('div', class_='wx-low').get_text())
        days_in_advance = utilities.calc_days_in_adv(predict_date,
                                                     forecast_utc//1000)
        if days_in_advance >= 0:
            days_to_max_min[days_in_advance] = (max_temp, min_temp)
    return days_to_max_min


def process_days_to_max_min(days_to_max_min, predict_date, source):
    """Iterate through dict holding days-in-advance and max/min temps, and
          call forecast creation function with the results.
    """
    for day_in_advance, (max_temp, min_temp) in days_to_max_min.items():
        date_reference = predict_date + timedelta(day_in_advance)
        try:
            _update_forecast(date_reference, day_in_advance, source,
                             max_temp, min_temp)
        except ValueError as error:
            print(error)



def get_retimed_fcsts_from_json(json_data, predict_date):
    """Harvests temperature points from json file.

    Returns a dict with keys as day in advance, values as (max_temp, min_temp).
    """
    date_max_min_temp = {}
    for row in json_data['list']:
        forecast_utc = row['dt']
        days_in_advance = utilities.calc_days_in_adv(predict_date, forecast_utc)
        new_temp = int(utilities.temp_f(row['main']['temp']))
        if days_in_advance in date_max_min_temp:
            (max_temp, min_temp) = date_max_min_temp[days_in_advance]
            date_max_min_temp[days_in_advance] = (max([new_temp, max_temp]),
                                                  min([new_temp, min_temp]))
        else:
            date_max_min_temp[days_in_advance] = (new_temp, new_temp)
    return date_max_min_temp


def get_actual(date, location, max_temp, min_temp):
    """Get the actual point, creating a new one if needed."""
    _qualify_act_fields(date, location, max_temp, min_temp)
    try:
        act = models.ActualDayRecord.objects.get(
            date_meas=date,
            location=location,
        )
    except models.ActualDayRecord.DoesNotExist:
        act = models.ActualDayRecord(
            date_meas=date,
            location=location,
            max_temp=max_temp,
            min_temp=min_temp
        )
    return act


def _qualify_act_fields(date, location, max_temp, min_temp):
    """Field qualifiers, prior to saving record."""
    if not _qualify_date(date):
        raise ValueError('Date not as expected.  Got {}'.format(date))
    if location not in models.LOCATIONS.values():
        raise ValueError('Source not correct.  Got {}'.format(source))
    if max_temp < -99 or max_temp > 199:
        raise ValueError('Max temp not correct.  Got {}'.format(str(max_temp)))
    if min_temp < -99 or min_temp > 199:
        raise ValueError('Min temp not correct.  Got {}'.format(str(min_temp)))
