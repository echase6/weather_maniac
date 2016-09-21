"""Weather Maniac Analysis modules."""

import datetime
import math
from django.db.models import Max, Min

from . import data_loader
from . import models



def create_histogram(source, location, type, day_in_advance):
    """Create Error Histogram.

    >>> create_histogram('api', 'PDX', 'max', 2)
    ErrorHistogram(source='api', type='max', location='PDX', day_in_advance=2)
    """
    return models.ErrorHistogram(
        source=source,
        location=location,
        type=type,
        day_in_advance=day_in_advance
    )


def create_bin(histo, error, quantity, start_date, end_date):
    """Create Error Bin.

    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> create_bin(histo, -1, 10,datetime.datetime(2016, 6, 1, 0, 0),
    ... datetime.datetime(2016, 8, 1, 0, 0))
    ...   # doctest: +NORMALIZE_WHITESPACE
    ErrorBin(member_of_hist=ErrorHistogram(source='api', type='max',
    location='PDX', day_in_advance=2), error=-1, quantity=10,
    start_date=datetime.datetime(2016, 6, 1, 0, 0),
    end_date=datetime.datetime(2016, 8, 1, 0, 0))
    """
    return models.ErrorBin(
        member_of_hist=histo,
        error=error,
        quantity=quantity,
        start_date=start_date,
        end_date=end_date
    )


def get_histogram(source, location, type, day_in_advance):
    """Get the histogram.  Make one if it does not exist.

    >>> get_histogram('api', 'PDX', 'max', 2)
    ErrorHistogram(source='api', type='max', location='PDX', day_in_advance=2)
    >>> get_histogram('api', 'PDX', 'max', 3)
    ErrorHistogram(source='api', type='max', location='PDX', day_in_advance=3)
    >>> for histo in models.ErrorHistogram.objects.all():
    ...   print(str(histo))
    api, max, PDX, 2
    api, max, PDX, 3
    """
    try:
        histo = models.ErrorHistogram.objects.get(
            location=location,
            day_in_advance=day_in_advance,
            source=source,
            type=type
        )
    except models.ErrorHistogram.DoesNotExist:
        histo = create_histogram(source, location, type, day_in_advance)
        histo.save()
    return histo


def get_bin(histo, error, date):
    """Get the error bin.  Make one if it does not exist.

    New bin initialized to have quantity=1 since its end date will disqualify
      it from being incremented in the next step.

    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> histo.save()
    >>> get_bin(histo, 2, datetime.date(2016, 6, 1))
    ...   # doctest: +NORMALIZE_WHITESPACE
    ErrorBin(member_of_hist=ErrorHistogram(source='api', type='max',
    location='PDX', day_in_advance=2), error=2, quantity=1,
    start_date=datetime.date(2016, 6, 1), end_date=datetime.date(2016, 6, 1))
    >>> get_bin(histo, 3, datetime.date(2016, 8, 1))
    ...   # doctest: +NORMALIZE_WHITESPACE
    ErrorBin(member_of_hist=ErrorHistogram(source='api', type='max',
    location='PDX', day_in_advance=2), error=3, quantity=1,
    start_date=datetime.date(2016, 8, 1), end_date=datetime.date(2016, 8, 1))
    >>> for bin in models.ErrorBin.objects.all():
    ...   print(str(bin))
    api, max, PDX, 2, 2, 1, 2016-06-01, 2016-06-01
    api, max, PDX, 2, 3, 1, 2016-08-01, 2016-08-01
    """
    try:
        bin = histo.errorbin_set.get(
            error=error
        )
    except models.ErrorBin.DoesNotExist:
        bin = create_bin(histo, error, 1, date, date)
        bin.save()
    return bin


def update_histogram(histo, error, date):
    """Update the forecast point, creating a new one if needed.

    Updating in this sense is:
      -- increment the count in an appropriate bin by 1
      -- change the end date to the record date (to avoid double-counting)

    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> histo.save()
    >>> update_histogram(histo, 1, datetime.date(2016, 8, 1))
    >>> update_histogram(histo, 1, datetime.date(2016, 8, 2))
    >>> update_histogram(histo, 1, datetime.date(2016, 7, 1))
    >>> for bin in models.ErrorBin.objects.all():
    ...   print(str(bin))
    api, max, PDX, 2, 1, 2, 2016-08-01, 2016-08-02
    >>> update_histogram(histo, -1, datetime.date(2016, 7, 1))
    >>> update_histogram(histo, -1, datetime.date(2016, 8, 2))
    >>> for bin in models.ErrorBin.objects.all():
    ...   print(str(bin))
    api, max, PDX, 2, 1, 2, 2016-08-01, 2016-08-02
    api, max, PDX, 2, -1, 2, 2016-07-01, 2016-08-02
    """
    bin = get_bin(histo, error, date)
    if bin.end_date < date:
        bin.quantity += 1
        bin.end_date = date
        bin.save()


def populate_histogram(source, location, type, day_in_advance):
    """Main function to populate Error Bins in appropriate Error Histogram.

    Combines data from ActualDayRecords (i.e., measured temperature) and data
       from matching DayRecords (i.e., forecast).

    >>> models.ActualDayRecord(date_meas=datetime.date(2016, 6, 1),
    ... location="PDX", max_temp=76, min_temp=55).save()
    >>> models.DayRecord(date_reference=datetime.date(2016, 6, 1),
    ... day_in_advance=3, source='api', max_temp=83, min_temp=50).save()
    >>> populate_histogram('api', 'PDX', 'max', 3)
    ErrorHistogram(source='api', type='max', location='PDX', day_in_advance=3)
    >>> populate_histogram('html', 'PDX', 'max', 3)
    No forecast matching actual record for 2016-06-01
    ErrorHistogram(source='html', type='max', location='PDX', day_in_advance=3)
    >>> for histo in models.ErrorHistogram.objects.all():
    ...   print(str(histo))
    api, max, PDX, 3
    html, max, PDX, 3
    >>> for bin in models.ErrorBin.objects.all():
    ...   print(str(bin))
    api, max, PDX, 3, 7, 1, 2016-06-01, 2016-06-01
    """
    actuals = models.ActualDayRecord.objects.filter(location=location)
    histo = get_histogram(source, location, type, day_in_advance)
    for act_record in actuals:
        date = act_record.date_meas
        try:
            forecast = models.DayRecord.objects.get(
                date_reference=date,
                source=source,
                day_in_advance=day_in_advance,
            )
        except models.DayRecord.DoesNotExist:
            print('No forecast matching actual record for {}'.format(date))
            continue
        if type == 'max':
            error = forecast.max_temp - act_record.max_temp
        else:
            error = forecast.min_temp - act_record.min_temp
        update_histogram(histo, error, date)
    return histo


def is_histogram_stale(source, location, type, day_in_advance):
    """Check whether data is waiting to be populated in histogram.

    The logic here is to label the histogram as stale if:
      -- it does not exist, or
      -- there is a forecast covering the day after the latest bin, and
      -- there is a measured point covering the day after the latest bin.

    >>> is_histogram_stale('api', 'PDX', 'max', 2)
    True
    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> histo.save()
    >>> models.ErrorBin(member_of_hist=histo, error=-1, quantity=10,
    ... start_date=datetime.datetime(2016, 6, 1, 0, 0),
    ... end_date=datetime.datetime(2016, 8, 1, 0, 0)).save()
    >>> is_histogram_stale('api', 'PDX', 'max', 2)
    False
    >>> models.ActualDayRecord(date_meas=datetime.date(2016, 8, 2),
    ... location="PDX", max_temp=76, min_temp=55).save()
    >>> is_histogram_stale('api', 'PDX', 'max', 2)
    False
    >>> models.DayRecord(date_reference=datetime.date(2016, 8, 2),
    ... day_in_advance=2, source='api', max_temp=83, min_temp=50).save()
    >>> is_histogram_stale('api', 'PDX', 'max', 2)
    True
    """
    try:
        histo = models.ErrorHistogram.objects.get(
            location=location,
            day_in_advance=day_in_advance,
            source=source,
            type=type
        )
    except models.ErrorHistogram.DoesNotExist:
        return True
    bins = histo.errorbin_set.all()
    latest_bin_date = bins.aggregate(Max('end_date'))['end_date__max']
    next_bin_date = latest_bin_date + datetime.timedelta(1)
    return ((len(models.DayRecord.objects.filter(
                date_reference=next_bin_date,
                day_in_advance=day_in_advance,
                source=source
            )) > 0) and
            (len(models.ActualDayRecord.objects.filter(
                date_meas=next_bin_date
            )) > 0))


def display_histogram(source, location, type, day_in_advance):
    """Histogram display.

    This is for troubleshooting and data study.  Since it displays on the
      server console it is unused by the web-site.

    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> histo.save()
    >>> models.ErrorBin(member_of_hist=histo, error=1, quantity=3,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> models.ErrorBin(member_of_hist=histo, error=2, quantity=10,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> models.ErrorBin(member_of_hist=histo, error=3, quantity=3,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> display_histogram('api', 'PDX', 'max', 2)
    ==== Histogram for 2 ====
    1: ***
    2: **********
    3: ***
    <BLANKLINE>
    Count: 16, Mean: 2.000, SD: 0.632
    <BLANKLINE>
    <BLANKLINE>
    """
    try:
        histo = models.ErrorHistogram.objects.get(
            location=location,
            day_in_advance=day_in_advance,
            source=source,
            type=type
        )
    except models.ErrorHistogram.DoesNotExist:
        print('Such histogram does not exist.')
        return
    error_to_qty = histo.errorbin_set.all()
    min_error = error_to_qty.aggregate(Min('error'))['error__min']
    max_error = error_to_qty.aggregate(Max('error'))['error__max']
    mean, sd = get_statistics_per_day(error_to_qty)
    print('==== Histogram for {} ===='.format(day_in_advance))
    count = 0
    for i in range(min_error, max_error+1):
        try:
            qty = error_to_qty.get(error=i).quantity
        except models.ErrorBin.DoesNotExist:
            qty = 0
        print('{}: {}'.format(i, '*'*qty))
        count += qty
    print('\nCount: {}, Mean: {:.3f}, SD: {:.3f}\n\n'.format(count, mean, sd))


def get_all_bins(source, location, type, day_in_advance):
    """Returns all bins for a particular histogram.

    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> histo.save()
    >>> models.ErrorBin(member_of_hist=histo, error=1, quantity=3,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> get_all_bins('api', 'PDX', 'max', 2)
    ...   # doctest: +NORMALIZE_WHITESPACE
    <QuerySet [ErrorBin(member_of_hist=ErrorHistogram(source='api', type='max',
    location='PDX', day_in_advance=2), error=1, quantity=3,
    start_date=datetime.date(2016, 6, 1), end_date=datetime.date(2016, 8, 1))]>
    """
    histo = get_histogram(source, location, type, day_in_advance)
    return histo.errorbin_set.all()


def get_statistics_per_day(bins):
    """Get the statistics from a collection of bins.

    >>> histo = models.ErrorHistogram(source='api', type='max', location='PDX',
    ... day_in_advance=2)
    >>> histo.save()
    >>> get_statistics_per_day([])
    (0, 0)
    >>> models.ErrorBin(member_of_hist=histo, error=1, quantity=3,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> models.ErrorBin(member_of_hist=histo, error=2, quantity=10,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> models.ErrorBin(member_of_hist=histo, error=3, quantity=3,
    ... start_date=datetime.date(2016, 6, 1),
    ... end_date=datetime.date(2016, 8, 1)).save()
    >>> bins = get_all_bins('api', 'PDX', 'max', 2)
    >>> get_statistics_per_day(bins)
    (2.0, 0.6324555320336759)
    """
    total = sum([bin.quantity for bin in bins])
    if total == 0:    # Avoids a div by zero error; stats are nulled out.
        return 0, 0
    mean = sum([bin.error * bin.quantity for bin in bins]) / total
    variance = sum([(bin.error - mean)**2 * bin.quantity for bin in bins])
    std = math.sqrt(variance / (total - 1))
    return mean, std


def get_statistics(source, location, type):
    """Main function to collect statistics for application to the forecast
         points on the web-site.
    """
    means = {}
    stds = {}
    for day in range(models.SOURCE_TO_LENGTH[source]):
        if is_histogram_stale(source, location, type, day):
            populate_histogram(source, location, type, day)
        bins = get_all_bins(source, location, type, day)
        means[day], stds[day] = get_statistics_per_day(bins)
    return means, stds


def get_json_of_forecast(forecast, means, stds, source, start_date):
    """Create the JSON object from the forecast and statistics data.

    >>> forecast = {0: 50, 1: 51, 2: 52, 3: 53, 4: 54}
    >>> means = {0: 1, 1: 0, 2: -1, 3: 0, 4: 1}
    >>> stds = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}
    >>> start_date = datetime.date(2016, 8, 1)
    >>> json = get_json_of_forecast(forecast, means, stds, 'api', start_date)
    >>> for item in json:
    ...   print(sorted(item.items()))
    ...   # doctest: +NORMALIZE_WHITESPACE
    [('date', '2016-08-01'), ('pct05', 47.04), ('pct25', 48.326), ('pct50', 49),
        ('pct75', 49.674), ('pct95', 50.96), ('source_raw', 50)]
    [('date', '2016-08-02'), ('pct05', 49.04), ('pct25', 50.326), ('pct50', 51),
        ('pct75', 51.674), ('pct95', 52.96), ('source_raw', 51)]
    [('date', '2016-08-03'), ('pct05', 51.04), ('pct25', 52.326), ('pct50', 53),
        ('pct75', 53.674), ('pct95', 54.96), ('source_raw', 52)]
    [('date', '2016-08-04'), ('pct05', 51.04), ('pct25', 52.326), ('pct50', 53),
        ('pct75', 53.674), ('pct95', 54.96), ('source_raw', 53)]
    [('date', '2016-08-05'), ('pct05', 51.04), ('pct25', 52.326), ('pct50', 53),
        ('pct75', 53.674), ('pct95', 54.96), ('source_raw', 54)]
    """
    json = []
    for ddate in range(models.SOURCE_TO_LENGTH[source]):
        if ddate in forecast:
            json.append({
                'date': str(start_date + datetime.timedelta(ddate))[:10],
                'source_raw': forecast[ddate],
                'pct05': forecast[ddate] - means[ddate] - 1.96 * stds[ddate],
                'pct25': forecast[ddate] - means[ddate] - 0.674 * stds[ddate],
                'pct50': forecast[ddate] - means[ddate],
                'pct75': forecast[ddate] - means[ddate] + 0.674 * stds[ddate],
                'pct95': forecast[ddate] - means[ddate] + 1.96 * stds[ddate]
            })
    return json


def return_json_of_forecast(source, type):
    """Function to return a JSON object containing the dates, forecast temp
         points and the statistical spread.
    """
    location = 'PDX'
    start_date = datetime.date.today()
    forecast = data_loader.get_forecast(source, type, start_date)
    means, stds = get_statistics(source, location, type)
    json = get_json_of_forecast(forecast, means, stds, source, start_date)
    return json


def main():
    display_histogram('api', 'PDX', 'max', 2)

if __name__ == '__main__()':
    main()
