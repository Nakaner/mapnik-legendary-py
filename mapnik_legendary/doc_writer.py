# SPDX-License-Identifier: MIT
import jinja2

class DocWriter:
    def __init__(self):
        self.entries = []
        self.image_width = 100
        self.env = jinja2.Environment(autoescape=True)

    def append(self, image, description):
        self.entries.append((image, description))

    def to_html(self):
        template = self.env.from_string("""
<html>
    <head></head>
    <body>
        <table>
            {% for entry in entries %}
            <tr><td><img src="{{ entry[0] }}"></td><td>{{ entry[1] }}</td></tr>
            {% endfor %}
        </table>
    </body>
</html>""")
        html = template.render(entries=self.entries)
        return html
