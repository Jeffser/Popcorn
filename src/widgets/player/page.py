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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_end_time()
        GLib.timeout_add(60000, self.update_end_time)
        GLib.timeout_add(64, self.update_position)

    def reset(self):
        pass

    def update_end_time(self):
        if model := self.get_property('player').get_property('model'):
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
