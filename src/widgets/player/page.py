# page.py

from gi.repository import Gtk, Adw, GLib, GObject, Gst
from ...integrations import models
from .player import Player
from ...constants import get_future_time, format_time_display

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/page.ui')
class PlayerPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornPlayerPage'

    player = GObject.Property(type=Player)
    end_time = GObject.Property(type=str)
    scale_seeking = GObject.Property(type=bool, default=False)
    position = GObject.Property(type=float)
    toolbarview = Gtk.Template.Child()
    controls_revealer = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_end_time()
        GLib.timeout_add(60000, self.update_end_time)
        GLib.timeout_add(64, self.update_position)
        self.hide_timeout_id = None
        self.last_motion_coordinates = [0,0]
        self.connect('notify::root', self.on_root_changed)

    def on_root_changed(self, widget, pspec):
        if widget.get_property(pspec.name) is None:
            if player := self.get_property('player'):
                if app := player.get_property('application'):
                    if not app.pip_window.get_visible():
                        player.get_property('gst').set_state(Gst.State.NULL)

    def reset(self):
        pass

    def update_end_time(self):
        if player := self.get_property('player'):
            if model := player.get_property('model'):
                duration = model.get_property('Duration')
                self.set_property('end-time', _("Ends at {}").format(get_future_time(duration-self.get_property('position'))))
        return True

    def update_position(self):
        if not self.get_property('scale_seeking'):
            self.set_property('position', self.get_property('player').get_property('position'))
        return True

    @Gtk.Template.Callback()
    def format_time_ellapsed(self, obj, position:float, duration:float) -> str:
        return format_time_display(position, duration > 3600)

    @Gtk.Template.Callback()
    def format_time_remaining(self, obj, position:float, duration:float) -> str:
        return format_time_display(duration-position, duration > 3600)

    @Gtk.Template.Callback()
    def adjustment_changed(self, adjustment):
        if self.get_property('scale_seeking'):
            self.set_property('position', adjustment.get_value())

    @Gtk.Template.Callback()
    def scale_pressed(self, *args):
        self.set_property('scale_seeking', True)

    @Gtk.Template.Callback()
    def scale_released(self, *args):
        self.get_property('player').get_property('gst').seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            int(self.get_property('position') * Gst.SECOND)
        )
        GLib.timeout_add(500, self.set_property, 'scale_seeking', False)
        GLib.timeout_add(500, lambda: self.update_end_time() and False)

    @Gtk.Template.Callback()
    def fullscreen_toggled(self, button, pspec):
        if button.get_property(pspec.name):
            self.get_root().fullscreen()
        else:
            self.get_root().unfullscreen()

    def toggle_controls(self, visible:bool):
        self.toolbarview.set_reveal_top_bars(visible)
        self.controls_revealer.set_reveal_child(visible)
        if root := self.get_root():
            root.set_cursor_from_name(None if visible else "none")
        if not visible and self.hide_timeout_id:
            self.hide_timeout_id = None

    @Gtk.Template.Callback()
    def on_pointer_motion(self, controller, x, y):
        if self.last_motion_coordinates != [x, y]:
            self.last_motion_coordinates = [x, y]
            self.toggle_controls(True)
            if self.hide_timeout_id is not None:
                GLib.source_remove(self.hide_timeout_id)
                self.hide_timeout_id = None
            self.hide_timeout_id = GLib.timeout_add(3000, self.toggle_controls, False)

    @Gtk.Template.Callback()
    def format_pip_button_visible(self, obj, window_title:str) -> bool:
        return window_title != 'Picture-in-Picture'

    @Gtk.Template.Callback()
    def open_pip_window(self, button):
        if root := self.get_root():
            if app := root.get_application():
                if navigationview := self.get_ancestor(Adw.NavigationView):
                    if window := app.pip_window:
                        window.present()
                    navigationview.pop()
                    root.unfullscreen()


