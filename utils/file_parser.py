# utils/file_parser.py

import easyocr
from PyPDF2 import PdfReader
import pandas as pd
from PIL import Image
import io
from pdf2image import convert_from_bytes
import numpy as np
import streamlit as st # <-- Import streamlit here for caching
import os # <-- Make sure this is imported

# --- Define the path to your local EasyOCR models ---
# Get the directory where this script (file_parser.py) is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the path to your 'ml_models/easyocr' folder relative to the project root
# SCRIPT_DIR is 'translate-and-speak/utils'
# '..' goes up one level to 'translate-and-speak'
# 'ml_models', 'easyocr' goes into the desired subfolders
EASYOCR_MODEL_DIR = os.path.join(SCRIPT_DIR, '..', 'ml_models', 'easyocr')

# Ensure the directory exists (optional, but good practice if you create it dynamically)
# This line primarily ensures that the path is correctly formed for EasyOCR to use.
os.makedirs(EASYOCR_MODEL_DIR, exist_ok=True)
# --- End of model path definition ---

@st.cache_resource
def get_easyocr_reader():
    st.info("Initializing EasyOCR reader. Loading models from local storage (this happens only once per deployment).")
    try:
        # Pass the custom model storage directory and crucial: disable automatic downloads
        reader_instance = easyocr.Reader(
            ['en'],
            gpu=False,
            model_storage_directory=EASYOCR_MODEL_DIR,
            download_enabled=False # <-- THIS IS CRUCIAL TO PREVENT REDOWNLOADS
        )
        st.success("EasyOCR reader initialized!")
        return reader_instance
    except Exception as e:
        st.error(f"Failed to initialize EasyOCR reader from local storage: {e}. Ensure models are in '{EASYOCR_MODEL_DIR}'.")
        st.stop() # Stop the app if a critical component fails to initialize
        return None

# Get the reader instance by calling the cached function
# This line will now call get_easyocr_reader() which handles the caching and local loading.
reader = get_easyocr_reader()

def extract_text_from_file(uploaded_file):
    # Ensure the reader was successfully initialized
    if reader is None:
        st.error("OCR functionality is not available due to initialization failure.")
        return "Error: OCR engine not loaded."

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
        try:
            st.info("Performing OCR on image-based PDF pages (this can be memory intensive for large files).")
            # Adjust dpi for performance/memory tradeoff. Lower dpi means smaller images, less memory, faster OCR.
            images = convert_from_bytes(pdf_bytes, dpi=150) # Example: Use 150 DPI
            for img_index, img in enumerate(images):
                img_rgb = img.convert("RGB")
                img_np = np.array(img_rgb)
                if img_np.size == 0:
                    st.warning(f"Skipping empty image for PDF page {img_index+1}.")
                    continue
                result = reader.readtext(img_np)
                text += ' '.join([item[1] for item in result]) + '\n'
            return text if text.strip() else "No readable text found in the PDF via OCR."
        except Exception as e:
            st.error(f"Error during PDF to image conversion or OCR fallback: {e}. This might happen with very large or complex PDFs exceeding memory limits. Try a smaller PDF or lower DPI.")
            return f"Error processing PDF for OCR: {e}"

    elif file_type == 'txt':
        uploaded_file.seek(0)
        return uploaded_file.getvalue().decode("utf-8")

    elif file_type == 'csv':
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        return df.to_string(index=False)

    elif file_type == 'xlsx':
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(axis=1, how='all')
        return df.to_string(index=False)

    elif file_type in ['png', 'jpg', 'jpeg']:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file).convert("RGB")
        image_np = np.array(image)
        if image_np.size == 0:
            return "Uploaded image appears to be empty or corrupted."
        result = reader.readtext(image_np)
        text = ' '.join([item[1] for item in result])
        return text if text.strip() else "No text found in the image."

    else:
        return "Unsupported file type. Please upload a PDF, TXT, CSV, XLSX, PNG, or JPG."