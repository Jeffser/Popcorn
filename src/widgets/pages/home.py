# home.py

from gi.repository import Gtk, Adw, Gio, GLib
from ..misc import UserViewButton
from ..series import SeriesOverview, SeriesButton
from ..episode import EpisodeButton
from ..movie import MovieButton
from ..containers import Carousel
from ...integrations import models
from ... import constants

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/home.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornHomePage'

    main_container = Gtk.Template.Child()
    overview_container = Gtk.Template.Child()
    user_views_container = Gtk.Template.Child()
    continue_watching_container = Gtk.Template.Child()
    next_up_container = Gtk.Template.Child()

    def reset(self):
        jellyfin = None
        if root := self.get_root():
            if app := root.get_application():
                jellyfin = app.jellyfin
        if not jellyfin:
            return

        overview_widgets = []
        for series in jellyfin.getFeaturedSeries():
            overview_widgets.append(
                SeriesOverview(model=series)
            )
        GLib.idle_add(self.overview_container.set_widgets, overview_widgets)

        user_view_models = jellyfin.getUserViews()
        for userView in user_view_models:
            GLib.idle_add(self.user_views_container.append,
                UserViewButton(model=userView)
            )

        resume_widgets = []
        for model in jellyfin.getResume():
            if isinstance(model, models.Episode):
                resume_widgets.append(
                    EpisodeButton(model=model)
                )
            elif isinstance(model, models.Movie):
                resume_widgets.append(
                    MovieButton(model=model)
                )
        GLib.idle_add(self.continue_watching_container.set_widgets, resume_widgets)

        episode_widgets = []
        for episode in jellyfin.getNextUp():
            episode_widgets.append(
                EpisodeButton(model=episode)
            )
        GLib.idle_add(self.next_up_container.set_widgets, episode_widgets)

        for userView in user_view_models:
            latest_widgets = []
            latest_dict = jellyfin.getLatest(userView.get_property('Id'))

            for series_model in latest_dict.get('Series'):
                latest_widgets.append(
                    SeriesButton(
                        model=series_model,
                        is_tall=True
                    )
                )

            for episode_model in latest_dict.get('Episode'):
                latest_widgets.append(
                    EpisodeButton(
                        model=episode_model,
                        is_tall=True
                    )
                )

            for movie_model in latest_dict.get('Movie'):
                latest_widgets.append(
                    MovieButton(
                        model=movie_model,
                        is_tall=True
                    )
                )

            if len(latest_widgets) > 0:
                new_carousel = Carousel(
                    title=_("Recently Added in {}").format(userView.get_property('Name').title()),
                    icon_name=constants.USERVIEWS_ICONS.get(userView.get_property('CollectionType')) or 'folder-symbolic'
                )
                GLib.idle_add(self.main_container.append, new_carousel)
                GLib.idle_add(new_carousel.set_widgets, latest_widgets)

