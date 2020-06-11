# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
import mapnik

class LayerStyles:

    logger = logging.getLogger("mapnik-legendary")

    """Mapping from layer names to style names in a Mapnik style"""
    def __init__(self, layers):
        """
        Args:
            layers(mapnik.Layers): layers of a style
        """
        self.styles_by_layer = {}
        for l in layers:
            # List comprehension is required to force Python to copy the list of styles. It goes
            # out of scope otherwise.
            styles = [ s for s in l.styles ]
            self.styles_by_layer[l.name] = styles

    def get_styles(self, layer_name):
        """Get the names of the styles used by a given layer."""
        return self.styles_by_layer.get(layer_name, [])

    def prepare_layer(self, layer_name, srs, part):
        l = mapnik.Layer(layer_name, srs)
        l.datasource = mapnik.Datasource(type="csv", inline=part.to_csv())
        styles = self.get_styles(layer_name)
        if len(styles) == 0:
            logger.warn("Can't find layer {} in the Mapnik xml file.".format(layer_name))
            return None
        for style in self.get_styles(layer_name):
            l.styles.append(style)
        return l
