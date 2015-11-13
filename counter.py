# -*- coding: utf-8 -*-
import os
import json
import argparse
from collections import OrderedDict

# Parser for the script's arguments
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="The path to the categories' dir")
parser.add_argument("-o", "--output", help="The file path to save the result")
args = parser.parse_args()

data = OrderedDict()
for root, dirs, files in os.walk(args.directory):
    if not dirs:
        subcategory = root.split('/').pop()
        category = root.split('/').pop(-2)
        if category not in data.keys():
            data.setdefault(category, OrderedDict())
        data[category].setdefault(subcategory, 0)
        for file in files:
            extension = file.split('.')[-1].lower()
            if extension in ['jpg', 'jpeg', 'png', 'gif']:
                data[category][subcategory] += 1
            else:
                print(root, file)

print(json.dumps(data, ensure_ascii=False, indent=4))
print('total', sum([c for k, s in data.items() for x, c in s.items()]))
if args.output:
    with open(args.output, 'w') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)
