"""Weather Maniac optical character recognition functions."""

from PIL import Image, ImageOps, ImageFilter
import subprocess
import io
import re
import csv
import os
from . import logic
from . import data_loader
from . import models
from . import file_processor

TESSERACT_EXE_NAME = r"c:/users/eric/desktop/weatherman/tesseract.exe"

WEEKDAY_TO_NUM = {
    'MON': 0,
    'TUE': 1,
    'WED': 2,
    'THU': 3,
    'FRI': 4,
    'SAT': 5,
    'SUN': 6
}


JPG_FEATURES = {
    'x_pitch': 86.5,
    'x_start': 98,
    'max_loc_y': 301,
    'min_loc_y': 334,
    'day_loc_y': 127,
    'max_win_x': 81,
    'max_win_y': 37,
    'min_win_x': 54,
    'min_win_y': 28,
    'day_win_x': 73,
    'day_win_y': 18
}

TEMP_RE = re.compile('-?\d{1,3}')
DAY_RE = re.compile('\w{3}')
O_RE = re.compile('O')
I_RE = re.compile('I')
B_RE = re.compile('B')
FHI_RE = re.compile('FHI')
FFI_RE = re.compile('FFI')
DATE_RE = re.compile('20\d{2}_\d{2}_\d{2}')


def max_crop_dim(day_num):
    """Return the max temp crop window.

    day_num holds the day (column) number, 0-referenced.
    """
    x_index = JPG_FEATURES['x_pitch'] * day_num + JPG_FEATURES['x_start']
    x_min = round(x_index - JPG_FEATURES['max_win_x'] / 2)
    y_min = round(JPG_FEATURES['max_loc_y'] - JPG_FEATURES['max_win_y'] / 2)
    x_max = round(x_index + JPG_FEATURES['max_win_x'] / 2)
    y_max = round(JPG_FEATURES['max_loc_y'] + JPG_FEATURES['max_win_y'] / 2)
    if day_num == 2:  # Kluge to eliminate a screen artifact at this point
        x_min += 1
    return x_min, y_min, x_max, y_max


def min_crop_dim(day_num):
    """Return the max temp crop window.

    day_num holds the day (column) number, 0-referenced.
    """
    x_index = JPG_FEATURES['x_pitch'] * day_num + JPG_FEATURES['x_start']
    x_min = round(x_index - JPG_FEATURES['min_win_x'] / 2)
    y_min = round(JPG_FEATURES['min_loc_y'] - JPG_FEATURES['min_win_y'] / 2)
    x_max = round(x_index + JPG_FEATURES['min_win_x'] / 2)
    y_max = round(JPG_FEATURES['min_loc_y'] + JPG_FEATURES['min_win_y'] / 2)
    return x_min, y_min, x_max, y_max


def day_crop_dim(day_num):
    """Return the max temp crop window.

    day_num holds the day (column) number, 0-referenced.
    """
    x_index = JPG_FEATURES['x_pitch'] * day_num + JPG_FEATURES['x_start']
    x_min = round(x_index - JPG_FEATURES['day_win_x'] / 2)
    y_min = round(JPG_FEATURES['day_loc_y'] - JPG_FEATURES['day_win_y'] / 2)
    x_max = round(x_index + JPG_FEATURES['day_win_x'] / 2)
    y_max = round(JPG_FEATURES['day_loc_y'] + JPG_FEATURES['day_win_y'] / 2)
    return x_min, y_min, x_max, y_max


def crop_enhance_item(img, box):
    """Crop out and enhance an item."""
    small_img = img.crop(box)
    small_img.load()
    small_bw_img = ImageOps.grayscale(small_img)
    small_bw_img = small_bw_img.point(lambda i: 255 if i > 128 else 0)
    # small_bw_img = small_bw_img.filter(ImageFilter.MinFilter(3))
    pad_img = ImageOps.expand(small_bw_img, border=20, fill='black')
    return pad_img


def get_virtual_jpeg(img):
    """Turn the image into a .jpeg item for piping."""
    output = io.BytesIO()
    img.save(output, format='JPEG')
    virtual_jpeg = output.getvalue()
    output.close()
    return virtual_jpeg


def clean_day_results(out_string):
    """Qualify the day results as much as possible."""
    out_string = out_string.upper()
    out_string = ''.join(re.findall('[A-Z]+', out_string))
    out_string = FHI_RE.sub('FRI', out_string)
    out_string = FFI_RE.sub('FRI', out_string)
    return out_string


def clean_temp_results(temp_string):
    """Qualify the temperature results."""
    temp_string = I_RE.sub('1', temp_string)
    temp_string = O_RE.sub('0', temp_string)
    temp_string = B_RE.sub('8', temp_string)
    temp_string = ''.join(re.findall('\d+', temp_string))
    if TEMP_RE.search(temp_string):
        out_string = TEMP_RE.search(temp_string).group(0)
    else:
        out_string = ''
    return out_string


def day_string_to_day_in_advance(day_string, day_num, first_day_num,
                                 predict_dow):
    """Convert the day string to the day in advance.

    Updates (in place) the first day number and cleans (in place) day string.
    """
    if DAY_RE.search(day_string):
        day_string = DAY_RE.search(day_string).group(0)
    else:
        day_string = ''
    if day_string in WEEKDAY_TO_NUM:
        if day_num == 0:
            first_day_num = (WEEKDAY_TO_NUM[day_string] - predict_dow) % 7
        day_in_adv = day_num + first_day_num
    else:
        day_in_adv = 10
    return day_in_adv


def get_day_of_week_offset(day_string, day_num, predict_dow, dow_offset):
    """  """
    if DAY_RE.search(day_string):
        day_string = DAY_RE.search(day_string).group(0)
        dow_offset = (WEEKDAY_TO_NUM[day_string] - day_num - predict_dow) % 7
    return dow_offset


def process_item(img, box):
    """Process the day, max or min temp item."""
    pad_img = crop_enhance_item(img, box)
    pad_jpeg = get_virtual_jpeg(pad_img)
    tess_string = call_tesseract(pad_jpeg)
    return tess_string


def process_image(jpeg_image, predict_date):
    """Main function to process a 7-day forecast image.

    The process is:
    -- Get the prediction date from the filename.
    -- Loop through 7 days:
       -- Crop out day portion for that particular day
       -- Make BW, add margin to image, and erode the edges.
       -- Call Tesseract on the image
       -- Process the string output from Tesseract
       -- Repeat the above steps for Max temp, and for Min temp
    """
    # virtual_jpeg = get_virtual_jpeg(jpeg_image)
    img = Image.open(io.BytesIO(jpeg_image))
    # img = Image.open(virtual_jpeg)
    # img.show()
    # print('Processing: {}'.format(jpeg_image))
    # predict_date = DATE_RE.search(jpeg_image).group(0)
    predict_dow = logic.get_date(predict_date).weekday()
    row_list = []
    dow_offset = 10  # Make sure the first day is read, or make data garbage.
    for day_num in range(models.SOURCE_TO_LENGTH['jpeg']):
        box = day_crop_dim(day_num)
        tess_string = process_item(img, box)
        day_string = clean_day_results(tess_string)
        dow_offset = get_day_of_week_offset(day_string, day_num,
                                            predict_dow, dow_offset)
        # day_in_adv = day_string_to_day_in_advance(day_string, day_num,
        #                                           first_day_num, predict_dow)

        box = max_crop_dim(day_num)
        tess_string = process_item(img, box)
        max_temp = clean_temp_results(tess_string)

        box = min_crop_dim(day_num)
        tess_string = process_item(img, box)
        min_temp = clean_temp_results(tess_string)

        row_list.append((max_temp, min_temp))
        print('Day: {}, Max: {}, Min: {}'.format(day_string, max_temp,
                                                 min_temp))
    days_to_max_min = {}
    if dow_offset == 10:
        return {}
    for day_num in range(models.SOURCE_TO_LENGTH['jpeg']):
        if row_list[day_num][0] != '' and row_list[day_num][1] != '':
            days_to_max_min[(day_num + dow_offset) % 7] = (int(row_list[day_num][0]), int(row_list[day_num][1]))
    return days_to_max_min


def call_tesseract(input_image):
    """Calls external tesseract.exe on input file (restrictions on types),
    outputting output_filename+'txt'"""
    # with open('max_0.jpg', 'rb') as f:
    #     input_image=f.read()
    args = [TESSERACT_EXE_NAME, 'stdin', 'stdout']
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    data, error = proc.communicate(input=input_image)
    return data.decode('utf-8')


def main():
    file_name = os.path.join(file_processor.jpeg_data_path,
                             'screen_2016_09_22.jpg')
    jpeg_image = data_loader.get_data(file_name)
    predict_date = DATE_RE.search(file_name).group(0)
    row_list = process_image(jpeg_image, predict_date)
    csv_file = os.path.join(file_processor.root_path, 'total.csv')
    with open(csv_file, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(row_list)


if __name__ == '__main__':
    main()
