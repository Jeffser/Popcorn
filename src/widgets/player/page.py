# page.py

from gi.repository import Gtk, Adw, GLib, GObject, Gst, Gio
from ...integrations import models
from .player import Player
from ...constants import get_future_time, format_time_display, SECTION_NAMES

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/page.ui')
class PlayerPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornPlayerPage'

    player = GObject.Property(type=Player)
    end_time = GObject.Property(type=str)
    scale_seeking = GObject.Property(type=bool, default=False)
    position = GObject.Property(type=float)
    current_media_segment = GObject.Property(type=models.MediaSegment) # If inside of a segment
    media_segments = {} # start time : segment
    toolbarview = Gtk.Template.Child()
    controls_revealer = Gtk.Template.Child()
    scale = Gtk.Template.Child()
    volume_menubutton = Gtk.Template.Child()
    volume_adjustment = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GLib.timeout_add(1000, self.check_segments)
        GLib.timeout_add(60000, self.update_end_time)
        GLib.timeout_add(64, self.update_position)
        self.hide_timeout_id = None
        self.last_motion_coordinates = [0,0]
        self.connect('notify::root', self.on_root_changed)
        self.connect('notify::player', self.on_player_changed)
        self.on_player_changed(self)

    def on_player_changed(self, widget, pspec=None):
        if player := widget.get_property('player'):
            player.get_property('media-segments').connect('notify::n-items', self.media_segments_changed)
            self.media_segments_changed(player.get_property('media-segments'))
            GLib.idle_add(self.update_end_time)
            if app := player.get_property('application'):
                app.settings.bind(
                    "volume",
                    self.volume_adjustment,
                    "value",
                    Gio.SettingsBindFlags.DEFAULT
                )

    def on_root_changed(self, widget, pspec=None):
        if not widget.get_property('root'):
            if player := self.get_property('player'):
                if app := player.get_property('application'):
                    if not app.pip_window or not app.pip_window.get_visible():
                        player.stop()

    def media_segments_changed(self, widget, pspec=None):
        self.scale.clear_marks()
        self.media_segments = {}
        for segment in list(widget):
            self.scale.add_mark(
                segment.get_property('StartPosition'),
                Gtk.PositionType.BOTTOM
            )
            self.scale.add_mark(
                segment.get_property('EndPosition'),
                Gtk.PositionType.BOTTOM
            )
            self.media_segments[segment.get_property('StartPosition')] = segment

    def check_segments(self):
        if not self.get_property('scale-seeking'):
            segment_found = False
            if position := self.get_property('position'):
                for ts, segment in self.media_segments.items():
                    if ts <= position <= ts + 10:
                        self.set_property('current-media-segment', segment)
                        segment_found = True
                        break
            if not segment_found:
                if current_media_segment := self.get_property('current-media-segment'):
                    current_type = current_media_segment.get_property('Type')
                    self.set_property('current-media-segment', models.MediaSegment(Type=current_type))
        return True

    def reset(self):
        pass

    def update_end_time(self):
        if player := self.get_property('player'):
            if model := player.get_property('model'):
                duration = model.get_property('Duration')
                self.set_property('end-time', _("Ends at {}").format(get_future_time(duration-self.get_property('position'))))
        return True

    def update_position(self):
        if not self.get_property('scale-seeking'):
            self.set_property('position', self.get_property('player').get_property('position'))
        return True

    @Gtk.Template.Callback()
    def format_time_ellapsed(self, obj, position:float, duration:float) -> str:
        return format_time_display(position, duration > 3600)

    @Gtk.Template.Callback()
    def format_time_remaining(self, obj, position:float, duration:float) -> str:
        return '-{}'.format(format_time_display(duration-position, duration > 3600))

    @Gtk.Template.Callback()
    def adjustment_changed(self, adjustment):
        if self.get_property('scale-seeking'):
            self.set_property('position', adjustment.get_value())

    @Gtk.Template.Callback()
    def scale_pressed(self, *args):
        self.set_property('scale-seeking', True)

    @Gtk.Template.Callback()
    def scale_released(self, *args):
        self.get_property('player').get_property('gst').seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            int(self.get_property('position') * Gst.SECOND)
        )
        GLib.timeout_add(500, self.set_property, 'scale-seeking', False)
        GLib.timeout_add(500, lambda: self.update_end_time() and False)

    @Gtk.Template.Callback()
    def fullscreen_toggled(self, button, pspec):
        if button.get_property(pspec.name):
            self.get_root().fullscreen()
        else:
            self.get_root().unfullscreen()

    def toggle_controls(self, visible:bool):
        if not visible and (self.get_property('scale-seeking') or self.volume_menubutton.get_active()):
            return
        self.toolbarview.set_reveal_top_bars(visible)
        self.controls_revealer.set_reveal_child(visible)
        if root := self.get_root():
            root.set_cursor_from_name(None if visible else "none")
        if not visible and self.hide_timeout_id:
            self.hide_timeout_id = None

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def on_pointer_motion(self, controller, x, y):
        if self.last_motion_coordinates != [x, y]:
            self.last_motion_coordinates = [x, y]
            self.toggle_controls(True)
            if self.hide_timeout_id is not None:
                GLib.source_remove(self.hide_timeout_id)
                self.hide_timeout_id = None
            self.hide_timeout_id = GLib.timeout_add(3000, self.toggle_controls, False)

    @Gtk.Template.Callback()
    def format_pip_button_visible(self, obj, window_title:str) -> bool:
        return window_title != 'Picture-in-Picture'

    @Gtk.Template.Callback()
    def open_pip_window(self, button):
        if root := self.get_root():
            if app := root.get_application():
                if navigationview := self.get_ancestor(Adw.NavigationView):
                    app.open_pip_window()
                    navigationview.pop()
                    root.unfullscreen()

    @Gtk.Template.Callback()
    def format_segment_skipper_label(self, obj, segment_type:str) -> str:
        return _("Skip {}").format(SECTION_NAMES.get(segment_type) or _("Segment"))

    @Gtk.Template.Callback()
    def skip_segment_clicked(self, button):
        if segment := self.get_property('current-media-segment'):
            self.get_property('player').get_property('gst').seek_simple(
                Gst.Format.TIME,
                Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                int(segment.get_property('EndPosition') * Gst.SECOND)
            )

    @Gtk.Template.Callback()
    def format_visible_state_button(self, obj, state) -> str:
        return 'pause' if state == Gst.State.PLAYING else 'play'

    @Gtk.Template.Callback()
    def play_clicked(self, button):
        if player := self.get_property('player'):
            if gst := player.get_property('gst'):
                gst.set_state(Gst.State.PLAYING)

    @Gtk.Template.Callback()
    def pause_clicked(self, button):
        if player := self.get_property('player'):
            if gst := player.get_property('gst'):
                gst.set_state(Gst.State.PAUSED)

    @Gtk.Template.Callback()
    def previous_clicked(self, button):
        if player := self.get_property('player'):
            if model := player.get_property('previous-model'):
                self.get_property('player').set_property('model', model)

    @Gtk.Template.Callback()
    def next_clicked(self, button):
        if player := self.get_property('player'):
            if model := player.get_property('next-model'):
                self.get_property('player').set_property('model', model)

    @Gtk.Template.Callback()
    def format_volume_icon_name(self, obj, value:float) -> str:
        if value == 0:
            return "speaker-0-symbolic"
        elif value < 0.33:
            return "speaker-1-symbolic"
        elif value < 0.66:
            return "speaker-2-symbolic"
        return "speaker-3-symbolic"

    @Gtk.Template.Callback()
    def mute_volume_clicked(self, button):
        self.volume_adjustment.set_value(0)

    @Gtk.Template.Callback()
    def full_volume_clicked(self, button):
        self.volume_adjustment.set_value(1)

