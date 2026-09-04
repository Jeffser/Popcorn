# home.py
from gi.repository import Gtk, Adw, Gio, GLib
from ..misc import UserViewButton
from ..series import SeriesOverview, SeriesButton
from ..episode import EpisodeButton
from ..movie import MovieButton
from ..containers import Carousel
from ...integrations import models
from ... import constants

resume_widget_map = {
    models.Episode: EpisodeButton,
    models.Movie: MovieButton,
}

next_up_widget_map = {
    models.Episode: EpisodeButton,
}

latest_widget_map = {
    models.Series: SeriesButton,
    models.Episode: EpisodeButton,
    models.Movie: MovieButton,
}


@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/home.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornHomePage'
    main_container = Gtk.Template.Child()
    overview_container = Gtk.Template.Child()
    continue_watching_container = Gtk.Template.Child()
    next_up_container = Gtk.Template.Child()
    widgets_to_delete_on_reset = []

    def reset(self):
        jellyfin = None
        if root := self.get_root():
            if app := root.get_application():
                jellyfin = app.jellyfin
        if not jellyfin:
            return
        for widget in self.widgets_to_delete_on_reset:
            widget.unparent()
        self.widgets_to_delete_on_reset = []

        # overview_container is OverviewCarousel (Adw.Carousel-backed) --
        # out of scope, unchanged.
        overview_widgets = []
        for series in jellyfin.getFeaturedSeries():
            overview_widgets.append(
                SeriesOverview(model=series)
            )
        GLib.idle_add(self.overview_container.set_widgets, overview_widgets)

        user_view_models = jellyfin.getUserViews()

        self.continue_watching_container.set_widget_map(resume_widget_map)
        GLib.idle_add(self.continue_watching_container.set_items, list(jellyfin.getResume()))

        self.next_up_container.set_widget_map(next_up_widget_map)
        GLib.idle_add(self.next_up_container.set_items, list(jellyfin.getNextUp()))

        for userView in user_view_models:
            latest_models = list(jellyfin.getLatest(userView.get_property('Id')))
            if len(latest_models) == 0:
                continue
            new_carousel = Carousel(
                title=_("Recently Added in {}").format(userView.get_property('Name').title()),
                icon_name=constants.USERVIEWS_ICONS.get(userView.get_property('CollectionType')) or 'folder-symbolic'
            )
            new_carousel.set_widget_map(latest_widget_map, is_tall=True)
            self.widgets_to_delete_on_reset.append(new_carousel)
            GLib.idle_add(self.main_container.append, new_carousel)
            GLib.idle_add(new_carousel.set_items, latest_models)
