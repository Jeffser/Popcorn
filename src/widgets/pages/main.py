# main.py

from gi.repository import GObject, Gtk, Adw, Gio, GLib
from .home import HomePage
from .wrapbox_page import WrapboxPage
from ... import constants
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/main.ui')
class MainPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornMainPage'

    view_stack = Gtk.Template.Child()
    is_wide = GObject.Property(type=bool, default=True)

    def setup(self):
        for page in self.view_stack.get_pages():
            threading.Thread(target=page.get_child().reset, daemon=True).start()
        return
        # Called in main thread only when login in / launching

        # Remove Pages

        # Homepage
        homepage = HomePage()
        self.view_stack.add_titled_with_icon(
            homepage,
            "home",
            _("Home"),
            "go-home-symbolic"
        )
        threading.Thread(target=homepage.reset, daemon=True).start()

        # UserViews
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    for model in jellyfin.getUserViews():
                        getter_function = lambda limit, startIndex, jellyfin, uvid=model.get_property('Id'): jellyfin.getModelsFromFolder(uvid, limit, startIndex)
                        page = WrapboxPage(
                            getter_cb=getter_function
                        )
                        self.view_stack.add_titled_with_icon(
                            page,
                            model.get_property("Id"),
                            model.get_property("Name"),
                            constants.USERVIEWS_ICONS.get(model.get_property('CollectionType')) or 'folder-symbolic'
                        )
                        threading.Thread(target=page.reset, daemon=True).start()

    def reset(self):
        # Called in different thread (ctrl+r)
        self.view_stack.get_visible_child().reset()

