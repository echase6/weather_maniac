# Weather Maniac
====


## Overview
----
Visitors to the **Weather Maniac** website will see temperature forecasts that
include a confidence range based on historical accuracy of the forecasting
service.  Such forecasts will take the form of bands of temperatures which (for
maximum daily temperature) indicate the highest high-temperature and a lowest 
high-temperature, both for a given confidence level.

The information will be available through various means, such as:
* A graph of 7-day in-advance predictions which includes
  * Temperature forecast
  * Daily temperature (max or min) range with 90% confidence
  * Daily temperature (max or min) range with 50% confidence
  * Daily temperature (max or min) as forecasted
* A selector to pick from (up to) three temperature forecasting services.
  * If more than one is selected, the results come from the average of them.


## Operation
----

The Weather Maniac application has two moving parts:
* Data load, archive and insertion into database
* Web site presentation of reduced data

### Operation:  Data Loading
Data loading is done from the data_loader.py block by running its main() 
  function.  This has been included in Django's commands so that it will
  run with this command:
  
'$ python manage.py runloader'
  
The *runloader* function needs to be run periodically (once per day) to 
  populate the database with information necessary to gather statistics.
  
When run, it will gather data from four sites which are specified in the
  key.py file.  One of the sites returns a .jpg file which is currently not in
  use, and one of the sites holds yesterday's max/min temperatures.
  
The gathered data is archived and then inserted into the SQLite database.  The 
  archive locations are configured in the path variables up top.

Since *runloader* updates the database immediately, the archive files are not 
  necessary, but are insurance in case the database needs to be rebuilt.


### Operation:  Viewing Web Site


  Relevant files:
    urls.py
    views.py
    analysis.py:
      The two big parts are the ErrorHistogram and the Forecast
      Website-requested data is back-calculated from:
        -- statistics (mean, stdev) calculated from the histogram
        -- the 5- or 7- day forecast
    app.js, app.css:
      These prepare and instantiate the graph (on prediction.html)


Operation:
  -- Run:  python manage.py runserver
  -- Landing page is at 127.0.0.1:8000
  -- Follow link to 7-Day Forecast
