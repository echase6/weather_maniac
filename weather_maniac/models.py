"""weather_maniac Models."""

from django.db import models
import datetime
import os
from . import file_processor
from . import settings

# SOURCES = ['html', 'api', 'jpeg', 'jpeg3', 'jpeg4']

SOURCES = {'html': {'length': 7, 'alias': 'Service A',
                    'data_path': os.path.join(file_processor.ROOT_PATH,
                                              'HTML_Data'),
                    'arch_path': os.path.join(file_processor.ROOT_PATH,
                                              'HTML_Arch'),
                    'location': settings.WM_SRC2_ID},
           'act': {'data_path': os.path.join(file_processor.ROOT_PATH,
                                             'ACT_Data'),
                   'arch_path': os.path.join(file_processor.ROOT_PATH,
                                             'ACT_Arch'),
                   'location': settings.WM_MEAS_ID},
           'api': {'length': 5, 'alias': 'Service B',
                   'data_path': os.path.join(file_processor.ROOT_PATH,
                                             'API_Data'),
                   'arch_path': os.path.join(file_processor.ROOT_PATH,
                                             'API_Arch'),
                   'id': settings.WM_APP_ID,
                   'key': settings.WM_APP_KEY},
           'jpeg': {'length': 7, 'alias': 'Service C',
                    'data_path': os.path.join(file_processor.ROOT_PATH,
                                              'JPEG_Data'),
                    'arch_path': os.path.join(file_processor.ROOT_PATH,
                                              'JPEG_Arch'),
                    'location': settings.WM_SRC1_ID,
                    'dims': {
                        'x_pitch': 86.5, 'x_start': 98,
                        'max': {'off_x': 0, 'loc_y': 301, 'win_x': 81,
                                'win_y': 37, 'dark_back': True, 'fat': True},
                        'min': {'off_x': 0, 'loc_y': 334, 'win_x': 54,
                                'win_y': 28, 'dark_back': True, 'fat': False},
                        'day': {'off_x': 0, 'loc_y': 127, 'win_x': 73,
                                'win_y': 18, 'dark_back': True,
                                'fat': False}}},
           'jpeg3': {'length': 7, 'alias': 'Service D',
                     'data_path': os.path.join(file_processor.ROOT_PATH,
                                               'JPEG3_Data'),
                     'arch_path': os.path.join(file_processor.ROOT_PATH,
                                               'JPEG3_Arch'),
                     'location': settings.WM_SRC3_ID,
                     'dims': {
                         'x_pitch': 114, 'x_start': 99,
                         'max': {'off_x': 24, 'loc_y': 100.5, 'win_x': 64,
                                 'win_y': 40, 'dark_back': True, 'fat': False},
                         'min': {'off_x': -29, 'loc_y': 119, 'win_x': 43,
                                 'win_y': 32, 'dark_back': True, 'fat': False},
                         'day': {'off_x': 0, 'loc_y': 352, 'win_x': 100,
                                 'win_y': 30, 'dark_back': False, 'fat': False}
                     }},
           'jpeg4': {'length': 7, 'alias': 'Service E',
                     'data_path': os.path.join(file_processor.ROOT_PATH,
                                               'JPEG4_Data'),
                     'arch_path': os.path.join(file_processor.ROOT_PATH,
                                               'JPEG4_Arch'),
                     'location': settings.WM_SRC4_ID,
                     'dims': {
                         'x_pitch': 90, 'x_start': 49,
                         'max': {'off_x': -9, 'loc_y': 305, 'win_x': 65,
                                 'win_y': 56, 'dark_back': True, 'fat': False},
                         'min': {'off_x': 20, 'loc_y': 353, 'win_x': 46,
                                 'win_y': 30, 'dark_back': True, 'fat': False},
                         'day': {'off_x': 0, 'loc_y': 121, 'win_x': 83,
                                 'win_y': 23, 'dark_back': False, 'fat': False}
                     }}
           }

# SOURCE_TO_LENGTH = {'html': 7, 'api': 5, 'jpeg': 7, 'jpeg3': 7, 'jpeg4': 7}
# SOURCE_TO_NAME = {'html': 'Service A', 'api': 'Service B', 'jpeg': 'Service C',
#                   'jpeg3': 'Service D', 'jpeg4': 'Service E'}
TYPES = ['max', 'min']
LOCATIONS = {'AURORA STATE AIRPORT OR US': 'AUR',
             'OREGON CITY OR US': 'OCO',
             'PORTLAND INTERNATIONAL AIRPORT OR US': 'PDX',
             'TROUTDALE OR US': 'TRO',
             'PORTLAND KGW TV OR US': 'KGW',
             'GRESHAM 2 SW OR US': 'GRE',
             'PORTLAND WEATHER FORECAST OFFICE OR US': 'PWO',
             'NATURE PARK BEAVERTON OR US': 'BNP'}


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

        >>> str(DayRecord(date_reference=datetime.date(2016, 6, 1),
        ... day_in_advance=3, source='html', max_temp=83, min_temp=50))
        '2016-06-01, 3, html, 83, 50'
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

        >>> repr(DayRecord(date_reference=datetime.date(2016, 6, 1),
        ... day_in_advance=3, source='html', max_temp=83, min_temp=50))
        ...   # doctest: +NORMALIZE_WHITESPACE
        "DayRecord(date=datetime.date(2016, 6, 1), day in advance=3,
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

        >>> str(ActualDayRecord(date_meas=datetime.date(2016, 6, 1),
        ... location="PDX", max_temp=83, min_temp=50))
        '2016-06-01, PDX, 83, 50'
        """
        return ', '.join([
            str(self.date_meas),
            self.location,
            str(self.max_temp),
            str(self.min_temp)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ActualDayRecord(date_meas=datetime.date(2016, 6, 1),
        ... location="PDX", max_temp=83, min_temp=50))
        ...   # doctest: +NORMALIZE_WHITESPACE
        "ActualDayRecord(date=datetime.date(2016, 6, 1),
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
    mtype is either 'max' or 'min'.  length kept longer in case this is
       expanded to include rain, or other forecasting metrics, a TYPES member
    location is a member of LOCATIONS, the measurement point

    Will hold modeled parameters to avoid re-calculation.
    Will be the parent of bins which represent the data.
    """
    source = models.CharField(max_length=6)
    location = models.CharField(max_length=6)
    mtype = models.CharField(max_length=6)
    day_in_advance = models.IntegerField()

    def __str__(self):
        r"""String function

        >>> str(ErrorHistogram(source='api', mtype='max', location='PDX',
        ... day_in_advance=2))
        'api, max, PDX, 2'
        """
        return ', '.join([
            self.source,
            self.mtype,
            self.location,
            str(self.day_in_advance)
        ])

    def __repr__(self):
        r"""Repr function

        >>> repr(ErrorHistogram(source='api', mtype='max', location='PDX',
        ... day_in_advance=2))
        ...   # doctest: +NORMALIZE_WHITESPACE
        "ErrorHistogram(source='api', mtype='max', location='PDX',
        day_in_advance=2)"
        """
        return 'ErrorHistogram(source={!r}, mtype={!r}, location={!r}, ' \
               'day_in_advance={!r})'.format(
                self.source,
                self.mtype,
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

        >>> histo = ErrorHistogram(source='api', mtype='max', location='PDX',
        ... day_in_advance=2)
        >>> str(ErrorBin(member_of_hist=histo, error=-1, quantity=10,
        ... start_date=datetime.date(2016, 6, 1),
        ... end_date=datetime.date(2016, 8, 1)))
        'api, max, PDX, 2, -1, 10, 2016-06-01, 2016-08-01'
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

        >>> histo = ErrorHistogram(source='api', mtype='max', location='PDX',
        ... day_in_advance=2)
        >>> repr(ErrorBin(member_of_hist=histo, error=-1, quantity=10,
        ... start_date=datetime.date(2016, 6, 1),
        ... end_date=datetime.date(2016, 8, 1)))
        ...  # doctest: +NORMALIZE_WHITESPACE
        "ErrorBin(member_of_hist=ErrorHistogram(source='api', mtype='max',
        location='PDX', day_in_advance=2), error=-1, quantity=10,
        start_date=datetime.date(2016, 6, 1),
        end_date=datetime.date(2016, 8, 1))"
        """
        return 'ErrorBin(member_of_hist={!r}, error={!r}, quantity={!r}, ' \
               'start_date={!r}, end_date={!r})'.format(
                self.member_of_hist,
                self.error,
                self.quantity,
                self.start_date,
                self.end_date
                )
