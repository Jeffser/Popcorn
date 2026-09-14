# user_selector.py

from gi.repository import Gtk, Gdk, Adw, GLib, GObject
from ...integrations import secret, jellyfin
from .login import LoginDialog
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/user_selector_button.ui')
class UserSelectorButton(Gtk.Button):
    __gtype_name__ = 'PopcornUserSelectorButton'

    model = GObject.Property(type=secret.ServerUser)
    avatar_paintable = GObject.Property(type=Gdk.Paintable)
    server_name = GObject.Property(type=str)

    def update_information(self):
        self.set_property('avatar-paintable', None)
        self.set_property('server-name', '')
        if temp_jellyfin := jellyfin.Jellyfin(user=self.get_property('model')):
            if temp_jellyfin.ping():
                if server_info := temp_jellyfin.getServerInformation():
                    self.set_property('avatar-paintable', server_info.get('picture'))
                    self.set_property('server-name', server_info.get('title'))

    @Gtk.Template.Callback()
    def format_subtitle(self, obj, server_name:str, server_address:str) -> str:
        if server_name:
            return '{}\n{}'.format(server_name, server_address)
        else:
            return server_address

    @Gtk.Template.Callback()
    def on_click(self, button):
        def run(model):
            if root := self.get_root():
                if app := root.get_application():
                    if jellyfin := app.get_property('jellyfin'):
                        jellyfin.set_property('user', model)
                        if jellyfin.ping():
                            GLib.idle_add(root.root_navigationview.replace_with_tags, ['main'])
                            GLib.idle_add(root.root_navigationview.find_page('main').setup)
                        else:
                            toast = Adw.Toast(
                                title=_("Error logging in")
                            )
                            GLib.idle_add(root.toast_overlay.add_toast, toast)
        if model := self.get_property('model'):
            threading.Thread(target=run, args=(model,), daemon=True).start()

@Gtk.Template(resource_path='/com/jeffser/Popcorn/pages/user_selector.ui')
class UserSelectorPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornUserSelectorPage'

    wrapbox = Gtk.Template.Child()

    def reset(self):
        GLib.idle_add(self.wrapbox.remove_all)
        user_models = secret.list_users()
        if len(user_models) > 0:
            for user_model in user_models:
                button = UserSelectorButton(model=user_model)
                GLib.idle_add(self.wrapbox.append, button)
                threading.Thread(target=button.update_information, daemon=True).start()
        else:
            GLib.idle_add(self.wrapbox.append, Gtk.Button(
                tooltip_text=_("Add User"),
                child=Adw.ButtonContent(
                    icon_name="list-add-symbolic",
                    label=_("Add User")
                ),
                css_classes=['pill', 'suggested-action'],
                halign=Gtk.Align.CENTER
            ))
            if root := self.get_root():
                GLib.idle_add(LoginDialog().present, root)

    @Gtk.Template.Callback()
    def add_user_requested(self, button):
        if root := self.get_root():
            LoginDialog().present(root)
            
