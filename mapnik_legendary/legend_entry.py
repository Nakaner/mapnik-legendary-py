# SPDX-License-Identifier: LGPL-2.1-or-later
class LegendEntry:
    def __init__(self, image, description, zoom, properties={}):
        self.image = image
        self.description = description
        self.zoom = zoom
        self.properties = properties
