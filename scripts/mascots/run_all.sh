#!/bin/bash
cd /home/claude/bl
for job in "pug idle 20 320 28" "alien idle 20 320 32" "kitten hang 16 320 40" "pug special 16 320 28" "alien special 16 320 32"; do
  set -- $job; echo "start $1 $2 $(date +%T)"; bin/python render_all.py $job 2>&1 | grep -iE "error|traceback" ; echo "done $1 $2 $(date +%T)"
done
