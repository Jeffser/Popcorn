# actions.py

from gi.repository import Adw, GLib
from . import widgets as Widgets
import threading

# -- Helpers --

def __show_page(window, page:Adw.NavigationPage):
    if app := window.get_application():
        if main_window := app.main_window:
            thread = threading.Thread(target=page.reset)
            GLib.idle_add(main_window.root_navigationview.push, page)
            GLib.idle_add(thread.start)

# -- Series --

def show_series(window, series_id:str):
    if app := window.get_application():
        if jellyfin := app.jellyfin:
            page = Widgets.SeriesPage(model=jellyfin.getModel(series_id))
            __show_page(window, page)

# -- Seasons --

def show_season(window, id_dict:dict):
    series_id = id_dict.get('series')
    season_id = id_dict.get('season')
    if series_id and season_id:
        if app := window.get_application():
            if jellyfin := app.jellyfin:
                page = Widgets.SeasonPage(
                    model=jellyfin.getModel(season_id),
                    series_model=jellyfin.getModel(series_id)
                )
                __show_page(window, page)
