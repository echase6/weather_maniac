# Proposal:  Weather Maniac
====


## Product Overview
----
Visitors to the **Weather Maniac** website will see temperature forecasts that
include a confidence range based on historical accuracy of the forecasting
service.  Such forecasts will take the form of two numbers which (for maximum
daily temperature) the highest high-temperature and a lowest high-temperature,
both for a given confidence level.

The information will be available through various means, such as:
* A graph of n-day in-advance predictions, from 7 to 1 (from 7-day forecasts.)
  * Temperature forecast
  * Minimum daily temperature
  * Maximum daily temperature
* A selector to pick from (up to) three temperature forecasting services.
  * If more than one is selected, the results come from the average of them.
* An entry field for confidence factor.


## Specific Functionality
----
* Download and store forecast data from 3 sites in a temporary container, using
  a process that is called periodically (at least daily), autonomously.
* Scrape the relevant min/max temperature forecasts from the above:
  * Use pattern recognition on sites that only up-load images.
  * Use API to get data from 'friendly' sites.
  * Extract data from sites that embed it in HTML.
* Store the min/max temperatures in a convenient database (SQL?), using a
  process that is called periodically, autonomously.
* On the Web-Site, down-load the data in accordance with the user's wishes.
* Create temperature range with 90% (or some other) confidence using either:
  * Gaussian modelling of the error, reducing it to mean and sigma.
  * Raw calculation of points were 90% of the distribution lies.

### Pages:
1. Landing Page
   Contains brief description of what the site is all about.
   Shows today's min/max temperature based on 90% confidence.
   Guides users to the Details Page and the Data Visualization Page.

2. Details Page
   Shows a 7-day temperature forecast with 90% confidence (based on pre-defined
   criteria) in the form of a table.
   Has selectors for the user to create their own 7-day forecast using:
   * Entered confidence level, from 50% to 99%
   * Select data sources, of three.  More than one will merge the data.
   * Select date range to include in the analysis, or all available data.
   After making selections, a new 7-day forecast is displayed.

3. Data Visualization Page (may get merged with 2. Details Page)
   Provides display (plot) of temperature error versus day-in-advance (7 - 1).
   Has a selector for the user to enter data source, of three.  
    More than one will merge the data using averages.
   Has a selector for the dates to consider.
   Plot will have five curves, each normalized to actual temperature:
   * Most error in positive direction, i.e., highest above eventual actual
   * 90% confidence error to maximum.
   * Average of all predictions
   * 90% confidence error to minimum.
   * Most error in the negative direction.


## Data Model
----
The data for each forecasting site (and for min + max) takes the form of a
multi-dimensional array:
  - each row represents the 7-day forecast made on that particular day.
  - each column represents the 7-days of the forecast, which is 7 - 1 days in
    advance of the actual.
Additionally, there is data on actual temperatures.  This may not need to be
stored in the database, however, but can be down-loaded at-will.
Searching will mostly be based on data-range and by forecasting site.
Searching will also be necessary for min/max temperatures, and n-days in-advance.


## Technical Components
----
Necessary Modules:
* Data harvesting modules, for each of the forecasting sites.
  * These are Python modules running on a server at regular intervals.
* Data interpretation and storing modules, necessary to derive data and enter
  into the database.
  * For the one site that is purely bit-mapped, use openCV for OCR.
  * For the API, and HTML sites, standard library tools for gathering the data.
  * Data will be entered into the database through a Django interface.
* Data visualization will come from a Javascript plotting Tool.  Candidates are:
  * D3.js
  * also: Google Charts, ChartJS, Chartlist.js
* Time allowing, implement remote-hosting service (such as AWS) for handling
  of both the data gathering/storage as well as web-hosting.


## Schedule
----
* Data harvesting modules -- needed first since the data is perishable --
  this is done but needs clean-up.
* Data interpretation modules, particularly bit-mapped character recognition --
  OCR will be hard and may be deferred.
* Data reduction modules, searching for min/max with confidence level
* Presentation functions -> graphs and 7-day forecast.
* Design of web-pages, layout, etc.



## Further Work
----
* Implement remote-hosting.
* Create ability to conveniently attach to other sites.
* Add data visualization methods to explore correlations.
* Subscription (and push to subscriber) 7-day forecasts in text msg, or e-mail.
