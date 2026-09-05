# models.py

from gi.repository import GObject, GLib, Gtk, Gio, Gdk
import io
from PIL import Image

class BasicModel(GObject.Object):
    __gtype_name__ = 'PopcornBasicModel'

    def __init__(self, **kwargs):
        super().__init__()
        self.update_data(**kwargs)

    def update_data(self, **kwargs):
        for prop in self.list_properties():
            if prop.get_name() in kwargs:
                if self.get_property(prop.get_name()) != kwargs.get(prop.get_name()):
                    try:
                        self.set_property(prop.get_name(), kwargs.get(prop.get_name()))
                    except:
                        self.set_property(prop.get_name(), prop.get_default_value())
            elif self.get_property(prop.get_name()) is None:
                self.set_property(prop.get_name(), prop.get_default_value())

class UserView(BasicModel):
    __gtype_name__ = 'PopcornUserView'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    CollectionType = GObject.Property(type=str)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)

class Series(BasicModel):
    __gtype_name__ = 'PopcornSeries'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    CommunityRating = GObject.Property(type=float)
    ProductionYear = GObject.Property(type=int)
    OfficialRating = GObject.Property(type=str)
    SeasonCount = GObject.Property(type=int, default=0)
    Genres = GObject.Property(type=Gio.ListStore)
    Overview = GObject.Property(type=str)
    LogoPaintable = GObject.Property(type=Gdk.Paintable)
    BackdropPaintable = GObject.Property(type=Gdk.Paintable)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)
    Played = GObject.Property(type=bool, default=False)
    IsFavorite = GObject.Property(type=bool, default=False)

class Season(BasicModel):
    __gtype_name__ = 'PopcornSeason'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    SeriesId = GObject.Property(type=str)
    IndexNumber = GObject.Property(type=int)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)
    Played = GObject.Property(type=bool, default=False)
    IsFavorite = GObject.Property(type=bool, default=False)

class TrickplayTileBytes(GObject.Object):
    __gtype_name__ = 'PopcornTrickplayTileBytes'

    content = GObject.Property(type=GLib.Bytes)

class Playable(BasicModel):
    __gtype_name__ = 'PopcornPlayable'
    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    PlayerTitle = GObject.Property(type=str)
    PlayerSubtitle = GObject.Property(type=str)
    Played = GObject.Property(type=bool, default=False)
    Progress = GObject.Property(type=float, default=0) # 0 - 1
    Duration = GObject.Property(type=float) # Seconds with decimals
    BackdropPaintable = GObject.Property(type=Gdk.Paintable)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)
    IsFavorite = GObject.Property(type=bool, default=False)

    # These are filled only when updateTrickplay is called
    TrickplayWidth = GObject.Property(type=int, default=0)
    TrickplayHeight = GObject.Property(type=int, default=0)
    TrickplayTileRows = GObject.Property(type=int, default=0)
    TrickplayTileColumns = GObject.Property(type=int, default=0)
    TrickplayCount = GObject.Property(type=int, default=0)
    TrickplayThumbnails = GObject.Property(type=Gio.ListStore)

    def getTrickplayThumbnail(self, index:int) -> Gdk.Paintable:
        row_n = self.get_property('TrickplayTileRows')
        column_n = self.get_property('TrickplayTileColumns')
        if elements_per_tile := row_n * column_n:
            if thumbnails := self.get_property('TrickplayThumbnails'):
                tile_index = index // elements_per_tile
                remainder = index % elements_per_tile
                row = remainder // column_n
                column = remainder & column_n
                if tile_index < thumbnails.get_property('n-items'):
                    if tile_thumbnail := list(thumbnails)[tile_index]:
                        if raw_data := tile_thumbnail.get_property('content').get_data():
                            with Image.open(io.BytesIO(raw_data)) as img:
                                tile_width = self.get_property('TrickplayWidth')
                                tile_height = self.get_property('TrickplayHeight')
                                left = column * tile_width
                                upper = row * tile_height
                                right = left + tile_width
                                lower = upper + tile_height
                                cropped = img.crop((left, upper, right, lower))
                                output_stream = io.BytesIO()
                                cropped.save(output_stream, format='PNG')
                                gbytes = GLib.Bytes.new(output_stream.getvalue())
                                return Gdk.Texture.new_from_bytes(gbytes)
                    print(type(thumbnails))
class Episode(Playable):
    __gtype_name__ = 'PopcornEpisode'

    SeriesName = GObject.Property(type=str)
    SeriesId = GObject.Property(type=str)
    SeasonNumber = GObject.Property(type=int)
    EpisodeNumber = GObject.Property(type=int)
    SeriesPrimaryPaintable = GObject.Property(type=Gdk.Paintable)
    Overview = GObject.Property(type=str)
    CommunityRating = GObject.Property(type=float)

class Movie(Playable):
    __gtype_name__ = 'PopcornMovie'

    CommunityRating = GObject.Property(type=float)
    ProductionYear = GObject.Property(type=int)
    OfficialRating = GObject.Property(type=str)
    Genres = GObject.Property(type=Gio.ListStore)
    Overview = GObject.Property(type=str)
    LogoPaintable = GObject.Property(type=Gdk.Paintable)

class MediaSegment(BasicModel):
    __gtype_name__ = 'PopcornMediaSegment'

    Id = GObject.Property(type=str)
    ItemId = GObject.Property(type=str)
    Type = GObject.Property(type=str)
    StartPosition = GObject.Property(type=float) # Seconds with decimals
    EndPosition = GObject.Property(type=float) # Seconds with decimals

class SubtitleLine(BasicModel):
    __gtype_name__ = 'PopcornSubtitleLine'

    StartPosition = GObject.Property(type=float) # Seconds with decimals
    EndPosition = GObject.Property(type=float) # Seconds with decimals
    Text = GObject.Property(type=str)

class Subtitle(BasicModel):
    __gtype_name__ = 'PopcornSubtitle'

    Title = GObject.Property(type=str)
    Lines = GObject.Property(type=Gio.ListStore)
