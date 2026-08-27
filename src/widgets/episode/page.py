# page.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from ...integrations import models
from ..episode import EpisodeButton

@Gtk.Template(resource_path='/com/jeffser/Popcorn/episode/page.ui')
class EpisodePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornEpisodePage'

    model = GObject.Property(type=models.Episode)
    series_model = GObject.Property(type=models.Series)
    top_overlay = Gtk.Template.Child()
    top_overlay_content = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.top_overlay.set_measure_overlay(self.top_overlay_content, True)

    def reset(self):
        pass

    @Gtk.Template.Callback()
    def format_name_number(self, obj, name:str, season_number:int, episode_number:int) -> str:
        return "{} - {}. {}".format(_('Season {}').format(season_number), episode_number, name)

