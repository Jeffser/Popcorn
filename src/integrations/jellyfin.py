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
            action='UserViews',
            params={'userId': self.get_property('userId')}
        ).get('Items', [])

        for view in view_dicts:
            view_models.append(models.UserView(
                Id=view.get('Id'),
                Name=view.get('Name'),
                SortName=view.get('SortName'),
                CollectionType=view.get('CollectionType')
            ))
        return view_models
