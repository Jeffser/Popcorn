# filter_checkbox.py

from gi.repository import Gtk, GObject, Adw, Gio, GLib
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/misc/filter_checkbutton.ui')
class FilterCheckButton(Gtk.CheckButton):
    __gtype_name__ = 'PopcornFilterCheckButton'

    model = GObject.Property(type=models.Filter)
    state = GObject.Property(type=int, default=0)
    updating = GObject.Property(type=bool, default=False)

    @Gtk.Template.Callback()
    def on_toggled(self, button):
        if not self.get_property('updating'):
            self.set_property('updating', True)
            if model := self.get_property('model'):
                self.set_property('state', (self.get_property('state') + 1) % (3 if model.get_property('InconsistentValue') else 2))
                state = self.get_property('state')
                if state == 0: # None
                    button.set_active(False)
                    button.set_inconsistent(False)
                elif state == 1:
                    button.set_active(True)
                    button.set_inconsistent(False)
                elif state == 2:
                    button.set_active(False)
                    button.set_inconsistent(True)
            self.set_property('updating', False)

    def get_value(self) -> str:
        if model := self.get_property('model'):
            if self.get_active():
                return model.get_property('ActiveValue')
            elif self.get_inconsistent():
                return model.get_property('InconsistentValue')
        return ''
