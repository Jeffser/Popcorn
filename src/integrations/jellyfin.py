# jellyfin.py

from gi.repository import Gtk, GLib, GObject, Gdk
from . import models, secret
from ..constants import subtitle_timestamp_to_position
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
        return self.getUrl(
            'Videos/{model_id}/stream?static=true&api_key={api_key}',
            model_id=model_id,
            api_key=self.get_property('accessToken')
        )

    def makeRequest(self, action:str, json:dict={}, params:dict={}, mode:str="GET", action_keys:dict={}) -> dict:
        headers = {
            **self.getBaseHeader(),
            "Accept": "application/json"
        }
        try:
            if mode in ('GET', 'RAWGET'):
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
                if mode == 'RAWGET':
                    return response
                else:
                    return response.json()
            elif response.status_code == 204:
                return {'state': 'ok'}
        except Exception as e:
            print(e)
            pass
        return {}

    def __makeModel(self, item:dict) -> models.BasicModel | None:
        if not item.get('Id') or not item.get('Type'):
            return
        if item.get('Type') == 'Series':
            if item.get('Id') not in self.loaded_models:
                self.loaded_models[item.get('Id')] = models.Series()
            self.loaded_models.get(item.get('Id')).update_data(
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
            self.loaded_models.get(item.get('Id')).get_property('Genres').remove_all()
            self.loaded_models.get(item.get('Id')).get_property('Genres').splice(
                0,
                0,
                [Gtk.StringObject.new(genre) for genre in item.get('Genres', [])]
            )
        elif item.get('Type') == 'Episode':
            if item.get('Id') not in self.loaded_models:
                self.loaded_models[item.get('Id')] = models.Episode()
            self.loaded_models.get(item.get('Id')).update_data(
                Id=item.get('Id'),
                Name=item.get('Name'),
                PlayerTitle=item.get('SeriesName'),
                PlayerSubtitle='{} - {}. {}'.format(_("Season {}").format(item.get('ParentIndexNumber')), item.get('IndexNumber'), item.get('Name')),
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
            if item.get('Id') not in self.loaded_models:
                self.loaded_models[item.get('Id')] = models.Movie()
            self.loaded_models.get(item.get('Id')).update_data(
                Id=item.get('Id'),
                Name=item.get('Name'),
                PlayerTitle=item.get('Name'),
                PlayerSubtitle='({})'.format(item.get('ProductionYear')),
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
            self.loaded_models.get(item.get('Id')).get_property('Genres').remove_all()
            self.loaded_models.get(item.get('Id')).get_property('Genres').splice(
                0,
                0,
                [Gtk.StringObject.new(genre) for genre in item.get('Genres', [])]
            )
        elif item.get('Type') == 'Season':
            if item.get('Id') not in self.loaded_models:
                self.loaded_models[item.get('Id')] = models.Season()
            self.loaded_models.get(item.get('Id')).update_data(
                Id=item.get('Id'),
                Name=item.get('Name'),
                SeriesId=item.get('SeriesId'),
                IndexNumber=item.get('IndexNumber'),
                PrimaryPaintable=self.getPaintable(item.get('Id'), image_type='Primary') or self.getPaintable(item.get('SeriesId'), image_type='Primary'),
                Played=item.get('UserData', {}).get('Played', False)
            )
        elif item.get('Type') in ('CollectionFolder', 'UserView'):
            if item.get('CollectionType') in ('tvshows', 'movies'):
                if item.get('Id') not in self.loaded_models:
                    self.loaded_models[item.get('Id')] = models.UserView()
                self.loaded_models.get(item.get('Id')).update_data(
                    Id=item.get('Id'),
                    Name=item.get('Name'),
                    CollectionType=item.get('CollectionType')
                )
        return self.loaded_models.get(item.get('Id'))

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
        if modelId in self.loaded_models:
            return self.loaded_models.get(modelId)
        item = self.makeRequest(
            action='Users/{userId}/Items/{itemId}',
            action_keys={
                'itemId': modelId,
                'fields': 'Genres,Overview,OfficialRating,RecursiveItemCount,ChildCount'
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

    def getSeriesNextUp(self, series_id:str) -> models.Episode | None:
        items = self.makeRequest(
            action='Shows/NextUp',
            params={
                'seriesId': series_id,
                'userId': self.get_property('userId'),
                'limit': 1,
                'fields': 'Overview'
            }
        ).get('Items', [])
        if len(items) > 0:
            if model := self.__makeModel(items[0]):
                return model

        # Just send the first episode
        items = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'parentId': series_id,
                'recursive': True,
                'IncludeItemTypes': 'Episode',
                'fields': 'Overview',
                'sortBy': 'IndexNumber',
                'sortOrder': 'Ascending',
                'limit': 1
            }
        ).get('Items', [])
        if len(items) > 0:
            return self.__makeModel(items[0])

    def getSeasonNextUp(self, season_id:str) -> models.Episode | None:
        items = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'parentId': season_id,
                'IncludeItemTypes': 'Episode',
                'fields': 'Overview',
                'sortBy': 'ParentIndexNumber,IndexNumber',
                'sortOrder': 'Ascending'
            }
        ).get('Items', [])
        for item in items:
            if 0 < item.get('UserData', {}).get('PlaybackPositionTicks', 0) < 1 or not item.get('UserData', {}).get('Played'):
                if model := self.__makeModel(item):
                    return model

        items = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'parentId': season_id,
                'recursive': True,
                'IncludeItemTypes': 'Episode',
                'fields': 'Overview',
                'sortBy': 'IndexNumber',
                'sortOrder': 'Ascending',
                'limit': 1
            }
        ).get('Items', [])
        if len(items) > 0:
            return self.__makeModel(items[0])

    def getMediaSegments(self, model_id:str) -> list:
        # Returns list of MediaSegment models
        media_segment_models = []
        items = self.makeRequest(
            action='MediaSegments/{model_id}',
            action_keys={
                'model_id': model_id
            }
        ).get('Items', [])
        for item in items:
            start_position = round((item.get('StartTicks') or 0) / 10_000_000, 2)
            end_position = round((item.get('EndTicks') or 0) / 10_000_000, 2)
            if start_position and end_position:
                media_segment_models.append(models.MediaSegment(
                    Id=item.get('Id'),
                    ItemId=item.get('ItemId'),
                    Type=item.get('Type'),
                    StartPosition=start_position,
                    EndPosition=end_position,
                ))
        return media_segment_models

    def getAdjacentEpisodes(self, episode_id:str) -> tuple:
        # returns: previous episode model, next episode model
        previous_model = None
        next_model = None
        if model := self.loaded_models.get(episode_id):
            if isinstance(model, models.Movie):
                return None, None
            if series_id := model.get_property('SeriesId'):
                items = self.makeRequest(
                    action='Shows/{series_id}/Episodes',
                    action_keys={
                        'series_id': series_id
                    },
                    params={
                        'userId': self.get_property('userId')
                    }
                ).get('Items', [])
                for i, item in enumerate(items):
                    if item.get('Id') == episode_id:
                        if i-1 >= 0:
                            previous_model = self.__makeModel(items[i-1])
                        if i+1 < len(items):
                            next_model = self.__makeModel(items[i+1])
                        break
        return previous_model, next_model

    def getSubtitles(self, playable_id:str) -> list:
        # Return list of subtitle models
        subtitle_models = []
        items = self.makeRequest(
            action='Users/{userId}/Items/{item_id}',
            action_keys={
                'item_id': playable_id
            }
        ).get("MediaSources", [])
        for item in items:
            for stream in item.get("MediaStreams", []):
                if stream.get("Type") == "Subtitle":
                    try:
                        subtitle_model = models.Subtitle(
                            Title=stream.get('DisplayTitle')
                        )
                        result = self.makeRequest(
                            action='Videos/{item_id}/{media_source_id}/Subtitles/{index}/Stream.vtt',
                            action_keys={
                                'item_id': playable_id,
                                'media_source_id': item.get("Id"),
                                'index': stream.get("Index")
                            },
                            mode='RAWGET'
                        ).content.decode('utf8')
                        raw_lines = [line for line in str(result).split('\n\n')[1:] if line]
                        for line in raw_lines:
                            sublines = line.split('\n')
                            timestamp = sublines.pop(0)
                            start_timestamp, end_timestamp = timestamp.split(' --> ')[:2]
                            line_model = models.SubtitleLine(
                                StartPosition=subtitle_timestamp_to_position(start_timestamp),
                                EndPosition=subtitle_timestamp_to_position(end_timestamp),
                                Text='\n'.join(sublines)
                            )
                            subtitle_model.get_property('Lines').append(line_model)
                        subtitle_models.append(subtitle_model)
                    except:
                        pass
        return subtitle_models

    def getModelsFromFolder(self, user_view_id:str, limit:int, startIndex:int) -> list:
        # returns list of models (can be anything, check types on return)
        model_list = []
        items = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'parentId': user_view_id,
                'limit': limit,
                'startIndex': startIndex,
                'fields': 'Genres,Overview,OfficialRating,RecursiveItemCount,ChildCount'
            }
        ).get('Items', [])
        for item in items:
            if model := self.__makeModel(item):
                model_list.append(model)
        return model_list
