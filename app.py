import streamlit as st
from dotenv import load_dotenv
import os
import wikipediaapi
from groq import Groq
import requests
from gtts import gTTS
import PyPDF2
from docx import Document
from langdetect import detect
import tempfile
import wikipedia  # Added for search functionality

# Set page configuration to wide layout
st.set_page_config(layout="wide", page_title="AI-Powered Educational Tool")

# Load environment variables
load_dotenv()

# Set API Key for Groq
Groq_API = os.getenv("Groq_API_Key")
if not Groq_API:
    raise ValueError("❌ Missing GROQ API Key. Set it in environment variables.")

# Initialize Groq client
client = Groq(api_key=Groq_API)

# Set Google Cloud Translate API Key
GOOGLE_TRANSLATE_API_KEY = os.getenv("Google_API")
if not GOOGLE_TRANSLATE_API_KEY:
    raise ValueError("❌ Missing Google Cloud Translate API Key. Set it in environment variables.")

# --- Educational Script Generator Functions ---

def fetch_wikipedia_summary(topic):
    """Fetches a Wikipedia summary for the given topic or a related topic."""
    wiki_wiki = wikipediaapi.Wikipedia(user_agent="EducationalScriptApp/1.0", language="en")
    page = wiki_wiki.page(topic)
    
    if page.exists():
        return page.summary
    
    # If exact topic not found, search for related topics
    try:
        search_results = wikipedia.search(topic, results=3)  # Get top 3 related topics
        for related_topic in search_results:
            page = wiki_wiki.page(related_topic)
            if page.exists():
                return page.summary
        # If no related topics found, return None to trigger Groq-based generation
        return None
    except Exception as e:
        return None

def generate_script(topic, duration):
    """Generates an educational script using Groq AI, with or without Wikipedia content."""
    try:
        factual_content = fetch_wikipedia_summary(topic)
        words_per_minute = 130
        target_words = duration * words_per_minute

        if factual_content:
            # Wikipedia content available, format it into a script
            prompt = f"Format the following factual content into an educational script in English with approximately {target_words} words. Do not include extra text like 'Here is the formatted script' or descriptions.\n\n{factual_content}"
        else:
            # No Wikipedia content, generate a script directly
            prompt = f"Generate an educational script in English on the topic '{topic}' with approximately {target_words} words. Ensure the content is factual, engaging, and suitable for an educational video. Do not include extra text like 'Here is the formatted script' or descriptions."

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI assistant that creates structured educational scripts. Start directly with the script content, focusing on the topic. Do NOT include introductory phrases, word counts, or metadata."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192"
        )

        script = response.choices[0].message.content.strip()
        script = script.replace("**", "").replace("*", "").replace("###", "").replace("##", "").replace("#", "")
        return script
    except Exception as e:
        return f"❌ Error in script generation: {str(e)}"

def generate_video_script(script_content):
    """Generates a video script describing scenes for visualization."""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI assistant that converts educational text into structured video scene descriptions for AI-generated videos."},
                {"role": "user", "content": f"Convert the following educational script into a video script with scene descriptions, suitable for AI-generated video production.\n\n{script_content}"}
            ],
            model="llama3-70b-8192"
        )
        video_script = response.choices[0].message.content.strip()
        return video_script
    except Exception as e:
        return f"❌ Error in video script generation: {str(e)}"

def translate_script(script_content, target_language):
    """Translates the script into the selected language using Google Cloud Translate API v2 REST endpoint."""
    try:
        if not script_content or script_content.startswith("❌"):
            return "⚠️ No valid script content to translate."

        paragraphs = script_content.split("\n\n")
        translated_paragraphs = []
        url = "https://translation.googleapis.com/language/translate/v2"

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            params = {
                "q": paragraph,
                "source": "en",
                "target": target_language,
                "format": "text",
                "key": GOOGLE_TRANSLATE_API_KEY
            }
            response = requests.post(url, data=params)
            response.raise_for_status()
            translated_text = response.json()["data"]["translations"][0]["translatedText"]
            translated_paragraphs.append(translated_text)

        translated_text = "\n\n".join(translated_paragraphs)
        return translated_text
    except Exception as e:
        return f"❌ Error in translation: {str(e)}"

def save_script(topic, script_content, script_type="script"):
    """Saves the generated script to a temporary file and returns the file path."""
    filename = f"{topic.replace(' ', '_')}_{script_type}.txt"
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", prefix=filename, delete=False, encoding="utf-8") as f:
            f.write(script_content)
        return f.name
    except Exception as e:
        return f"❌ Error saving script: {str(e)}"

# --- Text-to-Speech Functions ---

def extract_text(file):
    """Extract text from different file types."""
    file_extension = os.path.splitext(file.name)[1].lower()

    if file_extension == '.txt':
        return file.read().decode('utf-8')
    elif file_extension == '.pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_extension == '.docx':
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        raise ValueError("Unsupported file format. Please upload TXT, PDF, or DOCX files.")

def text_to_speech(file):
    """Convert uploaded file text to speech."""
    try:
        text = extract_text(file)
        if not text.strip():
            return "Error: No text found in the file.", None

        language = detect(text)
        tts = gTTS(text=text, lang=language, slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            output_file = f.name

        with open(output_file, "rb") as f:
            audio_data = f.read()

        os.remove(output_file)
        return f"Language detected: {language}", audio_data
    except Exception as e:
        return f"Error: {str(e)}", None

# --- Streamlit UI ---

st.title("🎬 AI-Powered Educational Tool")

tab1, tab2 = st.tabs(["Script Generator", "Text-to-Speech"])

with tab1:
    st.header("🎬 AI-Powered Educational Script Generator")
    
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
        <style>
        .stTextArea { margin-bottom: 20px; }
        .stTextArea textarea {
            font-size: 16px;
            line-height: 1.6;
            width: 100% !important;
        }
        .rtl-text {
            direction: rtl;
            text-align: right;
            font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Arial', sans-serif;
            font-size: 18px;
            line-height: 1.6;
            white-space: pre-wrap;
            border: 1px solid #cccccc;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8f9fa;
            height: 600px;
            overflow-y: auto;
            width: 100% !important;
        }
        .stTextInput, .stSlider, .stSelectbox, .stButton {
            width: 100% !important;
        }
        .stColumn {
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        topic = st.text_input("Enter Topic", placeholder="e.g., Quantum Mechanics")
    with col2:
        duration = st.slider("Duration (minutes)", min_value=1, max_value=30, value=2, step=1)

    if st.button("Clear All Content", key="clear_content"):
        st.session_state.clear()
        st.rerun()

    if st.button("Generate Script", key="generate_script"):
        with st.spinner("Generating script..."):
            script_content = generate_script(topic, duration)
            st.session_state['script_content'] = script_content

    if 'script_content' in st.session_state and st.session_state['script_content'] and not st.session_state['script_content'].startswith("❌"):
        st.text_area("Generated Script", value=st.session_state['script_content'], height=400, key="script_output")
        script_file = save_script(topic, st.session_state['script_content'], "script")
        with open(script_file, "rb") as f:
            st.download_button(
                label="Download English Script",
                data=f,
                file_name=f"{topic.replace(' ', '_')}_script.txt",
                mime="text/plain",
                key="download_script"
            )

    if 'script_content' in st.session_state and st.session_state['script_content'] and not st.session_state['script_content'].startswith("❌"):
        if st.button("Generate Script for Video", key="generate_video_script"):
            with st.spinner("Generating video script..."):
                video_script_content = generate_video_script(st.session_state['script_content'])
                st.session_state['video_script_content'] = video_script_content

    if 'video_script_content' in st.session_state and st.session_state['video_script_content'] and not st.session_state['video_script_content'].startswith("❌"):
        st.text_area("Generated Video Script", value=st.session_state['video_script_content'], height=600, key="video_script_output")
        video_script_file = save_script(topic, st.session_state['video_script_content'], "video_script")
        with open(video_script_file, "rb") as f:
            st.download_button(
                label="Download Video Script",
                data=f,
                file_name=f"{topic.replace(' ', '_')}_video_script.txt",
                mime="text/plain",
                key="download_video_script"
            )

    st.subheader("🌍 Translate Script")
    language_options = [
        ("Urdu", "ur"), ("Punjabi", "pa"), ("Pashto", "ps"), ("Sindhi", "sd"), ("Hindi", "hi"),
        ("Arabic", "ar"), ("Tamil", "ta"), ("Telugu", "te"), ("Chinese (Simplified)", "zh-CN"),
        ("Chinese (Traditional)", "zh-TW"), ("Turkish", "tr"), ("French", "fr"), ("Spanish", "es"),
        ("German", "de"), ("Italian", "it"), ("Russian", "ru"), ("Japanese", "ja")
    ]
    language_labels = [label for label, _ in language_options]
    language_codes = [code for _, code in language_options]
    selected_language = st.selectbox("Select Language for Translation", language_labels)
    target_language = language_codes[language_labels.index(selected_language)]

    if 'script_content' in st.session_state and st.session_state['script_content'] and not st.session_state['script_content'].startswith("❌"):
        if st.button("Translate Script", key="translate_script"):
            with st.spinner("Translating script..."):
                translated_content = translate_script(st.session_state['script_content'], target_language)
                st.session_state['translated_content'] = translated_content

    if 'translated_content' in st.session_state and st.session_state['translated_content'] and not st.session_state['translated_content'].startswith("❌"):
        translated_content_html = st.session_state['translated_content'].replace("&", "&").replace("<", "<").replace(">", ">")
        st.markdown(
            f"""
            <div class="rtl-text" dir="auto">
                {translated_content_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        translated_file = save_script(topic, st.session_state['translated_content'], "translated_script")
        with open(translated_file, "rb") as f:
            st.download_button(
                label="Download Translated Script",
                data=f,
                file_name=f"{topic.replace(' ', '_')}_translated_script.txt",
                mime="text/plain",
                key="download_translated_script"
            )

with tab2:
    st.header("🎙️ Language Detection & Text-to-Speech Converter")
    
    uploaded_file = st.file_uploader("Upload a TXT, PDF, or DOCX file", type=["txt", "pdf", "docx"], key="file_uploader")

    if uploaded_file and ('last_uploaded_file' not in st.session_state or st.session_state['last_uploaded_file'] != uploaded_file.name):
        st.session_state['audio_data'] = None
        st.session_state['status'] = None
        st.session_state['last_uploaded_file'] = uploaded_file.name

    if uploaded_file:
        if st.button("Convert to Speech", key="convert_speech"):
            with st.spinner("Converting to speech..."):
                st.session_state['audio_data'] = None
                st.session_state['status'] = None
                status, audio_data = text_to_speech(uploaded_file)
                st.session_state['status'] = status
                st.session_state['audio_data'] = audio_data

    if 'audio_data' in st.session_state and st.session_state['audio_data']:
        st.text(st.session_state['status'])
        st.audio(st.session_state['audio_data'], format="audio/mp3")
        st.download_button(
            label="Download Audio",
            data=st.session_state['audio_data'],
            file_name="output.mp3",
            mime="audio/mp3",
            key="download_audio"
        )