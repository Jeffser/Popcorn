# button.py
from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models
from ..misc.context import ContextMenu, ContextMenuRow, show_context_menu


@Gtk.Template(resource_path='/com/jeffser/Popcorn/season/button.ui')
class SeasonButton(Gtk.Box):
    __gtype_name__ = 'PopcornSeasonButton'
    model = GObject.Property(type=models.Season)

    def build_context_menu(self) -> ContextMenu:
        model = self.model
        menu = ContextMenu()

        play_row = ContextMenuRow(title=_("Play Season"), icon_name="media-playback-start-symbolic")
        play_row.connect('activated', lambda *_: self.activate_action(
            'app.play_season', GLib.Variant('s', model.get_property('Id'))
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
