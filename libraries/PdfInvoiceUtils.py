import re

import cv2
from DOP.RPA.Ocr import DopRpaOcr as Ocr
from pdf2image import convert_from_path
from robot.libraries.BuiltIn import BuiltIn


def find_invoice_series(raw_text):
    # invoice_series = re.search(r"(?:.*)([0-9A-Z\/]{6})(?:.*Invoice No.*)", raw_text)
    invoice_series = re.search(r"(?:.*)([A-Z]{2}/[A-Z0-9]*)(?:.*)", raw_text)
    if not invoice_series:
        raise ValueError("Not found Invoice Series")

    invoice_series = invoice_series.group(1)
    BuiltIn().log_to_console('\nInvoice Series: ' + invoice_series)

    return invoice_series


def find_invoice_template(raw_text):
    # invoice_template = re.search(r"(?:Form No.*)([A-Z0-9\/]{11})(?:.*)", raw_text)
    invoice_template = re.search(r"(?:.*)([0-9A-Z]{7}/[A-Z0-9]*)(?:.*)", raw_text)
    if not invoice_template:
        raise ValueError("Not found Invoice Template")

    invoice_template = invoice_template.group(1)
    BuiltIn().log_to_console('\nInvoice Template: ' + invoice_template)

    return invoice_template


def find_invoice_number(raw_text):
    # invoice_number = re.search(r"(?:Invoice No.*)([0-9]{7})(?:.*)", raw_text)
    invoice_number = re.search(r"(?:[A-Za-z_'])([0-9]{7})(?:_.*)", '_' + raw_text + '_')
    if not invoice_number:
        raise ValueError("Not found Invoice Number")

    invoice_number = invoice_number.group(1)
    BuiltIn().log_to_console('\nInvoice Number: ' + invoice_number)

    return invoice_number


def extract_invoice_data(pdf_file):
    dop_ocr = Ocr()

    # PDF to PNG file
    converted_images = convert_pdf_to_image(pdf_file)
    converted_image = converted_images[0]

    # Crop png file
    # array slices in startY:endY, startX:endX order
    converted_image_data = cv2.imread(converted_image, cv2.IMREAD_GRAYSCALE)
    height, width = converted_image_data.shape
    cropped_image = converted_image_data[0:int(height * 0.18), 0:width]
    cv2.imwrite(converted_image, cropped_image)

    raw_text = dop_ocr.get_text_from_image(
        img_path=converted_image,
        lang='Vietnamese')

    raw_text = raw_text['plainText']

    # remove all white \t spaces, new lines \n and tabs \t
    raw_text = re.sub('\s+', '_', raw_text)

    BuiltIn().log('\nOCR result: ' + raw_text + '\n')

    invoice_series = find_invoice_series(raw_text)
    invoice_number = find_invoice_number(raw_text)
    invoice_template = find_invoice_template(raw_text)
    seller_tax_code = find_seller_tax_code(raw_text)

    return {
        'seller_tax_code': seller_tax_code,
        'invoice_template': invoice_template,
        'invoice_number': invoice_number,
        'invoice_series': invoice_series
    }


def find_seller_tax_code(raw_text):
    # seller_tax_code = re.search(r"(?:Tax Code.*)([0-9]{10})(?:.*Address.*)", raw_text)
    seller_tax_code = re.search(r"(?:.*:.*)([0-9]{10})(?:.*)", raw_text)
    if not seller_tax_code:
        raise ValueError("Not found Seller Tax Code")

    seller_tax_code = seller_tax_code.group(1)
    BuiltIn().log_to_console('\nInvoice Seller TaxCode: ' + seller_tax_code)

    return seller_tax_code


def convert_pdf_to_image(pdf_file):
    converted_images = []
    images = convert_from_path(pdf_path=pdf_file, poppler_path=r"poppler-21.10.0\Library\bin")
    for index, image in enumerate(images):
        converted_image_file = f'{pdf_file}-{index}.png'
        image.save(converted_image_file)
        converted_images.append(converted_image_file)

    return converted_images

# def main():
#     raw_text = r'Mẫu số (Form No.):\t01GTKT0/001\r\nKý hiệu (Serial No.): MP/20E\r\nSố (Invoice No.):\t0000401'
#     print(find_invoice_series(raw_text))

# if __name__ == "__main__":
#     main()
