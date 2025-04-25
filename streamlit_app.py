import streamlit as st
from pytube import YouTube
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    st.markdown("### About")
    st.markdown("""
    This application allows you to:
    - Download YouTube videos
    - Choose video quality
    - Download audio only
    - View video information
    """)
    st.markdown("---")
    st.markdown("### Made with ❤️")
    st.markdown("Streamlit • Pytube")

# Main function
def main():
    st.title("🎥 YouTube Downloader")
    st.markdown("---")

    # URL input
    url = st.text_input("Paste YouTube video URL here:")

    if url:
        try:
            yt = YouTube(url)
            
            # Display video information
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(yt.thumbnail_url, width=300)
            
            with col2:
                st.subheader(yt.title)
                st.markdown(f"**Author:** {yt.author}")
                st.markdown(f"**Duration:** {datetime.timedelta(seconds=yt.length)}")
                st.markdown(f"**Views:** {yt.views:,}")
                
                # Download options
                st.markdown("### Download Options")
                download_type = st.radio(
                    "Choose download type:",
                    ["Video", "Audio only"]
                )
                
                if download_type == "Video":
                    # Quality selection
                    streams = yt.streams.filter(progressive=True)
                    quality_options = {f"{s.resolution} ({s.filesize_mb:.1f} MB)": s for s in streams}
                    selected_quality = st.selectbox(
                        "Choose quality:",
                        options=list(quality_options.keys())
                    )
                    stream = quality_options[selected_quality]
                else:
                    # Audio download
                    stream = yt.streams.get_audio_only()
                
                if st.button("Download"):
                    with st.spinner("Downloading..."):
                        download_path = stream.download()
                        st.success("Download complete!")
                        
                        # Download button
                        with open(download_path, 'rb') as f:
                            st.download_button(
                                label="Click here to download",
                                data=f,
                                file_name=os.path.basename(download_path),
                                mime="video/mp4" if download_type == "Video" else "audio/mp4"
                            )
                        
                        # Clean up temporary file
                        os.remove(download_path)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 