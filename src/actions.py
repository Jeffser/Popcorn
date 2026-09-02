# actions.py

from gi.repository import Adw, GLib, Gio
from . import widgets as Widgets
import threading, os

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

# -- Misc --

def show_user_view(app, user_view_id:str):
    if jellyfin := app.jellyfin:
        if model := jellyfin.getModel(user_view_id):
            getter_function = lambda limit, startIndex, jellyfin, uvid=user_view_id: jellyfin.getModelsFromFolder(uvid, limit, startIndex)
            page = Widgets.WrapboxPage(
                getter_cb=getter_function,
                title=model.get_property('Name')
            )
            __show_page(app, page)

def show_search_page(app):
    if main_window := app.main_window:
        if current_page := main_window.root_navigationview.get_visible_page():
            if current_page.get_tag() != 'player' or (app.pip_window and app.pip_window.get_visible()):
                if current_page.get_tag() == 'search':
                    main_window.set_focus(current_page.search_entry)
                else:
                    page = Widgets.SearchPage()
                    __show_page(app, page)

def reload_page(app):
    if main_window := app.main_window:
        if current_page := main_window.root_navigationview.get_visible_page():
            thread = threading.Thread(target=current_page.reset)
            GLib.idle_add(thread.start)

def toggle_played(app, model_id:str):
    if jellyfin := app.jellyfin:
        if model := jellyfin.loaded_models.get(model_id):
            jellyfin.setPlayedStatus(model_id, not model.get_property('Played'))

def toggle_favorite(app, model_id:str):
    if jellyfin := app.jellyfin:
        if model := jellyfin.loaded_models.get(model_id):
            jellyfin.setFavorite(model_id, not model.get_property('IsFavorite'))

def open_uri(app, uri:str):
    if uri.startswith('file://'):
        uri = Gio.File.new_for_path(uri.removeprefix('file://')).get_uri()
        os.system('xdg-open {}'.format(uri))
        return

    Gio.AppInfo.launch_default_for_uri(uri, None)
