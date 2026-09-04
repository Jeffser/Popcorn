# welcome.py

from gi.repository import Gtk, Adw, Gio, GLib
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/welcome.ui')
class WelcomePage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornWelcomePage'

    url_entry = Gtk.Template.Child()
    trust_checkbutton = Gtk.Template.Child()

    def reset(self):
        if root := self.get_root():
            if app := root.get_application():
                if settings := app.get_property('settings'):
                    self.url_entry.set_text(settings.get_value('url').unpack())
                    self.trust_checkbutton.set_active(settings.get_value('trust-server').unpack())

    def try_connect(self):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    if jellyfin.checkHealth():
                        GLib.idle_add(root.auth_navigationview.push_by_tag, 'login')
                        GLib.idle_add(root.auth_navigationview.find_page('login').reset)
                    else:
                        toast = Adw.Toast(
                            title=_("Error connecting to server")
                        )
                        GLib.idle_add(root.toast_overlay.add_toast, toast)

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
                    jellyfin.set_property('trustServer', self.trust_checkbutton.get_active())
                    threading.Thread(target=self.try_connect, daemon=True).start()
