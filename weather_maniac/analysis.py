"""Weather Maniac Analysis modules."""

from . import models


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


def create_bin(hist_id, error, quantity, start_date, end_date):
    """Create Error Histogram."""
    return models.ErrorHistogram(
        member_of_hist=hist_id,
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
        bin = create_bin(histo.id, error, quantity=0, start_date=date, end_date=date)
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
        print('Such histogram does not exist.')
    else:
        for bin in histo.errorbin_set.all():
            print('error: {}, count: {}'.format(bin.error, bin.quantity))
