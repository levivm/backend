# -*- coding: utf-8 -*-
import os
import argparse

# Parser for the script's arguments
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="The path to the categories' dir")
args = parser.parse_args()

for root, dirs, files in os.walk(args.directory):
    if not dirs:
        index = 1
        subcategory = root.split('/').pop()
        for file in files:
            extension = file.split('.')[-1].lower()
            if extension in ['jpg', 'jpeg', 'png', 'gif']:
                filename = '%s %s.%s' % (subcategory.lower(), str(index).zfill(2), extension)
                src = os.path.join(root, file)
                dst = os.path.join(root, filename)
                os.rename(src, dst)
                index += 1
