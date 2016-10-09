"""Weather Maniac optical character recognition functions."""

import io
import os
import re
import subprocess

from PIL import Image, ImageOps, ImageFilter

from . import logic
from . import models

TESSERACT_EXE_NAME = r"c:/users/eric/desktop/weatherman/tesseract.exe"

WEEKDAY_TO_NUM = {
    'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6
    }

TEMP_RE = re.compile('-?\d{1,3}')
DAY_RE = re.compile('\w{3}')
O_RE = re.compile('O')
I_RE = re.compile('I')
B_RE = re.compile('B')
FHI_RE = re.compile('FHI')
FFI_RE = re.compile('FFI')
DATE_RE = re.compile('20\d{2}_\d{2}_\d{2}')


def get_crop_dim(day_num, source_str, image_str):
    """Return the crop window.

    >>> get_crop_dim(1, 'jpeg', 'max')
    (144, 282, 225, 320)
    """
    source_item = models.SOURCES[source_str]
    x_index = (source_item['dims']['x_pitch'] * day_num +
               source_item['dims']['x_start'])
    dims = source_item['dims'][image_str]
    x_min = round(x_index + dims['off_x'] - dims['win_x'] / 2)
    x_max = round(x_index + dims['off_x'] + dims['win_x'] / 2)
    y_min = round(dims['loc_y'] - dims['win_y'] / 2)
    y_max = round(dims['loc_y'] + dims['win_y'] / 2)
    return x_min, y_min, x_max, y_max


def crop_enhance_item(img, box, image_item):
    """Crop out and enhance an item."""
    small_img = img.crop(box)
    small_img.load()
    small_bw_img = ImageOps.grayscale(small_img)
    if not image_item['dark_back']:
        small_bw_img = ImageOps.invert(small_bw_img)
    small_bw_img = small_bw_img.point(lambda i: 255 if i > 128 else 0)
    if image_item['proc'] == 'grow':
        size = (image_item['win_x'] * 2, image_item['win_y'] * 2)
        small_bw_img = small_bw_img.resize(size, Image.ANTIALIAS)
    if image_item['proc'] == 'squish':
        small_bw_img = small_bw_img.filter(ImageFilter.MinFilter(5))
        # size = (round(image_item['win_x'] / 1.0), round(image_item['win_y'] / 1.5))
        # small_bw_img = small_bw_img.resize(size, Image.ANTIALIAS)
        # small_bw_img = small_bw_img.filter(ImageFilter.MinFilter(3))
        # small_bw_img = small_bw_img.filter(ImageFilter.Kernel(
        #     (3, 3), [0, -0.5, 0, -0.5, 2, -0.5, 0, -0.5, 0]
        # )
        # )

    if image_item['proc'] == 'fat' or image_item['proc'] == 'grow':
        small_bw_img = small_bw_img.filter(ImageFilter.MinFilter(3))
    pad_img = ImageOps.expand(small_bw_img, border=20, fill='black')
    pad_img.show()
    return pad_img


def get_virtual_jpeg(img):
    """Turn the image into a .jpeg item for piping."""
    output = io.BytesIO()
    img.save(output, format='JPEG')
    virtual_jpeg = output.getvalue()
    output.close()
    return virtual_jpeg


def clean_day_results(out_string):
    """Qualify the day results as much as possible.

    >>> clean_day_results('FFIa')
    'FRI'
    >>> clean_day_results('11FRI..')
    'FRI'
    >>> clean_day_results('suN')
    'SUN'
    >>> clean_day_results('won')
    'WON'
    """
    out_string = out_string.upper()
    out_string = ''.join(re.findall('[A-Z]+', out_string))
    out_string = FHI_RE.sub('FRI', out_string)
    out_string = FFI_RE.sub('FRI', out_string)
    return out_string[:3]


def clean_temp_results(temp_string):
    """Qualify the temperature results.

    >>> clean_temp_results('76')
    '76'
    >>> clean_temp_results('7I')
    '71'
    >>> clean_temp_results('7O')
    '70'
    >>> clean_temp_results('B7')
    '87'
    >>> clean_temp_results('TUE')
    ''
    """
    temp_string = I_RE.sub('1', temp_string)
    temp_string = O_RE.sub('0', temp_string)
    temp_string = B_RE.sub('8', temp_string)
    temp_string = ''.join(re.findall('\d+', temp_string))
    if TEMP_RE.search(temp_string):
        out_string = TEMP_RE.search(temp_string).group(0)
    else:
        out_string = ''
    return out_string


def get_day_of_week_offset(day_string, day_num, predict_dow, dow_offset):
    """Find the forecast offset for the days in advance.

    >>> get_day_of_week_offset('TUE', 1, 0, 3)
    0
    >>> get_day_of_week_offset('RAN', 1, 0, 3)
    3
    >>> get_day_of_week_offset('TUE', 1, 3, 3)
    Traceback (most recent call last):
    ...
    ValueError: Forecast offset error: 3

    <<The above test is not working for unknown reasons.>>
    """
    if DAY_RE.search(day_string):
        day_string = DAY_RE.search(day_string).group(0)
        if day_string in WEEKDAY_TO_NUM:
            dow_offset = (WEEKDAY_TO_NUM[day_string]-day_num-predict_dow) % 7
        if dow_offset > 1:
            raise ValueError('Forecast offset error: {}'.format(dow_offset))
    return dow_offset


def process_item(img, day_num, source_str, image_str):
    """Process the day, max or min temp item."""
    image_item = models.SOURCES[source_str]['dims'][image_str]
    box = get_crop_dim(day_num, source_str, image_str)
    pad_img = crop_enhance_item(img, box, image_item)
    pad_jpeg = get_virtual_jpeg(pad_img)
    tess_string = call_tesseract(pad_jpeg)
    return tess_string


def conv_row_list_to_dict(row_list, dow_offset):
    """Turn list of max, min into dict with day-in-adv as the keys.

    >>> conv_row_list_to_dict([('78', '53'), ('79', '54')], 1)
    {1: (78, 53), 2: (79, 54)}
    >>> conv_row_list_to_dict([('78', ''), ('79', '54')], 1)
    {2: (79, 54)}
    """
    days_to_max_min = {}
    if dow_offset < 7:
        for day_num, max_min in enumerate(row_list):
            if max_min[0] != '' and max_min[1] != '':
                index = day_num + dow_offset
                days_to_max_min[index] = tuple(map(int, max_min))
    return days_to_max_min


def process_image(jpeg_image, source_str, predict_date):
    """Main function to process a 7-day forecast image.

    The process is:
    -- Get the prediction day of week from the filename.
    -- Loop through 7 days:
       -- Process the day window
       -- Figure out what the day-of-week offset is for the prediction day
       -- Process the max temp and min temps, making a list of tuples
    -- Store the resulting list.
       """
    img = Image.open(io.BytesIO(jpeg_image))
    predict_dow = logic.get_date(predict_date).weekday()
    row_list = []
    dow_offset = 10  # Make sure the first day is read, or make data garbage.
    for day_num in range(models.SOURCES[source_str]['length']):
        tess_string = process_item(img, day_num, source_str, 'day')
        day_string = clean_day_results(tess_string)
        try:
            dow_offset = get_day_of_week_offset(day_string, day_num,
                                                predict_dow, dow_offset)
        except ValueError:
            pass
        tess_string = process_item(img, day_num, source_str, 'max')
        max_temp = clean_temp_results(tess_string)
        tess_string = process_item(img, day_num, source_str, 'min')
        min_temp = clean_temp_results(tess_string)
        row_list.append((max_temp, min_temp))
        print('Day: {}, Max: {}, Min: {}'.format(day_string, max_temp,
                                                 min_temp))
    return row_list, dow_offset


def call_tesseract(input_image):
    """Calls external tesseract.exe on input file (restrictions on types),
    outputting output_filename+'txt'"""
    args = [TESSERACT_EXE_NAME, 'stdin', 'stdout']
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    data, error = proc.communicate(input=input_image)
    return data.decode('utf-8')


def main():
    source_str = 'jpeg4'
    file_name = os.path.join(models.SOURCES[source_str]['data_path'],
                             'screen_jpeg4_2016_10_07_16_53.jpg')
    print(file_name)
    with open(file_name, 'rb') as f:
        jpeg_contents = f.read()
    predict_date = DATE_RE.search(file_name).group(0) + '_0_0'
    row_list, predict_dow = process_image(jpeg_contents, source_str, predict_date)
    print('predict dow: {}, temps: {}.'.format(predict_dow, row_list))


if __name__ == '__main__':
    main()
