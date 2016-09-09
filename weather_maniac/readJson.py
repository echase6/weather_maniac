#!/usr/bin/env python

import json
from datetime import datetime
from itertools import groupby
from .utilities import calc_days_in_adv


def temp_f(temp_k):
    return round(9 * (temp_k - 273.15) / 5 + 32)


def get_min_max_from_json(file_name):
    with open(file_name) as data_file:
        data1 = json.load(data_file)
    date_temp = []
    date_format = '%Y_%m_%d'
    predict_date = datetime.strptime(file_name[-19:-9], date_format)
    for row in data1['list']:
        forecast_utc = row['dt']
        days_in_advance = calc_days_in_adv(predict_date, forecast_utc)
        temp = temp_f(row['main']['temp'])
        date_temp.append([days_in_advance, temp])
    highest_list = {0: None}
    lowest_list = {0: None}
    highest_list.update({k: max([v[1] for v in g])
                        for k, g in groupby(date_temp, lambda x: x[0])})
    lowest_list.update({k: min([v[1] for v in g])
                       for k, g in groupby(date_temp, lambda x: x[0])})
    return lowest_list, highest_list


def main():
    file_repo = 'C:/users/Eric/Desktop/WeatherMan/'
    file_name = file_repo + 'API_Arch/2016_06_16_23_00_16'
    lowest_list, highest_list = get_min_max_from_json(file_name)
    for i in range(len(highest_list)):
        print('{}:  min: {}, max: {}'
              .format(i, lowest_list[i], highest_list[i]))


if __name__ == '__main__':
    main()
