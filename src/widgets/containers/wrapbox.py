# wrapbox.py

from gi.repository import Gtk, GObject, GLib

@Gtk.Template(resource_path='/com/jeffser/Popcorn/containers/wrapbox.ui')
class Wrapbox(Gtk.Box):
    __gtype_name__ = 'PopcornWrapbox'

    title = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)
    action_name = GObject.Property(type=str)
    action_target = GObject.Property(type=str)

    list_el = Gtk.Template.Child()

    def set_widgets(self, widgets:list):
        self.set_visible(len(widgets) > 0)
        self.list_el.remove_all()
        for i, page in enumerate(widgets):
            self.list_el.append(page)

    @Gtk.Template.Callback()
    def format_header_visible(self, obj, title:str) -> bool:
        return bool(title)

    @Gtk.Template.Callback()
    def format_header_stack_visible_child_name(self, obj, action_name:str) -> str:
        return 'button' if action_name else 'label'

    @Gtk.Template.Callback()
    def format_header_visible(self, obj, title:str) -> bool:
        return bool(title)

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)
