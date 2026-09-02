# login.py

from gi.repository import GObject, Gtk, Adw, Gio, GLib, Gdk
from ...integrations import secret
import threading, time

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/login.ui')
class LoginPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornLoginPage'

    disclaimer = GObject.Property(type=str)
    splash_paintable = GObject.Property(type=Gdk.Paintable)
    user_el = Gtk.Template.Child()
    password_el = Gtk.Template.Child()
    login_button_el = Gtk.Template.Child()
    quick_connect_button_el = Gtk.Template.Child()

    def set_jellyfin_details(self, jellyfin):
        self.set_property('splash-paintable', jellyfin.getLoginSplash())
        self.set_property('disclaimer', jellyfin.getLoginDisclaimer())

    def reset(self):
        if root := self.get_root():
            if app := root.get_application():
                if settings := app.get_property('settings'):
                    self.user_el.set_text(settings.get_value('user').unpack())
                if jellyfin := app.jellyfin:
                    threading.Thread(target=self.set_jellyfin_details, args=(jellyfin,), daemon=True).start()
        self.password_el.set_text('')

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def format_login_sensitivity(self, obj, user_text:str, password_text:str) -> bool:
        return user_text and password_text

    @Gtk.Template.Callback()
    def login_requested(self, widget=None):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.jellyfin:
                    jellyfin.set_property('user', self.user_el.get_text())
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
                    uri="{}/web/#/quickconnect".format(integration.get_property('url'))
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
                if integration := app.jellyfin:
                    threading.Thread(target=run, args=(integration,), daemon=True).start()

