# preferences.py

from gi.repository import GObject, GLib, Gtk, Adw, Gdk, Gio
import threading, os

@Gtk.Template(resource_path='/com/jeffser/Popcorn/preferences.ui')
class PopcornPreferences(Adw.PreferencesDialog):
    __gtype_name__ = 'PopcornPreferencesDialog'

    # General
    blur_effect_el = Gtk.Template.Child()

    # Gnome Search
    is_gnome = GObject.Property(type=bool, default="GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", "").upper())
    gnome_search_movie_el = Gtk.Template.Child()
    gnome_search_series_el = Gtk.Template.Child()
    gnome_search_episode_el = Gtk.Template.Child()

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
            settings.bind(
                "gnome-search-include-movie",
                self.gnome_search_movie_el,
                "active",
                Gio.SettingsBindFlags.DEFAULT
            )
            settings.bind(
                "gnome-search-include-series",
                self.gnome_search_series_el,
                "active",
                Gio.SettingsBindFlags.DEFAULT
            )
            settings.bind(
                "gnome-search-include-episode",
                self.gnome_search_episode_el,
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
