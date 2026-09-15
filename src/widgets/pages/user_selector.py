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
    icon_name = GObject.Property(type=str, default='person-symbolic')
    server_name = GObject.Property(type=str)
    context_popover = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_secondary_click(self, gesture, n_press, x, y):
        rect = Gdk.Rectangle()
        rect.x, rect.y = int(x), int(y)
        if not self.context_popover.get_parent():
            self.context_popover.set_parent(gesture.get_widget())
        self.context_popover.set_pointing_to(rect)
        self.context_popover.popup()

    @Gtk.Template.Callback()
    def on_long_press(self, gesture, x, y):
        rect = Gdk.Rectangle()
        rect.x, rect.y = int(x), int(y)
        if not self.context_popover.get_parent():
            self.context_popover.set_parent(gesture.get_widget())
        self.context_popover.set_pointing_to(rect)
        self.context_popover.popup()

    def update_information(self):
        self.set_property('avatar-paintable', Adw.SpinnerPaintable(widget=self))
        self.set_property('server-name', '')
        if temp_jellyfin := jellyfin.Jellyfin(user=self.get_property('model')):
            if temp_jellyfin.ping():
                self.set_sensitive(True)
                self.set_property('icon-name', 'person-symbolic')
                if server_info := temp_jellyfin.getServerInformation():
                    self.set_property('avatar-paintable', server_info.get('picture'))
                    self.set_property('server-name', server_info.get('title'))
            else:
                self.set_sensitive(False)
                self.set_property('icon-name', 'network-wired-disconnected-symbolic')

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
                            app.get_property('settings').set_string('default-user-id', model.get_property('id'))
                            GLib.idle_add(root.root_navigationview.replace_with_tags, ['main'])
                            GLib.idle_add(root.root_navigationview.find_page('main').setup)
                        else:
                            toast = Adw.Toast(
                                title=_("Error logging in")
                            )
                            GLib.idle_add(root.toast_overlay.add_toast, toast)
                            jellyfin.set_property('user', secret.ServerUser())
        if model := self.get_property('model'):
            threading.Thread(target=run, args=(model,), daemon=True).start()

    @Gtk.Template.Callback()
    def remove_user_requested(self, button):
        self.context_popover.popdown()
        def on_response(task, result):
            if task.choose_finish(result) == 'delete':
                self.get_property('model').remove_user()
                self.unparent()

        username = self.get_property('model').get_property('username')
        dialog = Adw.AlertDialog(
            heading=_("Delete User"),
            body=_("Are you sure you want to delete '{}'?").format(username) if username else _("Are you sure you want to delete this user?")
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("delete", _("Delete"))
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("delete")
        dialog.set_close_response("cancel")
        dialog.choose(self.get_root(), None, on_response)

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
            if root := self.get_root():
                GLib.idle_add(LoginDialog().present, root)

    @Gtk.Template.Callback()
    def add_user_requested(self, button):
        if root := self.get_root():
            LoginDialog().present(root)
            
