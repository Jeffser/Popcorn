# button.py

from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/season/button.ui')
class SeasonButton(Gtk.Box):
    __gtype_name__ = 'PopcornSeasonButton'

    model = GObject.Property(type=models.Season)

    @Gtk.Template.Callback()
    def format_action_target(self, obj, series_id:str, season_id:str) -> GLib.Variant:
        return GLib.Variant('a{ss}', {
            'series': series_id,
            'season': season_id
        })
