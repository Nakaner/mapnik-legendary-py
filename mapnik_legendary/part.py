# SPDX-License-Identifier: LGPL-2.1-or-later
import csv
import io
from .exceptions import MapnikLegendaryError
from .geometry import Geometry

class Part:
    """A part is a combination of tags, geometry and layers."""

    def merge_tags(tags, extra_tags):
        t = tags
        if not t:
            t = {}
        et = extra_tags
        if not et:
            et = []
        result = { k: None for k in extra_tags }
        result.update(tags)
        return result

    def __init__(self, h, zoom, m, extra_tags, name):
        self.tags = Part.merge_tags(h.get('tags'), extra_tags)
        self.geom = Geometry(h.get('type'), zoom, m)
        try:
            if "layer" in h:
                self.layers = [h["layer"]]
            else:
                self.layers = h["layers"]
        except KeyError as err:
            raise MapnikLegendaryError("Key \"layers\" or \"layer\" missing in specification of feature/part {}".format(name))

    def to_csv(self):
        strio = io.StringIO()
        self.tags["wkt"] = self.geom.to_wkt()
        writer = csv.DictWriter(strio, fieldnames=self.tags.keys(), delimiter=",")
        writer.writeheader()
        writer.writerow(self.tags)
        return strio.getvalue()
