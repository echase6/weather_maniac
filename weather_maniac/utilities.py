#!/usr/bin/env python

from datetime import datetime


def round_down_day(ref_day):
    """Returns day, resetting time to midnight.
    >>> round_down_day(datetime.fromdatestamp(1466532111))
    datetime.datetime(2016, 6, 21, 0, 0)
    """
    return ref_day.replace(hour=0, minute=0, second=0, microsecond=0)


def calc_days_in_adv(predict_date, forecast_utc):
    """Returns calendar days in advance, converting second argument from UTC.

    >>> calc_days_in_adv(datetime.datetime(2016, 6, 11, 11, 0), 1466553600 )
    10
    """
    predict_date = round_down_day(predict_date)
    forcst_date = datetime.fromtimestamp(forecast_utc)
    forcst_date = round_down_day(forcst_date)
    return (forcst_date - predict_date).days