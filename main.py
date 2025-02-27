import streamlit as st
import requests
from gtts import gTTS

def fetch_hadith(keyword):
    """
    Fetch hadith from the Sutanlab Hadith API using a given keyword.
    The API is public and does not require an API key.
    """
    base_url = "https://api.hadith.sutanlab.id/hadiths/search"
    params = {"query": keyword}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        hadith_texts = []
        for item in data.get("data", []):
            # Try to get Arabic text; if unavailable, fall back to English.
            text = item.get("data", {}).get("arab", "")
            if not text:
                text = item.get("data", {}).get("en", "")
            hadith_texts.append(text)
        return hadith_texts
    else:
        st.error("Error fetching hadith from Sutanlab API: " + str(response.status_code))
        return []

def convert_text_to_speech(text, lang="en"):
    """
    Convert the given text to speech using gTTS.
    The audio is saved as an MP3 file.
    """
    try:
        tts = gTTS(text=text, lang=lang)
        audio_file_path = "hadith_output.mp3"
        tts.save(audio_file_path)
        return audio_file_path
    except Exception as e:
        st.error("Error converting text to speech: " + str(e))
        return None

# ---------- Streamlit App ----------

st.title("Hadees Vaani - Simplified")
st.write("Enter a keyword to search for relevant hadith:")

keyword = st.text_input("Keyword")

if keyword:
    hadiths = fetch_hadith(keyword)
    if hadiths:
        st.write("### Fetched Hadiths:")
        for idx, hadith in enumerate(hadiths, 1):
            st.write(f"**{idx}.** {hadith}")

        if st.button("Listen to Hadiths"):
            # Combine all hadith texts into one string.
            final_text = " ".join(hadiths)
            # Change 'en' to 'hi' if you want the speech in Hindi, 
            # but note that translation is not performed in this simplified version.
            audio_path = convert_text_to_speech(final_text, lang="en")
            if audio_path:
                st.audio(audio_path)
    else:
        st.write("No hadith found for this keyword.")

