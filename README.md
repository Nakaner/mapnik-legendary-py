# Mapnik Legendary – Python Port

[mapnik_legendary.py](https://github.com/nakaner/mapnik-legendary-py) is the
Python port of [Mapnik
Legendary](https://github.com/gravitystorm/mapnik-legendary) by Andy Allan, a
small utility to help with generating legends (aka map keys) from Mapnik
stylesheets. You describe in a config file which attributes, and which zoom
level(s) you want an image for, and it reads the stylesheet and spits out .png
files. It uses the Python-Mapnik bindings to load the stylesheets and mess
around with the datasources, so you don't actually need any of the shapefiles
or database connections to make this work.

## Requirements

* [Python-Mapnik bindings](https://github.com/mapnik/python-mapnik)
* Mapnik 3.x and Python3
* Pillow
* All data sources set up as required by the style for rendering. This means if your styles requires a database called "gis" with a specific schema, you have to load some data into it.

## Running

For full options, run

```sh
mapnik-legendary.py -h
```

## Example


```sh
mkdir -p output
mapnik-legendary.py -o output/legend.html -t tempaltes/plain_table.html -z 18 examples/openstreetmap-carto-legend.yml path/to/osm-carto.xml
```

In order to work as expected, this example requires OSM Carto cloned at
`path/to/style`, its Mapnik XML file at `path/to/style/osm-carto.xml` and a
database containing at least empty tables with all required columns. It wil
render the legend for zoom level 18.

See [examples/openstreetmap-carto-legend.yml](examples/openstreetmap-carto-legend.yml) as an example.

## License

Copyright (c) 2013 Andy Allan
Copyright (c) 2020 Michael Reichert

This software is based on mapnik-legendary (for Ruby) by Andy Allan and published under the terms
of the GNU Lesser General Public License version 2.1 or newer. See [COPYING](COPYING) for the full
text of version 3 of the license.

The original mapnik-legendary for Ruby was published under the terms of the X11 license. See
[X11_license.md](X11_license.md) for details.
