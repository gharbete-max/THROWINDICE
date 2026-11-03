"""Glossy 3D smiley-ball icons: big forehead, small dot eyes, small smile, plus one small accessory per theme.
Usage (bpy as a Python package):  python smiley.py <theme|all|list> outdir [res] [samples] [frames]
  -> outdir/<theme>/000.png ..  (frame 0 = still; the loop is a turntable spin about the vertical axis, lights fixed)
Themes live in THEMES below. Same ball, face, camera and lights as the original Token World smileys (yellow, blue)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Quaternion, Euler
from lib import reset, link, uv_sphere, tube, principled, stage, render

DARK, LIGHT = 'dark', 'light'
# name: (ball colour, feature colour, accessory, spin sign (-1 = clockwise seen from above), extra ball options)
THEMES = {
    'yellow':   ((1.0, 0.66, 0.0),   DARK,  None,         -1, {}),
    'blue':     ((0.05, 0.3, 1.0),   LIGHT, None,          1, {}),
    'home':     ((0.8, 0.48, 0.18),  DARK,  'roof',       -1, {}),
    'basics':   ((0.08, 0.62, 0.12), LIGHT, 'mortarboard', 1, {}),
    'fees':     ((0.0, 0.6, 0.42),   LIGHT, 'coinstack',  -1, {}),
    'game':     ((0.48, 0.18, 0.9),  LIGHT, 'orbitcoin',   1, {}),
    'invest':   ((0.85, 0.12, 0.08), LIGHT, 'arrow',      -1, {}),
    'explore':  ((0.05, 0.3, 1.0),   LIGHT, 'telescope',   1, {}),
    'wallet':   ((0.05, 0.3, 1.0),   LIGHT, 'wallet',     -1, {}),
    'world':    ((0.04, 0.5, 0.62),  LIGHT, 'continents', -1, {}),
    'industry': ((0.2, 0.25, 0.33),  LIGHT, 'gear',        1, {}),
    'tech':     ((0.0, 0.62, 0.62),  LIGHT, 'antenna',    -1, {}),
    'finance':  ((0.0, 0.2, 0.09),   LIGHT, 'slotcoin',    1, {}),
    'energy':   ((1.0, 0.2, 0.0),    DARK,  'flame',      -1, {}),
    'health':   ((0.8, 0.82, 0.86),  DARK,  'cross',       1, {}),
    'shops':    ((0.95, 0.12, 0.42), LIGHT, 'bag',        -1, {}),
    'property': ((0.45, 0.06, 0.02), LIGHT, 'roof',        1, {'roof': (0.12, 0.12, 0.14)}),
    'gold':     ((1.0, 0.72, 0.25),  DARK,  None,         -1, {'metal': True}),
    'silver':   ((0.86, 0.87, 0.9),  DARK,  None,          1, {'metal': True}),
    'copper':   ((0.95, 0.45, 0.25), DARK,  None,         -1, {'metal': True}),
    'nature':   ((0.18, 0.36, 0.04), LIGHT, 'sprout',      1, {}),
    'bonds':    ((0.07, 0.16, 0.38), LIGHT, 'band',       -1, {}),
    'token':    ((0.05, 0.3, 1.0),   LIGHT, 'pixelcoin',   1, {}),
    'chain':    ((0.05, 0.3, 1.0),   LIGHT, 'chain',      -1, {}),
}

GOLD = None
def gold():
    global GOLD
    if GOLD is None: GOLD = principled('gold', (1.0, 0.7, 0.18), 0.22, metallic=1.0, coat=0.4, coat_rough=0.05)
    return GOLD

def smooth(o):
    for p in o.data.polygons: p.use_smooth = True
    return o

def prim(kind, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), shade=True, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    o = bpy.context.active_object; o.scale = scale; o.data.materials.append(mat)
    if shade: smooth(o)
    return o

def bevel(o, w=0.012, seg=3):
    m = o.modifiers.new('bv', 'BEVEL'); m.width = w; m.segments = seg; m.limit_method = 'ANGLE'; return o

def surf(x, z, lift):
    y = -math.sqrt(max(0.0, 1 - x * x - z * z)); return Vector((x, y, z)) * (1 + lift)

def on_surface(o, p):
    o.rotation_euler = (Vector((0, 0, 0)) - p).to_track_quat('Y', 'Z').to_euler(); return o

def continents(mat, land):
    nt = mat.node_tree; b = nt.nodes['Principled BSDF']; ocean = tuple(b.inputs['Base Color'].default_value)
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.6; nz.inputs['Detail'].default_value = 5; nz.inputs['Roughness'].default_value = 0.55
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'LINEAR'
    e0, e1 = ramp.color_ramp.elements; e0.position = 0.53; e0.color = ocean; e1.position = 0.56; e1.color = (*land, 1)
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])

def accessory(kind, opts, feat):
    """Returns the objects that make up the accessory (they get parented to the spin pivot)."""
    out = []
    if kind == 'roof':
        col = opts.get('roof', (0.78, 0.25, 0.12))
        m = principled('roof', col, 0.35, coat=0.5, coat_rough=0.1)
        r = prim('cone', m, (0, 0, 1.1), (0, 0, math.radians(45)), vertices=4, radius1=0.62, radius2=0.0, depth=0.4, shade=False)
        out += [bevel(r, 0.02), bevel(prim('cube', m, (0.22, 0.1, 1.2), scale=(0.06, 0.06, 0.12), shade=False), 0.01)]
    elif kind == 'mortarboard':
        m = principled('cap', (0.08, 0.1, 0.18), 0.35, coat=0.5, coat_rough=0.1)
        out.append(prim('cylinder', m, (0, 0, 0.98), vertices=48, radius=0.36, depth=0.16))
        out.append(bevel(prim('cube', m, (0, 0, 1.07), (0, 0, math.radians(45)), scale=(0.48, 0.48, 0.025), shade=False), 0.01))
        out.append(prim('uv_sphere', gold(), (0, 0, 1.105), radius=0.04))
        out.append(tube('tassel', [(0, 0, 1.1), (0.25, -0.25, 1.095), (0.5, -0.5, 1.07), (0.53, -0.53, 0.9)], [0.012] * 3 + [0.025], gold()))
    elif kind == 'coinstack':
        for k in range(3):
            c = prim('cylinder', gold(), (0.85 + 0.015 * k, -0.55, -0.66 + 0.14 * k), vertices=48, radius=0.3, depth=0.12)
            out.append(bevel(c, 0.015))
    elif kind in ('orbitcoin', 'pixelcoin'):
        v = 48 if kind == 'orbitcoin' else 8
        c = prim('cylinder', gold(), (1.02, -0.3, 0.42), (math.radians(90), 0, math.radians(-20)), vertices=v, radius=0.27, depth=0.07, shade=kind == 'orbitcoin')
        out.append(bevel(c, 0.012 if v == 48 else 0.004, 3 if v == 48 else 1))
        mark = principled('mark', (0.75, 0.45, 0.05), 0.3, metallic=1.0)
        if kind == 'orbitcoin':
            out.append(prim('cylinder', mark, (1.02, -0.3, 0.42), (math.radians(90), 0, math.radians(-20)), vertices=48, radius=0.18, depth=0.085))
        else:
            out.append(prim('cube', mark, (1.02, -0.3, 0.42), (0, 0, math.radians(-20)), scale=(0.08, 0.045, 0.12), shade=False))
    elif kind == 'arrow':
        a, b = Vector((0.5, -0.45, 0.62)), Vector((0.98, -0.45, 1.12))
        out.append(tube('shaft', [tuple(a), tuple(a.lerp(b, 0.5)), tuple(b)], [0.085, 0.085, 0.085], gold()))
        d = (b - a).normalized()
        h = prim('cone', gold(), tuple(b + d * 0.12), vertices=32, radius1=0.21, radius2=0.0, depth=0.3)
        h.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); out.append(h)
    elif kind == 'telescope':
        body = principled('scope', (0.95, 0.95, 0.97), 0.3, coat=0.8, coat_rough=0.05)
        a, b = Vector((-0.25, 0.0, 1.0)), Vector((0.45, -0.2, 1.38))
        d = (b - a).normalized(); q = d.to_track_quat('Z', 'Y').to_euler()
        t = prim('cone', body, tuple(a.lerp(b, 0.5)), vertices=48, radius1=0.09, radius2=0.14, depth=(b - a).length); t.rotation_euler = q; out.append(bevel(t, 0.01))
        r = prim('torus', gold(), tuple(b), major_radius=0.14, minor_radius=0.025, major_segments=48, minor_segments=12); r.rotation_euler = q; out.append(r)
        out.append(tube('leg', [(0.05, -0.05, 0.96), (0.08, -0.08, 1.1), (0.1, -0.1, 1.18)], [0.025] * 3, gold()))
    elif kind == 'wallet':
        m = principled('leather', (0.45, 0.2, 0.06), 0.45, coat=0.4, coat_rough=0.15)
        L, R = Vector((0.82, -0.75, -0.42)), (0, 0, math.radians(-35))
        out.append(bevel(prim('cube', m, tuple(L), R, scale=(0.3, 0.11, 0.22), shade=False), 0.045, 4))
        f = prim('cube', principled('flap', (0.32, 0.13, 0.03), 0.45, coat=0.4), tuple(L + Vector((0.08, -0.09, 0.05))), R, scale=(0.22, 0.04, 0.11), shade=False)
        out.append(bevel(f, 0.02, 3))
        out.append(prim('uv_sphere', gold(), tuple(L + Vector((-0.04, -0.15, 0.05))), radius=0.05))
    elif kind == 'gear':
        m = principled('steel', (0.75, 0.76, 0.8), 0.25, metallic=1.0)
        L, R = Vector((0.95, -0.3, 0.5)), (math.radians(90), 0, math.radians(-20))
        out.append(prim('cylinder', m, tuple(L), R, vertices=48, radius=0.24, depth=0.1))
        rot = Euler(R).to_matrix()
        for k in range(8):
            a = 2 * math.pi * k / 8; d = rot @ Vector((math.cos(a) * 0.27, math.sin(a) * 0.27, 0))
            t = prim('cube', m, tuple(L + d), shade=False, scale=(0.05, 0.05, 0.05))
            t.rotation_mode = 'QUATERNION'; t.rotation_quaternion = Euler(R).to_quaternion() @ Quaternion((0, 0, 1), a)
            out.append(bevel(t, 0.008, 2))
        hole = principled('hole', (0.2, 0.22, 0.25), 0.5)
        out.append(prim('cylinder', hole, tuple(L), R, vertices=32, radius=0.08, depth=0.11))
    elif kind == 'antenna':
        m = principled('rod', (0.15, 0.15, 0.18), 0.3, metallic=1.0)
        out.append(tube('rod', [(0.12, 0, 0.97), (0.2, 0, 1.2), (0.28, 0, 1.33)], [0.025, 0.02, 0.018], m))
        out.append(prim('uv_sphere', principled('tip', (1.0, 0.15, 0.2), 0.25, coat=1.0, emit=(1.0, 0.1, 0.1), emit_str=1.5), (0.29, 0, 1.37), radius=0.075))
    elif kind == 'slotcoin':
        slot = principled('slot', (0.01, 0.06, 0.03), 0.6)
        out.append(prim('cube', slot, (0, 0, 0.995), scale=(0.24, 0.05, 0.02), shade=False))
        c = prim('cylinder', gold(), (0, 0, 1.15), (0, math.radians(90), 0), vertices=48, radius=0.22, depth=0.06)
        out.append(bevel(c, 0.012))
    elif kind == 'flame':
        outer = principled('flameO', (1.0, 0.25, 0.02), 0.35, emit=(1.0, 0.3, 0.02), emit_str=2.0, coat=0.6)
        inner = principled('flameI', (1.0, 0.85, 0.2), 0.35, emit=(1.0, 0.8, 0.2), emit_str=3.0)
        f = prim('uv_sphere', outer, (0, 0, 1.12), scale=(0.2, 0.2, 0.34), radius=1.0, segments=48, ring_count=24)
        tp = f.modifiers.new('tp', 'SIMPLE_DEFORM'); tp.deform_method = 'TAPER'; tp.factor = -1.2; tp.deform_axis = 'Z'
        g = prim('uv_sphere', inner, (0, -0.12, 1.08), scale=(0.1, 0.1, 0.18), radius=1.0, segments=32, ring_count=16)
        tg = g.modifiers.new('tp', 'SIMPLE_DEFORM'); tg.deform_method = 'TAPER'; tg.factor = -1.2; tg.deform_axis = 'Z'
        out += [f, g]
    elif kind == 'cross':
        m = principled('red', (0.9, 0.05, 0.08), 0.3, coat=0.8, coat_rough=0.05)
        p = surf(0, 0.5, 0.0)
        for sc in ((0.16, 0.05, 0.05), (0.05, 0.05, 0.16)):
            c = prim('cube', m, tuple(p), scale=sc, shade=False); on_surface(c, p)
            out.append(bevel(c, 0.015))
    elif kind == 'bag':
        m = principled('bag', (0.98, 0.95, 0.85), 0.5, coat=0.3)
        L = Vector((1.0, -0.25, -0.45))
        out.append(bevel(prim('cube', m, tuple(L), (0, 0, math.radians(-20)), scale=(0.2, 0.09, 0.22), shade=False), 0.02))
        h = principled('handle', (0.9, 0.1, 0.35), 0.4)
        d = Vector((math.cos(math.radians(-20)), math.sin(math.radians(-20)), 0))
        pts = [tuple(L + d * (0.1 * math.cos(a)) + Vector((0, 0, 0.21 + 0.12 * math.sin(a)))) for a in [math.radians(t) for t in range(0, 181, 30)]]
        out.append(tube('handle', pts, [0.018] * len(pts), h))
    elif kind == 'sprout':
        st = principled('stem', (0.45, 0.3, 0.12), 0.5); lf = principled('leaf', (0.4, 0.85, 0.2), 0.35, coat=0.6, sss=0.2, sss_radius=(0.4, 1, 0.2), sss_scale=0.05)
        out.append(tube('stem', [(0, 0, 0.97), (0.02, 0, 1.12), (0, 0, 1.24)], [0.03, 0.025, 0.02], st))
        for s in (-1, 1):
            l = prim('uv_sphere', lf, (s * 0.17, 0, 1.3), (0, s * math.radians(-35), 0), scale=(0.2, 0.06, 0.09), radius=1.0, segments=32, ring_count=16)
            out.append(l)
    elif kind == 'band':
        m = principled('ribbon', (0.95, 0.75, 0.2), 0.3, metallic=0.6, coat=0.6)
        z = 0.42; R = math.sqrt(1 - z * z) * 1.005
        out.append(prim('torus', m, (0, 0, z), major_radius=R, minor_radius=0.045, major_segments=96, minor_segments=16))
    elif kind == 'chain':
        m = gold()
        out.append(prim('torus', m, (0.98, -0.3, 0.5), (math.radians(90), 0, math.radians(-20)), major_radius=0.17, minor_radius=0.05, major_segments=48, minor_segments=16))
        out.append(prim('torus', m, (1.12, -0.35, 0.33), (0, math.radians(90), math.radians(-20)), major_radius=0.17, minor_radius=0.05, major_segments=48, minor_segments=16))
    return out

def build(name, out, res, samples, nfr):
    global GOLD; GOLD = None
    col, fk, acc, sign, opts = THEMES[name]
    reset()
    if opts.get('metal'):
        body = principled('ball', col, 0.3, metallic=1.0, coat=0.5, coat_rough=0.05)
    else:
        warm = col[0] >= col[2]
        body = principled('ball', col, 0.3, sss=0.12, sss_radius=(1, 0.6, 0.2) if warm else (0.3, 0.6, 1.0), sss_scale=0.15, coat=0.6, coat_rough=0.08)
    if fk == DARK: feat = principled('feat', (0.012, 0.01, 0.008), 0.25, coat=1.0, coat_rough=0.02)
    else: feat = principled('feat', (0.97, 0.98, 1.0), 0.3, coat=0.8, coat_rough=0.05, sss=0.2, sss_radius=(1, 1, 1), sss_scale=0.02)
    if acc == 'continents': continents(body, (0.12, 0.4, 0.18))
    ball = uv_sphere('ball', 1.0, (0, 0, 0), seg=128, rings=64); ball.data.materials.append(body)
    face = []
    for s in (-1, 1):
        p = surf(s * 0.2, -0.1, -0.012)
        e = uv_sphere(f'eye{s}', 0.062, tuple(p), (1, 0.55, 1.15)); e.data.materials.append(feat); on_surface(e, p); face.append(e)
    pts = []
    for k in range(13):
        a = math.radians(-58 + 116 * k / 12); x = 0.13 * math.sin(a); z = -0.31 - 0.055 * math.cos(a) + 0.055
        pts.append(tuple(surf(x, z, 0.004)))
    face.append(tube('smile', pts, [0.014, 0.019] + [0.021] * 9 + [0.019, 0.014], feat))
    if acc and acc != 'continents': face += accessory(acc, opts, feat)
    CAM = Vector((-0.9, -7.6, 0.9))
    # 84 mm instead of the original 110 mm leaves room for accessories; every icon uses it so balls stay the same size
    stage(res=res, samples=samples, cam_loc=tuple(CAM), target=(0.1, 0, 0.2), lens=84)
    if opts.get('metal'):  # metals only show what they reflect: give them a soft bright studio sky
        bg = bpy.context.scene.world.node_tree.nodes['Background']; bg.inputs['Strength'].default_value = 0.9
    vs = bpy.context.scene.view_settings; vs.view_transform = 'Standard'; vs.look = 'None'; vs.exposure = -0.2
    pivot = link(bpy.data.objects.new('pivot', None))
    for o in face + [ball]: o.parent = pivot
    pivot.rotation_mode = 'QUATERNION'
    d = os.path.join(out, name); os.makedirs(d, exist_ok=True)
    for i in range(nfr):
        pivot.rotation_quaternion = Quaternion((0, 0, 1), sign * 2 * math.pi * i / nfr)
        render(f'{d}/{i:03d}.png')

if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]
    if which == 'list': print(' '.join(THEMES)); sys.exit()
    res = int(sys.argv[3]) if len(sys.argv) > 3 else 192
    samples = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    nfr = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    for n in (THEMES if which == 'all' else which.split(',')): build(n, out, res, samples, nfr)
