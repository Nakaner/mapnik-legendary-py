#! /usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import logging
from mapnik_legendary import generate_legend

parser = argparse.ArgumentParser()
parser.add_argument("-z", "--zoom", type=int, default=None, help="Override the zoom level stated in the legend file")
parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
parser.add_argument("legend_file", type=argparse.FileType("r"), help="Legend file")
parser.add_argument("map_file", type=argparse.FileType("r"), help="Map file")
args = parser.parse_args()

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("mapnik_legendary")
logger.setLevel(logging.INFO)

try:
    generate_legend(args.legend_file, args.map_file, args.zoom, args.overwrite)
except Exception as e:
    logger.exception("Mapnik Legendary failed")
    exit(1)
