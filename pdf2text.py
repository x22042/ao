import re
import os
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

def normalize_text(text):

    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[０-９]', lambda m: chr(ord(m.group(0)) - 0xFEE0), text)
    text = text.replace('。', '。\n')
    text = text.replace('.', '.\n')

    return text

def convert_pdf_to_text(pdf_path, output_dir,custmized_name):

    laparams = LAParams()

    resource_manager = PDFResourceManager()
    text_output = StringIO()
    device = TextConverter(resource_manager, text_output, laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, device)

    with open(pdf_path, 'rb') as input_file:
        for page in PDFPage.get_pages(input_file):
            interpreter.process_page(page)


    extracted_text = text_output.getvalue()
    normalized_text = normalize_text(extracted_text)

    txt_filename = f"{custmized_name}.txt"
    txt_filepath = os.path.join(output_dir, txt_filename)

    with open(txt_filepath, 'w', encoding='utf-8') as output_file:
        output_file.write(normalized_text)

    device.close()
    text_output.close()

    return txt_filepath
