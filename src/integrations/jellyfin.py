# jellyfin.py

from gi.repository import Gtk, GLib, GObject, Gdk
from . import models, secret
import requests, io, urllib3, platform

# Just so that the logs don't get cluttered with warnings if trust-server = True
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Jellyfin(GObject.Object):
    __gtype_name__ = 'PopcornIntegrationJellyfin'

    AUTH_HEADER = 'MediaBrowser Client="Popcorn", Device="{}", DeviceId="{}", Version="1.0.0"'.format(platform.node(), str(abs(hash(platform.node()))))

    # Loaded when login
    trustServer = GObject.Property(type=bool, default=False)
    url = GObject.Property(type=str)
    user = GObject.Property(type=str)

    # Loaded by API
    accessToken = GObject.Property(type=str)
    userId = GObject.Property(type=str)

    loaded_models = {}

    def getBaseHeader(self) -> dict:
        headers = {
            "Authorization": self.AUTH_HEADER
        }
        if token := self.get_property('accessToken'):
            headers["Authorization"] += ', Token="{}"'.format(token)
        return headers

    def getUrl(self, action:str, **keys) -> str:
        action = action.format(userId=self.get_property('userId'), **keys)
        return '{}/{}'.format(self.get_property('url').strip('/'), action)

    def getStreamUrl(self, model_id:str) -> str:
        return self.getUrl('Videos/{model_id}/stream?static=true&api_key={api_key}', model_id=model_id, api_key=self.get_property('accessToken'))
        #return self.getUrl('Videos/{model_id}/master.m3u8?api_key={api_key}', model_id=model_id, api_key=self.get_property('accessToken'))

    def makeRequest(self, action:str, json:dict={}, params:dict={}, mode:str="GET", action_keys:dict={}) -> dict:
        headers = {
            **self.getBaseHeader(),
            "Accept": "application/json"
        }
        try:
            if mode == 'GET':
                response = requests.get(
                    self.getUrl(action, **action_keys),
                    params=params,
                    json=json,
                    headers=headers,
                    verify=not self.get_property('trustServer')
                )
            elif mode == 'POST':
                response = requests.post(
                    self.getUrl(action, **action_keys),
                    params=params,
                    json=json,
                    headers=headers,
                    verify=not self.get_property('trustServer')
                )
            elif mode == 'DELETE':
                response = requests.delete(
                    self.getUrl(action, **action_keys),
                    params=params,
                    json=json,
                    headers=headers,
                    verify=not self.get_property('trustServer')
                )
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 204:
                return {'state': 'ok'}
        except Exception as e:
            print(e)
            pass
        return {}

    def __makeModel(self, item:dict) -> models.BasicModel | None:
        if item.get('Type') == 'Series':
            model = models.Series(
                Id=item.get('Id'),
                Name=item.get('Name'),
                CommunityRating=round(item.get('CommunityRating') or 0, 1),
                ProductionYear=item.get('ProductionYear'),
                OfficialRating=item.get('OfficialRating'),
                SeasonCount=item.get('ChildCount') or 1,
                Overview=item.get('Overview'),
                LogoPaintable=self.getPaintable(item.get('Id'), image_type='logo'),
                BackdropPaintable=self.getPaintable(item.get('Id')),
                PrimaryPaintable=self.getPaintable(item.get('Id'), image_type='Primary'),
                Played=item.get('UserData', {}).get('Played', False)
            )
            model.get_property('Genres').remove_all()
            model.get_property('Genres').splice(
                0,
                0,
                [Gtk.StringObject.new(genre) for genre in item.get('Genres', [])]
            )
            return model
        elif item.get('Type') == 'Episode':
            return models.Episode(
                Id=item.get('Id'),
                Name=item.get('Name'),
                SeriesName=item.get('SeriesName'),
                SeriesId=item.get('SeriesId'),
                SeasonNumber=item.get('ParentIndexNumber'),
                EpisodeNumber=item.get('IndexNumber'),
                PrimaryPaintable=self.getPaintable(item.get('Id'), image_type='Primary'),
                BackdropPaintable=self.getPaintable(item.get('SeriesId')),
                SeriesPrimaryPaintable=self.getPaintable(item.get('SeriesId'), image_type='Primary'),
                Progress=item.get('UserData', {}).get('PlayedPercentage', 0) / 100,
                Overview=item.get('Overview'),
                CommunityRating=round(item.get('CommunityRating') or 0, 1),
                Duration=round((item.get('RunTimeTicks') or 0) / 10_000_000, 2),
                Played=item.get('UserData', {}).get('Played', False)
            )
        elif item.get('Type') == 'Movie':
            model = models.Movie(
                Id=item.get('Id'),
                Name=item.get('Name'),
                CommunityRating=round(item.get('CommunityRating') or 0, 1),
                ProductionYear=item.get('ProductionYear'),
                OfficialRating=item.get('OfficialRating'),
                Overview=item.get('Overview'),
                LogoPaintable=self.getPaintable(item.get('Id'), image_type='logo'),
                BackdropPaintable=self.getPaintable(item.get('Id')),
                PrimaryPaintable=self.getPaintable(item.get('Id'), image_type='Primary'),
                Played=item.get('UserData', {}).get('Played', False),
                Progress=item.get('UserData', {}).get('PlayedPercentage', 0) / 100,
                Duration=round((item.get('RunTimeTicks') or 0) / 10_000_000, 2)
            )
            model.get_property('Genres').remove_all()
            model.get_property('Genres').splice(
                0,
                0,
                [Gtk.StringObject.new(genre) for genre in item.get('Genres', [])]
            )
            return model
        elif item.get('Type') == 'Season':
            return models.Season(
                Id=item.get('Id'),
                Name=item.get('Name'),
                SeriesId=item.get('SeriesId'),
                IndexNumber=item.get('IndexNumber'),
                PrimaryPaintable=self.getPaintable(item.get('Id'), image_type='Primary') or self.getPaintable(item.get('SeriesId'), image_type='Primary'),
                Played=item.get('UserData', {}).get('Played', False)
            )
        elif item.get('Type') in ('CollectionFolder', 'UserView'):
            if item.get('CollectionType') in ('tvshows', 'movies'):
                return models.UserView(
                    Id=item.get('Id'),
                    Name=item.get('Name'),
                    CollectionType=item.get('CollectionType')
                )

    def initiateQuickConnect(self) -> dict:
        return self.makeRequest(
            action='QuickConnect/Initiate',
            mode='POST',
        )

    def checkQuickConnect(self, secret_str:str) -> bool:
        response = self.makeRequest(
            action='QuickConnect/Connect',
            params={'secret': secret_str}
        )
        if response.get('Authenticated'):
            secret.store_password(response.get("Secret"))
            return True
        return False

    def ping(self) -> bool:
        self.set_property('accessToken', "")
        self.set_property('userId', "")
        response = self.makeRequest(
            action='Users/AuthenticateWithQuickConnect',
            json={
                "Secret": secret.get_plain_password()
            },
            mode='POST'
        )
        self.set_property('accessToken', response.get('AccessToken'))
        self.set_property('userId', response.get('User', {}).get('Id'))
        if self.get_property("accessToken") and self.get_property("userId"):
            self.set_property("user", response.get('User', {}).get('Name'))
        else:
            response = self.makeRequest(
                action='Users/AuthenticateByName',
                json={
                    'Username': self.get_property('user'),
                    'Pw': secret.get_plain_password()
                },
                mode='POST'
            )
            self.set_property('accessToken', response.get('AccessToken'))
            self.set_property('userId', response.get('User', {}).get('Id'))
        return self.get_property('accessToken') and self.get_property('userId')

    def getUserViews(self) -> list:
        # Returns list of UserView models
        view_models = []
        items = self.makeRequest(
            action='Users/{userId}/Views'
        ).get('Items', [])

        for item in items:
            if model := self.__makeModel(item):
                view_models.append(model)
        return view_models

    def getPaintable(self, item_id, image_type:str="Backdrop", max_width:int=1280) -> Gdk.Paintable | None:
        try:
            url = self.getUrl("Items/{item_id}/Images/{image_type}", item_id=item_id, image_type=image_type)
            response = requests.get(url, params={'maxWidth': max_width, 'quality': 85}, timeout=5)
            response.raise_for_status()
            gbytes = GLib.Bytes.new(response.content)
            return Gdk.Texture.new_from_bytes(gbytes)
        except:
            pass
        return None

    def getFeaturedSeries(self) -> list:
        # Returns list of Series model
        series_models = []
        items = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'IncludeItemTypes': 'Series',
                'Recursive': 'true',
                'SortBy': 'Random',
                'Limit': 5,
                'fields': 'Genres,Overview,OfficialRating,RecursiveItemCount,ChildCount'
            }
        ).get('Items', [])

        for item in items:
            if model := self.__makeModel(item):
                series_models.append(model)
        return series_models

    def getResume(self) -> list:
        # Returns list of episode model
        episode_models = []
        items = self.makeRequest(
            action='Users/{userId}/Items/Resume',
            params={
                'limit': 10,
                'mediaTypes': 'Video',
                'Types': 'Episode',
                'fields': 'Overview'
            }
        ).get('Items', [])
        for item in items:
            if model := self.__makeModel(item):
                episode_models.append(model)
        return episode_models

    def getNextUp(self) -> list:
        # Returns list of episode model
        episode_models = []
        items = self.makeRequest(
            action='Shows/NextUp',
            params={
                'limit': 10,
                'mediaTypes': 'Video',
                'Types': 'Episode',
                'fields': 'Overview'
            }
        ).get('Items', [])
        for item in items:
            if model := self.__makeModel(item):
                episode_models.append(model)
        return episode_models

    def getUserAvatar(self) -> Gdk.Paintable | None:
        try:
            url = self.getUrl("Users/{userId}/Images/Primary")
            response = requests.get(url, params={'quality': 85}, timeout=5)
            response.raise_for_status()
            gbytes = GLib.Bytes.new(response.content)
            return Gdk.Texture.new_from_bytes(gbytes)
        except:
            pass
        return None

    def getLatest(self, libraryId:str) -> dict:
        # Returns dict of lists
        result_models = {
            'Series': [],
            'Episode': [],
            'Movie': []
        }
        items = self.makeRequest(
            action='Users/{userId}/Items/Latest',
            params={
                'limit': 10,
                'mediaTypes': 'Video',
                'parentId': libraryId,
                'fields': 'Genres,Overview,OfficialRating,RecursiveItemCount,ChildCount'
            }
        )
        for item in items:
            if item.get('Type') in list(result_models):
                if model := self.__makeModel(item):
                    result_models[item.get('Type')].append(model)
        return result_models

    def getModel(self, modelId:str) -> models.BasicModel | None:
        item = self.makeRequest(
            action='Users/{userId}/Items/{itemId}',
            action_keys={
                'itemId': modelId
            }
        )
        return self.__makeModel(item)

    def getSeasons(self, seriesId:str) -> list:
        # Returns list of season models
        season_models = []
        items = self.makeRequest(
            action='Shows/{seriesId}/Seasons',
            action_keys={
                'seriesId': seriesId
            },
            params={
                'fields': 'ChildCount'
            }
        ).get('Items', [])
        for item in items:
            if model := self.__makeModel(item):
                season_models.append(model)
        return season_models

    def getRecommendations(self, seriesId:str) -> list:
        # Returns list of Series/Movies models
        result_models = {
            'Series': [],
            'Movie': []
        }
        items = self.makeRequest(
            action='Items/{seriesId}/Similar',
            action_keys={
                'seriesId': seriesId
            },
            params={
                'limit': 10,
                'fields': 'Genres,Overview,OfficialRating,RecursiveItemCount,ChildCount'
            }
        ).get('Items', [])
        for item in items:
            if item.get('Type') in list(result_models):
                if model := self.__makeModel(item):
                    result_models[item.get('Type')].append(model)
        return result_models

    def getEpisodesFromSeason(self, season_id:str) -> list:
        # Returns list of episode model
        episode_models = []
        items = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'ParentId': season_id,
                'IncludeItemTypes': 'Episode',
                'fields': 'Overview'
            }
        ).get('Items', [])
        for item in items:
            if model := self.__makeModel(item):
                episode_models.append(model)
        return episode_models
