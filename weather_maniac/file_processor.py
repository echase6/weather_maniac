#!/usr/bin/env python

from os import listdir, rename
from os.path import getsize, isfile, join
from . import logic

root_path = 'C:/Users/Eric/Desktop/Weatherman/'
container_path = root_path + 'Reduced_Data/'
api_data_path = root_path + 'API_Data/'
api_arch_path = root_path + 'API_Arch/'
html_data_path = root_path + 'HTML_Data/'
html_arch_path = root_path + 'HTML_Arch/'
actual_data_path = root_path + 'ACT_Data/'
actual_arch_path = root_path + 'ACT_Arch/'


def move_file_to_archive(f, data_path, arch_path):
    rename(data_path + f, arch_path + f)


def process_api_files():
    onlyfiles = [f for f in listdir(api_data_path) if isfile(join(api_data_path, f))]
    for f in onlyfiles:
        date_string = f[:10]
        print('processing API {}'.format(date_string))
        if getsize(api_data_path + f) > 10000:
            logic.process_json_file(api_data_path + f)
            move_file_to_archive(f, api_data_path, api_arch_path)


def process_html_files():
    onlyfiles = [f for f in listdir(html_data_path) if isfile(join(html_data_path, f))]
    for f in onlyfiles:
        f_string = f[5:15]
        print('processing HTML {}'.format(f_string))
        if getsize(html_data_path + f) > 100000:
            logic.process_html_file(html_data_path + f)
            move_file_to_archive(f, html_data_path, html_arch_path)


def process_actual_files():
    onlyfiles = [f for f in listdir(actual_data_path) if isfile(join(actual_data_path, f))]
    for f in onlyfiles:
        f_string = f
        print('processing Actuals {}'.format(f_string))
        if getsize(actual_data_path + f) > 10:
            logic.process_actual_file(actual_data_path + f)
            move_file_to_archive(f, actual_data_path, actual_arch_path)


def main():
    process_html_files()
    process_api_files()
    process_actual_files()

if __name__ == '__main__':
    main()
