# carousel.py

from gi.repository import Gtk, GLib, Gdk, GObject

@Gtk.Template(resource_path='/com/jeffser/Popcorn/containers/carousel.ui')
class Carousel(Gtk.Box):
    __gtype_name__ = 'PopcornCarousel'

    title = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)

    scrolled_window = Gtk.Template.Child()
    list_el = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if controllers := self.scrolled_window.observe_controllers():
            for i in range(controllers.get_n_items()):
                if controller := controllers.get_item(i):
                    if isinstance(controller, Gtk.GestureDrag):
                        controller.set_touch_only(False)

    def remove_all(self):
        for page in list(self.list_el):
            self.list_el.remove(page)

    def set_widgets(self, widgets:list):
        self.set_visible(len(widgets) > 0)
        self.remove_all()
        for page in widgets:
            self.list_el.append(page)

    @Gtk.Template.Callback()
    def format_header_visible(self, obj, title:str) -> bool:
        return bool(title)
