# wrapbox_page.py

from gi.repository import Gtk, GObject, Adw, Gio, GLib
from ..movie import MovieButton
from ..series import SeriesButton
from ..season import SeasonButton
from ..episode import EpisodeButton
from ..misc import FilterCheckButton
from ...integrations import models
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/wrapbox_page.ui')
class WrapboxPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornWrapboxPage'

    page_size = GObject.Property(type=int, default=20)
    can_search = GObject.Property(type=bool, default=True)
    search_entry = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    list_el = Gtk.Template.Child()
    bottom_stack = Gtk.Template.Child()
    filter_menubutton = Gtk.Template.Child()
    filter_container = Gtk.Template.Child()
    current_index = 0
    populating = False

    # CB should return list of media models (series, movies, seasons, episodes)
    getter_cb:callable = lambda limit, startIndex, jellyfin: []

    def __init__(self, getter_cb:callable=None, filters:list=[], **kwargs):
        super().__init__(**kwargs)
        if getter_cb:
            self.getter_cb = getter_cb
        for model in filters:
            button = FilterCheckButton(model=model)
            button.connect('notify::state', lambda *_: self.search_changed())
            self.filter_container.append(button)
        self.filter_menubutton.set_visible(len(filters) > 0)

    def reset(self):
        GLib.idle_add(self.list_el.remove_all)
        threading.Thread(target=self.populate, daemon=True).start()

    def show_search(self):
        self.search_entry.grab_focus()

    def populate(self):
        if self.populating:
            return
        GLib.idle_add(self.main_stack.set_visible_child_name, 'loading')
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    self.populating = True
                    size = self.get_property('page-size')
                    filters = []
                    for widget in list(self.filter_container):
                        if filter_key := widget.get_value():
                            filters.append(filter_key)

                    result_models = self.getter_cb(jellyfin, size, self.current_index, self.search_entry.get_text() if self.get_property('can-search') else '', filters)
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
                    if len(result_models) == 0:
                        GLib.idle_add(self.main_stack.set_visible_child_name, 'no-results' if self.search_entry.get_text() else 'empty')
                    else:
                        GLib.idle_add(self.main_stack.set_visible_child_name, 'results')
                    GLib.idle_add(self.bottom_stack.set_visible_child_name, 'label' if len(result_models) < size else 'loading')
        self.populating = False

    @Gtk.Template.Callback()
    def search_changed(self, entry=None):
        self.list_el.remove_all()
        self.populating = False
        self.current_index = 0
        threading.Thread(target=self.populate, daemon=True).start()

    @Gtk.Template.Callback()
    def on_scroll_edge(self, sb, position):
        if position == Gtk.PositionType.BOTTOM:
            if self.bottom_stack.get_visible_child_name() == 'loading':
                threading.Thread(target=self.populate, daemon=True).start()
