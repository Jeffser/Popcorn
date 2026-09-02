# window.py

from gi.repository import Gtk, Adw, GLib, Gst
from ..player import PlayerPage

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/window.ui')
class PlayerWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PopcornPictureInPictureWindow'

    player_page = Gtk.Template.Child()
    window_handle = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        model = self.window_handle.observe_controllers()
        for i in range(model.get_n_items()):
            controller = model.get_item(i)
            if isinstance(controller, Gtk.GestureClick):
                self.window_handle.remove_controller(controller)

    @Gtk.Template.Callback()
    def on_close(self, window):
        if app := self.get_application():
            app.main_window.root_navigationview.push(PlayerPage(
                player=app.get_property('player')
            ))
            app.main_window.present()

    @Gtk.Template.Callback()
    def on_key_pressed(self, controller, keyval, keycode, modifier):
        if keycode == 111: #UP
            self.player_page.activate_action('player.change-volume', GLib.Variant('d', 0.1))
            return True
        elif keycode == 116: #DOWN
            self.player_page.activate_action('player.change-volume', GLib.Variant('d', -0.1))
            return True
        elif keycode == 114: #RIGHT
            self.player_page.activate_action('player.seek', GLib.Variant('i', 10))
            return True
        elif keycode == 113: #LEFT
            self.player_page.activate_action('player.seek', GLib.Variant('i', -10))
            return True
        elif keycode == 65: #SPACE
            self.player_page.activate_action('player.toggle-playback', None)
            return True
