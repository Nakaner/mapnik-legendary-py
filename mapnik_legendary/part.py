# SPDX-License-Identifier: MIT
import csv
import io
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

    def __init__(self, h, zoom, m, extra_tags):
        self.tags = Part.merge_tags(h.get('tags'), extra_tags)
        self.geom = Geometry(h.get('type'), zoom, m)
        if "layer" in h:
            self.layers = [h["layer"]]
        else:
            self.layers = h["layers"]

    def to_csv(self):
        strio = io.StringIO()
        self.tags["wkt"] = self.geom.to_wkt()
        writer = csv.DictWriter(strio, fieldnames=self.tags.keys(), delimiter=",")
        writer.writeheader()
        writer.writerow(self.tags)
        return strio.getvalue()
