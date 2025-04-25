import streamlit as st
import os
from datetime import datetime
import tempfile
import shutil
import requests
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

# Configuration de la page
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #CC0000;
    }
    .progress-bar {
        width: 100%;
        height: 20px;
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        background-color: #FF0000;
        transition: width 0.3s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📱 YouTube Downloader")
    st.markdown("---")
    st.markdown("### À propos")
    st.markdown("""
    Cette application vous permet de :
    - Télécharger des vidéos YouTube
    - Choisir la qualité de la vidéo
    - Télécharger uniquement l'audio
    - Voir les informations de la vidéo
    """)
    st.markdown("---")
    st.markdown("### Développé avec ❤️")
    st.markdown("Streamlit • YouTube API")

# Fonction pour extraire l'ID de la vidéo
def extract_video_id(url):
    video_id = None
    if 'youtube.com' in url:
        video_id = re.search(r'v=([^&]+)', url)
        if video_id:
            return video_id.group(1)
    elif 'youtu.be' in url:
        video_id = re.search(r'youtu.be/([^?]+)', url)
        if video_id:
            return video_id.group(1)
    return None

# Fonction pour obtenir les informations de la vidéo
def get_video_info(video_id, api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            return None
            
        video_data = response['items'][0]
        return {
            'title': video_data['snippet']['title'],
            'author': video_data['snippet']['channelTitle'],
            'thumbnail': video_data['snippet']['thumbnails']['high']['url'],
            'duration': video_data['contentDetails']['duration'],
            'views': int(video_data['statistics']['viewCount'])
        }
    except HttpError as e:
        st.error(f"Erreur API YouTube: {str(e)}")
        return None

# Fonction principale
def main():
    st.title("🎥 YouTube Downloader")
    st.markdown("---")

    # Configuration de l'API key
    api_key = st.text_input("Entrez votre clé API YouTube:", type="password")
    if not api_key:
        st.warning("Veuillez entrer une clé API YouTube pour continuer.")
        st.info("""
        Pour obtenir une clé API YouTube :
        1. Allez sur https://console.cloud.google.com/
        2. Créez un nouveau projet
        3. Activez l'API YouTube Data v3
        4. Créez des identifiants (clé API)
        """)
        return

    # Configuration du dossier de téléchargement
    download_dir = st.text_input("Dossier de téléchargement (optionnel):", value=os.path.expanduser("~/Downloads"))
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Champ de saisie URL
    url = st.text_input("Collez l'URL de la vidéo YouTube ici:")

    if url:
        try:
            # Extraction de l'ID de la vidéo
            video_id = extract_video_id(url)
            if not video_id:
                st.error("URL YouTube invalide. Veuillez entrer une URL valide.")
                return

            # Obtenir les informations de la vidéo
            video_info = get_video_info(video_id, api_key)
            if not video_info:
                st.error("Impossible d'obtenir les informations de la vidéo. Vérifiez votre clé API et l'URL.")
                return

            # Affichage des informations de la vidéo
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(video_info['thumbnail'], width=300)
            
            with col2:
                st.subheader(video_info['title'])
                st.markdown(f"**Auteur:** {video_info['author']}")
                st.markdown(f"**Vues:** {video_info['views']:,}")
                
                # Options de téléchargement
                st.markdown("### Options de téléchargement")
                download_type = st.radio(
                    "Choisissez le type de téléchargement:",
                    ["Vidéo", "Audio uniquement"]
                )
                
                if st.button("Télécharger"):
                    st.warning("""
                    ⚠️ Note importante :
                    L'API YouTube ne permet pas directement le téléchargement de vidéos.
                    Pour télécharger des vidéos YouTube, vous devez utiliser une bibliothèque tierce.
                    
                    Suggestions :
                    1. Utilisez youtube-dl (en ligne de commande)
                    2. Utilisez un service web de téléchargement
                    3. Utilisez un navigateur avec une extension de téléchargement
                    """)
        
        except Exception as e:
            st.error(f"Une erreur est survenue: {str(e)}")
            st.info("Conseils de dépannage:")
            st.markdown("""
            - Vérifiez que l'URL est correcte
            - Assurez-vous que la vidéo est publique
            - Vérifiez votre clé API
            - Essayez une autre vidéo
            """)

if __name__ == "__main__":
    main()