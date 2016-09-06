#!/usr/bin/env python

import urllib
from time import strftime
from urllib2 import Request, URLError, urlopen
from .key.py import app_id_str, src1_str, src2_str

request = Request('http://api.openweathermap.org/data/2.5/forecast/city' +
                  app_id_str)

try:
    response = urlopen(request)
    report = response.read()
except URLError:
    print('No kittez. Got an error code')

file_date = strftime('%Y_%m_%d_%H_%M_%S')
fileRepo = 'C:/Users/Eric/Desktop/WeatherMan/'

with open((fileRepo + 'Data/' + file_date), 'w') as file:
    file.write(report[:])

fileName = fileRepo + 'ScreenData/screen' + file_date + '.jpg'
urllib.urlretrieve(src1_str, fileName)

fileName = fileRepo + 'HTML_Data/html_' + file_date + '.html'
urllib.urlretrieve(src2_str, fileName)
