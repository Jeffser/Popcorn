# button.py

from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/button.ui')
class SeriesButton(Gtk.Box):
    __gtype_name__ = 'PopcornSeriesButton'

    model = GObject.Property(type=models.Series)
    is_tall = GObject.Property(type=bool, default=False)

    @Gtk.Template.Callback()
    def format_paintable(self, obj, is_tall:bool, wide_paintable, tall_paintable) -> Gdk.Paintable:
        return tall_paintable if is_tall else wide_paintable

    @Gtk.Template.Callback()
    def format_paintable_height(self, obj, is_tall:bool) -> int:
        return 360 if is_tall else 280

