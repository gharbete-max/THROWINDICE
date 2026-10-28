"""Usage: render_all.py <pug|alien|kitten> <idle|special|hang> <frames> <res> <samples> [only_frame]"""
import sys, os, math; sys.path.insert(0, '/home/claude/bl')
import bpy; from mathutils import Vector
from lib import *; import anim
char, mode, n, res, samples = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
only = int(sys.argv[6]) if len(sys.argv) > 6 else None
if char == 'pug':
    import pug; rig, parts = pug.build(); pose = anim.pug_pose; exp = 0.45
else:
    import cat; rig, parts = cat.build(char); pose = anim.alien_pose if char == 'alien' else anim.kitten_hang; exp = 0.0 if char == 'alien' else 0.15
if char == 'kitten':  # front-on orthographic framing around the hanging pose
    import numpy as np, json
    pose(rig, parts, 0); bpy.context.view_layer.update()
    body = [o for o in bpy.data.objects if o.type == 'MESH' and o.particle_systems and o.name.startswith('cat')][0]
    me = body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh(); P = np.array([body.matrix_world @ v.co for v in me.vertices])
    lo, hi = P.min(0), P.max(0); cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2; sc = max(hi[0] - lo[0], hi[2] - lo[2]) * 1.2
    stage(res=res, samples=samples, cam_loc=(cx, -8, cz), target=(cx, 0, cz), ortho=sc, exposure=exp)
    paws = [rig.matrix_world @ rig.pose.bones[f'fore.{n}'].tail for n in 'LR']
    json.dump({'paws_px': [[float((p.x - cx) / sc + 0.5), float(0.5 - (p.z - cz) / sc)] for p in paws]}, open('/home/claude/bl/kitten_frame.json', 'w'))
else:
    stage(res=res, samples=samples, cam_loc=(-1.7, -7.4, 1.9), target=(0, 0, 1.3), lens=74 if char != 'pug' else 78, exposure=exp)
    shadow_catcher()
out = f'/home/claude/bl/frames/{char}_{mode}'; os.makedirs(out, exist_ok=True)
for i in range(n):
    if only is not None and i != only: continue
    pose(rig, parts, i / n, special=(mode == 'special')); render(f'{out}/{i:03d}.png')
