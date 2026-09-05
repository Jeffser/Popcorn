# wrapbox_page.py

from gi.repository import Gtk, GObject, Adw, Gio, GLib
from ..movie import MovieButton
from ..series import SeriesButton
from ..season import SeasonButton
from ..episode import EpisodeButton
from ...integrations import models
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/wrapbox_page.ui')
class WrapboxPage(Gtk.ScrolledWindow):
    __gtype_name__ = 'PopcornWrapboxPage'

    page_size = GObject.Property(type=int, default=20)
    list_el = Gtk.Template.Child()
    bottom_stack = Gtk.Template.Child()
    current_index = 0
    populating = False

    # CB should return list of media models (series, movies, seasons, episodes)
    getter_cb:callable = lambda limit, startIndex, jellyfin: []

    def __init__(self, getter_cb:callable=None, **kwargs):
        super().__init__(**kwargs)
        if getter_cb:
            self.getter_cb = getter_cb

    def reset(self):
        GLib.idle_add(self.list_el.remove_all)
        threading.Thread(target=self.populate, daemon=True).start()

    def populate(self):
        if self.populating:
            return
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    self.populating = True
                    size = self.get_property('page-size')
                    result_models = self.getter_cb(size, self.current_index, jellyfin)
                    self.current_index += size
                    for model in result_models:
                        if isinstance(model, models.Movie):
                            GLib.idle_add(self.list_el.append, MovieButton(model=model))
                        elif isinstance(model, models.Series):
                            GLib.idle_add(self.list_el.append, SeriesButton(model=model))
                        elif isinstance(model, models.Season):
                            GLib.idle_add(self.list_el.append, SeasonButton(model=model))
                        elif isinstance(model, models.Episode):
                            GLib.idle_add(self.list_el.append, EpisodeButton(model=model))
                    GLib.idle_add(self.bottom_stack.set_visible_child_name, 'label' if len(result_models) < size else 'loading')
        self.populating = False


    @Gtk.Template.Callback()
    def on_scroll_edge(self, sb, position):
        if position == Gtk.PositionType.BOTTOM:
            if self.bottom_stack.get_visible_child_name() == 'loading':
                threading.Thread(target=self.populate, daemon=True).start()
