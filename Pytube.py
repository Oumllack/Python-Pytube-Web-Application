import streamlit as st
import yt_dlp
import os
from datetime import datetime
import tempfile
import shutil
import time
import random
import requests
from urllib.parse import urlparse

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
    st.markdown("Streamlit • yt-dlp")

# Liste de User-Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]

# Liste de proxies publics (à utiliser avec précaution)
PROXIES = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    'http://proxy3.example.com:8080',
]

# Fonction de progression
def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d.get('_percent_str', '0%')
        progress = float(progress.replace('%', '')) / 100
        st.progress(progress)
    elif d['status'] == 'finished':
        st.success("Téléchargement terminé!")

# Fonction pour vérifier si une URL est valide
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Fonction pour obtenir les informations de la vidéo avec retry
def get_video_info(url, max_retries=3):
    if not is_valid_url(url):
        st.error("URL invalide. Veuillez entrer une URL YouTube valide.")
        return None

    for attempt in range(max_retries):
        try:
            # Sélection aléatoire d'un User-Agent
            user_agent = random.choice(USER_AGENTS)
            
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'no_color': True,
                'extract_flat': False,
                'force_generic_extractor': False,
                'geo_bypass': True,
                'geo_verification_proxy': None,
                'http_headers': {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                }
            }
            
            # Ajout d'un proxy aléatoire si disponible
            if PROXIES:
                proxy = random.choice(PROXIES)
                ydl_opts['proxy'] = proxy
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return info
                
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Tentative {attempt + 1} échouée. Nouvelle tentative dans 2 secondes...")
                time.sleep(2)
            else:
                raise e
    
    return None

# Fonction principale
def main():
    st.title("🎥 YouTube Downloader")
    st.markdown("---")

    # Configuration du dossier de téléchargement
    download_dir = st.text_input("Dossier de téléchargement (optionnel):", value=os.path.expanduser("~/Downloads"))
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Champ de saisie URL
    url = st.text_input("Collez l'URL de la vidéo YouTube ici:")

    if url:
        try:
            # Obtenir les informations de la vidéo avec retry
            info = get_video_info(url)
            
            if not info:
                st.error("Impossible d'obtenir les informations de la vidéo. Vérifiez l'URL.")
                return
            
            # Affichage des informations de la vidéo
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(info.get('thumbnail', ''), width=300)
            
            with col2:
                st.subheader(info.get('title', 'Titre non disponible'))
                st.markdown(f"**Auteur:** {info.get('uploader', 'Auteur inconnu')}")
                st.markdown(f"**Durée:** {datetime.timedelta(seconds=info.get('duration', 0))}")
                st.markdown(f"**Vues:** {info.get('view_count', 'N/A'):,}")
                
                # Options de téléchargement
                st.markdown("### Options de téléchargement")
                download_type = st.radio(
                    "Choisissez le type de téléchargement:",
                    ["Vidéo", "Audio uniquement"]
                )
                
                if download_type == "Vidéo":
                    # Sélection de la qualité
                    formats = [f for f in info.get('formats', []) if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none']
                    if not formats:
                        st.warning("Aucun format vidéo disponible. Essayez une autre vidéo.")
                        return
                    quality_options = {f"{f.get('format_note', 'Qualité inconnue')} ({f.get('filesize', 0) / 1024 / 1024:.1f} MB)": f['format_id'] for f in formats}
                    selected_quality = st.selectbox(
                        "Choisissez la qualité:",
                        options=list(quality_options.keys())
                    )
                    format_id = quality_options[selected_quality]
                else:
                    format_id = 'bestaudio/best'
                
                if st.button("Télécharger"):
                    with st.spinner("Téléchargement en cours..."):
                        try:
                            # Création d'un dossier temporaire
                            with tempfile.TemporaryDirectory() as temp_dir:
                                # Sélection aléatoire d'un User-Agent
                                user_agent = random.choice(USER_AGENTS)
                                
                                ydl_opts = {
                                    'format': format_id,
                                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                                    'progress_hooks': [progress_hook],
                                    'nocheckcertificate': True,
                                    'ignoreerrors': True,
                                    'no_color': True,
                                    'extract_flat': False,
                                    'force_generic_extractor': False,
                                    'geo_bypass': True,
                                    'geo_verification_proxy': None,
                                    'http_headers': {
                                        'User-Agent': user_agent,
                                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                        'Accept-Language': 'en-us,en;q=0.5',
                                        'Sec-Fetch-Mode': 'navigate',
                                        'Sec-Fetch-Site': 'none',
                                        'Sec-Fetch-User': '?1',
                                        'Upgrade-Insecure-Requests': '1',
                                    }
                                }
                                
                                # Ajout d'un proxy aléatoire si disponible
                                if PROXIES:
                                    proxy = random.choice(PROXIES)
                                    ydl_opts['proxy'] = proxy
                                
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    ydl.download([url])
                                
                                # Trouver le fichier téléchargé
                                downloaded_files = os.listdir(temp_dir)
                                if not downloaded_files:
                                    st.error("Aucun fichier n'a été téléchargé. Vérifiez l'URL et réessayez.")
                                    return
                                
                                downloaded_file = downloaded_files[0]
                                download_path = os.path.join(temp_dir, downloaded_file)
                                
                                # Déplacement du fichier vers le dossier de téléchargement
                                final_path = os.path.join(download_dir, downloaded_file)
                                shutil.move(download_path, final_path)
                                
                                # Bouton de téléchargement
                                with open(final_path, 'rb') as f:
                                    st.download_button(
                                        label="Cliquez ici pour télécharger",
                                        data=f,
                                        file_name=downloaded_file,
                                        mime="video/mp4" if download_type == "Vidéo" else "audio/mp4"
                                    )
                        except Exception as e:
                            st.error(f"Erreur lors du téléchargement: {str(e)}")
        
        except Exception as e:
            st.error(f"Une erreur est survenue: {str(e)}")
            st.info("Conseils de dépannage:")
            st.markdown("""
            - Vérifiez que l'URL est correcte
            - Assurez-vous que la vidéo est publique
            - Vérifiez votre connexion internet
            - Essayez une autre vidéo
            - Si l'erreur persiste, essayez de :
              * Vider le cache de votre navigateur
              * Utiliser un VPN
              * Attendre quelques minutes avant de réessayer
              * Essayer une autre URL de la même vidéo
              * Désactiver temporairement votre pare-feu
            """)

if __name__ == "__main__":
    main()