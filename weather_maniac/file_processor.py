#!/usr/bin/env python

# import csv
from os import listdir, rename
from os.path import getsize, isfile, join
# import datetime
# from . import models
from . import logic

root_path = 'C:/Users/Eric/Desktop/Weatherman/'
container_path = root_path + 'Reduced_Data/'
api_data_path = root_path + 'API_Data/'
api_arch_path = root_path + 'API_Arch/'
html_data_path = root_path + 'HTML_Data/'
html_arch_path = root_path + 'HTML_Arch/'
#
#
# def push_json_data_to_csv(entry, min_max_str, date):
#     file_name = container_path + 'JSON_' + min_max_str + '.csv'
#     with open(file_name, 'a') as out:
#         csv_out = csv.writer(out, lineterminator='\n')
#         entry_list = list(entry.values())
#         entry_list[:0] = [date]
#         csv_out.writerow(entry_list)
#
#
# def push_html_data_to_csv(entry, min_max_str, date):
#     file_name = container_path + 'HTML_' + min_max_str + '.csv'
#     with open(file_name, 'a') as out:
#         csv_out = csv.writer(out, lineterminator='\n')
#         entry[:0] = [date]
#         csv_out.writerow(entry)


def move_file_to_archive(f, data_path, arch_path):
    rename(data_path + f, arch_path + f)


def process_api_files():
    onlyfiles = [f for f in listdir(api_data_path) if isfile(join(api_data_path, f))]
    for f in onlyfiles:
        date_string = f[:10]
        print('processing API {}'.format(date_string))
        if getsize(api_data_path + f) < 10000:
            return
        logic.process_json_file(api_data_path + f)
        move_file_to_archive(f, api_data_path, api_arch_path)


def process_html_files():
    onlyfiles = [f for f in listdir(html_data_path) if isfile(join(html_data_path, f))]
    for f in onlyfiles:
        f_string = f[5:15]
        print('processing HTML {}'.format(f_string))
        if getsize(html_data_path + f) < 100000:
            return
        logic.process_html_file(html_data_path + f)
        move_file_to_archive(f, html_data_path, html_arch_path)
#
#
# def _create_day_record(date):
#     """  """
#     new_record = models.DayRecord(date_reference=date)
#     for source in models.SOURCES:
#         new_source_record = models.SourceDayRecord(day=new_record, source=source)
#         new_source_record.save()
#     new_record.save()
#     return new_record
#
#
# def _date_range(start_date, end_date):
#     for n in range(int ((end_date - start_date).days)):
#         yield start_date + datetime.timedelta(n)
#
#
# def load_day_record():
#     """Load the day records."""
#     start_day = datetime.datetime(2016, 6, 16, 0, 0)
#     end_day = datetime.datetime(2016, 6, 26, 0, 0)
#     day_records = models.DayRecord.objects.filter(date_reference__range=(start_day, end_day))
#     for single_date in _date_range(start_day, end_day):
#         day_record = day_records.get(date_reference__iexact=single_date)
#         if not day_record:
#             day_record = _create_day_record(single_date)
#         for source in models.SOURCES:
#             models.SourceDayRecord.objects.get(date=single_date, source=source)


def main():
    process_html_files()
    process_api_files()
    # load_day_record()

if __name__ == '__main__':
    main()