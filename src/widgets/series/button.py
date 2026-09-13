# button.py
from gi.repository import Gtk, GLib, Gdk, GObject
from ...integrations import models
from ...constants import BUTTON_WIDE_SIZES, BUTTON_TALL_SIZES

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/button.ui')
class SeriesButton(Gtk.Button):
    __gtype_name__ = 'PopcornSeriesButton'

    model = GObject.Property(type=models.Series)
    is_tall = GObject.Property(type=bool, default=False)
    context_popover = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def format_paintable(self, obj, is_tall: bool, wide_paintable, tall_paintable) -> Gdk.Paintable:
        return tall_paintable if is_tall else wide_paintable

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_picture_height(self, obj, is_tall:bool) -> int:
        return BUTTON_TALL_SIZES[1] if is_tall else BUTTON_WIDE_SIZES[1]

    @Gtk.Template.Callback()
    def format_picture_width(self, obj, is_tall:bool) -> int:
        return BUTTON_TALL_SIZES[0] if is_tall else BUTTON_WIDE_SIZES[0]

    @Gtk.Template.Callback()
    def format_watched_label(self, obj, played:bool):
        return _("Mark as Unwatched") if played else _("Mark as Watched")

    @Gtk.Template.Callback()
    def format_heart_label(self, obj, is_favorite:bool):
        return _("Remove from Favorites") if is_favorite else _("Add to Favorites")

    @Gtk.Template.Callback()
    def format_heart_icon_name(self, obj, isFavorite: bool) -> str:
        return "heart-filled-symbolic" if isFavorite else "heart-outline-thick-symbolic"

    @Gtk.Template.Callback()
    def on_secondary_click(self, gesture, n_press, x, y):
        rect = Gdk.Rectangle()
        rect.x, rect.y = int(x), int(y)
        if not self.context_popover.get_parent():
            self.context_popover.set_parent(gesture.get_widget())
        self.context_popover.set_pointing_to(rect)
        self.context_popover.popup()

    @Gtk.Template.Callback()
    def on_long_press(self, gesture, x, y):
        rect = Gdk.Rectangle()
        rect.x, rect.y = int(x), int(y)
        if not self.context_popover.get_parent():
            self.context_popover.set_parent(gesture.get_widget())
        self.context_popover.set_pointing_to(rect)
        self.context_popover.popup()

    @Gtk.Template.Callback()
    def context_popdown(self, button):
        self.context_popover.popdown()
