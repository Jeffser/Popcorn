# overview.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/overview.ui')
class SeriesOverview(Gtk.Overlay):
    __gtype_name__ = 'PopcornSeriesOverview'

    model = GObject.Property(type=models.Series)

    @Gtk.Template.Callback()
    def format_one_decimal(self, obj, value) -> str:
        return f"{value:.1f}"

    @Gtk.Template.Callback()
    def format_season_count(self, obj, value) -> str:
        return ngettext("{} Season", "{} Seasons", value).format(value)

    @Gtk.Template.Callback()
    def format_overview(self, obj, value) -> str:
        return value.split('\n')[0]

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def format_stack_visible_child_name(self, obj, paintable) -> str:
        return 'logo' if paintable else 'label'

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)
