# player.py

from gi.repository import Gtk, Adw, GLib, Gdk, GObject, Gst, Gio

from mpris_server.adapters import MprisAdapter
from mpris_server.events import EventAdapter
from mpris_server.server import Server
from mpris_server import Metadata, ValidMetadata, Track, Position, Volume, Rate, PlayState, DbusObj, MetadataObj, ActivePlaylist, PlaylistEntry, MprisInterface
from ...integrations import models

import threading, logging

logger = logging.getLogger(__name__)

Gst.init(None)

class PlayerMprisAdapter(MprisAdapter):
    # Implementations from https://github.com/alexdelorenzo/mpris_server/blob/master/src/mpris_server/adapters.py

    def __init__(self, event_adapter):
        self.event_adapter = event_adapter

    # -- RootAdapter --

    def get_desktop_entry(self) -> str:
        return "com.jeffser.Popcorn"

    def can_fullscreen(self) -> bool:
        return True

    def can_quit(self) -> bool:
        return True

    def can_raise(self) -> bool:
        return True

    def has_tracklist(self) -> bool:
        return False

    def quit(self):
        #TODO
        pass

    def set_fullscreen(self, value:bool):
        #TODO
        pass

    def set_raise(self, value:bool):
        #TODO
        pass

    # -- PlayerAdapter --

    def metadata(self) -> ValidMetadata:
        #TODO
        return MetadataObj()

    def can_control(self) -> bool:
        return True

    def can_go_next(self) -> bool:
        return True

    def can_go_previous(self) -> bool:
        return True

    def can_pause(self) -> bool:
        return True

    def can_play(self) -> bool:
        return True

    def can_seek(self) -> bool:
        return True

    def get_current_position(self) -> Position:
        #TODO
        return Position(0/1000)

    def get_rate(self) -> Rate:
        return Rate(1)

    def get_maximum_rate(self) -> Rate:
        return Rate(1)

    def get_minimum_rate(self) -> Rate:
        return Rate(1)

    def get_next_track(self) -> Track:
        pass

    def get_previous_track(self) -> Track:
        pass

    def get_playstate(self) -> PlayState:
        #TODO
        return PlayState.PAUSED

    def get_shuffle(self) -> bool:
        return False

    def get_volume(self) -> Volume:
        #TODO
        return Volume(0)

    def is_mute(self) -> bool:
        #TODO
        return True

    def is_playlist(self) -> bool:
        return False

    def is_repeating(self) -> bool:
        return False

    def next(self):
        #TODO
        pass

    def open_uri(self, uri:str):
        pass

    def pause(self):
        #TODO
        pass

    def play(self):
        #TODO
        pass

    def previous(self):
        #TODO
        pass

    def resume(self):
        #TODO
        pass

    def seek(self, time:Position, track_id:DbusObj | None = None):
        #TODO
        pass

    def set_maximum_rate(self, value:Rate):
        pass

    def set_minimum_rate(self, value:Rate):
        pass

    def set_mute(self, value:bool):
        #TODO
        pass

    def set_rate(self, value:Rate):
        pass

    def set_repeating(self, value:bool):
        pass

    def set_shuffle(self, value:bool):
        pass

    def set_volume(self, value:Volume):
        #TODO
        pass

    def stop(self):
        #TODO
        pass

    def activate_playlist(self, id:DbusObj):
        pass

    def get_playlists(self, index:int, max_count:int, order:str, reverse:bool) -> list[PlaylistEntry]:
        pass

    def add_track(self, uri:str, after_track:DbusObj, set_as_current:bool):
        pass

    def can_edit_tracks(self) -> bool:
        return False

    def get_tracks(self) -> list[DbusObj]:
        return []

    def get_tracks_metadata(self, track_ids:list[DbusObj]) -> list[Metadata]:
        return []

    def go_to(self, track_id:DbusObj):
        pass

    def remove_track(self, track_id:DbusObj):
        pass

class PlayerEventAdapter(EventAdapter):

    def __init__(self, player):
        self.player = player
        self.adapter = PlayerMprisAdapter(self)
        self.mpris = Server("com.jeffser.Popcorn", adapter=self.adapter)
        super().__init__(root=self.mpris.root, player=self.mpris.player)
        self.interface = MprisInterface("Popcorn", self.adapter)
        try:
            self.mpris.publish()
        except Exception as e:
            logger.error(e)


class Player(GObject.Object):
    __gtype_name__ = 'PopcornPlayer'

    application = GObject.Property(type=Adw.Application)
    gst = GObject.Property(type=Gst.Element, default=Gst.ElementFactory.make("playbin", "player"))
    model = GObject.Property(type=models.Playable)
    paintable = GObject.Property(type=Gdk.Paintable)
    position = GObject.Property(type=float)
    media_segments = GObject.Property(type=Gio.ListStore, default=Gio.ListStore.new(item_type=models.MediaSegment))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # MPRIS stuff
        self.event_adapter = PlayerEventAdapter(self)

        # GST stuff
        self.get_property('gst').set_property("video-sink", Gst.ElementFactory.make("gtk4paintablesink", "video-sink"))
        self.get_property('gst').connect("source-setup", self.on_source_setup)
        self.bus = self.get_property('gst').get_bus()
        self.bus.connect("message::eos", print) # Video ended
        self.bus.connect("message::error", lambda bus, msg: logger.error(msg.parse_error()[0]))
        self.bus.connect("message::state-changed", print)
        self.connect("notify::model", self.model_changed)
        self.set_property('paintable', self.get_property('gst').get_property('video-sink').get_property('paintable'))
        GLib.timeout_add(64, self.update_stream_progress)

    def model_changed(self, player, pspec):
        if model := player.get_property(pspec.name):
            if jellyfin := self.get_property('application').jellyfin:
                if stream_url := jellyfin.getStreamUrl(model.get_property('Id')):
                    self.get_property('gst').set_state(Gst.State.READY)
                    self.get_property('gst').set_property('uri', stream_url)
                    self.get_property('gst').set_state(Gst.State.PLAYING)
                    progress = model.get_property('Progress')
                    duration = model.get_property('Duration')
                    if 0 < progress < 1:
                        GLib.timeout_add(500, lambda: self.get_property('gst').seek_simple(
                            Gst.Format.TIME,
                            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                            int(duration * progress * Gst.SECOND)
                        ) and False)
                    threading.Thread(target=self.update_media_segments, daemon=True).start()

    def on_source_setup(self, playbin, source):
        try:
            if GObject.type_is_a(source, Gst.ElementFactory.find("souphttpsrc").get_element_type()):
                if app := self.get_property('application'):
                    if jellyfin := app.jellyfin:
                        source.set_property("ssl-strict", not jellyfin.get_property('trustServer'))
        except:
            pass

    def update_media_segments(self):
        self.get_property('media-segments').remove_all()
        if model := self.get_property('model'):
            if app := self.get_property('application'):
                if jellyfin := app.jellyfin:
                    if media_segments := jellyfin.getMediaSegments(model.get_property('Id')):
                        self.get_property('media-segments').splice(
                            0,
                            0,
                            media_segments
                        )

    def update_stream_progress(self):
        success, position = self.get_property('gst').query_position(Gst.Format.TIME)
        self.set_property('position', position / Gst.SECOND)
        return True

