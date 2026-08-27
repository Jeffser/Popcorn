# wrapbox.py

from gi.repository import Gtk, Adw, GLib, Gdk, Gio, GObject

@Gtk.Template(resource_path='/com/jeffser/Popcorn/containers/wrapbox.ui')
class Wrapbox(Gtk.Box):
    __gtype_name__ = 'PopcornWrapbox'

    title = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)

    list_el = Gtk.Template.Child()

    def remove_all(self):
        for page in list(self.list_el):
            self.list_el.remove(page)

    def set_widgets(self, widgets:list):
        GLib.idle_add(self.set_visible, len(widgets) > 0)
        if len(list(self.list_el)) > 0:
            GLib.idle_add(self.remove_all)
        for i, page in enumerate(widgets):
            GLib.idle_add(self.list_el.append, page)

