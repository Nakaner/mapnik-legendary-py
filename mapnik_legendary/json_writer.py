# SPDX-License-Identifier: LGPL-2.1-or-later
import json
from .legend_entry import LegendEntry

class JSONWriter:
    """Write the HTML file of the legend table."""
    def __init__(self, width, template, merge_identical_entries=True):
        """
        Args:
            width (int): width of the legend images
            tempalte (str): content of the template as string
        """
        self.entries = []
        self.image_width = width
        self.merge_identical_entries = merge_identical_entries

    def append(self, legend_entry):
        """Add new legend entry. Returns false if last entry was updated instead."""
        if len(self.entries) > 0:
            last_entry = self.entries[-1]
            if legend_entry.equals(last_entry):
                if legend_entry.zoom - 1 == last_entry.maxzoom:
                    last_entry.maxzoom += 1
                    return False
                if legend_entry.zoom + 1 == last_entry.minzoom:
                    last_entry.minzoom -= 1
                    return False
        self.entries.append(legend_entry)
        return True

    def write(self):
        return json.dumps(self.entries, default=lambda o: o.as_dict())
