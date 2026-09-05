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
class HomePage(Gtk.ScrolledWindow):
    __gtype_name__ = 'PopcornHomePage'

    overview_container = Gtk.Template.Child()
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

