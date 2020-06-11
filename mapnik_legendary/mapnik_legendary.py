# SPDX-License-Identifier: LGPL-2.1-only

import logging
import mapnik
import os
import re
import yaml
from PIL import Image, ImageColor
from .doc_writer import DocWriter
from .feature import Feature
from .exceptions import MapnikLegendaryError
from .layer_styles import LayerStyles


def clean_name(old_id):
    """Replace invalid characters."""
    return re.sub(r"[^\w\s_-]+", "", old_id)

def clear_layers(mapnik_map):
    """Remove all layers from a mapnik.Map instance because mapnik_map.layers.clear() does not work."""
    length = len(mapnik_map.layers)
    for i in range(length - 1, -1, -1):
        # Since no proper method is exposed to delete a layer, we have to fall back to __delitem__
        mapnik_map.layers.__delitem__(i)


def image_only_background(path, background_color):
    """Check if the image shows background only."""
    with Image.open(path) as image:
        if background_color == "transparent":
            bc = "#ffffff00"
        else:
            bc = background_color
        width = image.width
        height = image.height
        if not bc.startswith("#"):
            bc = "#{}".format(bc)
        if len(bc) != 7 and len(bc) != 9:
            raise MapnikLegendaryError("Background color format not supported. Use #RRGGBB or #RRGGBBAA instead.")
        if len(bc) == 7:
            bc += "ff"
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        c = ImageColor.getcolor(bc, "RGBA")
        for x in range(width):
            for y in range(height):
                pixel_color = image.getpixel((x, y))
                if pixel_color != c and (pixel_color[3] != 0 and pixel_color[3] != c[3]):
                    return False
        return True


def generate_legend(legend_file, map_file, zoom=None, overwrite=False):
    DEFAULT_ZOOM = 17
    logger = logging.getLogger("mapnik-legendary")
    out_dir = os.path.join(os.getcwd(), "output")
    legend = yaml.safe_load(legend_file)
    if "fonts_dir" in legend:
        mapnik.FontEngine.register_fonts(legend["fonts_dir"])
    srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
    if "width" not in legend or "height" not in legend:
        raise MapnikLegendaryError("width or height not specified in legend definition")
    m = mapnik.Map(legend['width'], legend['height'], srs)
    mapnik.load_map_from_string(m, map_file.read().encode("utf-8"), False, os.path.dirname(map_file.name))
    m.width = legend['width']
    m.height = legend['height']
    background_color = legend.get("background", "transparent")
    if background_color == "transparent":
        m.background = mapnik.Color(255, 255, 255, 0)
    else:
        m.background = mapnik.Color(background_color)
    layer_styles = LayerStyles(m.layers)
    docs = DocWriter()
    docs.image_width = legend["width"]

    #TODO Allow to choose output directory from command line
    os.makedirs("output", exist_ok=True)
    for idx, feature in enumerate(legend["features"], start=0):
        z = zoom
        if z is None:
            z = feature.get("zoom", DEFAULT_ZOOM)
        feature = Feature(feature, z, m, legend["extra_tags"])
        m.zoom_to_box(feature.envelope())
        clear_layers(m)

        for part in feature.parts:
            if not part:
                logger.warn("Can't find any layers defined for a part of {}".format(feature.name))
                continue
            for layer_name in part.layers:
                l = layer_styles.prepare_layer(layer_name, m.srs, part)
                if l:
                    m.layers.append(l)

        fid = feature.name
        if not fid:
            fid = "legend-{}".format(idx)
        fid = clean_name(fid)
        filename = os.path.join(out_dir, "{}-{}.png".format(fid, z))
        i = 0
        while os.path.isfile(filename) and not overwrite:
            i += 1
            filename = os.path.join(out_dir, "{}-{}-{}.png".format(fid, z, i))
        try:
            mapnik.render_to_file(m, filename, "png256:t=2")
        except Exception as e:
            r = r"^CSV Plugin: no attribute '([^']+)'"
            match_data = re.match(r, str(e))
            if match_data:
                raise MapnikLegendaryError("{} is a key needed for feature \"{}\" on zoom level {}. Try adding {} to the extra_tags list.\n".format(match_data.group(1), feature.name, z, match_data.group(1)))
                continue
            else:
                raise e
        if image_only_background(filename, background_color):
            logger.warn("Feature \"{}\" on zoom {} not rendered, legend image is empty.".format(feature.name, z))
        docs.append(os.path.basename(filename), feature.description)

    with open(os.path.join(out_dir, "docs.html"), "w") as f:
        f.write(docs.to_html())
    # PDF output intentionally dropped
