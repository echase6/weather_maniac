"""Weather Maniac Logic modules.

These functions deal with:
  -- Creating instances of DayRecord to hold forecast data points
  -- Creating instances of ActualDayRecord to hold measure temperature points
  -- Qualifying and then loading the forecast data into DayRecord
  -- Qualifying and then loading the measured temps into ActualDayRecord
"""
from datetime import datetime, timedelta

from . import models
from . import utilities


def _create_forecast(date, day_in_advance, source, max_temp, min_temp):
    """Create Forecast model.

    >>> _create_forecast(datetime(2016, 8, 1).date(), 2, 'api', 83, 47)
    ... # doctest: +NORMALIZE_WHITESPACE
    DayRecord(date=datetime.date(2016, 8, 1), day in advance=2,
    source='api', max temp=83, min temp=47
    """
    return models.DayRecord(
        date_reference=date,
        day_in_advance=day_in_advance,
        source=source,
        max_temp=max_temp,
        min_temp=min_temp
    )


def _qualify_date(date):
    """Date qualifier.

    >>> _qualify_date(datetime(2016, 8, 1).date())
    True
    >>> _qualify_date(datetime(2006, 6, 1).date())
    False
    >>> _qualify_date(datetime(2200, 6, 1).date())
    False
    """
    return all([
        date > datetime(2016, 5, 1).date(),
        date < datetime(2116, 6, 1).date()
    ])


def _qualify_fields(date, day_in_advance, source, max_temp, min_temp):
    """Field qualifiers, prior to saving record.

    >>> _qualify_fields(datetime(2016, 5, 1).date(), 3, 'api', 65, 23)
    Traceback (most recent call last):
    ...
    ValueError: Date not as expected.  Got 2016-05-01
    >>> _qualify_fields(datetime(2016, 7, 1).date(), 3, 'aaa', 65, 23)
    Traceback (most recent call last):
    ...
    ValueError: Source not correct.  Got aaa
    >>> _qualify_fields(datetime(2016, 7, 1).date(), 3, 'api', 615, 23)
    Traceback (most recent call last):
    ...
    ValueError: Max temp not correct.  Got 615
    >>> _qualify_fields(datetime(2016, 7, 1).date(), 3, 'api', 65, -223)
    Traceback (most recent call last):
    ...
    ValueError: Min temp not correct.  Got -223
    >>> _qualify_fields(datetime(2016, 7, 1).date(), 8, 'api', 65, 23)
    Traceback (most recent call last):
    ...
    ValueError: Day in advance not correct.  Got 8
    >>> _qualify_fields(datetime(2016, 7, 1).date(), 4, 'api', 65, 23)
    """
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


def _qualify_act_fields(date, location, max_temp, min_temp):
    """Field qualifiers, prior to saving record.

    >>> _qualify_act_fields(datetime(2016, 5, 1).date(), 'PDX', 65, 23)
    Traceback (most recent call last):
    ...
    ValueError: Date not as expected.  Got 2016-05-01
    >>> _qualify_act_fields(datetime(2016, 7, 1).date(), 'PDX', 615, 23)
    Traceback (most recent call last):
    ...
    ValueError: Max temp not correct.  Got 615
    >>> _qualify_act_fields(datetime(2016, 7, 1).date(), 'PDX', 65, -123)
    Traceback (most recent call last):
    ...
    ValueError: Min temp not correct.  Got -123
    >>> _qualify_act_fields(datetime(2016, 7, 1).date(), 'PPP', 65, 23)
    Traceback (most recent call last):
    ...
    ValueError: Location not correct.  Got PPP
    >>> _qualify_act_fields(datetime(2016, 7, 1).date(), 'PDX', 65, 23)
    """
    if not _qualify_date(date):
        raise ValueError('Date not as expected.  Got {}'.format(date))
    if location not in models.LOCATIONS.values():
        raise ValueError('Location not correct.  Got {}'.format(location))
    if max_temp < -99 or max_temp > 199:
        raise ValueError('Max temp not correct.  Got {}'.format(str(max_temp)))
    if min_temp < -99 or min_temp > 199:
        raise ValueError('Min temp not correct.  Got {}'.format(str(min_temp)))


def _update_forecast(date, day_in_advance, source, max_temp, min_temp):
    """Update the forecast point, creating a new one if needed.

    >>> from . import models
    >>> _update_forecast(datetime(2016, 8, 1).date(), 2, 'api', 83, 47)
    ...  # doctest: +NORMALIZE_WHITESPACE
    DayRecord(date=datetime.date(2016, 8, 1), day in advance=2,
    source='api', max temp=83, min temp=47
    >>> _update_forecast(datetime(2016, 8, 1).date(), 2, 'api', 80, 47)
    ...  # doctest: +NORMALIZE_WHITESPACE
    DayRecord(date=datetime.date(2016, 8, 1), day in advance=2,
    source='api', max temp=83, min temp=47
    >>> _update_forecast(datetime(2016, 8, 1).date(), 2, 'api', 90, 40)
    ...  # doctest: +NORMALIZE_WHITESPACE
    DayRecord(date=datetime.date(2016, 8, 1), day in advance=2,
    source='api', max temp=90, min temp=40
    >>> _update_forecast(datetime(2016, 8, 2).date(), 2, 'api', 70, 40)
    ...  # doctest: +NORMALIZE_WHITESPACE
    DayRecord(date=datetime.date(2016, 8, 2), day in advance=2,
    source='api', max temp=70, min temp=40
    >>> for record in models.DayRecord.objects.all():
    ...   print(str(record))
    2016-08-01, 2, api, 90, 40
    2016-08-02, 2, api, 70, 40
    """
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

    >>> get_date('2016_06_01_10_10')
    datetime.date(2016, 6, 1)
    """
    date_format = '%Y_%m_%d_%H_%M'
    return datetime.strptime(date_string, date_format).date()


def get_retimed_fcsts_from_html(daily_forecasts, predict_date):
    """Harvests temperature points from html file.

    Returns a dict with keys as day in advance, values as (max_temp, min_temp).

    >>> from . import load_test_html
    >>> from . import data_loader
    >>> predict_date = datetime(2016, 7, 24).date()
    >>> html_soup = data_loader.extract_fcst_soup(load_test_html.test_html)
    >>> get_retimed_fcsts_from_html(html_soup, predict_date)
    ...   # doctest: +NORMALIZE_WHITESPACE
    {0: (83, 59), 1: (82, 61), 2: (80, 62), 3: (84, 60), 4: (87, 62),
    5: (92, 62)}
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

    >>> from . import models
    >>> days_to_max_min = ({0: (83, 59), 1: (82, 61), 2: (80, 62), 3: (84, 60),
    ...   4: (87, 62), 5: (92, 62)})
    >>> predict_date = datetime(2016, 7, 24).date()
    >>> process_days_to_max_min(days_to_max_min, predict_date, 'api')
    >>> for record in models.DayRecord.objects.all():
    ...   print(str(record))
    2016-07-24, 0, api, 83, 59
    2016-07-25, 1, api, 82, 61
    2016-07-26, 2, api, 80, 62
    2016-07-27, 3, api, 84, 60
    2016-07-28, 4, api, 87, 62
    2016-07-29, 5, api, 92, 62

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

    >>> from . import load_test_json
    >>> import json
    >>> predict_date = datetime(2016, 6, 16).date()
    >>> json_data = json.loads(load_test_json.test_json)
    >>> get_retimed_fcsts_from_json(json_data, predict_date)
    ... # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    {0: (59, 51), 1: (63, 47), 2: (60, 47), 3: (69, 39), 4: (82, 44),
    5: (82, 51)}
    """
    if 'list' not in json_data:
        return {}
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
    """Get the actual point, creating a new one if needed.

    >>> act = get_actual(datetime(2016, 8, 1).date(), 'PDX', 83, 47)
    >>> act.save()
    >>> act
    ...  # doctest: +NORMALIZE_WHITESPACE
    ActualDayRecord(date=datetime.date(2016, 8, 1), location='PDX',
    max_temp=83, min_temp=47)
    >>> act2 = get_actual(datetime(2016, 8, 1).date(), 'PDX', 0, 0)
    >>> act2
    ...  # doctest: +NORMALIZE_WHITESPACE
    ActualDayRecord(date=datetime.date(2016, 8, 1), location='PDX',
    max_temp=83, min_temp=47)
    """
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
