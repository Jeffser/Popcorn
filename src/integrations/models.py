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
                    self.set_property(prop.get_name(), kwargs.get(prop.get_name()))
            elif self.get_property(prop.get_name()) is None:
                if prop.value_type.name == 'PyObject': #LIST
                    self.set_property(prop.get_name(), [])
                else:
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
    Genres = GObject.Property(type=Gio.ListStore, default=Gio.ListStore.new(item_type=Gtk.StringObject))
    Overview = GObject.Property(type=str)
    LogoPaintable = GObject.Property(type=Gdk.Paintable)
    BackdropPaintable = GObject.Property(type=Gdk.Paintable)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)

class Episode(BasicModel):
    __gtype_name__ = 'PopcornEpisode'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    SeriesName = GObject.Property(type=str)
    SeriesId = GObject.Property(type=str)
    SeasonNumber = GObject.Property(type=int)
    EpisodeNumber = GObject.Property(type=int)
    BackdropPaintable = GObject.Property(type=Gdk.Paintable)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)
    Progress = GObject.Property(type=float, default=0) # 0 - 1

class Movie(BasicModel):
    __gtype_name__ = 'PopcornMovie'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    CommunityRating = GObject.Property(type=float)
    ProductionYear = GObject.Property(type=int)
    OfficialRating = GObject.Property(type=str)
    Genres = GObject.Property(type=Gio.ListStore, default=Gio.ListStore.new(item_type=Gtk.StringObject))
    Overview = GObject.Property(type=str)
    LogoPaintable = GObject.Property(type=Gdk.Paintable)
    BackdropPaintable = GObject.Property(type=Gdk.Paintable)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)

class Season(BasicModel):
    __gtype_name__ = 'PopcornSeason'

    Id = GObject.Property(type=str)
    Name = GObject.Property(type=str)
    SeriesId = GObject.Property(type=str)
    IndexNumber = GObject.Property(type=int)
    PrimaryPaintable = GObject.Property(type=Gdk.Paintable)


