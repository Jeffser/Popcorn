# models.py

from gi.repository import GObject, GLib

class BasicModel(GObject.Object):
    __gtype_name__ = 'PopcornBasicModel'

    def __init__(self, **kwargs):
        super().__init__()
        self.update_data(**kwargs)

    def update_data(self, **kwargs):
        for prop in self.list_properties():
            if prop.get_name() in kwargs:
                if self.get_property(prop.get_name()) != kwargs.get(prop.get_name()):
                    self.set_property(prop.get_name(), kwargs.get(prop.get_name()))
            elif self.get_property(prop.get_name()) is None:
                if prop.value_type.name == 'PyObject': #LIST
                    self.set_property(prop.get_name(), [])
                else:
                    self.set_property(prop.get_name(), prop.get_default_value())

    def connect_property(self, parameter:str, callback:callable) -> str:
        connection_id = self.connect(
            'notify::{}'.format(parameter),
            lambda *_, parameter=parameter, callback=callback: GLib.idle_add(callback, self.get_property(parameter))
        )
        GLib.idle_add(callback, self.get_property(parameter))
        return connection_id

class UserView(BasicModel):
    __gtype_name__ = 'PopcornUserView'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    SortName = GObject.Property(type=str)
    CollectionType = GObject.Property(type=str)

