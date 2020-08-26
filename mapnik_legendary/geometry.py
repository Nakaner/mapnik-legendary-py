# SPDX-License-Identifier: LGPL-2.1-or-later
import mapnik
import geojson
from .exceptions import MapnikLegendaryError


class Geometry:
    def __init__(self, geom_type, zoom, m):
        proj = mapnik.Projection(m.srs)
        width_of_world_in_pixels = 2**zoom * 256
        width_of_world_in_metres = proj.forward(mapnik.Coord(180, 0)).x - proj.forward(mapnik.Coord(-180, 0)).x
        width_of_image_in_metres = float(m.width) / width_of_world_in_pixels * width_of_world_in_metres
        height_of_image_in_metres = float(m.height) / width_of_world_in_pixels * width_of_world_in_metres

        self.max_x = width_of_image_in_metres
        self.max_y = height_of_image_in_metres
        self.min_x = 0
        self.min_y = 0

        if geom_type == "point":
            self.geom = geojson.Point((self.max_x/2, self.max_y/2))
        elif geom_type == "point75":
            self.geom = geojson.Point((self.max_x * 0.5, self.max_y * 0.75))
        elif geom_type == "polygon":
            self.geom = geojson.Polygon([[
                (0, 0),
                (self.max_x, 0),
                (self.max_x, self.max_y),
                (0, self.max_y),
                (0, 0)
            ]])
        elif geom_type == "linestring-with-gap":
            self.geom = geojson.MultiLineString([[
                (0, 0),
                (self.max_x * 0.45, self.max_y * 0.45),
                (self.max_x * 0.55, self.max_y * 0.55),
                (self.max_x, self.max_y)
            ]])
        elif geom_type == "polygon-with-hole":
            self.geom = geojson.Polygon([
                [
                    [0.7 * self.max_x, 0.2 * self.max_y], [0.9 * self.max_x, 0.9 * self.max_y],
                    [0.3 * self.max_x, 0.8 * self.max_y], [0.2 * self.max_x, 0.4 * self.max_y],
                    [0.7 * self.max_y, 0.2 * self.max_y]
                ],
                [
                    [0.4 * self.max_x, 0.6 * self.max_y], [0.7 * self.max_x, 0.7 * self.max_y],
                    [0.6 * self.max_x, 0.4 * self.max_y], [0.4 * self.max_x, 0.6 * self.max_y]
                ]
            ])
        elif geom_type == "linestring":
            self.geom = geojson.LineString([[0, 0], [self.max_x, self.max_y]])
        else:
            raise MapnikLegendaryError("Geometry type {} is not supported for legend entries.".format(geom_type))

    def to_wkt(self):
        return self.geom

    def to_geojson(self):
        return self.geom

    def envelope(self):
        return mapnik.Envelope(self.min_x, self.min_y, self.max_x, self.max_y)
