#!/bin/bash
# one Blender process per frame: keeps memory flat (the furry kitten peaks ~3.6 GB)
cd /home/claude/bl
for job in "kitten hang 24 320 40" "alien idle 20 320 32" "alien special 16 320 32" "pug idle 20 320 28" "pug special 16 320 28"; do
  set -- $job; echo "start $1 $2 $(date +%T)"
  for ((i=0; i<$3; i++)); do
    [ -f frames/$1_$2/$(printf %03d $i).png ] && continue
    bin/python render_all.py $job $i 2>&1 | grep -iE "traceback|error:" | grep -v CUEW
  done
  echo "done $1 $2 $(ls frames/$1_$2 | wc -l) frames $(date +%T)"
done
