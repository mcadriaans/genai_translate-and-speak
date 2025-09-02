# utils/file_parser.py

import tempfile
import pytesseract
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pandas as pd
from PIL import Image
import io

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'pdf':
        text = ''
        pdf_bytes = uploaded_file.read() # Read the uploaded file as bytes
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text += page.extract_text() or ''

        if not text.strip():
            images = convert_from_bytes(pdf_bytes)
            for image in images:
                text += pytesseract.image_to_string(image)
        return text

    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df.to_string(index=False)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(axis=1, how='all') # Drop empty columns
        return df.to_string(index=False)

    elif file_type in ['png', 'jpg', 'jpeg']:
        print("Performing OCR on image file.")
        image = Image.open(uploaded_file)
        return pytesseract.image_to_string(image)

    else:
        return "Unsupported file type."