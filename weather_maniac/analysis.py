"""Weather Maniac Analysis modules."""

from . import models
from django.db.models import Max, Min
import datetime


def display_error_vs_date(source, location, type, day_in_advance):
    """Test function to print error."""
    actuals = models.ActualDayRecord.objects.filter(location=location)
    for act_record in actuals:
        date = act_record.date_meas
        try:
            forecast = models.DayRecord.objects.get(
                date_reference=date,
                source=source,
                day_in_advance=day_in_advance,
            )
        except models.DayRecord.DoesNotExist:
            print('no matching record for {}'.format(date))
        else:
            if type == 'max':
                fcst = forecast.max_temp
                meas = act_record.max_temp
            else:
                fcst = forecast.min_temp
                meas = act_record.min_temp
            error = fcst - meas
            print('Date: {}, Meas: {}, Fcst: {}, Error: {}'.format(
                date, meas, fcst, error))
            _update_histogram(source, location, type, day_in_advance, error, date)


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


def _update_histogram(source, location, type, day_in_advance, error, date):
    """Update the forecast point, creating a new one if needed.
    
    Updating in this sense is to increment the count in an appropriate bin.
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
    try:
        bin = histo.errorbin_set.get(
            error=error
        )
    except models.ErrorBin.DoesNotExist:
        bin = create_bin(histo, error, quantity=0, start_date=date, end_date=date)
    # Need to add checking whether date is already covered....
    bin.quantity += 1
    bin.end_date = date
    bin.save()

    
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
        print('Such histogram does not exist.  Making it...')
        display_error_vs_date(source, location, type, day_in_advance)
        histo = models.ErrorHistogram.objects.get(
            location=location,
            day_in_advance=day_in_advance,
            source=source,
            type=type
        )
    error_to_qty = histo.errorbin_set.all()
    min_error = error_to_qty.aggregate(Min('error'))['error__min']
    max_error = error_to_qty.aggregate(Max('error'))['error__max']
    for i in range(min_error, max_error+1):
        try:
            qty = error_to_qty.get(error=i).quantity
        except models.ErrorBin.DoesNotExist:
            qty = 0
        print('{}: {}'.format(i, '*'*qty))


def return_json_of_forecast():
    """   """
    forecast = {0:83, 1:80, 2:84, 3:79, 4:82, 5:84, 6:85}
    means = {0:0, 1:0.2, 2:0.3, 3:0.4, 4:0.5, 5:0.5, 6:0.5}
    stds = {0:1, 1:1, 2:2, 3:2, 4:3, 5:3, 6:4}
    start_date = datetime.datetime.now()
    json = []
    for delta_date in range(7):
        json.append({
            'date': str(start_date + datetime.timedelta(delta_date))[:10],
            'pct05': forecast[delta_date] + means[delta_date] - 1.96 * stds[delta_date],
            'pct25': forecast[delta_date] + means[delta_date] - 0.674 * stds[delta_date],
            'pct50': forecast[delta_date] + means[delta_date],
            'pct75': forecast[delta_date] + means[delta_date] + 0.674 * stds[delta_date],
            'pct95': forecast[delta_date] + means[delta_date] + 1.96 * stds[delta_date]
        })
    return json


def main():
    display_histogram('html', 'PDX', 'max', 2)

if __name__ == '__main__':
    main()