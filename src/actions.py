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

def show_season(window, season_id:dict):
    if app := window.get_application():
        if jellyfin := app.jellyfin:
            if season_model := jellyfin.getModel(season_id):
                if series_model := jellyfin.getModel(season_model.get_property('SeriesId')):
                    page = Widgets.SeasonPage(
                        model=season_model,
                        series_model=series_model
                    )
                    __show_page(window, page)

# -- Episodes --

def show_episode(window, episode_id:dict):
    if app := window.get_application():
        if jellyfin := app.jellyfin:
            if episode_model := jellyfin.getModel(episode_id):
                if series_model := jellyfin.getModel(episode_model.get_property('SeriesId')):
                    page = Widgets.EpisodePage(
                        model=episode_model,
                        series_model=series_model
                    )
                    __show_page(window, page)
