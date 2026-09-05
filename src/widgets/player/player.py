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
        if player := self.event_adapter.gst_player:
            if app := player.get_property('application'):
                app.quit()

    def set_fullscreen(self, value:bool):
        if player := self.event_adapter.gst_player:
            if app := player.get_property('application'):
                if active_window := app.get_active_window():
                    if value:
                        active_window.fullscreen()
                    else:
                        active_window.unfullscreen()

    def set_raise(self, value:bool):
        if player := self.event_adapter.gst_player:
            if app := player.get_property('application'):
                if active_window := app.get_active_window():
                    active_window.present()

    # -- PlayerAdapter --

    def metadata(self) -> ValidMetadata:
        if player := self.event_adapter.gst_player:
            if model := player.get_property('model'):
                art_url = ''
                if app := player.get_property('application'):
                    if jellyfin := app.jellyfin:
                        art_url = jellyfin.getImageUrl(model.get_property('Id'), image_type="Primary")
                return MetadataObj(
                    title=model.get_property('PlayerTitle'),
                    artists=[model.get_property('PlayerSubtitle')],
                    as_text=[model.get_property('PlayerTitle')],
                    length=model.get_property('Duration')*1000000,
                    art_url=art_url
                )
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
        if player := self.event_adapter.gst_player:
            success, position = player.get_property('gst').query_position(Gst.Format.TIME)
            return Position(position/1000)
        return Position(0)

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
        if player := self.event_adapter.gst_player:
            success, state, pending = player.get_property('gst').get_state(0)
            return PlayState.PLAYING if state == Gst.State.PLAYING else PlayState.PAUSED
        return PlayState.PAUSED

    def get_shuffle(self) -> bool:
        return False

    def get_volume(self) -> Volume:
        if player := self.event_adapter.gst_player:
            return Volume(player.get_property('gst').get_property('volume'))
        return Volume(0)

    def is_mute(self) -> bool:
        if player := self.event_adapter.gst_player:
            return player.get_property('gst').get_property('volume') == 0
        return True

    def is_playlist(self) -> bool:
        return False

    def is_repeating(self) -> bool:
        return False

    def next(self):
        if player := self.event_adapter.gst_player:
            if next_model := player.get_property('next-model'):
                player.set_property('model', next_model)

    def open_uri(self, uri:str):
        pass

    def pause(self):
        if player := self.event_adapter.gst_player:
            player.get_property('gst').set_state(Gst.State.PAUSED)
        pass

    def play(self):
        if player := self.event_adapter.gst_player:
            player.get_property('gst').set_state(Gst.State.PLAYING)
        pass

    def previous(self):
        if player := self.event_adapter.gst_player:
            if previous_model := player.get_property('previous-model'):
                player.set_property('model', previous_model)

    def resume(self):
        if player := self.event_adapter.gst_player:
            player.get_property('gst').set_state(Gst.State.PLAYING)

    def seek(self, time:Position, track_id:DbusObj | None = None):
        if player := self.event_adapter.gst_player:
            player.get_property('gst').seek_simple(
                Gst.Format.TIME,
                Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                time*1000
            )
            self.event_adapter.emit_changes(self.player.mpris.player, changes=['Position'])

    def set_maximum_rate(self, value:Rate):
        pass

    def set_minimum_rate(self, value:Rate):
        pass

    def set_mute(self, value:bool):
        pass

    def set_rate(self, value:Rate):
        pass

    def set_repeating(self, value:bool):
        pass

    def set_shuffle(self, value:bool):
        pass

    def set_volume(self, value:Volume):
        if player := self.event_adapter.gst_player:
            player.get_property('application').settings.set_double('volume', value)

    def stop(self):
        if player := self.event_adapter.gst_player:
            player.get_property('gst').set_state(Gst.State.NULL)

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
        self.gst_player = player
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
    previous_model = GObject.Property(type=models.Playable)
    next_model = GObject.Property(type=models.Playable)
    paintable = GObject.Property(type=Gdk.Paintable)
    position = GObject.Property(type=float)
    media_segments = GObject.Property(type=Gio.ListStore, default=Gio.ListStore.new(item_type=models.MediaSegment))
    current_media_segment = GObject.Property(type=models.MediaSegment) # If inside of a segment
    available_subtitles = GObject.Property(type=Gio.ListStore, default=Gio.ListStore.new(item_type=models.Subtitle))
    gst_state = GObject.Property(type=Gst.State, default=Gst.State.NULL)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # For handling Jellyfin.StopSession
        self.last_model_id:str = None
        self.last_reported_position:float = 0.0

        # MPRIS stuff
        self.event_adapter = PlayerEventAdapter(self)

        # GST stuff
        self.get_property('gst').set_property("video-sink", Gst.ElementFactory.make("gtk4paintablesink", "video-sink"))
        self.get_property('gst').connect("source-setup", self.on_source_setup)
        self.bus = self.get_property('gst').get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::eos", self.stream_ended)
        self.bus.connect("message::error", lambda bus, msg: logger.error(msg.parse_error()[0]))
        self.bus.connect("message::state-changed", self.handle_message_state_changed)
        self.connect("notify::model", self.model_changed)
        self.set_property('paintable', self.get_property('gst').get_property('video-sink').get_property('paintable'))
        self.updating_volume = False
        self.get_property('application').get_property('settings').connect("changed::volume", self.settings_volume_changed)
        self.gst.connect("notify::volume", self.gst_volume_changed)
        GLib.timeout_add(64, self.update_stream_progress)
        GLib.timeout_add(10000, self.update_stream_progress_jellyfin)

    def handle_jellyfin_session(self, new_model_id:str=""):
        if jellyfin := self.get_property('application').jellyfin:
            if self.last_model_id:
                jellyfin.StopSession(self.last_model_id, self.last_reported_position)
            self.last_model_id = new_model_id
            if new_model_id:
                jellyfin.StartSession(new_model_id)

    def model_changed(self, player, pspec):
        if app := self.get_property('application'):
            if jellyfin := app.jellyfin:
                if model := player.get_property(pspec.name):
                    GLib.idle_add(app.inhibit_idle)
                    threading.Thread(target=self.handle_jellyfin_session, args=(model.get_property('Id'),), daemon=True).start()
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
                        threading.Thread(target=self.get_adjacent_episodes, daemon=True).start()
                        threading.Thread(target=self.update_subtitles, daemon=True).start()
                        threading.Thread(target=self.update_trickplay, daemon=True).start()
                else:
                    threading.Thread(target=self.handle_jellyfin_session, daemon=True).start()
                    GLib.idle_add(app.uninhibit_idle)

    def update_trickplay(self):
        if model := self.get_property('model'):
            if app := self.get_property('application'):
                if jellyfin := app.jellyfin:
                    jellyfin.updateTrickplay(model.get_property('Id'))

    def update_subtitles(self):
        self.get_property('available-subtitles').remove_all()
        if model := self.get_property('model'):
            if app := self.get_property('application'):
                if jellyfin := app.jellyfin:
                    if subtitles := jellyfin.getSubtitles(model.get_property('Id')):
                        self.get_property('available-subtitles').splice(
                            0,
                            0,
                            [models.Subtitle(Title=_("Off"), Lines=[]), *subtitles]
                        )

    def get_adjacent_episodes(self):
        if jellyfin := self.get_property('application').jellyfin:
            if current_model := self.get_property('model'):
                previous_model, next_model = jellyfin.getAdjacentEpisodes(current_model.get_property('Id'))
                self.set_property('previous-model', previous_model)
                self.set_property('next-model', next_model)
                return
        self.set_property('previous-model', None)
        self.set_property('next-model', None)

    def settings_volume_changed(self, settings, key):
        if not self.updating_volume:
            self.updating_volume = True
            try:
                value = settings.get_value(key).unpack() ** 3
                self.get_property('gst').set_property('volume', value)
            finally:
                self.updating_volume = False

    def gst_volume_changed(self, gst, gp):
        if not self.updating_volume:
            self.updating_volume = True
            try:
                value = gst.get_property('volume')
                self.get_property('application').get_property('settings').set_double('volume', value ** (1/3) if value > 0 else 0.0)
            finally:
                self.updating_volume = False

    def on_source_setup(self, playbin, source):
        try:
            if GObject.type_is_a(source, Gst.ElementFactory.find("souphttpsrc").get_element_type()):
                if app := self.get_property('application'):
                    if jellyfin := app.jellyfin:
                        source.set_property("ssl-strict", not jellyfin.get_property('trustServer'))
        except:
            pass

    def handle_message_state_changed(self, bus, message):
        if message.src == self.get_property('gst'):
            old_state, new_state, pending_state = message.parse_state_changed()
            if pending_state == Gst.State.VOID_PENDING and new_state != Gst.State.READY:
                self.set_property('gst-state', new_state)
                self.event_adapter.emit_changes(self.event_adapter.mpris.player, changes=['Metadata', 'PlaybackStatus'])

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

    def update_stream_progress_jellyfin(self):
        if jellyfin := self.get_property('application').jellyfin:
            if model := self.get_property('model'):
                is_paused = False
                success, state, pending = self.get_property('gst').get_state(0)
                if success:
                    is_paused = state == Gst.State.PAUSED
                if position := self.get_property("position"):
                    if position > 0:
                        self.last_reported_position = position
                        threading.Thread(
                            target=jellyfin.UpdateSession,
                            args=(
                                self.last_model_id,
                                self.last_reported_position,
                                is_paused
                            ),
                            daemon=True
                        ).start()
        return True

    def stop(self):
        self.get_property('gst').set_state(Gst.State.NULL)
        self.set_property('position', 0)
        self.set_property('model', None)
        self.get_property('media-segments').remove_all()

    def stream_ended(self, bus, message):
        if message.src == self.get_property('gst'):
            self.set_property('gst-state', Gst.State.NULL)
            self.set_property('model', self.get_property('next-model'))

