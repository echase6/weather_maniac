"""weather_maniac Models."""

from django.db import models
import datetime

SOURCES = ['html', 'api']
SOURCE_TO_LENGTH = {'html': 7, 'api': 5}
TYPES = ['max', 'min']
LOCATIONS = {'AURORA STATE AIRPORT OR US':'AUR',
             'OREGON CITY OR US':'OCO',
             'PORTLAND INTERNATIONAL AIRPORT OR US':'PDX',
             'TROUTDALE OR US':'TRO',
             'PORTLAND KGW TV OR US':'KGW',
             'GRESHAM 2 SW OR US':'GRE',
             'PORTLAND WEATHER FORECAST OFFICE OR US':'PWO',
             'NATURE PARK BEAVERTON OR US':'BNP'}


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
        ...   # doctest: +NORMALIZE_WHITESPACE
        "DayRecord(date=datetime.datetime(2016, 6, 1, 0, 0), day in advance=3,
        source='html', max temp=83, min temp=50"
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
    """
    date_meas = models.DateField()
    location = models.CharField(max_length=6)
    max_temp = models.IntegerField()
    min_temp = models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(ActualDayRecord(date_meas=datetime.datetime(2016, 6, 1),
        ... location="PDX", max_temp=83, min_temp=50))
        '2016-06-01 00:00:00, PDX, 83, 50'
        """
        return ', '.join([
            str(self.date_meas),
            self.location,
            str(self.max_temp),
            str(self.min_temp)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ActualDayRecord(date_meas=datetime.datetime(2016, 6, 1),
        ... location="PDX", max_temp=83, min_temp=50))
        ...   # doctest: +NORMALIZE_WHITESPACE
        "ActualDayRecord(date=datetime.datetime(2016, 6, 1, 0, 0),
        location='PDX', max_temp=83, min_temp=50)"
        """
        return 'ActualDayRecord(date={!r}, location={!r}, max_temp={!r}, ' \
               'min_temp={!r})'.format(
            self.date_meas,
            self.location,
            self.max_temp,
            self.min_temp
        )


class ErrorHistogram(models.Model):
    """Histogram of forecast errors

    source is the forecasting source, a member of SOURCES
    type is either 'max' or 'min'.  length kept longer in case this is
       expanded to include rain, or other forecasting metrics, a TYPES member
    location is a member of LOCATIONS, the measurement point

    Will hold modeled parameters to avoid re-calculation.
    Will be the parent of bins which represent the data.
    """
    source = models.CharField(max_length=6)
    location = models.CharField(max_length=6)
    type = models.CharField(max_length=6)
    day_in_advance= models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(ErrorHistogram(source='api', type='max', location='PDX',
        ... day_in_advance=2))
        'api, max, PDX, 2'
        """
        return ', '.join([
            self.source,
            self.type,
            self.location,
            str(self.day_in_advance)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ErrorHistogram(source='api', type='max', location='PDX',
        ... day_in_advance=2))
        ...   # doctest: +NORMALIZE_WHITESPACE
        "ErrorHistogram(source='api', type='max', location='PDX',
        day_in_advance=2)"
        """
        return 'ErrorHistogram(source={!r}, type={!r}, location={!r}, ' \
               'day_in_advance={!r})'.format(
            self.source,
            self.type,
            self.location,
            self.day_in_advance
        )


class ErrorBin(models.Model):
    """Bin holding forecast error

    member_of_hist holds the histogram ID
    error holds the error amount:  forecast - actual, deg Fahrenheit
    quantity holds the number of times this error occurred
    start and end dates indicate the date range the histogram bins have
       accumulated over, to prevent double-counting.
    """
    member_of_hist = models.ForeignKey(ErrorHistogram)
    error = models.IntegerField()
    quantity = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        r"""String function

        >>> histo = ErrorHistogram(source='api', type='max', location='PDX',
        ... day_in_advance=2)
        >>> str(ErrorBin(member_of_hist=histo, error=-1, quantity=10,
        ... start_date=datetime.datetime(2016, 6, 1, 0, 0),
        ... end_date=datetime.datetime(2016, 8, 1, 0, 0)))
        'api, max, PDX, 2, -1, 10, 2016-06-01 00:00:00, 2016-08-01 00:00:00'
        """
        return ', '.join([
            str(self.member_of_hist),
            str(self.error),
            str(self.quantity),
            str(self.start_date),
            str(self.end_date)
        ])

    def __repr__(self):
        r"""Repr function

        >>> histo = ErrorHistogram(source='api', type='max', location='PDX',
        ... day_in_advance=2)
        >>> repr(ErrorBin(member_of_hist=histo, error=-1, quantity=10,
        ... start_date=datetime.datetime(2016, 6, 1, 0, 0),
        ... end_date=datetime.datetime(2016, 8, 1, 0, 0)))
        ...  # doctest: +NORMALIZE_WHITESPACE
        "ErrorBin(member_of_hist=ErrorHistogram(source='api', type='max',
        location='PDX', day_in_advance=2), error=-1, quantity=10,
        start_date=datetime.datetime(2016, 6, 1, 0, 0),
        end_date=datetime.datetime(2016, 8, 1, 0, 0))"
        """
        return 'ErrorBin(member_of_hist={!r}, error={!r}, quantity={!r}, ' \
               'start_date={!r}, end_date={!r})'.format(
            self.member_of_hist,
            self.error,
            self.quantity,
            self.start_date,
            self.end_date
        )
