# secret.py

from gi.repository import Secret, GObject
import hashlib, secrets, string, os, uuid
from ..constants import FALLBACK_PASSWORD_PATH
from .models import BasicModel

BASE_ATTRIBUTES = {
    "id": Secret.SchemaAttributeType.STRING,
    "server_address": Secret.SchemaAttributeType.STRING,
    "trust_certificates": Secret.SchemaAttributeType.BOOLEAN,
    "username": Secret.SchemaAttributeType.STRING,
    "quick_connect": Secret.SchemaAttributeType.BOOLEAN,
}
BASE_SCHEMA = Secret.Schema.new(
    "com.jeffser.Popcorn.Account",
    Secret.SchemaFlags.NONE,
    BASE_ATTRIBUTES
)

def _init_db():
    conn = sqlite3.connect(FALLBACK_PASSWORD_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            server_address TEXT,
            trust_certificates INTEGER,
            username TEXT,
            quick_connect INTEGER,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

class ServerUser(GObject.Object):
    __gtype_name__ = 'PopcornServerUser'

    id = GObject.Property(type=str)
    server_address = GObject.Property(type=str)
    trust_certificates = GObject.Property(type=bool, default=False)
    username = GObject.Property(type=str)
    quick_connect = GObject.Property(type=bool, default=False)

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4()) # TODO maybe verify that uuid is truly unique
            #TODO verify that server-address starts with http
        super().__init__(**kwargs)

    def __get_attributes(self) -> dict:
        attributes = {}
        for key in list(BASE_ATTRIBUTES):
            value = self.get_property(key)
            if isinstance(value, bool):
                 attributes[key] = str(value).lower()
            else:
                attributes[key] = value
        return attributes

    def get_password(self) -> str:
        try:
            return Secret.password_lookup_sync(
                BASE_SCHEMA,
                self.__get_attributes(),
                None
            ) or ''
        except:
            _init_db()
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT password FROM accounts
                    WHERE server_address = ? AND username = ?
                """,
                (self.get_property('server_address'), self.get_property('username')),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return row[0]
        return ''

    def save_password(self, password:str):
        # creates entry in secret manager
        # remember to set quick_connect before calling this if necessary
        try:
            attributes = self.__get_attributes()
            Secret.password_store_sync(
                BASE_SCHEMA,
                attributes,
                Secret.COLLECTION_DEFAULT,
                "{} ({})".format(attributes.get('username').title(), attributes.get('server_address')),
                password,
                None
            )
        except:
            _init_db()
            conn = sqlite3.connect(FALLBACK_PASSWORD_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                    INSERT OR REPLACE INTO accounts
                    (server_address, trust_certificates, username, quick_connect, password)
                    VALUES (?, ?, ?, ?, ?)
                """,
                (
                    self.get_property('server_address'),
                    int(self.get_property('trust_certificates')),
                    self.get_property('username'),
                    int(self.get_property('quick_connect')),
                    password,
                ),
            )
            conn.commit()
            conn.close()

    def remove_user(self):
        # Should delete object after calling this to be safe
        try:
            Secret.password_clear_sync(
                BASE_SCHEMA,
                self.__get_attributes(),
                None
            )
        except:
            _init_db()
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM accounts WHERE id=?',
                (self.get_property('id'),)
            )
            conn.commit()
            conn.close()

def list_users() -> list:
    # returns list of ServerUser model
    result_list = []
    try:
        results = Secret.password_search_sync(
            BASE_SCHEMA,
            {},
            Secret.SearchFlags.ALL,
            None
        )
        for result in results:
            if attributes := result.get_attributes():
                attributes['trust_certificates'] = attributes.get('trust_certificates') == 'true'
                attributes['quick_connect'] = attributes.get('quick_connect') == 'true'
                result_list.append(ServerUser(**attributes))
    except:
        result_list = []
        _init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, server_address, trust_certificates, username, quick_connect FROM accounts'
        )
        for row in cursor.fetchall():
            result_list.append(ServerUser(
                id=row[0],
                server_address=row[1],
                trust_certificates=bool(row[2]),
                username=row[3],
                quick_connect=bool(row[4])
            ))
        conn.close()
    return result_list

def get_user(user_id:str) -> ServerUser | None:
    try:
        results = Secret.password_search_sync(
            BASE_SCHEMA,
            {'id': user_id},
            Secret.SearchFlags.NONE,
            None
        )
        if len(results) > 0:
            if attributes := results[0].get_attributes():
                attributes['trust_certificates'] = attributes.get('trust_certificates') == 'true'
                attributes['quick_connect'] = attributes.get('quick_connect') == 'true'
                return ServerUser(
                    **attributes
                )
    except:
        pass

###################################################################

def store_password_OLD(password:str, schema_type:str="password"): #TODO DELETE
    try:
        attributes = {"type": schema_type}

        Secret.password_store_sync(
            BASE_SCHEMA,
            attributes,
            Secret.COLLECTION_DEFAULT,
            "Popcorn Login",
            password,
            None
        )
    except:
        with open(FALLBACK_PASSWORD_PATH, 'w+') as f:
            f.write(password)

def get_plain_password_OLD(schema_type:str="password") -> str:
    # returns plain password
    try:
        attributes = {"type": schema_type}
        return Secret.password_lookup_sync(
            BASE_SCHEMA,
            attributes,
            None
        )
    except:
        if os.path.isfile(FALLBACK_PASSWORD_PATH):
            with open(FALLBACK_PASSWORD_PATH, 'r') as f:
                return f.read()
    return ""

