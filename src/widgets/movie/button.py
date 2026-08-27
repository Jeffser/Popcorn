# button.py

from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/movie/button.ui')
class MovieButton(Gtk.Box):
    __gtype_name__ = 'PopcornMovieButton'

    model = GObject.Property(type=models.Movie)
    is_tall = GObject.Property(type=bool, default=False)

    @Gtk.Template.Callback()
    def format_paintable(self, obj, is_tall:bool, wide_paintable, tall_paintable) -> Gdk.Paintable:
        return tall_paintable if is_tall else wide_paintable

