# wrapbox.py

from gi.repository import Gtk, GObject

@Gtk.Template(resource_path='/com/jeffser/Popcorn/containers/wrapbox.ui')
class Wrapbox(Gtk.Box):
    __gtype_name__ = 'PopcornWrapbox'

    title = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)

    list_el = Gtk.Template.Child()

    def set_widgets(self, widgets:list):
        self.set_visible(len(widgets) > 0)
        self.list_el.remove_all()
        for i, page in enumerate(widgets):
            self.list_el.append(page)

