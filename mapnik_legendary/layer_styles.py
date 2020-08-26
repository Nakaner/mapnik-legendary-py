# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
import mapnik
import os
import re
from .exceptions import MapnikLegendaryError

class LayerStyles:

    logger = logging.getLogger("mapnik-legendary")
    good_chars_re = re.compile("[^-a-zA-Z0-9_]")

    """Mapping from layer names to style names in a Mapnik style"""
    def __init__(self, layers, tmp_dir):
        """
        Args:
            layers(mapnik.Layers): layers of a style
        """
        self.styles_by_layer = {}
        self.tmp_dir = tmp_dir
        self.tmp_files = set()
        for l in layers:
            # List comprehension is required to force Python to copy the list of styles. It goes
            # out of scope otherwise.
            styles = [ s for s in l.styles ]
            self.styles_by_layer[l.name] = styles

    def get_styles(self, layer_name):
        """Get the names of the styles used by a given layer."""
        return self.styles_by_layer.get(layer_name, [])

    def escape_filename(filename):
        return LayerStyles.good_chars_re.sub("_", filename)

    def get_tmp_filename(self, layer_name):
        fname = os.path.join(self.tmp_dir, LayerStyles.escape_filename(layer_name))
        self.tmp_files.add(fname)
        return fname

    def cleanup(self):
        for fname in self.tmp_files:
            os.remove(fname)

    def prepare_layer(self, layer_name, srs, part):
        l = mapnik.Layer(layer_name, srs)
        styles = self.get_styles(layer_name)
        if len(styles) == 0:
            self.logger.warn("Can't find layer {} in the Mapnik xml file.".format(layer_name))
            return None
        with open(self.get_tmp_filename(layer_name), mode="w") as tmp_file:
            tmp_file_name = tmp_file.name
            tmp_file.write(part.to_geojson())
        l.datasource = mapnik.Datasource(type="geojson", file=tmp_file_name)
        for style in self.get_styles(layer_name):
            l.styles.append(style)
        return l
