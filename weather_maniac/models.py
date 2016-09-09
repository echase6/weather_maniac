"""weather_maniac Models."""

from django.db import models
import datetime

SOURCES = ['html', 'api']


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
        "ActualDayRecord(date=datetime.datetime(2016, 6, 1, 0, 0), location='PDX', max_temp=83, min_temp=50)"
        """
        return 'ActualDayRecord(date={!r}, location={!r}, max_temp={!r}, ' \
               'min_temp={!r})'.format(
            self.date_meas,
            self.location,
            self.max_temp,
            self.min_temp
        )
