# utils/file_parser.py

import easyocr                                  # to perform OCR on images and image-based PDFs
from PyPDF2 import PdfReader                    # to read PDF files
import pandas as pd                             # to handle CSV and Excel files
from PIL import Image                           # to handle image files
import io                                       # to handle in-memory file operations
from pdf2image import convert_from_bytes        # to convert PDF pages to images
import numpy as np                              # for image array manipulations
import streamlit as st                          # for caching
import os                                       # to handle paths

# ------Set-up a reliable local directory for storing EasyOCR model files-----------------
# Finds the full path to the folder where your current script lives.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Builds a path that goes one level up from the script directory (..), then into ml_models/easyocr.
EASYOCR_MODEL_DIR = os.path.join(SCRIPT_DIR, '..', 'ml_models', 'easyocr') 

#  Create the EasyOCR model directory if it doesn't already exist, including any necessary parent folders
os.makedirs(EASYOCR_MODEL_DIR, exist_ok=True)
#-------------------------

@st.cache_resource  # Caching the reader instance avoids reloading the OCR models every time the app reruns — which saves time and system resources.
def get_easyocr_reader():
    st.info("Initializing EasyOCR reader. Loading models from local storage (this happens only once per deployment).")
    try:
        reader_instance = easyocr.Reader(  
            ['en'],
            gpu=False,                  # Ensures your app runs reliably on any machine — local or cloud
            model_storage_directory=EASYOCR_MODEL_DIR,
            download_enabled=False      # Prevents EasyOCR from trying to download models, making app more deployment friendly
        )
        st.success("EasyOCR reader initialized!")
        return reader_instance
    except Exception as e:
        st.error(f"Failed to initialize EasyOCR reader from local storage: {e}. Ensure models are in '{EASYOCR_MODEL_DIR}'.")
        st.stop() # Stop the app if a critical component fails to initialize
        return None

# Get the reader instance by calling the cached function
reader = get_easyocr_reader()

def extract_text_from_file(uploaded_file):
    # Ensure the reader was successfully initialized
    if reader is None:
        st.error("OCR functionality is not available due to initialization failure.")
        return "Error: OCR engine not loaded."

    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'pdf':
        text = ''
        pdf_bytes = uploaded_file.read()                # Read the entire PDF file into memory
        reader_pdf = PdfReader(io.BytesIO(pdf_bytes))   # Use BytesIO to handle the in-memory bytes
        for page in reader_pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if text.strip():
            return text

        # OCR fallback for image-based PDFs
        try:
            st.info("Performing OCR on image-based PDF pages (this can be memory intensive for large files).") # Signal to user that OCR is being attempted
            images = convert_from_bytes(pdf_bytes, dpi=150) # Convert PDF pages to images at 150 DPI (balance between speed and quality)
            for img_index, img in enumerate(images):  # Loops through each image (page) in the PDF
                img_rgb = img.convert("RGB")   # Ensure image(page) is in RGB mode for EasyOCR
                img_np = np.array(img_rgb)     # Convert image(page) to numpy array for EasyOCR processing
                if img_np.size == 0:           # Check if the image(page) array is empty (which can happen with corrupted images)
                    st.warning(f"Skipping empty image for PDF page {img_index+1}.")  # Skips to next page if image(page) is empty
                    continue
                result = reader.readtext(img_np)      # Perform OCR on the image(page)
                text += ' '.join([item[1] for item in result]) + '\n'  # Concatenate recognized text from this page
            return text if text.strip() else "No readable text found in the PDF via OCR."   # Return OCR result or message if no text found
        except Exception as e:
            st.error(f"Error during PDF to image conversion or OCR fallback: {e}. This could be due to the size or complexity of the PDFS which exceeds  memory limits. Try a smaller PDF")
            return f"Error processing PDF for OCR: {e}"

    elif file_type == 'txt':
        uploaded_file.seek(0)                            # Ensure the file pointer is at the start
        return uploaded_file.getvalue().decode("utf-8")  # Decode bytes to string

    elif file_type == 'csv':
        uploaded_file.seek(0)                           # Ensure the file pointer is at the start
        df = pd.read_csv(uploaded_file)                 # Read CSV into DataFrame
        return df.to_string(index=False)                # Convert DataFrame to string for display

    elif file_type == 'xlsx':
        uploaded_file.seek(0)                                # Ensure the file pointer is at the start          
        df = pd.read_excel(uploaded_file, engine='openpyxl') # Read Excel into DataFrame
        df = df.dropna(axis=1, how='all')                    # Drop completely empty columns
        return df.to_string(index=False)

    elif file_type in ['png', 'jpg', 'jpeg']:
        uploaded_file.seek(0)                                 # Ensure the file pointer is at the start
        image = Image.open(uploaded_file).convert("RGB")      # Open image and convert to RGB
        image_np = np.array(image)                            # Convert image to numpy array for EasyOCR processing
        if image_np.size == 0:                                # Check if the image array is empty (which can happen with corrupted images)
            return "Uploaded image appears to be empty or corrupted."
        result = reader.readtext(image_np)                    # Perform OCR on the image
        text = ' '.join([item[1] for item in result])
        return text if text.strip() else "No text found in the image."

    else:
        return "Unsupported file type. Please upload a PDF, TXT, CSV, XLSX, PNG, or JPG."