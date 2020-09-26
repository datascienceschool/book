# -*- coding: utf-8 -*-

import os
import re

import nbformat
from nbconvert.exporters import MarkdownExporter

exporter = MarkdownExporter()
dirname = os.path.dirname(__file__)
filenames = [filename for filename in os.listdir() if
             filename.endswith(".ipynb") and re.match(r"^\d{2}.\d{2}", filename)]
filenames = sorted(filenames)

target_chapters = list(range(10))
target_sections = list(range(20))

target_chapters = [10]
target_sections = [4]

for filename in filenames:
    chap_num = int(filename[:2])
    sect_num = int(filename[3:5])
    if chap_num not in target_chapters:
        continue
    if sect_num not in target_sections:
        continue
    with open(filename, "r") as f:
        notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        (body, resources) = exporter.from_notebook_node(notebook)
        md_filename = filename[:-6] + ".txt"
    with open(os.path.join(dirname, "md", md_filename), "w") as fw:
        print("converting {}...".format(filename))
        fw.write(body)
