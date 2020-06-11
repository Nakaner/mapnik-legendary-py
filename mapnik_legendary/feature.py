# SPDX-License-Identifier: LGPL-2.1-only
from .part import Part

class Feature:
    def __init__(self, feature, zoom, m, extra_tags):
        self.name = feature["name"]
        self.description = feature.get("description", self.name.upper())
        self.parts = []
        if "parts" in feature:
            for part in feature["parts"]:
                self.parts.append(Part(part, zoom, m, extra_tags))
        else:
            self.parts.append(Part(feature, zoom, m, extra_tags))

    def envelope(self):
        return self.parts[0].geom.envelope()
