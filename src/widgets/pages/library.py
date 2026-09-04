# library.py

from gi.repository import Gtk, Adw, GLib
from ..misc import UserViewButton

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/library.ui')
class LibraryPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornLibraryPage'

    main_container = Gtk.Template.Child()
    user_views_container = Gtk.Template.Child()

    def reset(self):
        jellyfin = None
        if root := self.get_root():
            if app := root.get_application():
                jellyfin = app.jellyfin
        if not jellyfin:
            return

        for widget in list(self.user_views_container):
            GLib.idle_add(self.user_views_container.remove, widget)

        user_view_models = jellyfin.getUserViews()
        for userView in user_view_models:
            GLib.idle_add(self.user_views_container.append,
                UserViewButton(model=userView)
            )
            print(userView)
