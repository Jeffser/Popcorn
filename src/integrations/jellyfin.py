# jellyfin.py

from gi.repository import Gtk, GLib, GObject, Gdk
from . import models, secret
import requests, io, urllib3, platform

# Just so that the logs don't get cluttered with warnings if trust-server = True
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Jellyfin(GObject.Object):
    __gtype_name__ = 'PopcornIntegrationJellyfin'

    AUTH_HEADER = 'MediaBrowser Client="Nocturne", Device="{}", DeviceId="{}", Version="1.0.0"'.format(platform.node(), str(abs(hash(platform.node()))))

    # Loaded when login
    trustServer = GObject.Property(type=bool, default=False)
    url = GObject.Property(type=str)
    user = GObject.Property(type=str)

    # Loaded by API
    accessToken = GObject.Property(type=str)
    userId = GObject.Property(type=str)

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
        view_dicts = self.makeRequest(
            action='Users/{userId}/Views'
        ).get('Items', [])

        for view in view_dicts:
            if view.get('CollectionType') in ('tvshows', 'movies'):
                view_models.append(models.UserView(
                    Id=view.get('Id'),
                    Name=view.get('Name'),
                    CollectionType=view.get('CollectionType')
                ))
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
        series_dicts = self.makeRequest(
            action='Users/{userId}/Items',
            params={
                'IncludeItemTypes': 'Series',
                'Recursive': 'true',
                'SortBy': 'Random',
                'Limit': 5,
                'fields': 'Genres,Overview,OfficialRating,RecursiveItemCount'
            }
        ).get('Items', [])

        for series in series_dicts:
            model = models.Series(
                Id=series.get('Id'),
                Name=series.get('Name'),
                CommunityRating=series.get('CommunityRating'),
                ProductionYear=series.get('ProductionYear'),
                OfficialRating=series.get('OfficialRating'),
                SeasonCount=series.get('ChildCount') or 1,
                Overview=series.get('Overview'),
                logoPaintable=self.getPaintable(series.get('Id'), image_type='logo'),
                backdropPaintable=self.getPaintable(series.get('Id'))
            )
            model.get_property('Genres').remove_all()
            model.get_property('Genres').splice(
                0,
                0,
                [Gtk.StringObject.new(genre) for genre in series.get('Genres', [])]
            )
            series_models.append(model)
        return series_models

