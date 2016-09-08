"""weather_maniac Models."""

from django.db import models


class Forecast(models.Model):
    """Forecast from a particular source.

    date_made is the calendar day that the forecast was made
    source is a string holding a reference of the forecaster
    max/min temp dictionaries have keys as the day in advance the forecast
       covers, 0:today, 1:tomorrow, 2:day-after-tomorrow, etc.
    """
    date_made = models.DateField()
    source = models.TextField()
    max_temp = {k: models.IntegerField() for k in range(8)}
    min_temp = {k: models.IntegerField() for k in range(8)}

    def __str__(self):
        return self.source, self.date_made

    def __repr__(self):
        return 'Forecast(source:{!r}, date:{!r}'.format(
            self.source,
            self.date_made
        )


class DayRecord(models.Model):
    """Record for an individual day."""
    date = models.DateField()

    def __str__(self):
        return self.date

    def __repr__(self):
        return 'DayRecord(date:{!r}'.format(
            self.date
        )


class SourceDayRecord(models.Model):
    """Record for an individual forecaster.

    day is the day where a temperature wes measured.
    source is a string holding a reference of the forecaster
    min/max temp dictionaries have keys as the day in the past the forecast
       covers, 0:today, 1:yesterday, 2:day-before-yesterday, etc.
    """
    day = models.ForeignKey(DayRecord)
    source = models.TextField
    max_temp = {k: models.IntegerField() for k in range(8)}
    min_temp = {k: models.IntegerField() for k in range(8)}

    def __str__(self):
        return self.source, self.day

    def __repr__(self):
        return 'SourceDayRecord(source:{!r}, date:{!r}'.format(
            self.source,
            self.day
        )


class ActualDayRecord(models.Model):
    """Actual measured temp on a particular day."""
    day = models.ForeignKey(DayRecord)
    location = models.TextField()
    max_temp = models.IntegerField()
    min_temp = models.IntegerField()

    def __str__(self):
        return self.location, self.day

    def __repr__(self):
        return 'ActualDayRecord(location:{!r}, date:{!r}'.format(
            self.location,
            self.day
        )
