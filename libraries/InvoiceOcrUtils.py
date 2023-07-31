import os
import pathlib
import re
import requests
import cv2
import numpy as np
from DOP.RPA.Ocr import DopRpaOcr as Ocr
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
import json

dop_ocr = Ocr()

def read_image(file_path):
    return cv2.imread(file_path)

def gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    cv2.threshold(image, 0, 255, 3, image)
    return image

def gaussian(image):
    gaussian_image = cv2.GaussianBlur(image, (1, 1), 1)
    return gaussian_image

def adjust_gamma(image, gamma=0.8):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                        for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def pre_process_invoice(invoice_img_path):
    original_image = read_image(invoice_img_path)
    gray_image = gray(original_image)
    adjust_gamma_image = adjust_gamma(gray_image)
    thresholding_image = thresholding(adjust_gamma_image)
    sharpen_image = gaussian(thresholding_image)
    return sharpen_image

@keyword
def get_lookup_code(invoice_img_path):
    BuiltIn().log_to_console("\nPre-processed image at:" + invoice_img_path)
    processed_img = pre_process_invoice(invoice_img_path)
    processed_image_path = invoice_img_path + \
                            '_processed' + pathlib.Path(invoice_img_path).suffix

    # Remove exist file
    if os.path.exists(processed_image_path):
        os.remove(processed_image_path)

    # Save processed image for debug and improve
    BuiltIn().log_to_console("\nSave pre-processed image to:" + processed_image_path)

    height, width = processed_img.shape

    # array slices in startY:endY, startX:endX order
    cropped_image = processed_img[int(
        height * 0.95):height, int(width * 0.7):width]

    cv2.imwrite(processed_image_path, cropped_image)

    raw_text = dop_ocr.get_text_from_image(
        img_path=processed_image_path,
        lang='English')

    # Get lookup code use Regex
    raw_text = raw_text['plainText']

    BuiltIn().log('\nOCR result: ' + raw_text + '\n')

    search_result = re.search(r"(?::.*)([0-9A-Z]{11})(?:.*)", raw_text)

    if not search_result:
        return None

    lookup_code = search_result.group(1)

    if not is_lookup_code_valid(lookup_code=lookup_code):
        return None

    BuiltIn().log('\nOCR Found LookupCode: ' + lookup_code + '\n')

    return lookup_code

@keyword
def is_lookup_code_valid(lookup_code):
    if lookup_code and (len(lookup_code) == 11):
        logger.info("#Lookup Code: " + lookup_code + " is valid")
        return True
    else:
        return False
@keyword
def get_access_token(userName, password):
    url = "https://cccd-ocr.dominatech.xyz/api/token/"
    headers = {}
    payload={
    'username': userName,
    'password': password
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

@keyword
def get_lookup_code_ai(invoice_img_path, token):
    url = "https://cccd-ocr.dominatech.xyz/api/ocr_invoice/"
    payload = {}
    file_name = os.path.basename(invoice_img_path)
    files=[
        ('image',(file_name,open(invoice_img_path,'rb'),'image/jpeg'))
    ]
    headers = {
        'Authorization': "Bearer " + token
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.text

@keyword
def check_none_string(string):
    if not string:
        return False
    if string == None:
        return False
    if string == "":
        return False
    else:
        return True
    


