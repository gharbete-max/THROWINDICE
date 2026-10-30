#!/bin/bash
# one Blender process per frame; resumable (skips finished frames)
cd /home/claude/bl
for ((i=0; i<420; i++)); do
  [ -f frames/dancer_idle/$(printf %03d $i).png ] && continue
  bin/python render_all.py dancer idle 420 300 24 $i 2>&1 | grep -iE "traceback|error:" | grep -v CUEW
done
echo "done $(ls frames/dancer_idle | wc -l) $(date +%T)"
