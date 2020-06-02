# SPDX-License-Identifier: MIT

import mapnik
import os
import re
import sys
import yaml
from .doc_writer import DocWriter
from .feature import Feature

def clean_name(old_id):
    """Replace invalid characters."""
    return re.sub(r"[^\w\s_-]+", "", old_id)

def clear_layers(mapnik_map):
    """Remove all layers from a mapnik.Map instance because mapnik_map.layers.clear() does not work."""
    length = len(mapnik_map.layers)
    for i in range(length - 1, -1, -1):
        # Since no proper method is exposed to delete a layer, we have to fall back to __delitem__
        mapnik_map.layers.__delitem__(i)

def generate_legend(legend_file, map_file, zoom=None, overwrite=False):
    DEFAULT_ZOOM = 17
    out_dir = os.path.join(os.getcwd(), "output")
    legend = yaml.safe_load(legend_file)
    if "fonts_dir" in legend:
        mapnik.FontEngine.register_fonts(legend["fonts_dir"])
    srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
    #TODO Raise error instead of exception if width or height are missing
    m = mapnik.Map(legend['width'], legend['height'], srs)
    mapnik.load_map_from_string(m, map_file.read().encode("utf-8"), False, os.path.dirname(map_file.name))
    m.width = legend['width']
    m.height = legend['height']
    if "background" in legend:
        m.background = mapnik.Color(legend["background"])
    layer_styles = []
    for l in m.layers:
        # List comprehension is required to force Python to copy the list of styles. It goes out of scope otherwise.
        layer_styles.append({"name": l.name, "styles": [ s for s in l.styles ]})
    docs = DocWriter()
    docs.image_width = legend["width"]

    #TODO Allow to choose output directory from command line
    os.makedirs("output", exist_ok=True)
    for idx, feature in enumerate(legend["features"], start=0):
        # TODO: use a proper csv library rather than .join(",") !
        z = zoom
        if z is None:
            z = feature.get("zoom", DEFAULT_ZOOM)
        feature = Feature(feature, z, m, legend["extra_tags"])
        m.zoom_to_box(feature.envelope())
        clear_layers(m)

        for part in feature.parts:
            if not part:
                sys.stderr.write("WARNING: Can't find any layers defined for a part of {}\n".format(feature.name))
                continue
            for layer_name in part.layers:
                ls = [ l for l in layer_styles if l["name"] == layer_name ]
                if len(ls) == 0:
                    sys.stderr.write("WARNING: Can't find {} in the xml file.\n".format(layer_name))
                    continue
                for layer_style in ls:
                    l = mapnik.Layer(layer_name, m.srs)
                    datasource = mapnik.Datasource(type="csv", inline=part.to_csv())
                    l.datasource = datasource
                    for lls in layer_style["styles"]:
                        l.styles.append(lls)
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
                sys.stderr.write("ERROR: {} is a key needed for feature \"{}\" on zoom level {}. Try adding {} to the extra_tags list.\n".format(match_data.group(1), feature.name, z, match_data.group(1)))
                continue
            else:
                raise e
        docs.append(os.path.basename(filename), feature.description)

    with open(os.path.join(out_dir, "docs.html"), "w") as f:
        f.write(docs.to_html())
    # PDF output intentionally dropped
