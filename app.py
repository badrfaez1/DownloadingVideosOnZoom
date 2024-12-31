import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import io

st.set_page_config(
    page_title="Zoom Video Downloader",
    page_icon="🎥",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
    }
    .main {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .stTitle {
        color: #ffffff;
        font-size: 2.5rem !important;
        margin-bottom: 2rem !important;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #4a90e2;
        color: white;
        padding: 0.8rem 1rem;
        font-size: 1.1rem;
        border-radius: 5px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357abd;
        transform: translateY(-2px);
    }
    .instructions {
        background-color: #2d2d2d;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #404040;
        margin-bottom: 2rem;
    }
    .instructions h4 {
        color: #4a90e2;
        margin-top: 0;
    }
    .stTextInput>div>div {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
    }
    .stTextInput>div>div:focus-within {
        border-color: #4a90e2 !important;
    }
    .status-container {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def init_webdriver():
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def download_zoom_video(url):
    driver = init_webdriver()
    try:
        with st.status("📥 Download Progress", expanded=True) as status:
            status.write("🌐 Initializing browser...")
            driver.get(url)
            time.sleep(5)

            status.write("🔍 Locating video...")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "vjs_video_3_html5_api"))
            )

            video_element = driver.find_element(By.ID, "vjs_video_3_html5_api")
            video_url = video_element.get_attribute("src")

            if not video_url or ".mp4" not in video_url:
                return None, "No valid video URL found"

            status.write("🔄 Setting up download...")
            cookies = driver.get_cookies()
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            headers = {
                "User-Agent": driver.execute_script("return navigator.userAgent"),
                "Referer": driver.current_url
            }

            status.write("⬇️ Downloading video...")
            response = session.get(video_url, headers=headers, stream=True)

            return (response.content, None) if response.status_code == 200 else (None, f"Download failed with status code: {response.status_code}")

    except Exception as e:
        return None, str(e)
    finally:
        driver.quit()

st.markdown("<h1 class='stTitle'>🎥 Zoom Video Downloader</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class='instructions'>
        <h4>Quick Guide:</h4>
        <ol style='color: #ffffff; margin-bottom: 0;'>
            <li>Paste your Zoom video URL</li>
            <li>Click Download</li>
            <li>Wait for processing</li>
            <li>Save your video</li>
        </ol>
    </div>
""", unsafe_allow_html=True)

url = st.text_input("", placeholder="Enter Zoom video URL here...")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("📥 Download Video"):
        if url:
            video_content, error = download_zoom_video(url)

            if video_content:
                st.success("✅ Download complete!")
                st.download_button(
                    label="💾 Save Video",
                    data=video_content,
                    file_name="zoom_recording.mp4",
                    mime="video/mp4",
                )
            else:
                st.error(f"❌ {error}")
        else:
            st.warning("⚠️ Please enter a URL")