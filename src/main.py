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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Secret', '1')
gi.require_version('Gst', '1.0')

from gi.repository import Gtk, Gio, Adw, GLib
from .window import PopcornWindow

GLib.set_prgname('com.jeffser.Popcorn')
GLib.set_application_name("Popcorn")

class PopcornApplication(Adw.Application):
    __gtype_name__ = 'PopcornApplication'
    """The main application singleton class."""

    def __init__(self, version):
        self.version = version
        self.main_window = None
        super().__init__(application_id='com.jeffser.Popcorn',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/com/jeffser/Popcorn')

        self.create_action('quit', lambda *_: self.quit(), ['<control>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        if not self.main_window:
            self.main_window = PopcornWindow(application=self)
        self.main_window.present()

    def on_about_action(self, *args):
        about = Adw.AboutDialog(application_name='Popcorn',
                                application_icon='com.jeffser.Popcorn',
                                developer_name='Jeffry Samuel',
                                version='0.1.0',
                                translator_credits = _('translator-credits'),
                                developers=['Jeffry Samuel'],
                                copyright='© 2026 Jeffry Samuel')
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

def main(version):
    print("Popcorn version", version)
    return PopcornApplication(version).run(sys.argv)
