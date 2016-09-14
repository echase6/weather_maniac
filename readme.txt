Overview:

The Weather Maniac application has two moving parts:
[1] Data gather/archive/Django loader
[2] Web site presentation of data

========================
Data Loading
========================
Data gather:
  getData.py: get_data()
    This process is run asynchronously, currently by Windows task scheduler.
    It reads files from three sources and stores them w/o any processing.
      The three sources are an API(json), HTML, and Screen(jpg)
    File location is C:\Users\Eric\Desktop\Weatherman, in sub-directories.
    This server data is mirrored to my laptop periodically (not automatic)

Data archive:
  file_processor.py: process_XXXX_files()
    This is run as requested by me (i.e., not automatic)
    These processes
      -- look in the Weatherman sub-dirs for all files
      -- call a processor (in logic.py) on each one
      -- move the file to an archive

Data Django loader:
  logic.py: process_XXXX_file()
    This is run as requested by me (i.e., not automatic)
    These processes
      -- extract the data (json or html)
      -- re-time the dates, decoding which day each forecast point points to
      -- calls record update/creation process

Note:  Actual (measured) data currently comes from an off-line load of a .csv
  file from NOAA.  This will be automated later.

  =====================
  Web site presentation
  =====================

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
