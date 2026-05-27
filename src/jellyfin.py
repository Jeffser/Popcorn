# jellyfin.py

from gi.repository import Gtk, GLib, GObject, Gdk
from . import models, secret

# Just so that the logs don't get cluttered with warnings if trust-server = True
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
