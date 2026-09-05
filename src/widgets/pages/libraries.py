# libraries.py

from gi.repository import Gtk, Adw, Gio, GLib
from ..misc import UserViewButton
from ..series import SeriesOverview, SeriesButton
from ..episode import EpisodeButton
from ..movie import MovieButton
from ..containers import Carousel
from ...integrations import models
from ... import constants

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/libraries.ui')
class LibrariesPage(Gtk.ScrolledWindow):
    __gtype_name__ = 'PopcornLibrariesPage'

    main_stack = Gtk.Template.Child()
    main_carousel = Gtk.Template.Child()
    main_container = Gtk.Template.Child()

    def reset(self):
        GLib.idle_add(self.main_stack.set_visible_child_name, "loading")
        for widget in list(self.main_container):
            GLib.idle_add(self.main_container.remove, widget)
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    user_view_widgets = []
                    for userView in jellyfin.getUserViews():
                        user_view_widgets.append(UserViewButton(model=userView))
                        latest_widgets = []
                        for model in jellyfin.getLatest(userView.get_property('Id')):
                            if isinstance(model, models.Series):
                                latest_widgets.append(
                                    SeriesButton(
                                        model=model,
                                        is_tall=True
                                    )
                                )
                            elif isinstance(model, models.Episode):
                                latest_widgets.append(
                                    EpisodeButton(
                                        model=model,
                                        is_tall=True
                                    )
                                )
                            elif isinstance(model, models.Movie):
                                latest_widgets.append(
                                    MovieButton(
                                        model=model,
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
                    GLib.idle_add(self.main_carousel.set_widgets, user_view_widgets)
        GLib.idle_add(self.main_stack.set_visible_child_name, "content")
