import streamlit as st
import speech_recognition as sr
from io import BytesIO
from googletrans import Translator
import spacy
import requests
from gtts import gTTS
from pydub import AudioSegment
import os

# ---------- Helper Functions ----------

def transcribe_audio(uploaded_file, language="hi-IN"):
    """
    Transcribe uploaded audio using Google's Speech Recognition.
    Supports wav, mp3, and opus files.
    """
    # Check file extension
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".opus"):
        # Convert opus file to wav using pydub
        audio = AudioSegment.from_file(uploaded_file, format="opus")
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        audio_file = sr.AudioFile(wav_io)
    else:
        # For wav and mp3, use the file directly
        audio_file = sr.AudioFile(BytesIO(uploaded_file.read()))
    
    recognizer = sr.Recognizer()
    with audio_file as source:
        audio_data = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio_data, language=language)
        return transcript
    except Exception as e:
        st.error("Error transcribing audio: " + str(e))
        return None

def translate_text(text, dest_language):
    """Translate text to the destination language using googletrans."""
    translator = Translator()
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        st.error("Error translating text: " + str(e))
        return text

def extract_keywords(text):
    """Extract keywords (nouns/proper nouns) from English text using spaCy."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    # Extract tokens that are NOUNs or PROPER NOUNs.
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    return keywords

def fetch_hadith(keyword):
    """
    Fetch hadith from Sutanlab Hadith API using a given keyword.
    The Sutanlab API is public and does not require an API key.
    Endpoint documentation: https://api.hadith.sutanlab.id/
    """
    base_url = "https://api.hadith.sutanlab.id/hadiths/search"
    params = {"query": keyword}  # Adjust parameters as needed.
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        hadith_texts = []
        for item in data.get("data", []):
            # Try to extract the hadith text (Arabic first, then English if available)
            text = item.get("data", {}).get("arab", "")
            if not text:
                text = item.get("data", {}).get("en", "")
            hadith_texts.append(text)
        return hadith_texts
    else:
        st.error("Error fetching hadith from Sutanlab API: " + str(response.status_code))
        return []

def convert_text_to_speech(text, lang="hi"):
    """Convert text to speech and save as an MP3 file using gTTS."""
    try:
        tts = gTTS(text=text, lang=lang)
        audio_file_path = "hadith_output.mp3"
        tts.save(audio_file_path)
        return audio_file_path
    except Exception as e:
        st.error("Error converting text to speech: " + str(e))
        return None

# ---------- Streamlit App ----------

st.title("Hadith Finder Application")

st.markdown("""
This application accepts a Hindi/Urdu voice note, transcribes it, translates it to English,
extracts keywords, searches for relevant hadith from the Sutanlab Hadith API, translates them back to Hindi,
and finally speaks the results.
""")

# Upload voice note (supporting wav, mp3, and opus files)
uploaded_file = st.file_uploader("Upload your Hindi/Urdu voice note (wav, mp3, or opus)", type=["wav", "mp3", "opus"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/wav")
    
    if st.button("Process Audio"):
        # Step 1: Transcribe the uploaded audio
        transcript = transcribe_audio(uploaded_file, language="hi-IN")  # Use "ur-PK" for Urdu if needed
        if transcript:
            st.write("**Transcribed Text:**", transcript)
            
            # Step 2: Translate the transcribed text from Hindi/Urdu to English
            translated_to_english = translate_text(transcript, "en")
            st.write("**Translated to English:**", translated_to_english)
            
            # Step 3: Extract keywords from the English text
            keywords = extract_keywords(translated_to_english)
            st.write("**Extracted Keywords:**", keywords)
            
            # Step 4: Fetch hadith using one of the keywords
            if keywords:
                # For demonstration, we'll use the first extracted keyword.
                hadiths = fetch_hadith(keywords[0])
                st.write("**Fetched Hadiths:**", hadiths)
                
                if hadiths:
                    # Step 5: Translate each hadith back to Hindi (or Urdu)
                    translated_hadiths = [translate_text(text, "hi") for text in hadiths if text.strip()]
                    st.write("**Hadiths in Hindi:**")
                    for idx, hadith in enumerate(translated_hadiths, 1):
                        st.write(f"{idx}. {hadith}")
                    
                    # Step 6: Convert the final text to speech
                    final_text = " . ".join(translated_hadiths)
                    audio_path = convert_text_to_speech(final_text, lang="hi")
                    if audio_path:
                        st.audio(audio_path)
            else:
                st.warning("No keywords were extracted from the input.")

