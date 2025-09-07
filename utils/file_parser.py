# utils/file_parser.py

import pytesseract
from PyPDF2 import PdfReader
import pandas as pd
from PIL import Image
import io

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'pdf':
        text = ''
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text += page.extract_text() or ''

        # If no text found, inform user that OCR on PDFs isn't supported
        if not text.strip():
            return "This PDF contains scanned images or non-selectable text. Please convert it to an image (PNG/JPG) and upload that instead."
        return text

    elif file_type == 'txt':
        return uploaded_file.getvalue().decode("utf-8")

    elif file_type == 'csv':
        df = pd.read_csv(uploaded_file)
        return df.to_string(index=False)

    elif file_type == 'xlsx':
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(axis=1, how='all')
        return df.to_string(index=False)

    elif file_type in ['png', 'jpg', 'jpeg']:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text if text.strip() else "No text found in the image."

    else:
        return "Unsupported file type. Please upload a PDF, TXT, CSV, XLSX, PNG, or JPG."
