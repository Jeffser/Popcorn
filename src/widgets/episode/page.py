# page.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from ...integrations import models
from ..episode import EpisodeButton
from ...constants import format_duration_display, get_future_time

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

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def format_stack_visible_child_name(self, obj, paintable) -> str:
        return 'logo' if paintable else 'label'

    @Gtk.Template.Callback()
    def format_overview_ellipsize(self, obj, active:bool) -> Pango.EllipsizeMode:
        return Pango.EllipsizeMode.NONE if active else Pango.EllipsizeMode.END

    @Gtk.Template.Callback()
    def format_overview_button_icon_name(self, obj, active:bool) -> str:
        return "pan-up-symbolic" if active else "pan-down-symbolic"

    @Gtk.Template.Callback()
    def format_duration(self, obj, duration:float) -> str:
        return format_duration_display(duration)

    @Gtk.Template.Callback()
    def format_one_decimal(self, obj, value) -> str:
        return f"{value:.1f}"

    @Gtk.Template.Callback()
    def format_end_time(self, obj, duration:float) -> str:
        return _("Ends at {}").format(get_future_time(duration))
