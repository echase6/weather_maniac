"""Test record loader for tests."""

from . import models
import datetime


def histo_loader():
    """This dumps data into histograms for testing purposes."""
    for source_name, source_item in models.SOURCES.items():
        for mtype in models.TYPES:
            for day in range(source_item['length']):
                histo = models.ErrorHistogram(
                    source=source_name,
                    mtype=mtype,
                    location='PDX',
                    day_in_advance=day)
                histo.save()
                for error in range(1, 4):
                    qty = 10 - 7 * abs(error - 2)  # gives 3, 10, 3 distrib.
                    models.ErrorBin(
                        member_of_hist=histo,
                        error=error,
                        quantity=qty,
                        start_date=datetime.date(2016, 6, 1),
                        end_date=datetime.date(2016, 8, 1)
                    ).save()


def record_loader():
    """Dumps data into Day Records and Actual Day Records"""
    location = 'PDX'
    start_day = datetime.date(2016, 7, 1)
    day_count = 12
    day_iter = [start_day + datetime.timedelta(n) for n in range(day_count)]
    for date in day_iter:
        models.ActualDayRecord(date_meas=date,
                               location=location,
                               max_temp=76,
                               min_temp=55).save()
        for source in models.SOURCES:
            for day in range(3):
                models.DayRecord(date_reference=date,
                                 day_in_advance=day,
                                 source=source,
                                 max_temp=74 + day,
                                 min_temp=57 - day).save()
