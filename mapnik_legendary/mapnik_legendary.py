# SPDX-License-Identifier: LGPL-2.1-or-later

import logging
import mapnik
import os
import sys
import yaml
from PIL import Image, ImageColor
from .feature import Feature
from .exceptions import MapnikLegendaryError
from .layer_styles import LayerStyles
from .legend_entry import clean_name, LegendEntry


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


def generate_legend_item(mapnik_map, layer_styles, feature, zoom_level, background_color, properties, images_dir):
    """Render a legend item.

    Returns:
        Tuple (filename of the image, description)
    """
    logger = logging.getLogger("mapnik-legendary")
    logger.info("Rendering feature {} on zoom level {}".format(feature.name, zoom_level))
    mapnik_map.zoom_to_box(feature.envelope())
    clear_layers(mapnik_map)

    for part in feature.parts:
        if not part:
            logger.warn("Can't find any layers defined for a part of {}".format(feature.name))
            continue
        for layer_name in part.layers:
            l = layer_styles.prepare_layer(layer_name, mapnik_map.srs, part)
            if l:
                mapnik_map.layers.append(l)

    fid = feature.name
    if not fid:
        fid = "legend-{}".format(idx)
    fid = clean_name(fid)
    legend_entry = LegendEntry(fid, feature.description, zoom_level, properties, images_dir)
    filename = legend_entry.get_image_file_path()
    try:
        mapnik.render_to_file(mapnik_map, filename, "png256:t=2")
    except Exception as e:
        r = r"^CSV Plugin: no attribute '([^']+)'"
        match_data = re.match(r, str(e))
        if match_data:
            raise MapnikLegendaryError("{} is a key needed for feature \"{}\" on zoom level {}. Try adding {} to the extra_tags list.\n".format(match_data.group(1), feature.name, zoom_level, match_data.group(1)))
        else:
            raise e
    if image_only_background(filename, background_color):
        logger.warn("Feature \"{}\" on zoom {} not rendered, legend image is empty.".format(feature.name, zoom_level))
    return legend_entry


def generate_legend(legend_file, map_file, writer_class, **kwargs):#output_directory, zoom=None, overwrite=False):
    """Generate a map key for a Mapnik map style.

    Args:
        legend_file (file): File-like object the YAML document defining the items of the legend should be read from
        map_file (file): File-like object the Mapnik XML map style should be read from
        writer_class (class): instance of class implementing the output format

    Keyword Args:
        output_file (file): File-like object to write the rendered template to (default: sys.stdout)
        images_directory (str): Path to a directory where the images are supposed to be written to
            (defaults to the directory of the output file).
        zoom (int): The zoom level the legend should be produced for (defaults to None). If it is not provided,
            all zoom levels specified in the legend file will be produced.
        template (str): Jinja2 template to render
    """
        
    logger = logging.getLogger("mapnik-legendary")
    template = kwargs.get("template")
    zoom = kwargs.get("zoom")
    output_file = kwargs.get("output_file", sys.stdout)
    images_dir = kwargs.get("images_directory")
    if output_file != sys.stdout and images_dir is None:
        images_dir = os.path.dirname(os.path.abspath(output_file.name))
    elif output_file == sys.stdout and images_dir is None:
        raise MapnikLegendaryError("Cannot guess images output directory because the output file is not a regular file (e.g. standard output)")
    legend = yaml.safe_load(legend_file)
    if "fonts_dir" in legend:
        mapnik.FontEngine.register_fonts(legend["fonts_dir"])
    srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
    if "width" not in legend or "height" not in legend:
        raise MapnikLegendaryError("width or height not specified in legend definition")
    m = mapnik.Map(legend['width'], legend['height'], srs)
    mapnik.load_map_from_string(m, map_file.read().encode("utf-8"), False, os.path.dirname(map_file.name))
    default_width = legend['width']
    default_height = legend['height']
    m.width = default_width
    m.height = default_height
    background_color = legend.get("background", "transparent")
    if background_color == "transparent":
        m.background = mapnik.Color(255, 255, 255, 0)
    else:
        m.background = mapnik.Color(background_color)
    layer_styles = LayerStyles(m.layers, kwargs["tmp_dir"])
    writer = writer_class(legend["width"], template)

    for idx, feature in enumerate(legend["features"], start=0):
        z = feature.get("zoom")
        min_zoom = feature.get("min_zoom")
        max_zoom = feature.get("max_zoom")
        if z is not None and (min_zoom is not None or max_zoom is not None):
            raise MapnikLegendaryError("Conflicting zoom specification for {}. Sepcify either zoom only or both min_zoom and max_zoom.".format(feature.get("name")))
        if z is None and min_zoom is None and max_zoom is None:
            raise MapnikLegendaryError("Incomplete zoom specification for feature {}.".format(feature.get("name")))
        if min_zoom is None and max_zoom is None:
            min_zoom = int(z)
            max_zoom = int(z)
        if min_zoom is not None:
            min_zoom = int(min_zoom)
        else:
            min_zoom = 0
        if max_zoom is not None:
            max_zoom = int(max_zoom)
        else:
            max_zoom = 24
        if min_zoom > max_zoom:
            raise MapnikLegendaryError("min_zoom is larger than max_zoom for feature {}".format(feature.get("name")))
        properties = feature.get("properties", {})
        if not isinstance(properties, dict):
            raise MapnikLegendaryError("properties of feature {} is not a key-value mapping but {}".format(
                feature.get("name"), type(properties)
            ))
        for zoom_this in range(min_zoom, max_zoom + 1):
            f = Feature(feature, zoom_this, m, legend["extra_tags"])
            if zoom_this != zoom and zoom is not None:
                logger.debug("Skipping {} because it is on zoom level {} but {} was requested.".format(f.name, z, zoom))
                continue
            # Special height or width for this item
            m.height = feature.get("image", {}).get("height", default_height)
            m.width = feature.get("image", {}).get("width", default_width)
            legend_entry = generate_legend_item(m, layer_styles, f, zoom_this, background_color, properties, images_dir)
            writer.append(legend_entry)
    output_file.write(writer.write())
    output_file.flush()
    layer_styles.cleanup()
    # PDF output intentionally dropped
