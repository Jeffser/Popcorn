# preferences.py

from gi.repository import Gtk, Adw, GLib, Gst, Gio

@Gtk.Template(resource_path='/com/jeffser/Popcorn/preferences.ui')
class PopcornPreferences(Adw.PreferencesDialog):
    __gtype_name__ = 'PopcornPreferencesDialog'

    blur_effect_el = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        settings = Gio.Settings(schema_id="com.jeffser.Popcorn")
        settings.bind(
            "blur-effect",
            self.blur_effect_el,
            "active",
            Gio.SettingsBindFlags.DEFAULT
        )
