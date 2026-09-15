# login.py

from gi.repository import GObject, Gtk, Adw, Gio, GLib, Gdk
from ...integrations import secret, jellyfin
import threading, time, io, segno

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/login_dialog.ui')
class LoginDialog(Adw.Dialog):
    __gtype_name__ = 'PopcornLoginDialog'

    disclaimer = GObject.Property(type=str)
    quick_connect_code = GObject.Property(type=str)
    temp_jellyfin = GObject.Property(type=jellyfin.Jellyfin, default=jellyfin.Jellyfin())
    quick_connect_qr_paintable = GObject.Property(type=Gdk.Paintable)

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
        if jellyfin := self.get_property('temp-jellyfin'):
            jellyfin.set_property('user', secret.ServerUser())
            url = self.url_entry.get_text()
            if not url.startswith('http'):
                url = 'http://{}'.format(url)
            jellyfin.get_property('user').set_property('server-address', url)
            jellyfin.get_property('user').set_property('trust-certificates', self.trust_checkbutton.get_active())
            threading.Thread(target=self.try_connect, daemon=True).start()

    def try_connect(self):
        if jellyfin := self.get_property('temp-jellyfin'):
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
            if jellyfin := self.get_property('temp-jellyfin'):
                jellyfin.get_property('user').set_property('username', username)
                jellyfin.get_property('user').set_property('quick-connect', False)
                jellyfin.get_property('user').update_changes(password)
                if jellyfin.ping():
                    GLib.idle_add(self.get_root().root_navigationview.replace_with_tags, ['user-selector'])
                    threading.Thread(target=self.get_root().root_navigationview.find_page('user-selector').reset, daemon=True).start()
                    GLib.idle_add(lambda: self.close() and False)
                else:
                    toast = Adw.Toast(
                        title=_("Error logging in")
                    )
                    GLib.idle_add(self.toast_overlay.add_toast, toast)
                    jellyfin.get_property('user').remove_user()
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
        waited_turns = 10
        result_secret = False
        data = jellyfin.initiateQuickConnect()
        self.set_property('quick-connect-code', data.get("Code") or _("Error getting code"))
        if data.get('Code'):
            self.set_property('quick-connect-qr-paintable', None)
            try:
                url = self.format_quick_connect_uri(None, jellyfin.get_property('user').get_property('server-address'), data.get('Code'))
                qr = segno.make_qr(url)
                buffer = io.BytesIO()
                qr.save(buffer, kind="png", scale=10)
                buffer.seek(0)
                raw_bytes = buffer.getvalue()
                self.set_property('quick-connect-qr-paintable', Gdk.Texture.new_from_bytes(GLib.Bytes.new(raw_bytes)))
            except Exception as e:
                print(e)
                pass

            # Wait for response
            while waited_turns > 0 and not result_secret and self.navigation_view.get_visible_page_tag() == 'quick-connect' and self.get_root():
                result_secret = jellyfin.checkQuickConnect(data.get('Secret'))
                time.sleep(5)
                waited_turns -= 1

            jellyfin.get_property('user').set_property('username', '')
            if result_secret:
                jellyfin.get_property('user').set_property('quick-connect', True)
                jellyfin.get_property('user').update_changes(result_secret)
                if jellyfin.ping():
                    jellyfin.get_property('user').update_changes() # Saves username
                    GLib.idle_add(self.get_root().root_navigationview.replace_with_tags, ['user-selector'])
                    threading.Thread(target=self.get_root().root_navigationview.find_page('user-selector').reset, daemon=True).start()
                    GLib.idle_add(lambda: self.close() and False)
                else:
                    jellyfin.get_property('user').set_property('quick-connect', False)
                    self.set_property('quick-connect-code', _("Timed Out") if waited_turns == 0 else _("Error"))
                    toast = Adw.Toast(
                        title=_("Error logging in")
                    )
                    GLib.idle_add(self.toast_overlay.add_toast, toast)
                    jellyfin.get_property('user').remove_user()
            else:
                jellyfin.get_property('user').set_property('quick-connect', False)
                toast = Adw.Toast(
                    title=_("Error logging in")
                )
                GLib.idle_add(self.toast_overlay.add_toast, toast)
                jellyfin.get_property('user').remove_user()

    @Gtk.Template.Callback()
    def quick_connect_requested(self, button):
        if jellyfin := self.get_property('temp-jellyfin'):
            self.set_property('quick-connect-code', '')
            self.navigation_view.push_by_tag('quick-connect')
            threading.Thread(target=self.quick_connect_verify_loop, args=(jellyfin,), daemon=True).start()

    @Gtk.Template.Callback()
    def format_quick_connect_uri(self, obj, base_url:str, quick_connect_code:str) -> str:
        return "{}/web/#/quickconnect?code={}".format(base_url.strip('/'), quick_connect_code)


