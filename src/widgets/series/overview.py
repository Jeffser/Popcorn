# overview.py

from gi.repository import Gtk, Adw, Gio, GLib, GObject
from ...integrations import models

@Gtk.Template(resource_path='/com/jeffser/Popcorn/series/overview.ui')
class SeriesOverview(Gtk.Overlay):
    __gtype_name__ = 'PopcornSeriesOverview'

    model = GObject.Property(type=models.Series)

    main_container = Gtk.Template.Child()
    backdrop_picture = Gtk.Template.Child()
    logo_picture = Gtk.Template.Child()

    metadata_container = Gtk.Template.Child()
    community_rating_label = Gtk.Template.Child()
    production_year_label = Gtk.Template.Child()
    official_rating_label = Gtk.Template.Child()
    season_count_label = Gtk.Template.Child()
    overview_label = Gtk.Template.Child()

    def __init__(self, model):
        super().__init__()
        self.set_property('model', model)
        self.set_measure_overlay(self.main_container, True)

        self.model.connect_property('backdropPaintable', self.backdrop_changed)
        self.model.connect_property('logoPaintable', self.logo_changed)
        self.model.connect_property('CommunityRating', self.community_rating_chagend)
        self.model.connect_property('ProductionYear', self.production_year_changed)
        self.model.connect_property('OfficialRating', self.official_rating_changed)
        self.model.connect_property('SeasonCount', self.season_count_changed)
        self.model.connect_property('Overview', self.overview_changed)
        self.model.connect_property('Genres', self.genres_changed)

    def backdrop_changed(self, paintable):
        if paintable:
            self.backdrop_picture.set_paintable(paintable)
        self.backdrop_picture.set_visible(paintable)

    def logo_changed(self, paintable):
        if paintable:
            self.logo_picture.set_paintable(paintable)
        self.logo_picture.set_visible(paintable)

    def community_rating_chagend(self, rating:float):
        self.community_rating_label.get_parent().set_visible(rating > 0)
        self.community_rating_label.set_label(str(round(rating, 2)))

    def production_year_changed(self, year:int):
        self.production_year_label.set_visible(year > 0)
        self.production_year_label.set_label(str(year))

    def official_rating_changed(self, rating:str):
        self.official_rating_label.set_visible(rating)
        self.official_rating_label.set_label(rating or "")

    def season_count_changed(self, count:int):
        self.season_count_label.set_visible(count > 0)
        self.season_count_label.set_label(_("{} Seasons").format(count) if count > 1 else _("1 Season"))

    def overview_changed(self, overview:str):
        self.overview_label.set_label((overview or "").replace('\n', ' '))

    def genres_changed(self, genres):
        for genre in [genre.get_string() for genre in list(genres)][:5]:
            self.metadata_container.append(
                Gtk.Separator()
            )
            self.metadata_container.append(
                Gtk.Label(
                    label=genre
                )
            )
