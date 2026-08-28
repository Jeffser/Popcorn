# actions.py

from gi.repository import Adw, GLib
from . import widgets as Widgets
import threading

# -- Helpers --

def __show_page(app, page:Adw.NavigationPage):
    if main_window := app.main_window:
        thread = threading.Thread(target=page.reset)
        GLib.idle_add(main_window.root_navigationview.push, page)
        GLib.idle_add(thread.start)

def __play_model(app, model):
    if player := app.get_property('player'):
        player.set_property('model', model)
        if not app.pip_window or not app.pip_window.get_visible():
            page = Widgets.PlayerPage(
                player=player
            )
            __show_page(app, page)

# -- Series --

def show_series(app, series_id:str):
    if jellyfin := app.jellyfin:
        if series_model := jellyfin.getModel(series_id):
            page = Widgets.SeriesPage(model=series_model)
            __show_page(app, page)

def play_series(app, series_id:str):
    if jellyfin := app.jellyfin:
        if episode_model := jellyfin.getSeriesNextUp(series_id):
            __play_model(app, episode_model)

# -- Seasons --

def show_season(app, season_id:str):
    if jellyfin := app.jellyfin:
        if season_model := jellyfin.getModel(season_id):
            if series_model := jellyfin.getModel(season_model.get_property('SeriesId')):
                page = Widgets.SeasonPage(
                    model=season_model,
                    series_model=series_model
                )
                __show_page(app, page)

def play_season(app, season_id:str):
    if jellyfin := app.jellyfin:
        if episode_model := jellyfin.getSeasonNextUp(season_id):
            __play_model(app, episode_model)

# -- Episodes --

def show_episode(app, episode_id:str):
    if jellyfin := app.jellyfin:
        if episode_model := jellyfin.getModel(episode_id):
            if series_model := jellyfin.getModel(episode_model.get_property('SeriesId')):
                page = Widgets.EpisodePage(
                    model=episode_model,
                    series_model=series_model
                )
                __show_page(app, page)

def play_episode(app, episode_id:str):
    if jellyfin := app.jellyfin:
        if episode_model := jellyfin.getModel(episode_id):
            __play_model(app, episode_model)

# -- Movie --

def show_movie(app, movie_id:str):
    if jellyfin := app.jellyfin:
        if movie_model := jellyfin.getModel(movie_id):
            page = Widgets.MoviePage(
                model=movie_model
            )
            __show_page(app, page)

def play_movie(app, movie_id:str):
    if jellyfin := app.jellyfin:
        if movie_model := jellyfin.getModel(movie_id):
            __play_model(app, movie_model)
