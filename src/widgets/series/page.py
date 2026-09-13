# page.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from ...integrations import models
from ..season import SeasonButton
from ..series import SeriesButton
from ..movie import MovieButton
from ..episode import EpisodeButton
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/page.ui')
class SeriesPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornSeriesPage'

    model = GObject.Property(type=models.Series)
    season_dropdown = Gtk.Template.Child()
    episodes_container = Gtk.Template.Child()
    recommendations_container = Gtk.Template.Child()
    top_overlay = Gtk.Template.Child()
    top_overlay_content = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.top_overlay.set_measure_overlay(self.top_overlay_content, True)
        list(self.season_dropdown)[0].add_css_class('flat')

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

        GLib.idle_add(self.on_season_dropdown_selected_item, self.season_dropdown)

    def show_search(self):
        pass

    @Gtk.Template.Callback()
    def format_one_decimal(self, obj, value) -> str:
        return f"{value:.1f}"

    @Gtk.Template.Callback()
    def format_season_count(self, obj, value) -> str:
        return ngettext("{} Season", "{} Seasons", value).format(value)

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

    @Gtk.Template.Callback()
    def on_season_dropdown_setup(self, factory, list_item):
        list_item.set_child(Gtk.Label(
            xalign=0.0,
            halign=Gtk.Align.START
        ))

    @Gtk.Template.Callback()
    def on_season_dropdown_bind(self, factory, list_item):
        list_item.get_child().set_label(list_item.get_item().get_property('Name'))

    def update_episodes(self, jellyfin, season_id:str):
        GLib.idle_add(self.episodes_container.set_widgets, [Adw.Spinner(
            hexpand=True,
            height_request=240,
            width_request=240
        )])
        episode_widgets = []
        if jellyfin and season_id:
            for episode_model in jellyfin.getEpisodesFromSeason(season_id):
                episode_widgets.append(EpisodeButton(
                    model=episode_model,
                    mode='details'
                ))
        if len(episode_widgets) > 0:
            GLib.idle_add(self.episodes_container.set_widgets, episode_widgets)
        else:
            GLib.idle_add(self.episodes_container.set_widgets, [Gtk.Label(
                label=_("No Episodes Found"),
                hexpand=True,
                justify=Gtk.Justification.CENTER,
                css_classes=['title-1']
            )])

    @Gtk.Template.Callback()
    def on_season_dropdown_selected_item(self, dropdown, pspec=None):
        if selected_item := dropdown.get_property('selected-item'):
            if root := self.get_root():
                if app := root.get_application():
                    if jellyfin := app.jellyfin:
                        threading.Thread(
                            target=self.update_episodes,
                            args=(jellyfin, selected_item.get_property('Id')),
                            daemon=True
                        ).start()
        else:
            threading.Thread(
                target=self.update_episodes,
                args=(None, None),
                daemon=True
            ).start()

