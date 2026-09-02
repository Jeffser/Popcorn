# welcome.py

from gi.repository import Gtk, Adw, Gio, GLib
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/welcome.ui')
class WelcomePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornWelcomePage'

    url_entry = Gtk.Template.Child()

    def reset(self):
        if root := self.get_root():
            if app := root.get_application():
                if settings := app.get_property('settings'):
                    self.url_entry.set_text(settings.get_value('url').unpack())

    def try_connect(self):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    if jellyfin.checkHealth():
                        GLib.idle_add(root.root_navigationview.push_by_tag, 'login')
                        GLib.idle_add(root.root_navigationview.find_page('login').reset)

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> str:
        return bool(value)

    @Gtk.Template.Callback()
    def connect_requested(self, button):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    url = self.url_entry.get_text()
                    if not url.startswith('http'):
                        url = 'http://{}'.format(url)
                        self.url_entry.set_text(url)
                    jellyfin.set_property('url', url)
                    threading.Thread(target=self.try_connect, daemon=True).start()
