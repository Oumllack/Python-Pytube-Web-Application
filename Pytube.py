import streamlit as st
from pytube3 import YouTube
import os
from datetime import datetime
import tempfile
import shutil

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
    st.markdown("Streamlit • pytube3")

# Fonction de progression
def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    st.progress(percentage / 100)

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
            # Création de l'objet YouTube avec le callback de progression
            yt = YouTube(url, on_progress_callback=progress_callback)
            
            # Affichage des informations de la vidéo
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(yt.thumbnail_url, width=300)
            
            with col2:
                st.subheader(yt.title)
                st.markdown(f"**Auteur:** {yt.author}")
                st.markdown(f"**Durée:** {datetime.timedelta(seconds=yt.length)}")
                st.markdown(f"**Vues:** {yt.views:,}")
                
                # Options de téléchargement
                st.markdown("### Options de téléchargement")
                download_type = st.radio(
                    "Choisissez le type de téléchargement:",
                    ["Vidéo", "Audio uniquement"]
                )
                
                if download_type == "Vidéo":
                    # Sélection de la qualité
                    streams = yt.streams.filter(progressive=True)
                    if not streams:
                        st.warning("Aucun flux vidéo disponible. Essayez une autre vidéo.")
                        return
                    quality_options = {f"{s.resolution} ({s.filesize_mb:.1f} MB)": s for s in streams}
                    selected_quality = st.selectbox(
                        "Choisissez la qualité:",
                        options=list(quality_options.keys())
                    )
                    stream = quality_options[selected_quality]
                else:
                    # Téléchargement audio
                    stream = yt.streams.get_audio_only()
                    if not stream:
                        st.warning("Aucun flux audio disponible. Essayez une autre vidéo.")
                        return
                
                if st.button("Télécharger"):
                    with st.spinner("Téléchargement en cours..."):
                        try:
                            # Création d'un dossier temporaire
                            with tempfile.TemporaryDirectory() as temp_dir:
                                download_path = stream.download(output_path=temp_dir)
                                st.success("Téléchargement terminé!")
                                
                                # Déplacement du fichier vers le dossier de téléchargement
                                final_path = os.path.join(download_dir, os.path.basename(download_path))
                                shutil.move(download_path, final_path)
                                
                                # Bouton de téléchargement
                                with open(final_path, 'rb') as f:
                                    st.download_button(
                                        label="Cliquez ici pour télécharger",
                                        data=f,
                                        file_name=os.path.basename(final_path),
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
            """)

if __name__ == "__main__":
    main()