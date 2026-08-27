# window.py
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

from gi.repository import Gtk, Adw, GLib, Gst
from . import widgets as Widgets
from . import actions
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/window.ui')
class PopcornWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PopcornWindow'

    root_navigationview = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_close(self, window):
        if app := self.get_application():
            if app.pip_window.get_visible():
                app.pip_window.close()
            app.get_property('player').get_property('gst').set_state(Gst.State.NULL)
            app.get_property('player').event_adapter.mpris.unpublish()
            app.quit()

    def create_action(self, callback:callable, shortcuts:list=[], parameter_type:str="s"):
        def call_action(cb, va):
            if va is None:
                cb(self.get_application())
            else:
                cb(self.get_application(), va.unpack())

        self.get_application().create_action(
            name=callback.__name__,
            callback=lambda at, va, cb=callback: threading.Thread(target=call_action, args=(cb, va), daemon=True).start(),
            shortcuts=shortcuts,
            parameter_type=GLib.VariantType.new(parameter_type) if parameter_type else None
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.create_action(actions.show_series)
        self.create_action(actions.play_series)
        self.create_action(actions.show_season)
        self.create_action(actions.show_episode)
        self.create_action(actions.play_episode)
        self.create_action(actions.show_movie)
        self.create_action(actions.play_movie)
