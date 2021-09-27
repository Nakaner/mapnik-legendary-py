# SPDX-License-Identifier: LGPL-2.1-or-later
import jinja2
from .legend_entry import LegendEntry

class HTMLWriter:
    """Write the HTML file of the legend table."""
    def __init__(self, width, template):
        """
        Args:
            width (int): width of the legend images
            tempalte (str): content of the template as string
        """
        self.entries = []
        self.image_width = width
        self.env = jinja2.Environment(autoescape=True)
        self.template = self.env.from_string(template)

    def append(self, legend_entry):
        self.entries.append(legend_entry)
        return True

    def write(self):
        html = self.template.render(entries=self.entries)
        return html
