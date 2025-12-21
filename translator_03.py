import os
import streamlit as st
from PIL import Image  # Import Image from Pillow
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

# Set page configurations

# Function to translate text using Google Generative AI
def translate_text(text, target_language):
    try:
        system_message = "You are a helpful assistant that translates text."
        prompt = f"{system_message}\n\nTranslate the following text to {target_language}. Provide the translation only:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:

         # Log the error for debugging
        print(f"[Translation Error] Failed to translate text to '{target_language}': {e}")
         # Check for quota exhaustion
        error_message = str(e)
        if "quota" in error_message.lower() or "exceeded" in error_message.lower():
            return "Translation failed due to API quota exhaustion. Please wait or upgrade your plan to continue."
        return "Translation failed. Please try again or check the input."


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
    

# Set page configurations
st.set_page_config(page_title="Translator and Text-to-Speech App", page_icon="🌐", layout="centered")

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Change the top bar background */
        header[data-testid="stHeader"] {
            background-color: #FFF5E1;  /* Cream color */
    }

        /* Optional: remove box shadow for cleaner look */
        header[data-testid="stHeader"]::before {
            box-shadow: none;
    }
    .stApp {
        background-color: #FFF8E7;
    }
    
    textarea, .stFileUploader, .stSelectbox{
        background-color: white !important;
        color: black !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-size: 16px !important;
    }
            
    .stButton>button { 
            background-color: #FF6F61; 
            color: white; 
            font-weight: bold; 
            border-radius: 5px; 
            padding: 10px 20px;
    }
            
    .stButton>button:hover {
        background-color: #E65C4F;
    }
    
    .stSidebar {    
        background-color: #FF6F61;
    }
    </style>
    """, unsafe_allow_html=True)
    

# App title and description
st.markdown(
    "<h1 style='font-size:30px;'>🌍 Google Gemini Translator & Text-to-Speech</h1>",
    unsafe_allow_html=True
)

# App description
st.markdown(
    "<p style='color:#E65C4F; font-style:italic; font-weight:bold; text-align:center;'>Effortlessly translate English text into your chosen language and hear it spoken aloud.</p>",
    unsafe_allow_html=True
)


# Text input or file upload
user_input = st.text_area("Enter text to translate:", placeholder="Type or paste your text here...")
uploaded_file = st.file_uploader("Or upload a file (PDF, TXT, CSV, XLSX):", type=["pdf", "txt", "csv", "xlsx"])

# Language selection
with st.sidebar:
    # Add vertical space
    st.markdown("<br><br>", unsafe_allow_html=True)
    img = Image.open("assets/images/translator.png") # Open the image file
    st.image(img, use_container_width=True)  

    
    language = {
        "Afrikaans 🇿🇦": "af",
        "Arabic 🇸🇦": "ar",
        "Bengali 🇧🇩": "bn",
        "Chinese (Simplified) 🇨🇳": "zh-CN",
        "Dutch 🇳🇱": "nl",
        "English 🇬🇧 ": "en",
        "French 🇫🇷": "fr",
        "German 🇩🇪": "de",
        "Greek 🇬🇷": "el",
        "Hebrew 🇮🇱": "he",
        "Hindi 🇮🇳": "hi",
        "Indonesian 🇮🇩": "id",
        "Italian 🇮🇹": "it",
        "Japanese 🇯🇵": "ja",
        "Korean 🇰🇷": "ko",
        "Polish 🇵🇱": "pl",
        "Portuguese 🇵🇹": "pt",
        "Russian 🇷🇺": "ru",
        "Spanish 🇪🇸": "es",
        "Swedish 🇸🇪": "sv",
        "Turkish 🇹🇷": "tr",
        "Ukrainian 🇺🇦": "uk",
        "Vietnamese 🇻🇳": "vi"
    }

    # Language selection dropdown
    selected_language = st.selectbox("Select target language:", options=list(language.keys()))

# Translate button
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
        with st.spinner("Translating...🔤"):
            translated_text = translate_text(user_input, selected_language)
        st.subheader(f"Translation to {selected_language}:")
        st.markdown(f"""
        <div style="background-color:#F0F0F0; color:#333333; padding:15px; border-radius:8px; font-size:16px;">
        {translated_text}
        </div>
        """, unsafe_allow_html=True)

        # Convert translated text to speech
        with st.spinner("Generating audio...🔊"):
            audio_file = text_to_speech(translated_text, language[selected_language])
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name="translated_audio.mp3", mime="audio/mp3")
        else:
            st.error("Error generating audio file.")

