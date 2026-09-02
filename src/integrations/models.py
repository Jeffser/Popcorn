# models.py

from gi.repository import GObject, GLib, Gtk, Gio, Gdk

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
