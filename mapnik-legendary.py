#! /usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import sys
from mapnik_legendary import generate_legend

parser = argparse.ArgumentParser()
parser.add_argument("-z", "--zoom", type=int, default=None, help="Override the zoom level stated in the legend file")
parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
parser.add_argument("legend_file", type=argparse.FileType("r"), help="Legend file")
parser.add_argument("map_file", type=argparse.FileType("r"), help="Map file")
args = parser.parse_args()

try:
    generate_legend(args.legend_file, args.map_file, args.zoom, args.overwrite)
except Exception as e:
    sys.stderr.write("ERROR: {}\n".format(e))
    exit(1)
