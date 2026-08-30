# constants.py

import os, re
from datetime import datetime, timedelta

IN_FLATPAK = bool(os.getenv("FLATPAK_ID"))

def get_xdg_home(env: str, default: str) -> str:
    base = os.getenv(env) or os.path.expanduser(default)
    if IN_FLATPAK:
        return base
    path = os.path.join(base, "com.jeffser.Popcorn")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

DATA_DIR = get_xdg_home("XDG_DATA_HOME", "~/.local/share")
CONFIG_DIR = get_xdg_home("XDG_CONFIG_HOME", "~/.config")
CACHE_DIR = get_xdg_home("XDG_CACHE_HOME", "~/.cache")
FALLBACK_PASSWORD_PATH = os.path.join(CONFIG_DIR, 'pass.txt')

USERVIEWS_ICONS = {
    'movies': 'video-clip-symbolic',
    'tvshows': 'tv-symbolic'
}

SECTION_NAMES = { # For translations
    'Intro': _("Intro"),
    'Outro': _("Outro")
}

def format_duration_display(seconds:float) -> str:
    if seconds < 60:
        return f"{round(seconds)}s"
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    minutes = minutes % 60
    if minutes == 0:
        return f"{hours}h"
    return f"{hours}h {minutes}m"

def get_future_time(seconds:float) -> str:
    future_time = datetime.now() + timedelta(seconds=seconds)
    #TODO check if system format asks for 24h or 12h time
    if True:
        return future_time.strftime("%H:%M")
    else:
        return future_time.strftime("%I:%M %p")

def format_time_display(total_seconds:float, force_include_hours:bool) -> str:
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    if hours > 0 or force_include_hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def subtitle_timestamp_to_position(ts:str) -> float:
    return sum(float(p) * (60 ** i) for i, p in enumerate(reversed(ts.split(':'))))

def subtitle_text_to_pango(line:str) -> str:
    if not line:
        return ""

    def replace_font(match):
        attrs = match.group(1)
        content = match.group(2)

        color_match = re.search(r'color=["\']?([^"\'>\s]+)["\']?', attrs, re.IGNORECASE)
        face_match = re.search(r'face=["\']?([^"\'>\s]+)["\']?', attrs, re.IGNORECASE)

        span_attrs = []
        if color_match:
            span_attrs.append(f'foreground="{color_match.group(1)}"')
        if face_match:
            span_attrs.append(f'face="{face_match.group(1)}"')

        attr_str = " ".join(span_attrs)
        if attr_str:
            return f'<span {attr_str}>{content}</span>'
        return content

    line = re.sub(r'<font\s+([^>]+)>(.*?)</font>', replace_font, line, flags=re.DOTALL)
    # Also handle malformed/mismatched WebVTT closing tags like </c> for a <font> open tag
    line = re.sub(r'<font\s+([^>]+)>(.*?)</c>', replace_font, line, flags=re.DOTALL)

    line = re.sub(r'<v\s+([^>]+)>(.*?)</v>', r'<b>\1:</b> \2', line, flags=re.DOTALL)
    line = re.sub(r'</?v[^>]*>', '', line)

    def replace_ruby(match):
        base = match.group(1)
        rt = match.group(2)
        return f"{base} (<i>{rt}</i>)"

    line = re.sub(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>', replace_ruby, line, flags=re.DOTALL)
    line = re.sub(r'</?(?:ruby|rt)>', '', line)

    line = re.sub(r'<c\.[\w-]+>(.*?)</c>', r'\1', line, flags=re.DOTALL)
    line = re.sub(r'<c>(.*?)</c>', r'\1', line, flags=re.DOTALL)
    line = re.sub(r'</?c[^>]*>', '', line)

    return line
