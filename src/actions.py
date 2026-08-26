# actions.py

from gi.repository import Adw, GLib
from . import widgets as Widgets

# -- Helpers --

def __show_page(window, page:Adw.NavigationPage):
    if app := window.get_application():
        if main_window := app.main_window:
            GLib.idle_add(main_window.root_navigationview.push, page)

# -- Series --

def show_series(window, series_id:str):
    if app := window.get_application():
        if jellyfin := app.jellyfin:
            page = Widgets.SeriesPage(model=jellyfin.getModel(series_id))
            __show_page(window, page)

