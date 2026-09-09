# main.py

from gi.repository import Gtk, Adw, Gio, GLib
from .home import HomePage
from .wrapbox_page import WrapboxPage
from ... import constants
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/main.ui')
class MainPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornMainPage'

    view_stack = Gtk.Template.Child()

    def setup(self):
        for page in self.view_stack.get_pages():
            threading.Thread(target=page.get_child().reset, daemon=True).start()

    def reset(self):
        # Called in different thread (ctrl+r)
        self.view_stack.get_visible_child().reset()

    @Gtk.Template.Callback()
    def format_invert_bool(self, obj, value:bool) -> bool:
        return not value

    def show_search(self):
        self.view_stack.set_visible_child_name("search")
        self.view_stack.get_visible_child().search_entry.grab_focus()
