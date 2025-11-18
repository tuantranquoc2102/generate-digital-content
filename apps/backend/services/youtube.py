import os
import re
import yt_dlp
import tempfile
from typing import Tuple

def sanitize_filename(title: str) -> str:
    """Bỏ dấu, bỏ ký tự đặc biệt, chỉ giữ lại chữ cái, số và gạch dưới"""
    return re.sub(r'[^a-zA-Z0-9_]', '_', title)

def download_youtube_audio(youtube_url: str) -> Tuple[str, str]:
    """
    Download audio từ YouTube URL
    Returns: (audio_file_path, video_title)
    """
    # Tạo temp directory
    temp_dir = tempfile.mkdtemp(prefix="youtube_audio_")
    output_template = os.path.join(temp_dir, '%(title).50s.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best[ext=mp4]/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        # Enhanced anti-bot measures
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        },
        'extractor_retries': 5,
        'fragment_retries': 5,
        'retries': 5,
        'file_access_retries': 3,
        'sleep_interval_requests': 2,
        'sleep_interval': 2,
        'max_sleep_interval': 10,
        # Additional bypass options
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'extract_flat': False,
        'simulate': False,
        'skip_download': False,
        'writethumbnail': False,
        'writeinfojson': False,
        'writeautomaticsub': False,
        'writesubtitles': False,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        title = info_dict.get("title", "unknown_title")

    # Tìm file mp3 vừa tạo
    files = [f for f in os.listdir(temp_dir) if f.endswith(".mp3")]
    if not files:
        raise FileNotFoundError("Không tìm thấy file mp3 nào sau khi tải.")

    # Lấy file mới nhất
    files.sort(key=lambda f: os.path.getmtime(os.path.join(temp_dir, f)), reverse=True)
    mp3_file_path = os.path.join(temp_dir, files[0])
    
    print(f"✅ Đã tải file audio từ YouTube: {mp3_file_path}")
    return mp3_file_path, title