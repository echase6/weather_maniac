"""Weather Maniac Analysis modules."""

from . import models
from . import utilities
from . import getData
from . import file_processor
from django.db.models import Max, Min
import datetime
import math

SOURCE_TO_LENGTH = {'html': 7, 'api': 5}


def create_histogram(source, location, type, day_in_advance):
    """Create Error Histogram."""
    return models.ErrorHistogram(
        source=source,
        location=location,
        type=type,
        day_in_advance=day_in_advance
    )


def create_bin(histo, error, quantity, start_date, end_date):
    """Create Error Histogram."""
    return models.ErrorBin(
        member_of_hist=histo,
        error=error,
        quantity=quantity,
        start_date=start_date,
        end_date=end_date
    )


def get_histogram(source, location, type, day_in_advance):
    """Get the histogram.  Make one if not done yet."""
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
    """Get the error bin.  Make one if not done yet."""
    try:
        bin = histo.errorbin_set.get(
            error=error
        )
    except models.ErrorBin.DoesNotExist:
        bin = create_bin(histo, error, quantity=1,
                         start_date=date, end_date=date)
        bin.save()
    return bin


def update_histogram(histo, error, date):
    """Update the forecast point, creating a new one if needed.

    Updating in this sense is:
      increment the count in an appropriate bin by 1
      change the end date to the record date (to avoid double-counting)
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
    """Check whether data is waiting to be populated in histogram."""
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
            )) == 0) or
           (len(models.ActualDayRecord.objects.filter(
                date_meas=next_bin_date
            )) == 0))


def display_histogram(source, location, type, day_in_advance):
    """Histogram display."""
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


def load_forecast_record(source, today):
    """Ensure that the forecast record is current."""
    try:
        models.DayRecord.objects.get(
            source=source,
            date_reference=today,
            day_in_advance=0
        )
    except models.DayRecord.DoesNotExist:
        getData.get_data()
        file_processor.process_html_files()
        file_processor.process_api_files()


def get_forecast(source, type):
    """Get the current temperature forecast."""
    today = utilities.round_down_day(datetime.datetime.now())
    load_forecast_record(source, today)
    records = []
    for day in range(SOURCE_TO_LENGTH[source]):
        records += [models.DayRecord.objects.get(
            source=source,
            day_in_advance=day,
            date_reference=today + datetime.timedelta(day)
        )]
    if type == 'max':
        days_to_temp ={record.day_in_advance: record.max_temp
                       for record in records}
    else:
        days_to_temp ={record.day_in_advance: record.min_temp
                       for record in records}
    return days_to_temp


def get_all_bins(source, location, type, day_in_advance):
    """Returns all bins for a particular histogram."""
    histo = get_histogram(source, location, type, day_in_advance)
    return histo.errorbin_set.all()


def get_statistics_per_day(bins):
    """Get the statistics from a collection of bins."""
    total = sum([bin.quantity for bin in bins])
    if total == 0:    # Avoids a div by zero error; stats are nulled out.
        return 0, 0
    mean = sum([bin.error * bin.quantity for bin in bins]) / total
    variance = sum([(bin.error - mean)**2 * bin.quantity for bin in bins])
    std = math.sqrt(variance / (total - 1))
    return mean, std


def get_statistics(source, location, type):
    """  """
    means = {}
    stds = {}
    for day in range(SOURCE_TO_LENGTH[source]):
        if is_histogram_stale(source, location, type, day):
            populate_histogram(source, location, type, day)
        bins = get_all_bins(source, location, type, day)
        means[day], stds[day] = get_statistics_per_day(bins)
    return means, stds


def return_json_of_forecast(source, type):
    """   """
    location = 'PDX'
    forecast = get_forecast(source, type)
    means, stds = get_statistics(source, location, type)
    start_date = utilities.round_down_day(datetime.datetime.now())
    json = []
    for ddate in range(SOURCE_TO_LENGTH[source]):
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


def main():
    display_histogram('api', 'PDX', 'max', 2)

if __name__ == '__main__':
    main()
