**This port is experimental and has still some serious bugs.**

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

* [Python-Mapnik bindings](https://github.com/mapnik/Ruby-Mapnik) >= 0.2.0
* mapnik 3.x and Python3
* Pillow
* All data sources set up as required by the style for rendering. This means if your styles requires a database called "gis" with a specific schema, you have to load some data into it.

## Running

For full options, run

```sh
mapnik-legendary.py -h
```

## Examples

```sh
mapnik-legendary.py examples/openstreetmap-carto-legend.yml osm-carto.xml
```

See [examples/openstreetmap-carto-legend.yml](examples/openstreetmap-carto-legend.yml)

## License

This software is based on mapnik-legendary (for Ruby) by Andy Allan and published under the terms of the MIT license. See [LICENSE.md](LICENSE.md) for details.
