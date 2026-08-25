# user_view.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject
from ... import constants
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/misc/user_view_button.ui')
class UserViewButton(Gtk.Button):
    __gtype_name__ = 'PopcornUserViewButton'

    model = GObject.Property(type=models.UserView)

    @Gtk.Template.Callback()
    def format_icon_name(self, obj, value) -> str:
        return constants.USERVIEWS_ICONS.get(value) or 'folder-symbolic'
