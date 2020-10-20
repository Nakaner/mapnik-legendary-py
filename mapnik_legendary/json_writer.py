# SPDX-License-Identifier: LGPL-2.1-or-later
import json
from .legend_entry import LegendEntry

class JSONWriter:
    """Write the HTML file of the legend table."""
    def __init__(self, width, template):
        """
        Args:
            width (int): width of the legend images
            tempalte (str): content of the template as string
        """
        self.entries = []
        self.image_width = width

    def append(self, image, description, zoom, properties={}):
        self.entries.append(LegendEntry(image, description, zoom, properties))

    def write(self):
        return json.dumps(self.entries, default=lambda o: o.__dict__)
