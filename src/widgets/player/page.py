# page.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from ...integrations import models
from .player import Player

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/page.ui')
class PlayerPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornPlayerPage'

    player = GObject.Property(type=Player)

    def reset(self):
        pass
