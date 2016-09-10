"""weather_maniac Models."""

from django.db import models
import datetime

SOURCES = ['html', 'api']
TYPES = ['max', 'min']
LOCATIONS = ['AUR', 'OCO', 'PDX', 'TRO', 'KGW', 'GRE', 'PWO', 'BNP']


class ForecastPoint(models.Model):
    """Models to hold forecast points.

    date_made holds the date the forecast was made
    date_covers holds the date the forecast if for
    source identifies the forecaster; it is a member of SOURCES
    max/min are the forecasted max/min, in Fahrenheit
    """
    date_made = models.DateField()
    date_covers = models.DateField()
    source = models.CharField(max_length=6)
    max_temp = models.IntegerField()
    min_temp = models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(ForecastPoint(date_made=datetime.datetime(2016,6,1),
        ... date_covers=datetime.datetime(2016,6,2),
        ... source='html', max_temp=83, min_temp=50))
        '2016-06-01 00:00:00, 2016-06-02 00:00:00, html, 83, 50'
        """
        return ', '.join([
            str(self.date_made),
            str(self.date_covers),
            self.source,
            str(self.max_temp),
            str(self.min_temp)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ForecastPoint(date_made=datetime.datetime(2016,6,1),
        ... date_covers=datetime.datetime(2016,6,2),
        ... source='html', max_temp=83, min_temp=50))
        "ForecastPoint(date_made=datetime.datetime(2016, 6, 1, 0, 0), date_covers=datetime.datetime(2016, 6, 2, 0, 0), source='html', max_temp=83, min_temp=50"
        """
        return 'ForecastPoint(date_made={!r}, date_covers={!r}, source={!r}, ' \
               'max_temp={!r}, min_temp={!r}'.format(
            self.date_made,
            self.date_covers,
            self.source,
            self.max_temp,
            self.min_temp
        )


class DayRecord(models.Model):
    """Record (forecasted) for an individual day.

    date_reference is the date a temperature forecast applies to.
    day_in_advance is the number of days in advance the forecast was made (0-7)
    source identifies the forecaster; it is a member of SOURCES
    """
    date_reference = models.DateField()
    day_in_advance = models.IntegerField()
    source = models.CharField(max_length=6)
    max_temp = models.IntegerField()
    min_temp = models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(DayRecord(date_reference=datetime.datetime(2016,6,1),
        ... day_in_advance=3, source='html', max_temp=83, min_temp=50))
        '2016-06-01 00:00:00, 3, html, 83, 50'
        """
        return ', '.join([
            str(self.date_reference),
            str(self.day_in_advance),
            self.source,
            str(self.max_temp),
            str(self.min_temp)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(DayRecord(date_reference=datetime.datetime(2016,6,1),
        ... day_in_advance=3, source='html', max_temp=83, min_temp=50))
        "DayRecord(date=datetime.datetime(2016, 6, 1, 0, 0), day in advance=3, source='html', max temp=83, min temp=50"
        """
        return 'DayRecord(date={!r}, day in advance={!r}, source={!r}, ' \
               'max temp={!r}, min temp={!r}'.format(
            self.date_reference,
            self.day_in_advance,
            self.source,
            self.max_temp,
            self.min_temp
        )


class ActualDayRecord(models.Model):
    """Actual temperatures on an individual day.

    date_meas is the date a temperature was measured.
    location is a string that identifies the location the temp was measured.
    type is 'max' or 'min', a member of TYPES
    """
    date_meas = models.DateField()
    location = models.CharField(max_length=6)
    type = models.CharField(max_length=6)
    temp = models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(ActualDayRecord(date_meas=datetime.datetime(2016, 6, 1),
        ... location="PDX", type='min', temp=50))
        '2016-06-01 00:00:00, PDX, min, 50'
        """
        return ', '.join([
            str(self.date_meas),
            self.location,
            self.type,
            str(self.temp)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ActualDayRecord(date_meas=datetime.datetime(2016, 6, 1),
        ... location="PDX", type='min', temp=50))
        "ActualDayRecord(date=datetime.datetime(2016, 6, 1, 0, 0), location='PDX', type='min', temp=50)"
        """
        return 'ActualDayRecord(date={!r}, location={!r}, type={!r}, ' \
               'temp={!r})'.format(
            self.date_meas,
            self.location,
            self.type,
            self.temp
        )


class ErrorHistogram(models.Model):
    """Histogram of forecast errors

    source is the forecasting source, a member of SOURCES
    type is either 'max' or 'min'.  length kept longer in case this is
       expanded to include rain, or other forecasting metrics

    Will hold modeled parameters to avoid re-calculation.
    Will be the parent of bins which represent the data.
    """
    source = models.CharField(max_length=6)
    type = models.CharField(max_length=6)

    def __str__(self):
        r"""String function

        >>> str(ErrorHistogram(source='api', type='max'))
        'api, max'
        """
        return ', '.join([
            self.source,
            self.type
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ErrorHistogram(source='api', type='max'))
        "ErrorHistogram(source='api', type='max')"
        """
        return 'ErrorHistogram(source={!r}, type={!r})'.format(
            self.source,
            self.type
        )


class ErrorBin(models.Model):
    """Bin holding forecast error

    member_of_hist holds the histogram ID
    error holds the error amount:  forecast - actual, deg Fahrenheit
    quantity holds the number of times this error occurred
    """
    member_of_hist = models.ForeignKey(ErrorHistogram)
    error = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(ErrorBin(error=-1, quantity=10))
        '-1, 10'
        """
        return ', '.join([
            str(self.error),
            str(self.quantity)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ErrorBin(error=-1, quantity=10))
        'ErrorBin(error=-1, quantity=10)'
        """
        return 'ErrorBin(error={!r}, quantity={!r})'.format(
            self.error,
            self.quantity
        )
