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

from gi.repository import Gtk, Adw, GLib, Gst, Gio
from . import widgets as Widgets
from . import actions
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/window.ui')
class PopcornWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PopcornWindow'

    toast_overlay = Gtk.Template.Child()
    root_navigationview = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_close(self, window):
        if app := self.get_application():
            if pip_win := app.pip_window:
                if pip_win.get_visible():
                    pip_win.close()
            app.get_property('player').stop()
            app.get_property('player').event_adapter.mpris.unpublish()
            app.quit()

    @Gtk.Template.Callback()
    def on_key_pressed(self, controller, keyval, keycode, modifier):
        if visible_page := self.root_navigationview.get_visible_page():
            if visible_page.get_tag() == 'player':
                if keycode == 111: #UP
                    visible_page.activate_action('player.change-volume', GLib.Variant('d', 0.1))
                    return True
                elif keycode == 116: #DOWN
                    visible_page.activate_action('player.change-volume', GLib.Variant('d', -0.1))
                    return True
                elif keycode == 114: #RIGHT
                    visible_page.activate_action('player.seek', GLib.Variant('i', 10))
                    return True
                elif keycode == 113: #LEFT
                    visible_page.activate_action('player.seek', GLib.Variant('i', -10))
                    return True
                elif keycode == 65: #SPACE
                    visible_page.activate_action('player.toggle-playback', None)
                    return True

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
        self.create_action(actions.play_season)
        self.create_action(actions.show_episode)
        self.create_action(actions.play_episode)
        self.create_action(actions.show_movie)
        self.create_action(actions.play_movie)
        self.create_action(actions.show_user_view)
        self.create_action(actions.show_search_page, shortcuts=['<ctrl>f'], parameter_type=None)
        self.create_action(actions.toggle_played)
        self.create_action(actions.reload_page, shortcuts=['<ctrl>r'], parameter_type=None)
        self.create_action(actions.toggle_favorite)
        self.create_action(actions.open_uri)

        settings = self.get_application().get_property('settings')
        settings.connect('changed::blur-effect', self.css_toggled, 'blur-effect')
        self.css_toggled(settings, 'blur-effect', 'blur-effect')

    def css_toggled(self, settings, key:str, css_class:str):
        if settings.get_value(key).unpack():
            self.add_css_class(css_class)
        else:
            self.remove_css_class(css_class)
