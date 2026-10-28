# Mascots

Rendered in Blender (Cycles, particle fur) through the `bpy` Python package.

    python3.13 -m venv bl && bl/bin/pip install bpy==5.2.3
    ./run_all.sh          # frames -> /home/claude/bl/frames (edit paths at the top of each script)
    python3 export.py     # -> assets/mascots/*.webp

`pug.py` / `cat.py` build the characters, `anim.py` holds the dance curves.
