"""How much does a character's body distort while dancing? Reports the 99th-percentile edge stretch vs rest and how far
the face skin drifts relative to the rigid eyes (in body units; the head is ~1 unit wide). Usage: shape_check.py <char>"""
import sys; char = sys.argv[1]; sys.argv = sys.argv[:1]; sys.path.insert(0, '/home/claude/bl')
import bpy, numpy as np, anim
from lib import *
if char == 'pug': import pug; rig, parts = pug.build(); pose = anim.pug_pose
else: import cat; rig, parts = cat.build(char); pose = anim.alien_pose if char == 'alien' else anim.kitten_hang
body = [o for o in bpy.data.objects if o.type == 'MESH' and o.particle_systems and o.name.split('.')[0] in ('pug', 'cat')][0]
eye = [o for o in bpy.data.objects if o.name.startswith('eye')][0]
E = np.array([e.vertices[:] for e in body.data.edges])
def state():
    bpy.context.view_layer.update(); me = body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    P = np.array([body.matrix_world @ v.co for v in me.vertices]); M = np.array(eye.matrix_world.inverted())
    return P, M
P0, M0 = state(); L0 = np.linalg.norm(P0[E[:, 0]] - P0[E[:, 1]], axis=1)
loc = lambda P, M: (np.c_[P, np.ones(len(P))] @ M.T)[:, :3]
near = np.argsort(np.linalg.norm(P0 - np.array(eye.matrix_world.translation), axis=1))[:300]; F0 = loc(P0[near], M0)
ws, wd = [], []
for t in np.linspace(0, 1, 9)[:-1]:
    for sp in ([False, True] if char != 'kitten' else [False]):
        pose(rig, parts, t, special=sp); P, M = state()
        L = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1); ws.append(np.percentile(np.abs(L / L0 - 1), 99))
        sc = np.linalg.norm(np.array(eye.matrix_world.to_3x3()), axis=0).mean()
        wd.append(np.linalg.norm(loc(P[near], M) - F0, axis=1).max() * sc)
print(f'{char}: worst edge stretch {max(ws)*100:.1f}%  worst face drift around the eye {max(wd):.3f}')
