# SPDX-License-Identifier: LGPL-2.1-or-later

import re
import os.path
from PIL import Image, ImageColor


def clean_name(old_id):
    """Replace invalid characters."""
    return re.sub(r"[^-a-zA-Z0-9_]+", "", old_id)


class LegendEntry:
    def __init__(self, image, description, zoom, properties, images_directory):
        self.image = image
        self.image_directory = images_directory
        self.description = description
        self.minzoom = zoom
        self.maxzoom = zoom
        self.zoom = zoom
        self.properties = properties

    def as_dict(self):
        a = { k:v for k,v in self.__dict__.items() if k in ["description", "minzoom", "maxzoom", "properties"] }
        a["image"] = self.get_image_file_path()
        return a

    def image_name(self):
        return "{}-{}.png".format(self.image, self.zoom)

    def get_image_file_path(self):
        return os.path.join(self.image_directory, self.image_name())

    def equals(self, other):
        return self.description == other.description and self.properties == other.properties and self.compare_image(other)

    def compare_image(self, other):
        """Return true if image of this entry and another entry is equal (pixel-wise)."""
        with Image.open(self.get_image_file_path()) as image1:
            width1 = image1.width
            height1 = image1.height
            with Image.open(other.get_image_file_path()) as image2:
                width2 = image2.width
                height2 = image2.height
                if width1 != width2 or height1 != height2:
                    return False
                for x in range(width1):
                    for y in range(height1):
                        if image1.getpixel((x, y)) != image2.getpixel((x, y)):
                            return False
        return True
