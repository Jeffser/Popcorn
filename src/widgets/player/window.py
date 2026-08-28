# window.py

from gi.repository import Gtk, Adw, GLib, Gst
from ..player import PlayerPage

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/window.ui')
class PlayerWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PopcornPictureInPictureWindow'

    player_page = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_close(self, window):
        if app := self.get_application():
            app.main_window.root_navigationview.push(PlayerPage(
                player=app.get_property('player')
            ))
            app.main_window.present()
