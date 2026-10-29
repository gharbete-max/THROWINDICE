#!/bin/bash
# one Blender process per frame (memory stays flat); resumable
cd /home/claude/bl
for job in "alien idle 66 360 32" "alien special 24 360 32" "alien flip 24 360 32" "alien pose 24 360 32" "pug idle 66 360 32" "pug special 24 360 32" "pug flip 24 360 32" "pug pose 24 360 32"; do
  set -- $job; echo "start $1 $2 $(date +%T)"
  for ((i=0; i<$3; i++)); do
    [ -f frames/$1_$2/$(printf %03d $i).png ] && continue
    bin/python render_all.py $job $i 2>&1 | grep -iE "traceback|error:" | grep -v CUEW
  done
  echo "done $1 $2 $(ls frames/$1_$2 | wc -l) frames $(date +%T)"
done
