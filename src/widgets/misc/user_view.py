# user_view.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject
from ... import constants
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/misc/user_view_button.ui')
class UserViewButton(Gtk.Button):
    __gtype_name__ = 'PopcornUserViewButton'

    model = GObject.Property(type=models.UserView)

    def __init__(self, model):
        super().__init__()
        self.set_property('model', model)
        self.model.connect_property('Name', self.name_changed)
        self.model.connect_property('CollectionType', self.type_changed)
        self.model.connect_property('Id', self.id_changed)

    def id_changed(self, model_id:str):
        self.set_action_target_value(GLib.Variant.new_string(model_id))
        self.set_sensitive(model_id)

    def name_changed(self, name:str):
        self.get_child().set_label(name)
        self.set_tooltip_text(name)

    def type_changed(self, collectionType:str):
        self.get_child().set_icon_name(
            constants.USERVIEWS_ICONS.get(collectionType, 'folder-symbolic')
        )
