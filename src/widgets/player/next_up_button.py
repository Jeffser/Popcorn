# next_up_button.py

from gi.repository import Gtk, Adw, GLib, GObject, Gst, Gio
from ...integrations import models
from .player import Player
from ...constants import get_future_time, format_time_display, SECTION_NAMES

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/next_up_button.ui')
class NextUpButton(Gtk.Button):
    __gtype_name__ = 'PopcornNextUpButton'

    model = GObject.Property(type=models.Playable)

    @Gtk.Template.Callback()
    def format_title(self, obj, model:models.Playable, title:str, subtitle:str) -> str:
        if isinstance(model, models.Episode):
            return subtitle
        return title

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_action_name(self, obj, model) -> str:
        if isinstance(model, models.Episode):
            return "app.play_episode"
        elif isinstance(model, models.Movie):
            return "app.play_movie"
        return ""
                        
