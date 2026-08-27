# page.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from ...integrations import models
from ..episode import EpisodeButton

@Gtk.Template(resource_path='/com/jeffser/Popcorn/season/page.ui')
class SeasonPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornSeasonPage'

    model = GObject.Property(type=models.Season)
    series_model = GObject.Property(type=models.Series)
    episodes_container = Gtk.Template.Child()
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

        episode_widgets = []
        for episode_model in jellyfin.getEpisodesFromSeason(model_id):
            episode_widgets.append(EpisodeButton(
                model=episode_model,
                mode='details'
            ))
        GLib.idle_add(self.episodes_container.set_widgets, episode_widgets)

    @Gtk.Template.Callback()
    def format_stack_visible_child_name(self, obj, paintable) -> str:
        return 'logo' if paintable else 'label'

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

