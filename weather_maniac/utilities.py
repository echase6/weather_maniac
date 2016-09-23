#!/usr/bin/env python

import datetime
import math


def round_down_day(ref_day):
    """Returns day, resetting time to midnight.
    >>> round_down_day(datetime.datetime.fromtimestamp(1466532111))
    datetime.datetime(2016, 6, 21, 0, 0)
    """
    return ref_day.replace(hour=0, minute=0, second=0, microsecond=0)


def calc_days_in_adv(predict_date, forecast_utc):
    """Returns calendar days in advance, converting second argument from UTC.

    >>> calc_days_in_adv(datetime.date(2016, 6, 11), 1466553600 )
    10
    """
    # predict_date = predict_date
    forcst_date = datetime.datetime.fromtimestamp(forecast_utc).date()
    # forcst_date = round_down_day(forcst_date)
    return (forcst_date - predict_date).days


def temp_f(temp_k):
    """Kelvin to Fahrenheit converter.

    >>> temp_f(240)
    -28
    """
    return round(9 * (temp_k - 273.15) / 5 + 32)

def find_abs_largest(num_list):
    """Return the number farthest from zero.

    >>> find_abs_largest([1, 2, -3])
    -3.0
    """
    num_list.sort()
    min_num = num_list[0]
    max_num = num_list[-1]
    return math.copysign(max([abs(min_num), abs(max_num)]), min_num + max_num)