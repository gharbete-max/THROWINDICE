#!/bin/bash
# one Blender process per frame (memory stays flat); resumable
cd /home/claude/bl
for job in "kitten hang 32 360 40" "kitten scared 14 360 40" "alien idle 32 360 36" "alien special 24 360 36" "pug idle 32 360 40" "pug special 24 360 40"; do
  set -- $job; echo "start $1 $2 $(date +%T)"
  for ((i=0; i<$3; i++)); do
    [ -f frames/$1_$2/$(printf %03d $i).png ] && continue
    bin/python render_all.py $job $i 2>&1 | grep -iE "traceback|error:" | grep -v CUEW
  done
  echo "done $1 $2 $(ls frames/$1_$2 | wc -l) frames $(date +%T)"
done
