# 🎈 AI-Powered Educational Tool

This is a Streamlit-based web application designed to generate educational scripts, create video scene descriptions, translate content into multiple languages, and convert text to speech. The app leverages APIs from Groq, Google Cloud Translate, and Wikipedia to provide a comprehensive tool for educators, content creators, and learners.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## ✨ Features
### Educational Script Generation: 
Generate structured educational scripts based on Wikipedia summaries for a given topic and desired duration.
### Video Script Creation: 
Convert educational scripts into detailed video scene descriptions suitable for AI-generated video production.
### Multilingual Translation: 
Translate scripts into various languages (e.g., Urdu, Arabic, Spanish, Chinese, etc.) using the Google Cloud Translate API.
### Text-to-Speech Conversion: 
Upload TXT, PDF, or DOCX files and convert their content to speech with automatic language detection.
### Responsive UI: 
A wide-layout Streamlit interface with RTL support for languages like Urdu and Arabic, and downloadable outputs for scripts and audio files.

## 🛠️ Technologies Used
**Streamlit:** For building the interactive web interface.

**Groq API:** For generating educational and video scripts using AI.

**Google Cloud Translate API:** For translating scripts into multiple languages.

**Wikipedia API:** For fetching factual content to base scripts on.

**gTTS (Google Text-to-Speech):** For converting text to speech.

**PyPDF2 & python-docx:** For extracting text from PDF and DOCX files.

**Langdetect:** For automatic language detection in uploaded files.

**Tempfile:** For handling temporary file storage for downloads.

## 📋 Prerequisites

To run this application locally, ensure you have the following:

   Python 3.8 or higher

   A Groq API key (set as ```Groq_API_Key``` in a ```.env``` file)

   A Google Cloud Translate API key (set as ```Google_API``` in a ```.env``` file)

   Required Python packages listed in ```requirements.txt```

## 🚀 How to run the App Locally

#### 1. Clone the Repository

   ```
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

#### 2. Install Requirements
   
Create a virtual environment (optional but recommended) and install dependencies:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
#### 3. Set Up Environment Variables
   
Create a ```.env``` file in the root directory and add your API keys:

   ```
   Groq_API_Key=your_groq_api_key
   Google_API=your_google_cloud_translate_api_key
   ```
#### 4. Run the App
   
Start the Streamlit app:

   ```
   streamlit run app.py
   ```
The app will be available at  ```http://localhost:8501``` in your browser.
