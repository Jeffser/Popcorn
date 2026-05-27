# home.py

from gi.repository import Gtk, Adw, Gio, GLib
from ..misc import UserViewButton

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/home.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornHomePage'

    user_views_container = Gtk.Template.Child()

    def reset(self):
        jellyfin = None
        if root := self.get_root():
            if app := root.get_application():
                jellyfin = app.jellyfin
        if not jellyfin:
            return


        for userView in jellyfin.getUserViews():
            button = UserViewButton(userView)
            self.user_views_container.append(button)
        
