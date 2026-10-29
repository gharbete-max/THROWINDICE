import sys; char = sys.argv[1]; sys.argv = ['x']; sys.path.insert(0, '/home/claude/bl')
import numpy as np, bpy, anim
if char == 'pug': import pug; rig, parts = pug.build(); pose = anim.pug_pose; hc, hr, mv = 1.76, 0.5, anim.PUG_DANCE
else: import cat; rig, parts = cat.build('alien'); pose = anim.alien_pose; hc, hr, mv = 1.75, 0.46, anim.ALIEN_DANCE
total = sum(b for _, b in mv); bounds = np.cumsum([0] + [b for _, b in mv]) / total
res = {}
for t in np.linspace(0, 1, 133)[:-1]:
    pose(rig, parts, t); bpy.context.view_layer.update()
    hb = rig.pose.bones['head']; Hc = rig.matrix_world @ (hb.head + (hb.tail - hb.head).normalized() * (hc - 1.36))
    d = min((rig.matrix_world @ rig.pose.bones[f'fore.{n}'].tail - Hc).length - hr for n in 'LR')
    m = mv[int(np.searchsorted(bounds, t, 'right') - 1)][0].__name__; res[m] = min(res.get(m, 9), d)
print(char, {k: round(v, 3) for k, v in res.items()})
