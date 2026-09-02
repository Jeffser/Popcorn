# preferences.py

from gi.repository import GObject, GLib, Gtk, Adw, Gdk, Gio
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/preferences.ui')
class PopcornPreferences(Adw.PreferencesDialog):
    __gtype_name__ = 'PopcornPreferencesDialog'

    blur_effect_el = Gtk.Template.Child()

    # Session
    session_server_name = GObject.Property(type=str)
    session_username = GObject.Property(type=str)
    session_user_paintable = GObject.Property(type=Gdk.Paintable)
    session_url = GObject.Property(type=str)

    def reset(self, app):
        if settings := app.get_property('settings'):
            settings.bind(
                "blur-effect",
                self.blur_effect_el,
                "active",
                Gio.SettingsBindFlags.DEFAULT
            )
        if jellyfin := app.jellyfin:
            if information := jellyfin.getServerInformation():
                self.set_property('session-server-name', information.get('title'))
                self.set_property('session-username', information.get('username'))
                self.set_property('session-user-paintable', information.get('picture'))
                self.set_property('session-url', information.get('link'))

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)
