"""Weather Maniac optical character recognition functions."""

from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import subprocess
import io
import re
import csv
from . import logic

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
    small_img.show()
    small_img.load()
    small_bw_img = ImageEnhance.Color(small_img).enhance(0)
    small_bw_img = small_bw_img.point(lambda i: 255 if i > 128 else 0)
    small_bw_img = small_bw_img.filter(ImageFilter.MinFilter(3))
    pad_img = ImageOps.expand(small_bw_img, border=20, fill='black')
    pad_img.show()
    return pad_img


def get_jpg_bytes(img):
    """Turn the image into a .jpeg item for piping."""
    output = io.BytesIO()
    img.save(output, format='JPEG')
    pad_jpg = output.getvalue()
    output.close()
    return pad_jpg


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


def day_string_to_day_in_advance(day_string, day_num, first_day_num, predict_dow):
    """Convert the day string to the day in advance.

    Updates (in place) the first day number and cleans (in place) day string.
    """
    if DAY_RE.search(day_string):
        day_string = DAY_RE.search(day_string).group(0)
    else:
        day_string = ''
    if day_string in WEEKDAY_TO_NUM:
        if day_num == 0:
            first_day_num = (WEEKDAY_TO_NUM[day_string] - predict_dow + 7) % 7
        day_in_adv = day_num + first_day_num
    else:
        day_in_adv = 10
    return day_in_adv


def process_image(img_file, csv_file):
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
    img = Image.open(img_file)
    img.show()
    print('Processing: {}'.format(img_file))
    predict_date = DATE_RE.search(img_file).group(0)
    predict_dow = logic.get_date(predict_date).weekday()
    row_list = [predict_date]
    first_day_num = 10  # Make sure the first day is read, or make data garbage.
    for day_num in range(2):
        box = day_crop_dim(day_num)
        pad_img = crop_enhance_item(img, box)
        pad_jpg = get_jpg_bytes(pad_img)
        day_string = call_tesseract(pad_jpg)
        day_string = clean_day_results(day_string)
        day_in_adv = day_string_to_day_in_advance(day_string, day_num,
                                                  first_day_num, predict_dow)
        row_list.append(day_in_adv)

        box = max_crop_dim(day_num)
        pad_img = crop_enhance_item(img, box)
        output = io.BytesIO()
        pad_img.save(output, format='JPEG')
        pad_jpg = output.getvalue()
        output.close()
        out_string = call_tesseract(pad_jpg)
        max_string = clean_temp_results(out_string)
        row_list.append(max_string)

        box = min_crop_dim(day_num)
        small_img = img.crop(box)
        small_img.show()
        small_img.load()
        small_bw_img = ImageOps.grayscale(small_img)
        small_bw_img = small_bw_img.point(lambda i: 255 if i > 128 else 0)
        pad_img = ImageOps.expand(small_bw_img, border=20, fill='black')
        small_bw_img.show()
        output = io.BytesIO()
        pad_img.save(output, format='JPEG')
        pad_jpg = output.getvalue()
        output.close()
        out_string = call_tesseract(pad_jpg)
        out_string= I_RE.sub('1', out_string)
        out_string= O_RE.sub('0', out_string)
        out_string= B_RE.sub('8', out_string)
        out_string = ''.join(re.findall('\d+', out_string))
        if TEMP_RE.search(out_string):
            min_string = TEMP_RE.search(out_string).group(0)
        else:
            min_string = ''
        row_list.append(min_string)
        print('Day: {}, Max: {}, Min: {}'.format(day_string, max_string, min_string))
    with open(csv_file, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(row_list)


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
    process_image('C:/Users/Eric/weather_maniac/rawdatafiles/Screen_Data/screen_2016_09_22.jpg',
               'C:/Users/Eric/weather_maniac/rawdatafiles/total.csv')


if __name__ == '__main__':
    main()

