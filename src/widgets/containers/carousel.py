# carousel.py

from gi.repository import Gtk, GLib, Gdk, GObject

@Gtk.Template(resource_path='/com/jeffser/Popcorn/containers/carousel.ui')
class Carousel(Gtk.Box):
    __gtype_name__ = 'PopcornCarousel'

    title = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)

    list_el = Gtk.Template.Child()
    start_value = 0
    has_dragged = False

    def remove_all(self):
        for page in list(self.list_el):
            self.list_el.remove(page)

    def set_widgets(self, widgets:list):
        self.set_visible(len(widgets) > 0)
        self.remove_all()
        for page in widgets:
            self.list_el.append(page)

    @Gtk.Template.Callback()
    def drag_begin(self, gesture, start_x:float, start_y:float):
        self.start_value = gesture.get_widget().get_hadjustment().get_value()
        self.has_dragged = False

    @Gtk.Template.Callback()
    def drag_update(self, gesture, offset_x:float, offset_y:float):
        new_value = self.start_value - offset_x

        if not self.has_dragged and abs(offset_x) > 5:
            self.has_dragged = True
            gesture.set_state(Gtk.EventSequenceState.CLAIMED)

        if self.has_dragged:
            hadjustment = gesture.get_widget().get_hadjustment()
            lower = hadjustment.get_lower()
            upper = hadjustment.get_upper() - hadjustment.get_page_size()
            hadjustment.set_value(max(lower, min(new_value, upper)))


