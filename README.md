# 🌍🔊Multilingual Text-to-Speech Web App for English Input (Streamlit, Gemini API, gTTS)

Translate English text into dozens of languages and hear it spoken aloud — all in one smooth, easy-to-use web app with audio download included.
Simply input your English text (or upload a file!), choose your target language, and receive both the translated text and a downloadable audio file.

## 🧭Getting Started

Follow these steps to set up and run the application in you local machine

### 1. 📝Prerequisites
* Python 3.8 +
* Python package installer `pip`

### 2. 🧬Clone the repository

```bash
git clone 
```

### 3. ⚙️Set Up a Virtual Environment
It's best practice to use a virtual environment.

<b>For Windows (Powershell)</b>
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```
(If you encounter script execution issues, you might need to run:
```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

<b>For macOS/Linux</b>
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. 📦Install Dependencies
Install all neccessary Python packages:
```bash
pip install -r requirements.txt
```

### 5. 🔑Configure Your Gemini API Key
This application requires a Google Gemini API key.
1. Generate a key from [Google AI Studio](https://aistudio.google.com/prompts/new_chat)
2. Create a file named <b>`.env`</b> in the root of your project directory.
3. Add your API key to this file:
```python
GOOGLE_API_KEY = your_api_key_here
```
Replace your_api_key_here with you actual key.

### 6. 🚀Launch the Application
Activate the virtual enviroment, configure the API key and then run the application:
```bash
python -m streamlit run translator_app.py
```
Your default web browser will open the application, ready for use.

## 🧱Technology Stack
| Category                | Tools Used                                     |
| :---------------------- | :--------------------------------------------- |
| **Web Framework**       | Streamlit                                      |
| **AI/Translation**      | Google Generative AI (Gemini 1.5 Flash) API    |
| **Text-to-Speech**      | gTTS (Google Text-to-Speech)                   |
| **File Parsing**        | PyPDF2, pdf2image, pytesseract, pandas, openpyxl |
| **Environment Management** | python-dotenv                                  |

## 📄Detailed Documentation
For a comprehensive understanding of the project's design, architectural decisions, testing methodology, detailed feature explanations etc., refer to the documentation.pdf file in this repository.

## 📁Project Structure 
```
translate_speak/
├── app.py                      # Main Streamlit application logic and UI.
├── requirements.txt            # List of Python dependencies.
├── .env                        # Environment variables (e.g., API keys).
├── assets/                     # Static assets (images, sample files).
│   └── sample_files/           # Example input files for testing.
├── utils/                      # Helper functions and modules.
│   └── file_parser.py          # Handles text extraction from various file types.
├── README.md                   # This overview file.
├── documentation.pdf           # Comprehensive project documentation.
└── .gitignore                  # Specifies files/folders to exclude from Git.
```
## ⚠️Important Considerations and Limitations
* **Input Language**: Currently, the applkication processes **English text only** for translation. This was a deliberate design choice for complexity management and consistent quality.
* **gTTS Language Support**: gTTS has a limited set of supported languages for speech synthesis.
* **File Size**: Maximum upload size is 200MB.
* **No Reak-Time Preview**: Translation and audio generation automatically occurs after text is submitted.

## 🤝Contributing
Contributions are welcome! If you have suggestions, bug reports, or want to contribute code, please feel free to open an issue or submit a pull request.

## 📜License
This project is licensed under the MIT License.
