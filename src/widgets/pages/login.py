# login.py

from gi.repository import GObject, Gtk, Adw, Gio, GLib, Gdk
from ...integrations import secret
import threading, time

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/login_dialog.ui')
class LoginDialog(Adw.Dialog):
    __gtype_name__ = 'PopcornLoginDialog'

    disclaimer = GObject.Property(type=str)
    quick_connect_code = GObject.Property(type=str)

    toast_overlay = Gtk.Template.Child()
    navigation_view = Gtk.Template.Child()

    # Connect
    url_entry = Gtk.Template.Child()
    trust_checkbutton = Gtk.Template.Child()

    # Login
    user_el = Gtk.Template.Child()
    password_el = Gtk.Template.Child()
    login_button_el = Gtk.Template.Child()
    quick_connect_button_el = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def connect_requested(self, button):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.get_property('jellyfin'):
                    url = self.url_entry.get_text()
                    if not url.startswith('http'):
                        url = 'http://{}'.format(url)
                    jellyfin.get_property('user').set_property('server-address', url)
                    jellyfin.get_property('user').set_property('trust-certificates', self.trust_checkbutton.get_active())
                    threading.Thread(target=self.try_connect, daemon=True).start()

    def try_connect(self):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.get_property('jellyfin'):
                    if jellyfin.checkHealth():
                        self.set_property('disclaimer', jellyfin.getLoginDisclaimer())
                        GLib.idle_add(self.navigation_view.push_by_tag, 'login')
                    else:
                        toast = Adw.Toast(
                            title=_("Error connecting to server")
                        )
                        GLib.idle_add(self.toast_overlay.add_toast, toast)

    @Gtk.Template.Callback()
    def login_requested(self, widget=None):
        def run(username:str, password:str):
            if root := self.get_root():
                if app := root.get_application():
                    if jellyfin := app.get_property('jellyfin'):
                        jellyfin.get_property('user').set_property('username', username)
                        jellyfin.get_property('user').set_property('quick-connect', False)
                        jellyfin.get_property('user').update_changes(password)
                        if jellyfin.ping():
                            GLib.idle_add(root.root_navigationview.replace_with_tags, ['user-selector'])
                            threading.Thread(target=root.root_navigationview.find_page('user-selector').reset, daemon=True).start()
                            GLib.idle_add(self.close)
                        else:
                            toast = Adw.Toast(
                                title=_("Error logging in")
                            )
                            GLib.idle_add(self.toast_overlay.add_toast, toast)
        if username := self.user_el.get_text():
            if password := self.password_el.get_text():
                threading.Thread(target=run, args=(username, password), daemon=True).start()

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def format_login_sensitivity(self, obj, user_text:str, password_text:str) -> bool:
        return user_text and password_text

    def quick_connect_verify_loop(self, jellyfin):
        waited_turns = 0
        result_secret = False
        data = jellyfin.initiateQuickConnect()
        self.set_property('quick-connect-code', data.get("Code") or _("Error getting code"))
        if data.get('Code'):
            while waited_turns < 5 and not result_secret and self.navigation_view.get_visible_page_tag() == 'quick-connect' and self.get_root():
                result_secret = jellyfin.checkQuickConnect(data.get('Secret'))
                time.sleep(5)
                waited_turns += 1

            jellyfin.get_property('user').set_property('username', '')
            if result_secret:
                jellyfin.get_property('user').set_property('quick-connect', True)
                jellyfin.get_property('user').update_changes(result_secret)
                if jellyfin.ping():
                    GLib.idle_add(root.root_navigationview.replace_with_tags, ['user-selector'])
                    threading.Thread(target=root.root_navigationview.find_page('user-selector').reset, daemon=True).start()
                    GLib.idle_add(self.close)
                else:
                    toast = Adw.Toast(
                        title=_("Error logging in")
                    )
                    GLib.idle_add(self.toast_overlay.add_toast, toast)
            else:
                jellyfin.get_property('user').set_property('quick-connect', False)
                jellyfin.get_property('user').update_changes()
                toast = Adw.Toast(
                    title=_("Error logging in")
                )
                GLib.idle_add(self.toast_overlay.add_toast, toast)

    @Gtk.Template.Callback()
    def quick_connect_requested(self, button):
        if root := self.get_root():
            if app := root.get_application():
                if jellyfin := app.get_property('jellyfin'):
                    self.set_property('quick-connect-code', '')
                    self.navigation_view.push_by_tag('quick-connect')
                    threading.Thread(target=self.quick_connect_verify_loop, args=(jellyfin,), daemon=True).start()

    @Gtk.Template.Callback()
    def format_quick_connect_uri(self, obj, base_url:str) -> str:
        return "{}/web/#/quickconnect".format(base_url.strip('/'))

