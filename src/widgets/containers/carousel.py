# carousel.py
from gi.repository import Gtk, GLib, GObject, Gio, Adw
from ...integrations import models

# Every carousel navigates the same way regardless of which model mix it
# holds -- Series always opens show_series, etc. -- so this is fixed here
# rather than threaded through every set_widget_map() call site.
ACTIVATE_ACTION_MAP = {
    models.Series: 'app.show_series',
    models.Episode: 'app.show_episode',
    models.Movie: 'app.show_movie',
    models.Season: 'app.show_season',
}


@Gtk.Template(resource_path='/com/jeffser/Popcorn/containers/carousel.ui')
class Carousel(Gtk.Box):
    __gtype_name__ = 'PopcornCarousel'

    title = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)

    scrolled_el = Gtk.Template.Child()
    list_el = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widget_map = {}
        self.widget_kwargs = {}

        self.store = Gio.ListStore(item_type=GObject.Object)
        selection = Gtk.NoSelection(model=self.store)
        self.list_el.set_model(selection)
        self.list_el.connect('activate', self.on_activate)

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.on_setup)
        factory.connect('bind', self.on_bind)
        self.list_el.set_factory(factory)

    def set_widget_map(self, widget_map: dict, **widget_kwargs):
        """widget_map: {model_class: widget_class}. See prior docstring --
        unchanged. Navigation is handled separately via ACTIVATE_ACTION_MAP,
        not through the widgets themselves anymore."""
        self.widget_map = widget_map
        self.widget_kwargs = widget_kwargs

    def widget_class_for(self, item):
        for model_cls, widget_cls in self.widget_map.items():
            if isinstance(item, model_cls):
                return widget_cls
        raise TypeError(f'No widget class registered for {type(item)!r} -- call set_widget_map() first')

    # -- Gtk.ListView factory lifecycle ----------------------------------

    def on_setup(self, factory, list_item):
        # Activatable -- with the cards no longer containing their own
        # navigation button, row activation (single-click-activate: true,
        # see carousel.blp) is now the only way a card navigates anywhere.
        list_item.set_activatable(True)

    def on_bind(self, factory, list_item):
        item = list_item.get_item()
        widget_cls = self.widget_class_for(item)
        child = list_item.get_child()
        if type(child) is widget_cls:
            child.set_property('model', item)
        else:
            list_item.set_child(widget_cls(model=item, **self.widget_kwargs))

    def on_activate(self, list_view, position):
        item = self.store.get_item(position)
        if item is None:
            return
        action_name = None
        for model_cls, name in ACTIVATE_ACTION_MAP.items():
            if isinstance(item, model_cls):
                action_name = name
                break
        if action_name is None:
            return
        list_view.activate_action(action_name, GLib.Variant('s', item.get_property('Id')))

    # -- public API --------------------------------------------------------

    def remove_all(self):
        self.store.remove_all()

    def set_items(self, models: list):
        def scroll_to_start():
            adjustment = self.scrolled_el.get_hadjustment()
            adjustment.set_value(adjustment.get_lower())

        self.set_visible(len(models) > 0)
        self.remove_all()
        if models:
            self.store.splice(0, 0, models)
        GLib.timeout_add(200, scroll_to_start)
