"""Glossy 3D smiley balls for the Token World button: big forehead, small dot eyes, small smile.
Usage: smiley.py <yellow|blue> outdir [res] [samples] [frames]  -> outdir/000.png.. (frame 0 = still; the loop spins
the face around the view axis, yellow clockwise, blue anticlockwise, with the lights fixed)"""
import sys, math; sys.path.insert(0, '/home/claude/bl')
import bpy
from mathutils import Vector
from lib import *

kind, out = sys.argv[1], sys.argv[2]
res = int(sys.argv[3]) if len(sys.argv) > 3 else 512; samples = int(sys.argv[4]) if len(sys.argv) > 4 else 128
reset()
if kind == 'yellow':
    body = principled('ball', (1.0, 0.66, 0.0), 0.32, sss=0.12, sss_radius=(1, 0.6, 0.2), sss_scale=0.15, coat=0.6, coat_rough=0.08)
    feat = principled('feat', (0.012, 0.01, 0.008), 0.25, coat=1.0, coat_rough=0.02)
else:
    body = principled('ball', (0.05, 0.3, 1.0), 0.3, sss=0.12, sss_radius=(0.3, 0.6, 1.0), sss_scale=0.15, coat=0.6, coat_rough=0.08)
    feat = principled('feat', (0.97, 0.98, 1.0), 0.3, coat=0.8, coat_rough=0.05, sss=0.2, sss_radius=(1, 1, 1), sss_scale=0.02)

ball = uv_sphere('ball', 1.0, (0, 0, 0), seg=128, rings=64); ball.data.materials.append(body)
face = []
def _surf(x, z, lift):
    y = -math.sqrt(max(0.0, 1 - x * x - z * z)); return Vector((x, y, z)) * (1 + lift)
# eyes: small glossy dots set low on the face (leaves a big forehead)
for s in (-1, 1):
    p = _surf(s * 0.2, -0.1, -0.012)
    e = uv_sphere(f'eye{s}', 0.062, tuple(p), (1, 0.55, 1.15)); e.data.materials.append(feat)
    e.rotation_euler = (Vector((0, 0, 0)) - p).to_track_quat('Y', 'Z').to_euler(); face.append(e)
# small smile following the ball's surface
pts = []
for k in range(13):
    a = math.radians(-58 + 116 * k / 12); x = 0.13 * math.sin(a); z = -0.31 - 0.055 * math.cos(a) + 0.055
    pts.append(tuple(_surf(x, z, 0.004)))
face.append(tube('smile', pts, [0.014, 0.019] + [0.021] * 9 + [0.019, 0.014], feat))

import os
nfr = int(sys.argv[5]) if len(sys.argv) > 5 else 1
CAM = Vector((-0.9, -7.6, 0.9))
cam = stage(res=res, samples=samples, cam_loc=tuple(CAM), target=(0, 0, 0), lens=110, exposure=0.15 if kind == 'yellow' else -0.35)
vs = bpy.context.scene.view_settings; vs.view_transform = 'Standard'; vs.look = 'None'; vs.exposure = -0.2  # vivid toy colours
pivot = link(bpy.data.objects.new('pivot', None))
for o in face + [ball]: o.parent = pivot
axis = (-CAM).normalized()            # the line of sight: spinning about it turns the face like a wheel, lights stay put
sign = -1 if kind == 'yellow' else 1   # yellow clockwise, blue anticlockwise (as seen by the viewer)
os.makedirs(out, exist_ok=True)
from mathutils import Quaternion
for i in range(nfr):
    pivot.rotation_mode = 'QUATERNION'; pivot.rotation_quaternion = Quaternion(axis, sign * 2 * math.pi * i / nfr)
    render(f'{out}/{i:03d}.png')
