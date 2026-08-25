# episode.py

from gi.repository import Gtk, GLib, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/episode.ui')
class Episode(Gtk.Button):
    __gtype_name__ = 'PopcornSeriesEpisode'

    model = GObject.Property(type=models.Episode)

    @Gtk.Template.Callback()
    def format_subtitle(self, obj, season, episode, episode_name) -> str:
        return "<b>{}</b> | {}".format(_("S{} E{}").format(season, episode), GLib.markup_escape_text(episode_name))
        
