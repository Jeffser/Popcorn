# button.py

from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/episode/button.ui')
class EpisodeButton(Gtk.Box):
    __gtype_name__ = 'PopcornEpisodeButton'

    model = GObject.Property(type=models.Episode)
    is_tall = GObject.Property(type=bool, default=False)

    @Gtk.Template.Callback()
    def format_subtitle(self, obj, season, episode, episode_name) -> str:
        return "<b>{}</b> | {}".format(_("S{} E{}").format(season, episode), GLib.markup_escape_text(episode_name))

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def format_paintable(self, obj, is_tall:bool, primary, series_primary, series_backdrop) -> Gdk.Paintable:
        return series_primary if is_tall else (primary or series_backdrop)

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_picture_height(self, obj, is_tall:bool) -> int:
        return 360 if is_tall else 240

    @Gtk.Template.Callback()
    def format_picture_width(self, obj, is_tall:bool) -> int:
        return 220 if is_tall else 420
