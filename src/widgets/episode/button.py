# button.py
from gi.repository import Gtk, GLib, Gdk, GObject
from gettext import gettext as _
from ...integrations import models
from ...constants import format_duration_display, get_future_time
from ..misc.context import ContextMenu, ContextMenuRow, show_context_menu


@Gtk.Template(resource_path='/com/jeffser/Popcorn/episode/button.ui')
class EpisodeButton(Gtk.Box):
    __gtype_name__ = 'PopcornEpisodeButton'

    model = GObject.Property(type=models.Episode)
    is_tall = GObject.Property(type=bool, default=False)
    mode = GObject.Property(type=str, default='simple')

    @Gtk.Template.Callback()
    def format_subtitle(self, obj, season, episode, episode_name) -> str:
        return "<b>{}</b> | {}".format(_("S{} E{}").format(season, episode), GLib.markup_escape_text(episode_name))

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def format_progressbar_visible(self, obj, progress: float) -> bool:
        return 0 < progress < 1

    @Gtk.Template.Callback()
    def format_paintable(self, obj, is_tall: bool, primary, series_primary, series_backdrop) -> Gdk.Paintable:
        return series_primary if is_tall else (primary or series_backdrop)

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_picture_height(self, obj, is_tall: bool) -> int:
        return 360 if is_tall else 240

    @Gtk.Template.Callback()
    def format_picture_width(self, obj, is_tall: bool) -> int:
        return 220 if is_tall else 400

    @Gtk.Template.Callback()
    def format_name_number(self, obj, name: str, number: int) -> str:
        return "{}. {}".format(number, name)

    @Gtk.Template.Callback()
    def format_duration(self, obj, duration: float) -> str:
        return format_duration_display(duration)

    @Gtk.Template.Callback()
    def format_one_decimal(self, obj, value) -> str:
        return f"{value:.1f}"

    @Gtk.Template.Callback()
    def format_end_time(self, obj, duration: float) -> str:
        return _("Ends at {}").format(get_future_time(duration))

    @Gtk.Template.Callback()
    def format_heart_icon_name(self, obj, isFavorite: bool) -> str:
        return "heart-filled-symbolic" if isFavorite else "heart-outline-thick-symbolic"

    @Gtk.Template.Callback()
    def format_play_button_label(self, obj, progress: float):
        return _("Resume Episode") if progress > 0 else _("Play Episode")

    def build_context_menu(self) -> ContextMenu:
        model = self.model
        menu = ContextMenu()

        play_row = ContextMenuRow(
            title=_("Resume Episode") if model.get_property('Progress') > 0 else _("Play Episode"),
            icon_name="media-playback-start-symbolic",
        )
        play_row.connect('activated', lambda *_: self.activate_action(
            'app.play_episode', GLib.Variant('s', model.get_property('Id'))
        ))
        menu.add_row(play_row)

        played_row = ContextMenuRow(
            title=_("Mark as Unwatched") if model.get_property('Played') else _("Mark as Watched"),
            icon_name="check-plain-symbolic",
        )
        played_row.connect('activated', lambda *_: self.activate_action(
            'app.toggle_played', GLib.Variant('s', model.get_property('Id'))
        ))
        menu.add_row(played_row)

        favorite_row = ContextMenuRow(
            title=_("Remove from Favorites") if model.get_property('IsFavorite') else _("Add to Favorites"),
            icon_name="heart-filled-symbolic" if model.get_property('IsFavorite') else "heart-outline-thick-symbolic",
        )
        favorite_row.connect('activated', lambda *_: self.activate_action(
            'app.toggle_favorite', GLib.Variant('s', model.get_property('Id'))
        ))
        menu.add_row(favorite_row)

        return menu

    @Gtk.Template.Callback()
    def on_secondary_click(self, gesture, n_press, x, y):
        show_context_menu(self, self.build_context_menu(), x, y)

    @Gtk.Template.Callback()
    def on_long_press(self, gesture, x, y):
        show_context_menu(self, self.build_context_menu(), x, y)
