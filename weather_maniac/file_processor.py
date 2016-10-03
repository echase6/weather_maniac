#!/usr/bin/env python

import csv
import datetime
import json
import os
import re
from os import listdir, rename
from os.path import getsize, isfile, join

from bs4 import BeautifulSoup

from . import logic
from . import logic_ocr
from . import models
from . import settings

ROOT_PATH = os.path.join(settings.BASE_DIR, 'rawdatafiles')
CONTAINER_PATH = os.path.join(ROOT_PATH, 'Reduced_Data')
API_DATA_PATH = os.path.join(ROOT_PATH, 'API_Data')
API_ARCH_PATH = os.path.join(ROOT_PATH, 'API_Arch')
HTML_DATA_PATH = os.path.join(ROOT_PATH, 'HTML_Data')
HTML_ARCH_PATH = os.path.join(ROOT_PATH, 'HTML_Arch')
ACTUAL_DATA_PATH = os.path.join(ROOT_PATH, 'ACT_Data')
ACTUAL_ARCH_PATH = os.path.join(ROOT_PATH, 'ACT_Arch')
SCREEN_DATA_PATH = os.path.join(ROOT_PATH, 'Screen_Data')
SCREEN_ARCH_PATH = os.path.join(ROOT_PATH, 'Screen_Arch')

DATA_RE = re.compile('20\d{2}_\d{2}_\d{2}')


def _get_html_soup(file_name):
    """HTML file loader."""
    with open(file_name) as html_file:
        html_string = html_file.read()
    return BeautifulSoup(html_string, 'html.parser')


def get_forecasts_from_html(html_soup):
    """HTML file content loader."""
    return html_soup.find_all('div', class_='weather-box daily-forecast')


def process_html_file(file_name):
    """Main function to extract max and min temperatures from one HTML file
        and save the contents to a DayRecord.

    The prediction date comes from when the file was read, and is encoded in
       the filename.  The html file contains a forecast time; this is ignored.
    The date the forecast applies to is normalized to PDT, and max/min temps
       are found for the time from midnight to midnight.
    """
    predict_date = logic.get_date(DATA_RE.search(file_name).group(0))
    html_soup = _get_html_soup(file_name)
    daily_forecasts = get_forecasts_from_html(html_soup)
    days_to_max_min = logic.get_retimed_fcsts_from_html(daily_forecasts,
                                                        predict_date)
    logic.process_days_to_max_min(days_to_max_min, predict_date, 'html')


def _get_json(file_name):
    """JSON file content loader. """
    with open(file_name) as data_file:
        json_data = json.load(data_file)
    return json_data


def process_json_file(file_name):
    """Main function to extract max and min temperatures from one API(json) file
        and save the contents to a DayRecord.

    The file contains temperature predictions every hour (not max/min) so the
       process is to find the max and min for a given day.
    The prediction date comes from when the file was read, and is encoded in
       the filename.  The json file does not contain prediction time.
    The date the forecast applies to is normalized to PDT, and max/min temps
       are found for the time from midnight to midnight.
    """
    predict_date = logic.get_date(DATA_RE.search(file_name).group(0))
    json_data = _get_json(file_name)
    days_to_max_min = logic.get_retimed_fcsts_from_json(json_data, predict_date)
    logic.process_days_to_max_min(days_to_max_min, predict_date, 'api')


# def process_jpeg_file(file_name):
    """Main function to extract max and min temperatures from one API(json) file
        and save the contents to a DayRecord.

    The file contains temperature predictions every hour (not max/min) so the
       process is to find the max and min for a given day.
    The prediction date comes from when the file was read, and is encoded in
       the filename.  The json file does not contain prediction time.
    The date the forecast applies to is normalized to PDT, and max/min temps
       are found for the time from midnight to midnight.
    """
    # predict_date = logic.get_date(DATA_RE.search(file_name).group(0))
    # json_data = _get_json(file_name)
    # days_to_max_min = logic.get_retimed_fcsts_from_json(json_data,
    # predict_date)
    # logic.process_days_to_max_min(days_to_max_min, predict_date, 'api')


def _process_csv_row(row, max_temp_index, min_temp_index):
    """Convert the csv rows into saved model records."""
    date = datetime.datetime.strptime(row[2], '%Y%m%d').date()
    location = models.LOCATIONS[row[1]]
    max_temp = int(row[max_temp_index])
    min_temp = int(row[min_temp_index])
    try:
        act_temp_model = logic.get_actual(date, location, max_temp, min_temp)
    except ValueError as error:
        print(error)
    else:
        act_temp_model.save()


def process_actual_csv_file(filename):
    """Main function to extract actual temperatures from the .csv file and
       save the contents in an ActualDayRecord.
    TMAX/TMIN column parameterized in case the .csv file changes format.
    """
    with open(filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header_row = next(csv_reader)
        max_temp_index = header_row.index('TMAX')
        min_temp_index = header_row.index('TMIN')
        for row in csv_reader:
            print(row)
            if row[1] == 'PORTLAND INTERNATIONAL AIRPORT OR US':
                _process_csv_row(row, max_temp_index, min_temp_index)


def _process_jpeg_csv_row(row):
    """Convert the csv rows into saved model records.

    """
    days_to_max_min = {}
    for index in range(1, 20, 3):  # TODO: make this aware of short rows
        if all([item != '' for item in row[index:index+3]]):
            day_in_advance = int(row[index])
            max_temp = int(row[index + 1])
            min_temp = int(row[index + 2])
            days_to_max_min[day_in_advance] = (max_temp, min_temp)
    return days_to_max_min


def process_jpeg_csv_file(filename):
    """Main function to extract forecast records from the .csv file and
       save the contents in an DayRecord.
    """
    source = 'jpeg'
    with open(filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csv_reader:
            print(row)
            predict_date = datetime.datetime.strptime(row[0], '%Y_%m_%d').date()
            days_to_max_min = _process_jpeg_csv_row(row)
            logic.process_days_to_max_min(days_to_max_min, predict_date, source)


def move_file_to_archive(f, data_path, arch_path):
    """Move the processed file to the archive, by renaming it."""
    rename(os.path.join(data_path, f), os.path.join(arch_path, f))


def process_api_files():
    """Process the files loaded thought the API (JSON files).

    Comparison with 100B done to strip off partial files (normal: 15kB)
    """
    only_files = [f for f in listdir(API_DATA_PATH)
                  if isfile(os.path.join(API_DATA_PATH, f))]
    for f in only_files:
        date_string = DATA_RE.search(f).group(0)
        print('processing API {}'.format(date_string))
        if getsize(os.path.join(API_DATA_PATH, f)) > 100:
            process_json_file(API_DATA_PATH + f)
            move_file_to_archive(f, API_DATA_PATH, API_ARCH_PATH)


def process_html_files():
    """Process the files loaded thought the web site (i.e., HTML).

    Comparison with 10KB done to strip off partial files
      (original: 115kB, archived: 15kB)
    """
    only_files = [f for f in listdir(HTML_DATA_PATH)
                  if isfile(os.path.join(HTML_DATA_PATH, f))]
    for f in only_files:
        date_string = DATA_RE.search(f).group(0)
        print('processing HTML {}'.format(date_string))
        if getsize(os.path.join(HTML_DATA_PATH, f)) > 10000:
            process_html_file(HTML_DATA_PATH + f)
            move_file_to_archive(f, HTML_DATA_PATH, HTML_ARCH_PATH)


def process_jpeg_files():
    """Process the files loaded thought the web site (i.e., JPEG)."""
    only_files = [f for f in listdir(SCREEN_DATA_PATH)
                  if isfile(os.path.join(SCREEN_DATA_PATH, f))]
    for f in only_files:
        if f == 'thumbs.db':
            continue
        date_string = DATA_RE.search(f).group(0)
        print('processing JPEG {}'.format(date_string))
        file_name = os.path.join(SCREEN_DATA_PATH, f)
        if getsize(file_name) > 10000:
            row_list = logic_ocr.process_image(file_name, date_string)
            csv_file = os.path.join(ROOT_PATH, 'total.csv')
            with open(csv_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                csv_writer.writerow(row_list)
            # process_jpeg_file(HTML_DATA_PATH + f)
            # move_file_to_archive(f, SCREEN_DATA_PATH, SCREEN_ARCH_PATH)


def process_actual_files():
    """Process the files loaded thought the web site as JPG."""
    only_files = [f for f in listdir(ACTUAL_DATA_PATH)
                  if isfile(join(ACTUAL_DATA_PATH, f))]
    for f in only_files:
        f_string = f
        print('processing Actuals {}'.format(f_string))
        if getsize(ACTUAL_DATA_PATH + f) > 10:
            process_actual_csv_file(ACTUAL_DATA_PATH + f)
            move_file_to_archive(f, ACTUAL_DATA_PATH, ACTUAL_ARCH_PATH)


def main():
    process_html_files()
    process_api_files()
    process_actual_files()
    process_jpeg_files()

if __name__ == '__main__':
    main()
