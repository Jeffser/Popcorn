# main.py
#
# Copyright 2026 Jeffry Samuel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys, threading
from pydbus import SessionBus
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Secret', '1')
gi.require_version('Gst', '1.0')

from gi.repository import Gtk, GObject, Gio, Adw, GLib
from .window import PopcornWindow
from .preferences import PopcornPreferences
from . import widgets as Widgets
from .integrations import Jellyfin
from .constants import set_popcorn_version, TRANSLATORS

GLib.set_prgname('com.jeffser.Popcorn')
GLib.set_application_name("Popcorn")

class PopcornService:
    """
    <node>
        <interface name="com.jeffser.Popcorn.Service">
            <method name="Search">
                <arg type="a{sa{sv}}" name="result" direction="out"/>
                <arg type="s" name="query" direction="in"/>
            </method>
        </interface>
    </node>
    """

    def __init__(self, app):
        self.app = app

    def Search(self, query:str) -> dict:
        if jellyfin := self.app.jellyfin:
            return self.app.jellyfin.systemSearch(query)
        return {}

class PopcornApplication(Adw.Application):
    __gtype_name__ = 'PopcornApplication'
    """The main application singleton class."""

    player = GObject.Property(type=Widgets.Player)
    settings = GObject.Property(type=Gio.Settings, default=Gio.Settings(schema_id="com.jeffser.Popcorn"))

    def __init__(self, version):
        super().__init__(application_id='com.jeffser.Popcorn',
             flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
             resource_base_path='/com/jeffser/Popcorn')
        self.version = version
        self.set_property('player', Widgets.Player(application=self))
        settings = self.get_property('settings')
        self.jellyfin = Jellyfin(
            user=settings.get_value('user').unpack(),
            url=settings.get_value('url').unpack(),
            trustServer=settings.get_value('trust-server').unpack()
        )
        self.main_window = None
        self.pip_window = None

        self.create_action('quit', lambda *_: self.quit(), ['<control>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        if not self.main_window:
            self.main_window = PopcornWindow(application=self)
            threading.Thread(target=self.try_login, daemon=True).start()
        self.main_window.present()
        app_service = PopcornService(self)
        if 'linux' in sys.platform:
            bus = SessionBus()
            dbus_proxy = bus.get('org.freedesktop.DBus', '/org/freedesktop/DBus')
            if not dbus_proxy.NameHasOwner('com.jeffser.Popcorn.Service'):
                bus.publish('com.jeffser.Popcorn.Service', ('/com/jeffser/Popcorn/Service', app_service))

    def open_pip_window(self):
        if window := self.pip_window:
            window.close()
        self.pip_window = Widgets.PlayerWindow(application=self)
        self.pip_window.present()

    def on_about_action(self, *args):
        about = Adw.AboutDialog(
            application_icon='com.jeffser.Popcorn',
            application_name='Popcorn',
            copyright='© 2026 Jeffry Samuel',
            developer_name='Jeffry Samuel',
            issue_url="https://github.com/Jeffser/Popcorn/issues",
            license="GPL-3.0-or-later",
            support_url="https://github.com/Jeffser/Popcorn/discussions",
            version=self.version,
            website="https://jeffser.com/popcorn",
            developers=['Jeffser https://jeffser.com'],
            designers=['Jeffser https://jeffser.com'],
            translator_credits='\n'.join(TRANSLATORS),
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        def open_preferences_dialog():
            dialog = PopcornPreferences()
            dialog.reset(self)
            GLib.idle_add(dialog.present, self.props.active_window)
        threading.Thread(target=open_preferences_dialog, daemon=True).start()

    def try_login(self):
        if self.jellyfin.ping(): # Login Ok
            settings = self.get_property('settings')
            settings.set_string('url', self.jellyfin.get_property('url'))
            settings.set_string('user', self.jellyfin.get_property('user'))
            settings.set_boolean('trust-server', self.jellyfin.get_property('trustServer'))
            GLib.idle_add(self.main_window.root_navigationview.replace_with_tags, ['home'])
            threading.Thread(target=self.main_window.root_navigationview.find_page('home').reset).start()
        elif self.main_window.root_navigationview.get_visible_page_tag() == 'login': # Failed Login
            GLib.idle_add(self.main_window.root_navigationview.replace_with_tags, ['welcome', 'login'])
            if self.get_property('settings').get_value("user").unpack():
                toast = Adw.Toast(
                    title=_("Error logging in")
                )
                GLib.idle_add(self.main_window.toast_overlay.add_toast, toast)
            GLib.idle_add(self.main_window.root_navigationview.find_page('login').reset)
        else: # First Login
            GLib.idle_add(self.main_window.root_navigationview.replace_with_tags, ['welcome'])
            GLib.idle_add(self.main_window.root_navigationview.find_page('welcome').reset)

    def create_action(self, name, callback, shortcuts=None, parameter_type=None):
        action = Gio.SimpleAction.new(name, parameter_type)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

def main(version):
    print("Popcorn version", version)
    set_popcorn_version(version)
    return PopcornApplication(version).run(sys.argv)

