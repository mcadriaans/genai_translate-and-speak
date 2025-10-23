import os
import streamlit as st
from PIL import Image 
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
import tempfile
from utils.file_parser import extract_text_from_file
from langdetect import detect    
import re  

## Set up Google Generative AI API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
print("Loaded API Key:", "API Key found" if API_KEY else "No API Key found")
genai.configure(api_key=API_KEY)


## Configure model
## List available models (for debugging purposes)
#for model in genai.list_models():
#    print(model.name, model.supported_generation_methods)
model_name = "gemini-2.5-flash"
model = genai.GenerativeModel(model_name)


## Function to translate text using Google Generative AI
def translate_text(text, target_language):
    try:
        system_message = "You are a helpful assistant that translates text."
        prompt = f"{system_message}\n\nTranslate the following text to {target_language}.Provide the translation only:\n\n{text}"
        response = model.generate_content(prompt)
        print(f"Translation response: {response.text}")
        return response.text.strip()
    except Exception as e:
        error_message = str(e)
        match = re.search(r"404 models/", error_message)
        if match:
            st.error(f"The model {model_name} could not be found. It may have been deprecated or is unsupported in the current API version. Please select a newer model.")
            st.info("Call `list_models()` to view available options.")
            st.stop()
        elif "quota" in error_message.lower() or "exceeded" in error_message.lower(): # Check for quota exhaustion
            st.error("Translation failed due to API quota exhaustion. Please wait or upgrade your plan to continue.")
            st.info("Check your Google Cloud Console for quota details.")
        else:
            st.error("Translation failed. Please try again or check the input.")
    



## Function to convert text to speech
def text_to_speech(text, language="en"):
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")
        return None
    

## Set page configurations
st.set_page_config(page_title="Translator and Text-to-Speech App", page_icon="🌐", layout="centered")

## Custom CSS for better appearance
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
    


## App title and description
st.markdown(
    "<h1 style='font-size:30px;'>🌍 Google Gemini Translator & Text-to-Speech</h1>",
    unsafe_allow_html=True
)


## App description
st.markdown(
    "<p style='color:#E65C4F; font-style:italic; font-weight:bold; text-align:center;'>Effortlessly translate English text into your chosen language and hear it spoken aloud.</p>",
    unsafe_allow_html=True
)

## Text input or file upload
user_input = st.text_area("Enter text to translate:", placeholder="Type or paste your text here...")
uploaded_file = st.file_uploader("Or upload a file (PDF, TXT, CSV, XLSX):", type=["pdf", "txt", "csv", "xlsx", "png", "jpg", "jpeg"])

## Language selection
with st.sidebar:
    # Add vertical space
    st.markdown("<br><br>", unsafe_allow_html=True)
    img = Image.open("assets/images/translator.png") # Open the image file
    st.image(img, width='stretch')  
    language = {
        "Afrikaans 🇿🇦": "af",
        "Arabic 🇸🇦": "ar",
        "Bengali 🇧🇩": "bn",
        "Chinese (Simplified) 🇨🇳": "zh-CN",
        "Dutch 🇳🇱": "nl",
        #"English 🇬🇧 ": "en",
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
        "Vietnamese 🇻🇳": "vi",
        "Zulu 🇿🇦": "zu"
    }

    ## Language selection dropdown
    selected_language = st.selectbox("🌐 Select Language",options=list(language.keys()))

## Translate button
if st.button("Translate"):
    if uploaded_file is not None:
      ## Extract text from uploaded file
      user_input = extract_text_from_file(uploaded_file)
    else:
      user_input = user_input 
      print(user_input)

    ## Validate user input
    if not user_input.strip():
        print(user_input)
        st.error("No input detected. Please type something or upload a file.")
    else:
        try:
            if len(user_input) < 30:
                st.warning("Input too short for reliable language detection. Please enter a longer English sentence..")
                st.stop() # Stop further execution
            else:
                detected_lang = detect(user_input)
                #print(f"Detected language: {detected_lang}")
                if detected_lang != 'en':
                    st.error("Translation only works with English input. Please switch your text to English and try again.")
                    st.stop() # Stop further execution
                else:
                 ## Translate text
                    with st.spinner("Translating...🔤"):
                        translated_text = translate_text(user_input, selected_language)
                        st.subheader(f"Translation to {selected_language}:")
                        st.markdown(f"""
                <div style="background-color:#F0F0F0; color:#333333; padding:15px; border-radius:8px; font-size:16px;">
                {translated_text}
                </div>
                """, unsafe_allow_html=True)
                    print("Translated text:", translated_text)
                ## Convert translated text to speech
                with st.spinner("Generating audio...🔊"):
                    audio_file = text_to_speech(translated_text, language[selected_language])
                    st.subheader(f"Text-to-Speech in {selected_language}:")

                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    with open(audio_file, "rb") as f:
                        st.download_button("Download Audio", f, file_name="translated_audio.mp3", mime="audio/mp3")
                else:
                    st.error(f"Unfortunately, text-to-speech is not available for {selected_language} at this time. You can still translate the text, but to hear it spoken, please choose a different language from the dropdown.")

        except Exception as e:
            st.error(f"An error occurred: {e}") # Display the error message to the user
            

