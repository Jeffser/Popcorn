# page.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from ...integrations import models
from ..series import SeriesButton
from ..movie import MovieButton

@Gtk.Template(resource_path='/com/jeffser/Popcorn/movie/page.ui')
class MoviePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornMoviePage'

    model = GObject.Property(type=models.Movie)
    recommendations_container = Gtk.Template.Child()
    top_overlay = Gtk.Template.Child()
    top_overlay_content = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.top_overlay.set_measure_overlay(self.top_overlay_content, True)

    def reset(self):
        jellyfin = None
        model_id = None
        if root := self.get_root():
            if app := root.get_application():
                jellyfin = app.jellyfin
        if model := self.get_property('model'):
            model_id = model.get_property('Id')
        if not jellyfin or not model_id:
            return

        recommendation_widgets = []
        for model in jellyfin.getRecommendations(model_id):
            if isinstance(model, models.Series):
                recommendation_widgets.append(SeriesButton(
                    model=model,
                    is_tall=True
                ))
            elif isinstance(model, models.Movie):
                recommendation_widgets.append(MovieButton(
                    model=model,
                    is_tall=True
                ))
        GLib.idle_add(self.recommendations_container.set_widgets, recommendation_widgets)

    @Gtk.Template.Callback()
    def format_one_decimal(self, obj, value) -> str:
        return f"{value:.1f}"

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
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_heart_icon_name(self, obj, isFavorite:bool) -> str:
        return "heart-filled-symbolic" if isFavorite else "heart-outline-thick-symbolic"
