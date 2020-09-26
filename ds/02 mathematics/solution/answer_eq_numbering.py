# -*- coding: utf-8 -*-

import os
import re

import nbformat

filenames = [filename for filename in os.listdir() if
             filename.endswith(".ipynb") and re.match(r"^A.\d{2}", filename)]
filenames = sorted(filenames)

target_chapters = list(range(10))
target_sections = list(range(20))

chap_num = "A"
target_sections = [10]

for filename in filenames:
    sect_num = int(filename[2:4])
    if sect_num not in target_sections:
        continue
    print(filename, sect_num)
    with open(filename, "r+") as f:
        count = 0  # equation counter
        notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        markdown_cells = [cell for cell in notebook.cells if cell.cell_type == "markdown"]
        for cell in markdown_cells:
            eqs = re.findall(r"(\$\$.*?\$\$)", cell.source, re.MULTILINE | re.DOTALL)
            if len(eqs) > 0:
                for eq in eqs:
                    idx = cell.source.find(eq)
                    if idx > 4:
                        if cell.source[idx + 2] == "`":
                            continue
                        if cell.source[idx - 4: idx - 1] == "```":
                            continue

                    count += 1

                    eq = eq.strip()

                    # 만약 한줄이면 여러줄로 분리
                    eq_lines = eq.split("\n")
                    if len(eq_lines) == 1:
                        eq_lines0 = eq_lines[0]
                        eq_lines0 = re.sub(r"^\$\$\s*", r"$$\n", eq_lines0, 1)
                        eq_lines0 = re.sub(r"\s*\$\$$", r"\n$$", eq_lines0, 1)
                        eq_lines = eq_lines0.split("\n")

                    # \begin{align} 이나 \begin{aligned} 가 없으면 추가
                    if eq.find(r"\begin{align}") == -1 and eq.find(r"\begin{align*}") == -1:
                        eq_lines.insert(1, r"\begin{align}")
                        eq_lines.insert(len(eq_lines) - 1, r"\end{align}")

                    # 태그 검색
                    tags = re.findall(r"\\tag\{.*?\}", eq, re.MULTILINE | re.DOTALL)

                    if len(tags) == 0:
                        # 태그 추가
                        new_tag = r"\tag{{{0}.{1}.{2}}}".format(chap_num, sect_num, count)
                        eq_lines.insert(len(eq_lines) - 2, new_tag)
                        new_eq = "\n".join(eq_lines)
                    else:
                        # 태그 변경
                        new_tag = r"\\tag{{{0}.{1}.{2}}}".format(chap_num, sect_num, count)
                        new_eq = "\n".join(eq_lines)
                        new_eq = re.sub(r"\\tag\{.*?\}", new_tag, new_eq, 1)

                    cell.source = cell.source.replace(eq, new_eq)

                # \begin{align*} => \begin{align}
                cell.source = cell.source.replace(r"\begin{align*}", r"\begin{align}")
                cell.source = cell.source.replace(r"\end{align*}", r"\end{align}")

        nbformat.validate(notebook)

    if count > 0:
        with open(filename, "w") as f:
            nbformat.write(notebook, f)
