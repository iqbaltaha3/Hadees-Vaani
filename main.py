import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.title("Quran & Hadith Semantic Search")
st.write("Enter a natural language query to search across Quran ayat and Hadith.")

# --- Data Loading ---
@st.cache_data
def load_data():
    quran_df = pd.read_csv("quran.csv")
    hadith_df = pd.read_csv("hadith.csv")
    return quran_df, hadith_df

quran_df, hadith_df = load_data()

# --- Model Loading ---
@st.cache_resource
def load_model():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

model = load_model()

# --- Compute Embeddings ---
@st.cache_data(show_spinner=True)
def compute_embeddings(texts):
    return model.encode(texts, show_progress_bar=True)

quran_texts = quran_df["ayahs-translation"].tolist()
hadith_texts = hadith_df["text_en"].tolist()

quran_embeddings = compute_embeddings(quran_texts)
hadith_embeddings = compute_embeddings(hadith_texts)

# --- User Query ---
query = st.text_input("Enter your search query:")

if query:
    # Convert query to embedding
    query_embedding = model.encode([query])
    
    # Compute cosine similarities
    quran_similarities = cosine_similarity(query_embedding, quran_embeddings)[0]
    hadith_similarities = cosine_similarity(query_embedding, hadith_embeddings)[0]
    
    # Add similarity scores to dataframes
    quran_df["similarity"] = quran_similarities
    hadith_df["similarity"] = hadith_similarities
    
    # Get top 5 results from each dataset
    top_n = 5
    top_quran = quran_df.sort_values("similarity", ascending=False).head(top_n)
    top_hadith = hadith_df.sort_values("similarity", ascending=False).head(top_n)
    
    st.markdown("### Top Matching Quran Ayat")
    for _, row in top_quran.iterrows():
        st.write(f"**Surah {row['surahs']} - Ayat {row['ayahs']}**")
        st.write(row["ayahs-translation"])
        st.write(f"Similarity Score: {row['similarity']:.2f}")
        st.markdown("---")
    
    st.markdown("### Top Matching Hadith")
    for _, row in top_hadith.iterrows():
        st.write(f"**Source:** {row['source']}, **Hadith No:** {row['hadith_no']}")
        st.write(row["text_en"])
        st.write(f"Similarity Score: {row['similarity']:.2f}")
        st.markdown("---")
