# search.py
from gi.repository import Gtk, GObject, Adw, Gio, GLib
from ..movie import MovieButton
from ..series import SeriesButton
from ..episode import EpisodeButton
from ...integrations import models
import threading

movie_widget_map = {models.Movie: MovieButton}
series_widget_map = {models.Series: SeriesButton}
episode_widget_map = {models.Episode: EpisodeButton}


@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/search.ui')
class SearchPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornSearchPage'

    search_entry = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    movie_container = Gtk.Template.Child()
    series_container = Gtk.Template.Child()
    episode_container = Gtk.Template.Child()

    searching = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.movie_container.set_widget_map(movie_widget_map, is_tall=True)
        self.series_container.set_widget_map(series_widget_map, is_tall=True)
        self.episode_container.set_widget_map(episode_widget_map)

    def reset(self):
        self.get_root().set_focus(self.search_entry)
        self.search_entry.set_text('')

    def search(self, query: str):
        if query != self.search_entry.get_text():
            threading.Thread(target=self.search, args=(self.search_entry.get_text(),), daemon=True).start()
            return
        if not query:
            GLib.idle_add(self.main_stack.set_visible_child_name, 'empty')
            return
        self.searching = True
        GLib.idle_add(self.main_stack.set_visible_child_name, 'loading')
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    if results := jellyfin.search(query):
                        movie_models = []
                        series_models = []
                        episode_models = []
                        for model in results:
                            if isinstance(model, models.Movie):
                                movie_models.append(model)
                            elif isinstance(model, models.Series):
                                series_models.append(model)
                            elif isinstance(model, models.Episode):
                                episode_models.append(model)

                        GLib.idle_add(self.movie_container.set_items, movie_models)
                        GLib.idle_add(self.series_container.set_items, series_models)
                        GLib.idle_add(self.episode_container.set_items, episode_models)
                        GLib.idle_add(self.main_stack.set_visible_child_name, 'results')
                    else:
                        GLib.idle_add(self.main_stack.set_visible_child_name, 'no-results')
        self.searching = False
        if query != self.search_entry.get_text():
            threading.Thread(target=self.search, args=(self.search_entry.get_text(),), daemon=True).start()

    @Gtk.Template.Callback()
    def search_changed(self, entry):
        if not self.searching:
            if query := entry.get_text():
                threading.Thread(target=self.search, args=(query,), daemon=True).start()
            else:
                self.main_stack.set_visible_child_name('empty')
