#!/usr/bin/env python

import arrow

SOURCES = ['json', 'html', 'screen']


class Forecast:
    """Class that contains a forecast.

    """
    def __init__(self, source, day_made, days_to_temps):
        """Initialize new forecast.
        source is a string
        day_made is an Arrow date object
        days_to_temps is a dict of the form: {0: temp1, 1: temp2, 2: temp3..}

        """
        self.source = source
        self.day_made = day_made
        self.days_to_temps = days_to_temps

    def __eq__(self, other):
        """Test for equality

        """
        return (self.source == other.source and
                self.day_made == other.day_made and
                self.days_to_temps == other.days_to_temps
                )

    def __repr__(self):
        """Magic repr function for display and debug.

        """
        return 'Forecast({}, {}, {})'.format(
            self.source, self.day_made, self.days_to_temps)


def add_forecast(source, day_made, temp_list):
    """Add forecast to overall list of forecasts.
    Checking added to ensure fields are expected types.
    """
    if source not in SOURCES:
        raise ValueError('source {} not expected'.format(source))
    in_size = len(temp_list)
    if in_size == 0 or in_size > 7:
        raise ValueError('temp list is not valid')
    temp_dict = {index: temp for index, temp in enumerate(temp_list)}

    date_made_object = arrow.get(day_made)
    return Forecast(source, date_made_object, temp_dict)


def distill_forecast(forecast_list):
    source = forecast_list[0].source
    date_made = forecast_list[0].day_made
    summary_temp_dict = {}
    for index in range(7):
        summary_temp_dict.update(index: mean([forecast.days_to_temps[index] for forecast in forecast_list]))
