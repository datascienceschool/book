# -*- coding: utf-8 -*-

import errno
import os
import re
import sys
from os import environ, pathsep, chdir
from string import Template
from subprocess import call, DEVNULL
from textwrap import dedent

import nbformat

FONTS = [
    "ccfonts",
    "cmbright",
    "fouriernc",
    "mathpazo",
    "mathptmx",
    "newtxmath"
    "pxfonts",
    "txfonts",
]

FONT_NAME = "txfonts"

filenames = [filename for filename in os.listdir() if
             filename.endswith(".ipynb") and re.match(r"^\d{2}.\d{2}", filename)]
filenames = sorted(filenames)

cur_dir = os.path.dirname(__file__)
eq_dir = os.path.join(cur_dir, "eq")
try:
    os.makedirs(eq_dir)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(eq_dir):
        pass
chdir(eq_dir)

env = environ.copy()
if 'TEXINPUTS' in env:
    env['TEXINPUTS'] = eq_dir + pathsep + env['TEXINPUTS']
else:
    env['TEXINPUTS'] = eq_dir + pathsep * 2

target_chapters = list(range(10))
target_sections = list(range(20))

target_chapters = [3]
target_sections = [2]

for filename in filenames:
    chap_num = int(filename[:2])
    sect_num = int(filename[3:5])
    if chap_num not in target_chapters:
        continue
    if sect_num not in target_sections:
        continue
    print(os.path.join(cur_dir, filename))
    with open(os.path.join(cur_dir, filename), "r+") as f:
        count = 0  # equation counter
        notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        markdown_cells = [cell for cell in notebook.cells if cell.cell_type == "markdown"]
        for cell in markdown_cells:
            eqs = re.findall(r"(\$\$.*?\$\$)", cell.source, re.MULTILINE | re.DOTALL)
            if len(eqs) > 0:
                for eq in eqs:
                    # 태그 검색
                    tags = re.findall(r"\\tag\{(.*?)\}", eq, re.MULTILINE | re.DOTALL)
                    if len(tags) > 0:
                        eq_filename = "eq.{}.tex".format(tags[0])
                        print(eq_filename)

                        template = Template(dedent(r"""
                            \documentclass[preview,fleqn]{standalone}
                            \usepackage{kotex}
                            \usepackage{amsmath}
                            \usepackage{cancel}
                            \usepackage{${fontname}}
                            \begin{document}
                            ${eq}
                            \end{document}
                            """))

                        content = template.substitute(eq=eq.replace("$$", "").strip(), fontname=FONT_NAME)

                        eq_fullpath = os.path.join(eq_dir, eq_filename)
                        with open(eq_fullpath, "w") as fw:
                            fw.write(content)

                        try:
                            retcode = call("xelatex --shell-escape {}".format(eq_filename), shell=True, env=env,
                                           stdout=DEVNULL)
                            if retcode != 0:
                                print("LaTeX terminated with signal", -retcode, file=sys.stderr)
                                ret_log = True
                            os.unlink(os.path.join(eq_dir, "{}.log".format(os.path.splitext(eq_filename)[0])))
                            os.unlink(os.path.join(eq_dir, "{}.aux".format(os.path.splitext(eq_filename)[0])))
                            os.unlink(os.path.join(eq_dir, "{}.tex".format(os.path.splitext(eq_filename)[0])))
                        except OSError as e:
                            print("LaTeX execution failed:", e, file=sys.stderr)
