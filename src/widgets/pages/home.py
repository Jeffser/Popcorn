# home.py

from gi.repository import Gtk, Adw, Gio, GLib
from ..misc import UserViewButton
from ..series import SeriesOverview, SeriesButton
from ..episode import EpisodeButton
from ..movie import MovieButton
from ..containers import Carousel
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

        for series in jellyfin.getFeaturedSeries():
            self.overview_container.append(
                SeriesOverview(model=series)
            )

        user_view_models = jellyfin.getUserViews()
        for userView in user_view_models:
            self.user_views_container.append(
                UserViewButton(model=userView)
            )

        episode_widgets = []
        for episode in jellyfin.getResume():
            episode_widgets.append(
                EpisodeButton(model=episode)
            )
        self.continue_watching_container.set_widgets(episode_widgets)

        episode_widgets = []
        for episode in jellyfin.getNextUp():
            episode_widgets.append(
                EpisodeButton(model=episode)
            )
        self.next_up_container.set_widgets(episode_widgets)

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
                new_carousel.set_widgets(latest_widgets)
                self.main_container.append(new_carousel)

        GLib.timeout_add(15000, self.auto_scroll_overview)

    def auto_scroll_overview(self):
        position_float = self.overview_container.get_position()
        position_int = int(position_float)
        if position_float == position_int:
            next_index = position_int + 1
            if next_index >= self.overview_container.get_n_pages():
                next_index = 0
            self.overview_container.scroll_to(self.overview_container.get_nth_page(next_index), True)
        return True

    def pan_overview(self, position_modifier:int):
        current_position = int(self.overview_container.get_position() + position_modifier)
        if current_position >= self.overview_container.get_n_pages():
            current_position = 0
        elif current_position < 0:
            current_position = self.overview_container.get_n_pages() - 1
        self.overview_container.scroll_to(self.overview_container.get_nth_page(current_position), True)

    @Gtk.Template.Callback()
    def pan_overview_start(self, btn):
        self.pan_overview(-1)

    @Gtk.Template.Callback()
    def pan_overview_end(self, btn):
        self.pan_overview(1)



