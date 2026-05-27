# login.py

from gi.repository import Gtk, Adw, Gio, GLib

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
        self.url_el.set_text('http://127.0.0.1:8096')
        self.user_el.set_text('')
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
        print('LOGIN!!!')

    @Gtk.Template.Callback()
    def quick_connect_requested(self, button):
        print('QUICK CONNECT!!!')
