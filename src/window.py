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

from gi.repository import Gtk, Adw, GLib, Gst, Gio, Pango
from . import widgets as Widgets
from . import actions
import threading

@Gtk.Template(resource_path='/com/jeffser/Popcorn/window.ui')
class PopcornWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PopcornWindow'

    toast_overlay = Gtk.Template.Child()
    loading_stack = Gtk.Template.Child()
    auth_navigationview = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    home_nav_view = Gtk.Template.Child()
    search_nav_view = Gtk.Template.Child()
    library_nav_view = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()

    def get_active_nav_view(self) -> Adw.NavigationView:
        """The Adw.NavigationView belonging to whichever main_stack
        section (home/search) is currently visible. Used to push
        detail pages (series/movie/episode/season/player) on top of
        the right section, and to inspect the currently visible page
        (e.g. to check for the player tag on key events).
        """
        return self.main_stack.get_visible_child()

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
        if self.loading_stack.get_visible_child_name() != 'main':
            return
        nav_view = self.get_active_nav_view()
        if visible_page := nav_view.get_visible_page():
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
        self.create_action(actions.logout, parameter_type=None)

        settings = self.get_application().get_property('settings')
        settings.connect('changed::blur-effect', self.css_toggled, 'blur-effect')
        self.css_toggled(settings, 'blur-effect', 'blur-effect')

        list(list(list(list(self.header_bar)[0])[0])[1])[0].set_ellipsize(Pango.EllipsizeMode.NONE)

    def css_toggled(self, settings, key:str, css_class:str):
        if settings.get_value(key).unpack():
            self.add_css_class(css_class)
        else:
            self.remove_css_class(css_class)
