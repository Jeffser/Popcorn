# login.py

from gi.repository import Gtk, Adw, Gio, GLib
from ...integrations import secret
import threading, time

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/login.ui')
class LoginPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornLoginPage'

    url_el = Gtk.Template.Child()
    user_el = Gtk.Template.Child()
    password_el = Gtk.Template.Child()
    login_button_el = Gtk.Template.Child()
    quick_connect_button_el = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        settings = Gio.Settings(schema_id="com.jeffser.Popcorn")
        self.url_el.set_text(settings.get_value('url').unpack())
        self.user_el.set_text(settings.get_value('user').unpack())
        self.password_el.set_text('')
        self.entry_changed()

    @Gtk.Template.Callback()
    def entry_changed(self, entry=None):
        has_url = self.url_el.get_text()
        has_user = self.user_el.get_text()
        has_password = self.password_el.get_text()
        self.login_button_el.set_sensitive(has_url and has_user and has_password)
        self.quick_connect_button_el.set_sensitive(has_url)

    @Gtk.Template.Callback()
    def login_requested(self, widget=None):
        if root := self.get_root():
            if app := root.get_application():
                app.jellyfin.set_property('url', self.url_el.get_text())
                app.jellyfin.set_property('user', self.user_el.get_text())
                secret.store_password(self.password_el.get_text())
                threading.Thread(target=self.get_root().get_application().try_login, daemon=True).start()

    @Gtk.Template.Callback()
    def quick_connect_requested(self, button):
        def wait_confirmation(data, dialog, integration):
            waited_turns = 0
            is_authenticated = False
            while not is_authenticated and dialog.get_root():
                is_authenticated = integration.checkQuickConnect(data.get('Secret'))
                if is_authenticated:
                    GLib.idle_add(dialog.close)
                    threading.Thread(target=self.get_root().get_application().try_login, daemon=True).start()
                    break
                time.sleep(5)
                waited_turns += 1
                if waited_turns >= 5:
                    GLib.idle_add(dialog.close)
                    break

        def run(integration):
            data = integration.initiateQuickConnect()
            dialog = Adw.AlertDialog(
                heading=_("Quick Connect"),
                body=data.get("Code") or _("Error getting code"),
                extra_child=Gtk.LinkButton(
                    label=_("Quick Connect Page"),
                    uri="{}/web/#/quickconnect".format(self.url_el.get_text())
                )
            )
            dialog.add_response(
                "cancel",
                _("Cancel")
            )
            dialog.set_close_response("cancel")
            GLib.idle_add(dialog.choose,
                self.get_root(),
                None,
                lambda *_: None
            )
            GLib.idle_add(threading.Thread(target=wait_confirmation, args=(data, dialog, integration), daemon=True).start)

        if root := self.get_root():
            if app := root.get_application():
                integration = app.jellyfin
                integration.set_property('url', self.url_el.get_text())
                threading.Thread(target=run, args=(integration,), daemon=True).start()
