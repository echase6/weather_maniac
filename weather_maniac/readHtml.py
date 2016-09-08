#!/usr/bin/env python

from datetime import datetime
from itertools import chain, groupby
from bs4 import BeautifulSoup
from utilities import calc_days_in_adv



def get_min_max_from_html(file_name):
    date_format = '%Y_%m_%d'
    predict_date = datetime.strptime(file_name[-24:-14], date_format)
    with open(file_name) as html_file:
        html_string = html_file.read()
    html_soup = BeautifulSoup(html_string, 'html.parser')
    highest_list = []
    lowest_list = []
    daily_forecasts = html_soup.find_all('div',
                                         class_='weather-box daily-forecast')
    for forecast in daily_forecasts:
        forecast_utc = int(forecast.span['data-time'])
        days_in_advance = calc_days_in_adv(predict_date, forecast_utc//1000)
        if days_in_advance >= 0:
            highest_list += [forecast.find('td', class_='high').get_text()]
            lowest_list += [forecast.find('td', class_='low').get_text()]
    return lowest_list, highest_list


def main():
    file_repo = 'C:/users/Eric/Desktop/WeatherMan/'
    file_name = file_repo + 'HTML_Arch/html_2016_07_23_12_51_32.html'
    get_min_max_from_html(file_name)
    lowest_list, highest_list = get_min_max_from_html(file_name)
    for i in range(len(highest_list)):
        print('min: {}, max: {}'.format(lowest_list[i], highest_list[i]))


if __name__ == '__main__':
    main()
