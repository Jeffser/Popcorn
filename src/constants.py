# constants.py

import os

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
