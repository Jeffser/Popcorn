# context.py

from gettext import gettext as _
from gi.repository import Gtk, GObject, Gdk


def show_context_menu(widget: Gtk.Widget, menu, x: float, y: float):
    menu.set_parent(widget)
    rect = Gdk.Rectangle()
    rect.x, rect.y, rect.width, rect.height = int(x), int(y), 1, 1
    menu.set_pointing_to(rect)
    menu.connect('closed', lambda popover: popover.unparent())
    menu.popup()

class ContextMenuRow(Gtk.Button):
    __gtype_name__ = 'PopcornContextMenuRow'

    title = GObject.Property(type=str, default="")
    icon_name = GObject.Property(type=str, default="")
    destructive = GObject.Property(type=bool, default=False)

    __gsignals__ = {
        'activated': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, **kwargs):
        super().__init__(css_classes=['flat'], **kwargs)
        self.set_hexpand(True)

        self.icon = Gtk.Image()
        self.icon.set_visible(bool(self.icon_name))

        self.label = Gtk.Label(xalign=0)
        self.label.add_css_class('body')
        self.label.set_label(self.title)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, halign=Gtk.Align.START)
        content.append(self.icon)
        content.append(self.label)
        self.set_child(content)

        self.connect('notify::title', lambda *_: self.label.set_label(self.title))
        self.connect('notify::icon-name', self.update_icon)
        self.connect('notify::destructive', self.update_destructive_style)
        self.connect('clicked', lambda *_: self.emit('activated'))
        self.update_icon()
        self.update_destructive_style()

    def update_icon(self, *_args):
        self.icon.set_visible(bool(self.icon_name))
        if self.icon_name:
            self.icon.set_from_icon_name(self.icon_name)

    def update_destructive_style(self, *_args):
        if self.destructive:
            self.add_css_class('destructive-action')
        else:
            self.remove_css_class('destructive-action')


class ContextMenuHorizontalRow(Gtk.Box):
    __gtype_name__ = 'PopcornContextMenuHorizontalRow'

    def __init__(self, spacing: int = 6, **kwargs):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=spacing,
            margin_start=12,
            margin_end=12,
            margin_top=6,
            margin_bottom=6,
            **kwargs,
        )


class ContextMenu(Gtk.Popover):
    __gtype_name__ = 'PopcornContextMenu'

    def __init__(self, **kwargs):
        super().__init__(css_classes=['menu'], **kwargs)
        self.set_has_arrow(False)
        self.set_halign(Gtk.Align.START)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.box.set_margin_start(6)
        self.box.set_margin_end(6)
        self.box.set_margin_top(6)
        self.box.set_margin_bottom(6)

        self.set_child(self.box)

    def add_row(self, row):
        row.connect('activated', lambda *_: self.popdown())
        self.box.append(row)

    def add_separator(self):
        self.box.append(Gtk.Separator(margin_top=5, margin_bottom=5))
