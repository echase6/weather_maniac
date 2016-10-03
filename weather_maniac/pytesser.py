"""OCR in Python using the Tesseract engine from Google
http://code.google.com/p/pytesser/
by Michael J.T. O'Kelly
V 0.0.1, 3/10/07"""

import subprocess
import os
# import Image

TESSERACT_EXE_NAME = r"c:/users/eric/desktop/weatherman/tesseract.exe"  # Name of executable to be called at command line
SCRATCH_IMAGE_NAME = "temp.bmp"  # This file must be .bmp or other Tesseract-compatible format
SCRATCH_TEXT_NAME_ROOT = "temp"  # Leave out the .txt extension
CLEANUP_SCRATCH_FLAG = True  # Temporary files cleaned up after OCR operation

"""Test for exceptions raised in the tesseract.exe logfile"""


class TesserGeneralException(Exception):
    pass


def check_for_errors(logfile='tesseract.log'):
    with open(logfile) as inf:
        inf_text = inf.read()
    # All error conditions result in "Error" somewhere in logfile
    if inf_text.find("Error") != -1:
        raise TesserGeneralException(inf_text)


"""Utility functions for processing images for delivery to Tesseract"""


def image_to_scratch(im, scratch_image_name):
    """Saves image in memory to scratch file.  .bmp format will be read
    correctly by Tesseract
    """
    im.save(scratch_image_name, dpi=(200, 200))


def retrieve_text(scratch_text_name_root):
    with open(scratch_text_name_root + 'txt') as inf:
        inf_text = inf.read()
    return inf_text


def perform_cleanup(scratch_image_name, scratch_text_name_root):
    """Clean up temporary files from disk"""
    for name in (scratch_image_name,
                 scratch_text_name_root + '.txt', "tesseract.log"):
        try:
            os.remove(name)
        except OSError:
            pass


def call_tesseract(input_image, output_filename):
    """Calls external tesseract.exe on input file (restrictions on types),
    outputting output_filename+'txt'"""
    with open('max_0.jpg', 'rb') as f:
        input_image=f.read()
    args = [TESSERACT_EXE_NAME, 'stdin', 'stdout']
    print(args)
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    data, error = proc.communicate(input=input_image)
    return data.decode('utf-8').strip()


def image_to_string(img, cleanup=CLEANUP_SCRATCH_FLAG):
    """Converts im to file, applies tesseract, and fetches resulting text.
    If cleanup=True, delete scratch files after operation."""
    try:
        image_to_scratch(img, SCRATCH_IMAGE_NAME)
        call_tesseract(SCRATCH_IMAGE_NAME, SCRATCH_TEXT_NAME_ROOT)
        img_text = retrieve_text(SCRATCH_TEXT_NAME_ROOT)
    finally:
        if cleanup:
            perform_cleanup(SCRATCH_IMAGE_NAME, SCRATCH_TEXT_NAME_ROOT)
    return img_text


def image_file_to_string(filename, cleanup=CLEANUP_SCRATCH_FLAG,
                         graceful_errors=True):
    """Applies tesseract to filename; or,

    If image is incompatible and graceful_errors=True:
      converts to compatible format and then applies tesseract.

    Fetches resulting text.

    If cleanup=True, delete scratch files after operation.
    """
    try:
        try:
            call_tesseract(filename, SCRATCH_TEXT_NAME_ROOT)
            img_text = retrieve_text(SCRATCH_TEXT_NAME_ROOT)
        except TesserGeneralException:
            if graceful_errors:
                # img = Image.open(filename)
                # img_text = image_to_string(img, cleanup)
                pass
            else:
                raise
    finally:
        if cleanup:
            perform_cleanup(SCRATCH_IMAGE_NAME, SCRATCH_TEXT_NAME_ROOT)
    return img_text


if __name__ == '__main__':
    pass
    # im = Image.open('phototest.tif')
    # text = image_to_string(im)
    # print(text)
    # try:
    #     text = image_file_to_string('fnord.tif', graceful_errors=False)
    # except TesserGeneralException(error):
    #     print('fnord.tif is incompatible filetype.  Try graceful_errors=True')
    #     print(value)
    # text = image_file_to_string('fnord.tif', graceful_errors=True)
    # print('fnord.tif contents: {}'.format(text))
    # text = image_file_to_string('fonts_test.png', graceful_errors=True)
    # print(text)
