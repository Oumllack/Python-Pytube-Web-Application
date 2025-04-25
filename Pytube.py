import streamlit as st
from pytube import YouTube
import os
from datetime import datetime

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
    st.markdown("Streamlit • Pytube")

# Fonction principale
def main():
    st.title("🎥 YouTube Downloader")
    st.markdown("---")

    # Champ de saisie URL
    url = st.text_input("Collez l'URL de la vidéo YouTube ici:")

    if url:
        try:
            yt = YouTube(url)
            
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
                    quality_options = {f"{s.resolution} ({s.filesize_mb:.1f} MB)": s for s in streams}
                    selected_quality = st.selectbox(
                        "Choisissez la qualité:",
                        options=list(quality_options.keys())
                    )
                    stream = quality_options[selected_quality]
                else:
                    # Téléchargement audio
                    stream = yt.streams.get_audio_only()
                
                if st.button("Télécharger"):
                    with st.spinner("Téléchargement en cours..."):
                        download_path = stream.download()
                        st.success("Téléchargement terminé!")
                        
                        # Bouton de téléchargement
                        with open(download_path, 'rb') as f:
                            st.download_button(
                                label="Cliquez ici pour télécharger",
                                data=f,
                                file_name=os.path.basename(download_path),
                                mime="video/mp4" if download_type == "Vidéo" else "audio/mp4"
                            )
                        
                        # Supprimer le fichier temporaire
                        os.remove(download_path)
        
        except Exception as e:
            st.error(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    main()