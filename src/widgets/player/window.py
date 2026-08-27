# window.py

from gi.repository import Gtk, Adw, GLib, Gst

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/window.ui')
class PlayerWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PopcornPictureInPictureWindow'

    player_page = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_close(self, window):
        if player := self.player_page.get_property('player'):
            player.get_property('gst').set_state(Gst.State.NULL)
