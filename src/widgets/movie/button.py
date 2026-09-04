# button.py
from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models
from ..misc.context import ContextMenu, ContextMenuRow, show_context_menu


@Gtk.Template(resource_path='/com/jeffser/Popcorn/movie/button.ui')
class MovieButton(Gtk.Box):
    __gtype_name__ = 'PopcornMovieButton'
    model = GObject.Property(type=models.Movie)
    is_tall = GObject.Property(type=bool, default=False)

    @Gtk.Template.Callback()
    def format_paintable(self, obj, is_tall: bool, wide_paintable, tall_paintable) -> Gdk.Paintable:
        return tall_paintable if is_tall else wide_paintable
    @Gtk.Template.Callback()
    def format_progressbar_visible(self, obj, progress: float) -> bool:
        return 0 < progress < 1
    @Gtk.Template.Callback()
    def format_picture_height(self, obj, is_tall: bool) -> int:
        return 360 if is_tall else 240
    @Gtk.Template.Callback()
    def format_picture_width(self, obj, is_tall: bool) -> int:
        return 220 if is_tall else 420

    def build_context_menu(self) -> ContextMenu:
        model = self.model
        menu = ContextMenu()

        play_row = ContextMenuRow(
            title=_("Resume Movie") if model.get_property('Progress') > 0 else _("Play Movie"),
            icon_name="media-playback-start-symbolic",
        )
        play_row.connect('activated', lambda *_: self.activate_action(
            'app.play_movie', GLib.Variant('s', model.get_property('Id'))
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

    def show_context_menu(self, x: float, y: float):
        menu = self.build_context_menu()
        menu.set_parent(self)
        menu.set_pointing_to(Gdk.Rectangle(x=int(x), y=int(y), width=1, height=1))
        menu.connect('closed', lambda popover: popover.unparent())
        menu.popup()

    @Gtk.Template.Callback()
    def on_secondary_click(self, gesture, n_press, x, y):
        show_context_menu(self, self.build_context_menu(), x, y)

    @Gtk.Template.Callback()
    def on_long_press(self, gesture, x, y):
        show_context_menu(self, self.build_context_menu(), x, y)
