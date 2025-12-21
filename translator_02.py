import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
import pandas as pd
import PyPDF2
import  tempfile
import pytesseract
from pdf2image import convert_from_path






# Set up Google Generative AI API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
print("Loaded API Key:", "API Key found" if API_KEY else "No API Key found")
genai.configure(api_key=API_KEY)
# Configure model
model = genai.GenerativeModel("gemini-1.5-flash")


# Function to translate text using Google Generative AI
try:
    def translate_text(text, target_language):
        system_message = "You are a helpful assistant that translates text."
        prompt = f"{system_message}\n\nTranslate the following text to {target_language}. Provide the translation only:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
except Exception as e:
    print(f"Error during translation: {e}")

# Function to extract text from uploaded files
def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        print("Processing PDF file...")
        text = ""

        # Save uploaded PDF file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        try:
            # Try extracting text using PyPDF2 (text-based pdfs)
            with open(temp_file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
        
        # Set Tesseract path explicitly for OCR
        # If no text was extracted, use OCR with pytesseract
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if not text.strip():
            print("Using OCR for PDF extraction...")
            try:  
                images = convert_from_path(temp_file_path, poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin')
                print('test again')
                for image in images:
                    # Use pytesseract to extract text from each image
                    page_text = pytesseract.image_to_string(image)
                    if page_text:
                        text += page_text + "\n"
            except Exception as ocr_error:
                print(f"OCR extraction failed: {ocr_error}")
        
            
        # Ensure the file is deleted after processing
        try:
            os.remove(temp_file_path)
        except Exception as remove_error:
            print(f"Failed to delete temp file: {remove_error}")
        return text

    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8")

    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df.to_string(index=False)

    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df = df.dropna(axis=1, how='all')  # Drop empty columns
        return df.to_string(index=False)

    else:
        return "Unsupported file type. Please upload a PDF, TXT, CSV, or XLSX file."


    
# Function to convert text to speech
def text_to_speech(text, language="en"):
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")
        return None
    

# Create Streamlit app
st.set_page_config(page_title="SnapTranslator and Text 2 Speech Conversion", page_icon="📝", layout="wide")
st.title("📝 Google Gemini Translation and Text-to-Speech App")
st.write("Translate text and convert it to speech using Google Gemini.")    

# Text input or file upload
user_input = st.text_area("Enter text to translate:", placeholder="Type or paste your text here...")
uploaded_file = st.file_uploader("Or upload a file (PDF, TXT, CSV, XLSX):", type=["pdf", "txt", "csv", "xlsx"])
language = {
    "Afrikaans": "af",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko"
} 

selected_language = st.selectbox("Select target language:", list(language.keys()))
if st.button("Translate"):
    if uploaded_file is not None:
      user_input = extract_text_from_file(uploaded_file)
    else:
      user_input = user_input 

    # Validate user input
    if not user_input.strip():
        print(user_input)
        st.error("Please enter some text or upload a file to translate.")
    else:
        translated_text = translate_text(user_input, selected_language)
        st.subheader(f"Translation to {selected_language}:")
        st.write(translated_text)

        # Convert translated text to speech
        audio_file = text_to_speech(translated_text, language[selected_language])
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name="translated_audio.mp3", mime="audio/mp3")
        else:
            st.error(" Error generating audio file.")

