# -*- coding: utf-8 -*-

import json
import os
import re
from copy import deepcopy

dirname = os.path.dirname(__file__)
filenames = [filename for filename in os.listdir() if
             filename.endswith(".ipynb") and re.match(r"^\d{2}.\d{2}", filename)]
filenames = sorted(filenames)

target_chapters = list(range(1, 10))
target_sections = list(range(20))

# target_chapters = [2]
# target_sections = [1]

for filename in filenames:
    chap_num = int(filename[:2])
    sect_num = int(filename[3:5])
    if chap_num not in target_chapters:
        continue
    if sect_num not in target_sections:
        continue
    with open(filename, "r") as f:
        json_data = json.load(f)
        cells = deepcopy(json_data["cells"])
        print("converting {}...".format(filename), end=" ")
        print("cells : ", len(cells), end=" => ")
        for cell in json_data["cells"]:
            if cell["cell_type"] == "markdown":
                cells.remove(cell)
        print(len(cells))
        json_data["cells"] = cells

    if len(cells) > 0:
        with open(os.path.join(dirname, "codeonly", filename[:5] + ".ipynb"), "w") as fw:
            json.dump(json_data, fw)
