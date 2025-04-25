import streamlit as st
from pytube import YouTube
import os
from datetime import timedelta
import re
import time

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

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return bool(re.match(youtube_regex, url))

def get_video_info(url):
    try:
        yt = YouTube(url)
        return yt
    except Exception as e:
        raise Exception(f"Error getting video info: {str(e)}")

# Main function
def main():
    st.title("🎥 YouTube Downloader")
    st.markdown("---")

    # URL input
    url = st.text_input("Paste YouTube video URL here:")

    if url:
        if not is_valid_youtube_url(url):
            st.error("Please enter a valid YouTube URL")
            return

        try:
            with st.spinner("Connecting to YouTube..."):
                yt = get_video_info(url)
                
                # Display video information
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(yt.thumbnail_url, width=300)
                
                with col2:
                    st.subheader(yt.title)
                    st.markdown(f"**Author:** {yt.author}")
                    st.markdown(f"**Duration:** {timedelta(seconds=yt.length)}")
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
                        if not streams:
                            st.error("No video streams available for this video")
                            return
                            
                        quality_options = {f"{s.resolution} ({s.filesize_mb:.1f} MB)": s for s in streams}
                        selected_quality = st.selectbox(
                            "Choose quality:",
                            options=list(quality_options.keys())
                        )
                        stream = quality_options[selected_quality]
                    else:
                        # Audio download
                        stream = yt.streams.get_audio_only()
                        if not stream:
                            st.error("No audio stream available for this video")
                            return
                    
                    if st.button("Download"):
                        try:
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
                        except Exception as download_error:
                            st.error(f"Error during download: {str(download_error)}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("If you're seeing an error, please try again in a few minutes.")

if __name__ == "__main__":
    main() 