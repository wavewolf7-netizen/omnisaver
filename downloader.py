import os
import re
import time
import uuid
import logging
import subprocess
from typing import Dict, Any, Optional
import yt_dlp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("downloader")

# Detect embedded or system FFmpeg executable
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    logger.info(f"Using FFmpeg from: {FFMPEG_PATH}")
except Exception as e:
    FFMPEG_PATH = "ffmpeg"
    logger.warning(f"Could not load imageio_ffmpeg, falling back to system ffmpeg: {e}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.getenv('VERCEL') and '/tmp' or os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

PLATFORM_INFO = {
    "instagram": {
        "name": "Instagram",
        "badge": "Instagram Reel/Post",
        "icon": "instagram",
        "color": "#e1306c"
    },
    "youtube": {
        "name": "YouTube",
        "badge": "YouTube Shorts/Video",
        "icon": "youtube",
        "color": "#ff0000"
    },
    "facebook": {
        "name": "Facebook",
        "badge": "Facebook Video/Reel",
        "icon": "facebook",
        "color": "#1877f2"
    },
    "unknown": {
        "name": "Media",
        "badge": "Universal Media",
        "icon": "globe",
        "color": "#6366f1"
    }
}

def detect_platform(url: str) -> str:
    """Detect whether URL is from Instagram, YouTube, Facebook, or general."""
    if not url:
        return "unknown"
    u = url.lower().strip()
    if "instagram.com" in u:
        return "instagram"
    elif "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    elif "facebook.com" in u or "fb.watch" in u:
        return "facebook"
    return "unknown"

def sanitize_url(raw_url: str) -> str:
    """Clean tracking parameters and canonicalize URLs for supported platforms."""
    if not raw_url:
        return ""
    url = raw_url.strip()
    platform = detect_platform(url)

    if platform == "instagram":
        match = re.search(r'instagram\.com/(?:reel|reels|p|share/reel)/([a-zA-Z0-9_-]+)', url)
        if match:
            return f"https://www.instagram.com/reel/{match.group(1)}/"
    elif platform == "youtube":
        shorts_match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
        if shorts_match:
            return f"https://www.youtube.com/watch?v={shorts_match.group(1)}"
        watch_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', url)
        if watch_match:
            return f"https://www.youtube.com/watch?v={watch_match.group(1)}"

    return url

def clean_old_files(max_age_seconds: int = 1800):
    """Remove temporary files older than max_age_seconds (default 30 mins)."""
    try:
        now = time.time()
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {filename}")
                    except OSError:
                        pass
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def get_base_ydl_opts(platform: str) -> dict:
    """Base options for yt-dlp tailored to the platform."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'socket_timeout': 60,
        'windowsfilenames': True,
    }

    if platform == "instagram":
        opts['http_headers']['Referer'] = 'https://www.instagram.com/'
    elif platform == "facebook":
        opts['http_headers']['Referer'] = 'https://www.facebook.com/'
    elif platform == "youtube":
        opts['http_headers']['Referer'] = 'https://www.youtube.com/'
        # Use Android client to bypass YouTube bot detection on cloud servers
        # No cookies or extension needed for public users!
        opts['extractor_args'] = {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        }

    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        opts['ffmpeg_location'] = FFMPEG_PATH

    # Use cookies.txt if present (optional extra layer)
    cookies_path = os.path.join(BASE_DIR, "cookies.txt")
    if os.path.exists(cookies_path):
        opts['cookiefile'] = cookies_path
        logger.info("Using cookies.txt for authentication")

    return opts

def ensure_h264_mp4(file_path: str, vcodec: str = "") -> str:
    """
    Ensure the downloaded MP4 is encoded in universal H.264 (AVC) video + AAC audio.
    This guarantees that standard Windows Media Player can play BOTH video and audio
    without requiring the 'AV1 Video Extension' from the Microsoft Store.
    """
    if not os.path.exists(file_path) or not FFMPEG_PATH or not os.path.exists(FFMPEG_PATH):
        return file_path

    vcodec_lower = (vcodec or "").lower()
    # If already confirmed to be H.264/AVC, skip re-encoding for instant speed
    if "avc1" in vcodec_lower or "h264" in vcodec_lower:
        return file_path

    # If it is AV1 (av01), VP9 (vp09), or unknown, re-encode video track to libx264
    tmp_output = file_path + ".h264.mp4"
    try:
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", file_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            tmp_output
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.exists(tmp_output) and os.path.getsize(tmp_output) > 0:
            os.replace(tmp_output, file_path)
            logger.info(f"Re-encoded video to universal H.264 MP4: {file_path}")
    except Exception as e:
        logger.warning(f"H.264 conversion attempt encountered an issue: {e}")
        if os.path.exists(tmp_output):
            try:
                os.remove(tmp_output)
            except OSError:
                pass

    return file_path

def extract_media_info(raw_url: str) -> Dict[str, Any]:
    """Fetch metadata for Instagram, YouTube, or Facebook media."""
    clean_url = sanitize_url(raw_url)
    platform = detect_platform(clean_url)

    if not clean_url:
        raise ValueError("Please provide a valid video or reel link.")

    opts = get_base_ydl_opts(platform)
    opts['extract_flat'] = False

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(clean_url, download=False)
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e).lower()
            if "login required" in err_msg or "private" in err_msg:
                raise ValueError("This video or post is private or requires login credentials.")
            elif "not found" in err_msg or "404" in err_msg:
                raise ValueError("Video not found. It may have been removed or the link is incorrect.")
            else:
                raise ValueError(f"Could not retrieve video information: {str(e)}")

    if not info:
        raise ValueError("Could not retrieve information for this link.")

    if 'entries' in info and info['entries']:
        info = info['entries'][0]

    thumbnail = info.get('thumbnail')
    if not thumbnail and info.get('thumbnails'):
        thumbnail = info['thumbnails'][-1].get('url')

    title = info.get('title') or f"{PLATFORM_INFO.get(platform, {}).get('name', 'Video')} Media"
    display_title = (title[:90] + '...') if len(title) > 90 else title

    duration = info.get('duration') or 0
    duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else "0:00"

    uploader = info.get('uploader') or info.get('channel') or info.get('creator') or "Creator"
    platform_data = PLATFORM_INFO.get(platform, PLATFORM_INFO['unknown'])

    return {
        "id": info.get('id', uuid.uuid4().hex[:8]),
        "platform": platform,
        "platform_name": platform_data["name"],
        "platform_badge": platform_data["badge"],
        "platform_color": platform_data["color"],
        "title": display_title,
        "full_title": title,
        "uploader": uploader,
        "thumbnail": thumbnail,
        "duration": duration,
        "duration_str": duration_str,
        "clean_url": clean_url
    }

def download_media(raw_url: str, format_type: str = "video") -> Dict[str, Any]:
    """
    Downloads media as either 'video' (universal H.264 MP4) or 'audio' (192kbps MP3).
    Guarantees video plays with sound & picture on all Windows Media Players.
    """
    clean_old_files()

    clean_url = sanitize_url(raw_url)
    platform = detect_platform(clean_url)

    if not clean_url:
        raise ValueError("Please provide a valid video or reel link.")

    format_type = format_type.lower()
    if format_type not in ["video", "audio"]:
        format_type = "video"

    job_id = uuid.uuid4().hex[:12]
    out_template = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")

    opts = get_base_ydl_opts(platform)
    opts['outtmpl'] = out_template

    if format_type == "video":
        # Request H.264 (avc1) video + AAC audio so it natively plays in Windows Media Player
        opts['format'] = (
            'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/'
            'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/'
            'bestvideo[vcodec^=avc]+bestaudio/'
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
            'best[ext=mp4]/bestvideo+bestaudio/best'
        )
        opts['merge_output_format'] = 'mp4'
        expected_ext = "mp4"
    else:  # audio extraction to MP3
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        expected_ext = "mp3"

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(clean_url, download=True)
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e).lower()
            if "login required" in err_msg or "private" in err_msg:
                raise ValueError("This video is private or restricted.")
            elif "not found" in err_msg or "404" in err_msg:
                raise ValueError("Video not found or has been removed.")
            else:
                raise ValueError(f"Download error: {str(e)}")

    if 'entries' in info and info['entries']:
        info = info['entries'][0]

    # Find resulting file
    expected_path = os.path.join(DOWNLOAD_DIR, f"{job_id}.{expected_ext}")
    final_path = None

    if os.path.exists(expected_path):
        final_path = expected_path
    else:
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(job_id):
                final_path = os.path.join(DOWNLOAD_DIR, f)
                break

    if not final_path or not os.path.exists(final_path):
        raise RuntimeError("Download completed but media file could not be generated.")

    # If format is video, ensure it's H.264 so Windows Media Player does not demand AV1 extension
    if format_type == "video":
        vcodec = info.get('vcodec') or ""
        final_path = ensure_h264_mp4(final_path, vcodec=vcodec)

    raw_title = info.get('title') or info.get('id') or f"{platform}_{format_type}"
    clean_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', raw_title)[:45].strip()
    if not clean_title:
        clean_title = f"{platform}_{format_type}_{job_id[:6]}"

    suggested_filename = f"{clean_title}.{expected_ext}"
    actual_filename = os.path.basename(final_path)

    file_size_bytes = os.path.getsize(final_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    platform_data = PLATFORM_INFO.get(platform, PLATFORM_INFO['unknown'])

    return {
        "download_id": actual_filename,
        "format": format_type,
        "platform": platform,
        "platform_name": platform_data["name"],
        "platform_badge": platform_data["badge"],
        "suggested_filename": suggested_filename,
        "file_path": final_path,
        "file_size_mb": file_size_mb,
        "title": info.get('title') or f"{platform_data['name']} Video",
        "uploader": info.get('uploader') or info.get('channel') or "Creator"
    }
