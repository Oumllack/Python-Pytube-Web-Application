import streamlit as st
import yt_dlp
import os
from datetime import datetime
import re
import time
import random

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
    st.markdown("Streamlit • yt-dlp")

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return bool(re.match(youtube_regex, url))

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'geo_bypass': True,
        'geo_verification_proxy': None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'skip_download': True,
        'proxy': 'socks5://127.0.0.1:9050',  # Using Tor proxy
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("Could not extract video information")
            return info
        except Exception as e:
            raise Exception(f"Error getting video info: {str(e)}")

def download_video(url, format_type, quality=None):
    ydl_opts = {
        'format': 'best' if format_type == 'audio' else f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]' if quality else 'best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'geo_bypass': True,
        'geo_verification_proxy': None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'proxy': 'socks5://127.0.0.1:9050',  # Using Tor proxy
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Could not download video")
            return f"{info['title']}.{info['ext']}"
        except Exception as e:
            raise Exception(f"Error downloading video: {str(e)}")

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
                info = get_video_info(url)
                
                # Display video information
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(info.get('thumbnail', ''), width=300)
                
                with col2:
                    st.subheader(info.get('title', 'Unknown Title'))
                    st.markdown(f"**Author:** {info.get('uploader', 'Unknown')}")
                    st.markdown(f"**Duration:** {datetime.timedelta(seconds=info.get('duration', 0))}")
                    st.markdown(f"**Views:** {info.get('view_count', 0):,}")
                    
                    # Download options
                    st.markdown("### Download Options")
                    download_type = st.radio(
                        "Choose download type:",
                        ["Video", "Audio only"]
                    )
                    
                    if download_type == "Video":
                        # Quality selection
                        quality = st.selectbox(
                            "Choose quality:",
                            ["720p", "480p", "360p", "240p", "144p"]
                        )
                        quality = int(quality.replace('p', ''))
                    else:
                        quality = None
                    
                    if st.button("Download"):
                        try:
                            with st.spinner("Downloading..."):
                                download_path = download_video(url, download_type.lower(), quality)
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