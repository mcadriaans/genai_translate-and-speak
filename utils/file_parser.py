# utils/file_parser.py

import easyocr
from PyPDF2 import PdfReader
import pandas as pd
from PIL import Image
import io
from pdf2image import convert_from_bytes
import numpy as np

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'pdf':
        text = ''
        pdf_bytes = uploaded_file.read()
        reader_pdf = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader_pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if text.strip():
            return text

        # OCR fallback for image-based PDFs
        images = convert_from_bytes(pdf_bytes)
        for img in images:
            img_rgb = img.convert("RGB")  # Ensure RGB format
            img_np = np.array(img_rgb)
            if img_np.size == 0:
                continue
            result = reader.readtext(img_np)
            text += ' '.join([item[1] for item in result]) + '\n'
        return text if text.strip() else "No readable text found in the PDF."

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
        image = Image.open(uploaded_file).convert("RGB")  # Ensure RGB format
        image_np = np.array(image)
        if image_np.size == 0:
            return "Uploaded image appears to be empty or corrupted."
        result = reader.readtext(image_np)
        text = ' '.join([item[1] for item in result])
        return text if text.strip() else "No text found in the image."

    else:
        return "Unsupported file type. Please upload a PDF, TXT, CSV, XLSX, PNG, or JPG."



       
