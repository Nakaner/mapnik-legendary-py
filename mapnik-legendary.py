#! /usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later

import argparse
import logging
import os.path
from mapnik_legendary import generate_legend, HTMLWriter, JSONWriter

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--format", type=str, help="Output format (html, json)", default="html")
parser.add_argument("-i", "--images-dir", type=str, help="Output directory for images")
parser.add_argument("-o", "--output-file", type=argparse.FileType("w"), required=True, help="Output file (rendered template)")
parser.add_argument("-t", "--template", type=argparse.FileType("r"), help="File to read the HTML template from")
parser.add_argument("-T", "--tmp-dir", type=str, required=True, help="Temporary directory")
parser.add_argument("-z", "--zoom", type=int, default=None, help="Render the legend for the specified zoom level only")
parser.add_argument("legend_file", type=argparse.FileType("r"), help="Legend file")
parser.add_argument("map_file", type=argparse.FileType("r"), help="Map file")
args = parser.parse_args()

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("mapnik_legendary")
logger.setLevel(logging.INFO)

if not os.path.isdir(args.images_dir):
    logger.error("Images output directory {} does not exist".format(args.images_dir))
    exit(1)

if not os.path.isdir(args.tmp_dir):
    logger.error("Temporary directory {} does not exist".format(args.tmp_dir))

try:
    template = None
    if args.template:
        template = args.template.read()

    writer = HTMLWriter
    if args.format == "json":
        writer = JSONWriter

    generate_legend(args.legend_file, args.map_file, template=template, zoom=args.zoom, images_directory=args.images_dir, output_file=args.output_file, tmp_dir=args.tmp_dir, writer_class=writer)
except Exception as e:
    logger.exception("Mapnik Legendary failed")
    exit(1)
