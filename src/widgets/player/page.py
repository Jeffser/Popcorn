# page.py

from gi.repository import Gtk, Adw, GLib, GObject, Gst, Gio
from ...integrations import models
from .player import Player
from ...constants import get_future_time, format_time_display, SECTION_NAMES

class SubtitleCheckButton(Gtk.CheckButton):
    __gtype_name__ = 'PopcornSubtitleCheckButton'

    model = GObject.Property(type=models.Subtitle)

@Gtk.Template(resource_path='/com/jeffser/Popcorn/player/page.ui')
class PlayerPage(Adw.NavigationPage):
    __gtype_name__ = 'PopcornPlayerPage'

    player = GObject.Property(type=Player)
    end_time = GObject.Property(type=str)
    scale_seeking = GObject.Property(type=bool, default=False)
    position = GObject.Property(type=float)
    current_media_segment = GObject.Property(type=models.MediaSegment) # If inside of a segment
    current_subtitle_line = GObject.Property(type=models.SubtitleLine) # If subtitle line should be shown
    overlay_icon_name = GObject.Property(type=str)
    overlay_progress = GObject.Property(type=float) # 0-1
    media_segments = {} # start time : segment
    toolbarview = Gtk.Template.Child()
    controls_revealer = Gtk.Template.Child()
    button_revealer = Gtk.Template.Child()
    button_revealer_stack = Gtk.Template.Child()
    subtitle_menu_button = Gtk.Template.Child()
    subtitle_options_container = Gtk.Template.Child()
    scale = Gtk.Template.Child()
    volume_menubutton = Gtk.Template.Child()
    volume_adjustment = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GLib.timeout_add(1000, self.check_segments)
        GLib.timeout_add(1000, self.check_subtitles)
        GLib.timeout_add(60000, self.update_end_time)
        GLib.timeout_add(64, self.update_position)
        self.hide_timeout_id = None
        self.overlay_icon_timeout_id = None
        self.last_motion_coordinates = [0,0]
        self.connect('notify::root', self.on_root_changed)
        self.connect('notify::player', self.on_player_changed)
        self.install_action("player.seek", 'i', self.seek)
        self.install_action("player.change-volume", 'd', self.change_volume)
        self.install_action("player.toggle-playback", None, self.toggle_playback)
        self.on_player_changed(self)

    def on_player_changed(self, widget, pspec=None):
        if player := widget.get_property('player'):
            player.get_property('media-segments').connect('notify::n-items', self.media_segments_changed)
            player.get_property('available-subtitles').connect('notify::n-items', self.available_subtitles_changed)
            self.available_subtitles_changed(player.get_property('available-subtitles'))
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

    def available_subtitles_changed(self, widget, pspec=None):
        for item in list(self.subtitle_options_container):
            self.subtitle_options_container.remove(item)
        first_check = None
        options_list = list(widget)
        for i, model in enumerate(options_list):
            check_button = SubtitleCheckButton(
                label=model.get_property('Title'),
                group=first_check,
                model=model,
                active=i==min(1, len(options_list))
            )
            if not first_check:
                first_check = check_button
            self.subtitle_options_container.append(check_button)

    def check_segments(self):
        self.button_revealer_stack.set_sensitive(True)
        if not self.get_property('scale-seeking'):
            segment_found = False
            if position := self.get_property('position'):
                for ts, segment in self.media_segments.items():
                    if ts <= position <= ts + 10:
                        self.set_property('current-media-segment', segment)
                        segment_found = True
                        break
            if segment_found:
                self.button_revealer_stack.set_visible_child_name('segment')
                self.button_revealer.set_reveal_child(True)
                return True
            else:
                if current_media_segment := self.get_property('current-media-segment'):
                    current_type = current_media_segment.get_property('Type')
                    self.set_property('current-media-segment', models.MediaSegment(Type=current_type))
                if player := self.get_property('player'):
                    if model := player.get_property('model'):
                        if duration := model.get_property('Duration'):
                            if 20 >= duration - position > 1:
                                self.button_revealer_stack.set_visible_child_name('next-up')
                                self.button_revealer.set_reveal_child(player.get_property('next-model'))
                                return True
        self.button_revealer.set_reveal_child(False)
        return True

    def check_subtitles(self):
        subtitle_model = None
        for option in list(self.subtitle_options_container):
            if option.get_active():
                subtitle_model = option.get_property('model')
                break

        if subtitle_model:
            if position := self.get_property('position'):
                for line in list(subtitle_model.get_property('Lines') or []):
                    if line.get_property('StartPosition') < position < line.get_property('EndPosition'):
                        self.set_property('current-subtitle-line', line)
                        return True
        self.set_property('current-subtitle-line', models.SubtitleLine())
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
        if not visible and (self.get_property('scale-seeking') or self.volume_menubutton.get_active() or self.subtitle_menu_button.get_active()):
            return
        self.toolbarview.set_reveal_top_bars(visible)
        self.controls_revealer.set_reveal_child(visible)
        if root := self.get_root():
            root.set_cursor_from_name(None if visible else "none")
        if not visible and self.hide_timeout_id:
            self.hide_timeout_id = None

    def show_controls(self):
        self.toggle_controls(True)
        if self.hide_timeout_id is not None:
            GLib.source_remove(self.hide_timeout_id)
            self.hide_timeout_id = None
        self.hide_timeout_id = GLib.timeout_add(3000, self.toggle_controls, False)

    @Gtk.Template.Callback()
    def format_to_bool(self, obj, value) -> bool:
        return bool(value)

    @Gtk.Template.Callback()
    def on_pointer_motion(self, controller, x, y):
        if self.last_motion_coordinates != [x, y]:
            self.last_motion_coordinates = [x, y]
            self.show_controls()

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
        self.button_revealer_stack.set_sensitive(False)
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

    @Gtk.Template.Callback()
    def format_subtitle_button_visible(self, obj, n_subtitles):
        return n_subtitles > 1

    @Gtk.Template.Callback()
    def format_subtitle_visible(self, obj, subtitle_line) -> bool:
        if subtitle_line:
            return bool(subtitle_line.get_property('Text'))
        return False

    @Gtk.Template.Callback()
    def format_subtitle_label(self, obj, subtitle_line) -> str:
        if subtitle_line:
            return subtitle_line.get_property('Text').strip()
        return ''

    @Gtk.Template.Callback()
    def format_action_target(self, obj, value, variant) -> GLib.Variant:
        return GLib.Variant(variant, value)

    @Gtk.Template.Callback()
    def format_heart_icon_name(self, obj, isFavorite:bool) -> str:
        return "heart-filled-symbolic" if isFavorite else "heart-outline-thick-symbolic"

    @Gtk.Template.Callback()
    def on_gesture_clicked(self, gesture, n_clicks:int, x:float, y:float):
        if n_clicks == 2:
            percentage = x / self.get_width()
            if 0 <= percentage <= 0.4 :
                self.seek(None, None, GLib.Variant('i', 10))
            elif 0.4 <= percentage <= 0.6:
                self.toggle_playback(None, None, None)
            elif 0.6 <= percentage <= 1:
                self.seek(None, None, GLib.Variant('i', -10))
            return True

    @Gtk.Template.Callback()
    def format_picture_renderer_content_fit(self, obj, settings:Gio.Settings, is_fullscreen:bool) -> Gtk.ContentFit:
        if is_fullscreen:
            return settings.get_value('fullscreen-content-fit').unpack()
        else:
            return Gtk.ContentFit.CONTAIN

    def reset_overlay_icon(self):
        self.set_property('overlay-progress', 0)
        self.set_property('overlay-icon-name', '')

    def seek(self, obj, action_name, seek_amount):
        seek_amount = seek_amount.unpack()
        icon_name = 'media-seek-{}-symbolic'.format('forward' if seek_amount > 0 else 'backward')
        self.get_property('player').get_property('gst').seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            int((self.get_property('position') + seek_amount) * Gst.SECOND)
        )
        self.set_property('overlay-icon-name', icon_name)
        self.set_property('overlay-progress', 0)
        if self.overlay_icon_timeout_id:
            GLib.source_remove(self.overlay_icon_timeout_id)
        self.overlay_icon_timeout_id = GLib.timeout_add(1000, self.reset_overlay_icon)

    def change_volume(self, obj, action_name, volume):
        volume = volume.unpack()
        if root := self.get_root():
            if app := root.get_application():
                volume = app.settings.get_value("volume").unpack() + volume
                app.settings.set_double("volume", max(0, min(volume, 1)))
                icon_name = self.format_volume_icon_name(None, volume)

        self.set_property('overlay-icon-name', icon_name)
        self.set_property('overlay-progress', volume*5)
        if self.overlay_icon_timeout_id:
            GLib.source_remove(self.overlay_icon_timeout_id)
        self.overlay_icon_timeout_id = GLib.timeout_add(1000, self.reset_overlay_icon)

    def toggle_playback(self, obj, action_name, param):
        icon_name = ''
        if player := self.get_property('player'):
            if gst := player.get_property('gst'):
                success, state, pending = gst.get_state(0)
                if success:
                    if state == Gst.State.PAUSED:
                        gst.set_state(Gst.State.PLAYING)
                        icon_name = "media-playback-start-symbolic"
                    else:
                        gst.set_state(Gst.State.PAUSED)
                        icon_name = "media-playback-pause-symbolic"
        self.set_property('overlay-icon-name', icon_name)
        self.set_property('overlay-progress', 0)
        if self.overlay_icon_timeout_id:
            GLib.source_remove(self.overlay_icon_timeout_id)
        self.overlay_icon_timeout_id = GLib.timeout_add(1000, self.reset_overlay_icon)

