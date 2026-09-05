# overview_carousel.py

from gi.repository import Gtk, Gdk, Adw, GLib, Gst

@Gtk.Template(resource_path='/com/jeffser/Popcorn/misc/overview_carousel.ui')
class OverviewCarousel(Gtk.Overlay):
    __gtype_name__ = 'PopcornOverviewCarousel'

    list_el = Gtk.Template.Child()
    pan_start_button = Gtk.Template.Child()
    pan_end_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GLib.timeout_add(15000, self.auto_scroll_overview)

    def remove_all(self):
        for page in list(self.list_el):
            self.list_el.remove(page)

    def set_widgets(self, widgets:list):
        self.list_el.set_visible(len(widgets) > 0)
        self.set_margin_top(0 if len(widgets) > 0 else 25)
        if self.list_el.get_n_pages() > 0:
            self.remove_all()
        for i, page in enumerate(widgets):
            self.list_el.append(page)

    def auto_scroll_overview(self):
        if self.list_el.get_n_pages() == 0:
            return True
        position_float = self.list_el.get_position()
        position_int = int(position_float)
        if position_float == position_int:
            next_index = position_int + 1
            if next_index >= self.list_el.get_n_pages():
                next_index = 0
            if next_page := self.list_el.get_nth_page(next_index):
                self.list_el.scroll_to(next_page, True)
        return True

    def pan_overview(self, position_modifier:int):
        current_position = int(self.list_el.get_position() + position_modifier)
        if current_position >= self.list_el.get_n_pages():
            current_position = 0
        elif current_position < 0:
            current_position = self.list_el.get_n_pages() - 1
        if next_page := self.list_el.get_nth_page(current_position):
            self.list_el.scroll_to(next_page, True)

    @Gtk.Template.Callback()
    def pan_start(self, btn):
        self.pan_overview(-1)

    @Gtk.Template.Callback()
    def pan_end(self, btn):
        self.pan_overview(1)

    @Gtk.Template.Callback()
    def on_scroll(self, controller, dx, dy):
        position = self.list_el.get_position()
        if position == int(position):
            event = controller.get_current_event()
            state = event.get_modifier_state()
            if (state & Gdk.ModifierType.SHIFT_MASK) or dx != 0:
                direction = dy or dx
                next_position = int(max(0, min(position + direction, self.list_el.get_n_pages())))
                next_page = self.list_el.get_nth_page(next_position)
                if next_page:
                    self.list_el.scroll_to(next_page, True)
        return Gdk.EVENT_PROPAGATE

    @Gtk.Template.Callback()
    def format_visible_button(self, obj, n_pages:int) -> bool:
        return n_pages > 1
