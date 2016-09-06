#!/usr/bin/env python

import csv
import itertools
from os import listdir, rename
from os.path import getsize, isfile, join

from readJson import get_min_max_from_json
from readHtml import get_min_max_from_html

root_path = 'C:/Users/Eric/Desktop/Weatherman/'
container_path = root_path + 'Reduced_Data/'
api_data_path = root_path + 'API_Data/'
api_arch_path = root_path + 'API_Arch/'
html_data_path = root_path + 'HTML_Data/'
html_arch_path = root_path + 'HTML_Arch/'


def push_json_data_to_csv(entry, min_max_str, date):
    file_name = container_path + 'JSON_' + min_max_str + '.csv'
    with open(file_name, 'a') as out:
        csv_out = csv.writer(out, lineterminator='\n')
        entry_list = list(entry.values())
        entry_list[:0] = [date]
        csv_out.writerow(entry_list)


def push_html_data_to_csv(entry, min_max_str, date):
    file_name = container_path + 'HTML_' + min_max_str + '.csv'
    with open(file_name, 'a') as out:
        csv_out = csv.writer(out, lineterminator='\n')
        entry[:0] = [date]
        csv_out.writerow(entry)


def move_file_to_archive(f, data_path, arch_path):
    rename(data_path + f, arch_path + f)


def process_api_files():
    onlyfiles = [f for f in listdir(api_data_path) if isfile(join(api_data_path, f))]
    for f in onlyfiles:
        f_string = f[:10]
        print('processing API {}'.format(f_string))
        if getsize(api_data_path + f) > 10000:
            min_entry, max_entry = get_min_max_from_json(api_data_path + f)
            push_json_data_to_csv(max_entry, 'max', f_string)
            push_json_data_to_csv(min_entry, 'min', f_string)
        move_file_to_archive(f, api_data_path, api_arch_path)


def process_html_files():
    onlyfiles = [f for f in listdir(html_data_path) if isfile(join(html_data_path, f))]
    for f in onlyfiles:
        f_string = f[5:15]
        print('processing HTML {}'.format(f_string))
        if getsize(html_data_path + f) > 100000:
            min_entry, max_entry = get_min_max_from_html(html_data_path + f)
            push_html_data_to_csv(max_entry, 'max', f_string)
            push_html_data_to_csv(min_entry, 'min', f_string)
        move_file_to_archive(f, html_data_path, html_arch_path)


def main():
    process_html_files()
    process_api_files()


if __name__ == '__main__':
    main()
