# episode.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/episode.ui')
class Episode(Gtk.Button):
    __gtype_name__ = 'PopcornSeriesEpisode'

    model = GObject.Property(type=models.Episode)

    @Gtk.Template.Callback()
    def format_subtitle(self, obj, season, episode) -> str:
        return _("S{} E{}").format(season, episode)
        
