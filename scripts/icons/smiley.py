"""Glossy 3D smiley-ball icons: big forehead, small dot eyes, small smile, plus one small accessory per theme.
Usage (bpy as a Python package):  python smiley.py <theme|all|list> outdir [res] [samples] [frames]
  -> outdir/<theme>/000.png ..  (frame 0 = still; the loop is a turntable spin about the vertical axis, lights fixed)
Themes live in THEMES below. Same ball, face, camera and lights as the original Token World smileys (yellow, blue)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Quaternion, Euler
from lib import reset, link, uv_sphere, tube, principled, stage, render

PAL = {  # Loppa palette (THROWPAPER), as base colours calibrated so the rendered ball reads as the token
    'gold': (0.2874, 0.1809, 0.0402),
    'sheen': (0.6542, 0.4651, 0.2656),
    'bronze': (0.1186, 0.061, 0.0099),
    'platinum': (0.3179, 0.338, 0.3633),
    'pewter': (0.0861, 0.0963, 0.1073),
    'graphite': (0.0223, 0.0266, 0.0326),
    'paper': (1.0, 1.0, 1.0),
    'roomgold': (0.5433, 0.2357, 0.0253),
    'lavender': (0.2256, 0.2403, 0.5067),  # Token World
    'violet': (0.1133, 0.092, 0.3297),  # Token World
    'periwinkle': (0.091, 0.1053, 0.2944),  # Token World
    'ice': (0.6528, 0.6785, 0.9737),  # Token World
}
INK = (0.004, 0.004, 0.005)
ACC_SCALE = float(os.environ.get('ACC_SCALE', 1.5))  # content icons render with ACC_SCALE=1.9 so accessories read at text size
LENS = 70  # nav framing: the ball is drawn at 70/110 of the coin's size, CSS scales the image up so balls match
DARK, LIGHT = 'dark', 'light'  # all icons now use DARK (black eyes and mouth); LIGHT kept for reference
# name: (ball colour, feature colour, accessory, spin sign (-1 = clockwise seen from above), extra ball options)
THEMES = {
    'yellow':   (PAL['gold'],     DARK,  None,         -1, {'lens': 110}),
    'blue':     (PAL['lavender'], DARK,  None,          1, {'lens': 110}),
    'home':     (PAL['sheen'],    DARK,  'roof',       -1, {}),
    'basics':   (PAL['platinum'], DARK,  'mortarboard', 1, {}),
    'fees':     (PAL['gold'],   DARK,  'coinstack',  -1, {}),
    'game':     (PAL['pewter'],   DARK,  'orbitcoin',   1, {}),
    'invest':   (PAL['bronze'],   DARK,  'arrow',      -1, {}),
    'explore':  (PAL['violet'],   DARK,  'telescope',   1, {}),
    'wallet':   ((0.05, 0.3, 1.0),   DARK,  'wallet',     -1, {}),
    'world':    (PAL['platinum'],  DARK,  'continents', -1, {}),
    'industry': (PAL['pewter'],  DARK,  'gear',        1, {}),
    'tech':     (PAL['platinum'],  DARK,  'antenna',    -1, {}),
    'finance':  (PAL['gold'],   DARK,  'slotcoin',    1, {}),
    'energy':   (PAL['bronze'],    DARK,  'flame',      -1, {}),
    'health':   (PAL['paper'],  DARK,  'cross',       1, {}),
    'shops':    (PAL['sheen'], DARK,  'bag',        -1, {}),
    'property': (PAL['bronze'], DARK,  'roof',        1, {'roof': PAL['graphite']}),
    'gold':     ((1.0, 0.72, 0.25),  DARK,  None,         -1, {'metal': True}),  # metals: reflectance colours, not calibrated plastic
    'silver':   ((0.86, 0.87, 0.9),  DARK,  None,          1, {'metal': True}),
    'copper':   ((0.72, 0.47, 0.24), DARK,  None,         -1, {'metal': True}),
    'nature':   (PAL['sheen'], DARK,  'sprout',      1, {}),
    'bonds':    (PAL['pewter'], DARK,  'band',       -1, {}),
    'token':    (PAL['platinum'],   DARK,  'pixelcoin',   1, {}),
    # Token World versions of the shared nav smileys (blue-violet palette)
    'home-t':   (PAL['ice'],        DARK,  'roof',        1, {'roof': PAL['violet']}),
    'basics-t': (PAL['lavender'],   DARK,  'mortarboard', -1, {}),
    'game-t':   (PAL['periwinkle'], DARK,  'orbitcoin',   1, {}),
    # Investing popup balls: no face, the ball and accessory carry the meaning
    'pop-world':       (PAL['platinum'], DARK, 'continents', -1, {'face': False}),
    'pop-sectors':     (PAL['pewter'],   DARK, 'gear',        1, {'face': False, 'acc_scale': 2.0}),
    'pop-commodities': ((1.0, 0.72, 0.25),  DARK, None,         -1, {'face': False, 'metal': True}),
    'pop-options':     (PAL['lavender'], DARK, 'pixelcoin',   1, {'face': False, 'acc_scale': 2.0}),
    'pop-networks':    (PAL['periwinkle'], DARK, 'chain',      -1, {'face': False, 'acc_scale': 2.0}),
    'pop-issuance':    (PAL['violet'], DARK, 'scroll',      1, {'face': False, 'acc_scale': 1.6}),
    # game power-ups: faceless balls with one big front badge
    'pu-shield': (PAL['platinum'], DARK, 'shieldbadge', 1, {'face': False, 'acc_scale': 1.0}),
    'pu-magnet': (PAL['pewter'],   DARK, 'magnet',     -1, {'face': False, 'acc_scale': 1.0}),
    'pu-x2':     (PAL['sheen'],    DARK, 'x2',          1, {'face': False, 'acc_scale': 1.0}),
    # particle sprites (no ball)
    'spark-star':      ((1.0, 0.75, 0.15),  DARK, 'star',        1, {'noball': True}),
    'spark-coin':      ((1.0, 0.7, 0.18),   DARK, 'coin',       -1, {'noball': True}),
    'chain':    (PAL['platinum'],   DARK,  'chain',      -1, {}),
    'quantum':  (PAL['violet'],     DARK,  'atom',        1, {'acc_scale': 1.0}),
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

def cyl_(mat, loc, r, depth):
    o = prim('cylinder', mat, loc, vertices=32, radius=r, depth=depth); return bevel(o, 0.02)

def accessory(kind, opts, feat):
    """Returns the objects that make up the accessory (they get parented to the spin pivot)."""
    out = []
    if kind == 'roof':
        col = opts.get('roof', PAL['bronze'])
        m = principled('roof', col, 0.35, coat=0.5, coat_rough=0.1)
        r = prim('cone', m, (0, 0, 1.1), (0, 0, math.radians(45)), vertices=4, radius1=0.62, radius2=0.0, depth=0.4, shade=False)
        out += [bevel(r, 0.02), bevel(prim('cube', m, (0.22, 0.1, 1.2), scale=(0.06, 0.06, 0.12), shade=False), 0.01)]
    elif kind == 'atom':  # quantum: two tilted electron orbits around the ball, a glowing electron on each
        ring = principled('orbit', (0.12, 0.2, 0.85), 0.12, metallic=0.3, coat=1.0, emit=(0.2, 0.3, 1.0), emit_str=0.25)
        el = principled('electron', (0.7, 0.85, 1.0), 0.2, emit=(0.6, 0.8, 1.0), emit_str=3.0)
        for tilt, ph, rz in ((70, 0.6, 28), (-70, 3.6, -28)):
            r = prim('torus', ring, (0, 0, 0), (math.radians(tilt), math.radians(18), math.radians(rz)), major_radius=1.3, minor_radius=0.05, major_segments=96, minor_segments=12)
            out.append(r)
            v = Vector((1.3 * math.cos(ph), 1.3 * math.sin(ph), 0))  # in the torus plane
            v.rotate(Euler((math.radians(tilt), math.radians(18), math.radians(rz))))
            out.append(prim('uv_sphere', el, tuple(v), radius=0.1))
    elif kind == 'mortarboard':
        m = principled('cap', INK, 0.35, coat=0.5, coat_rough=0.1)
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
        body = principled('scope', PAL['graphite'], 0.3, coat=0.8, coat_rough=0.05)
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
    elif kind == 'scroll':  # a certificate: cream sheet, red band, gold seal
        paper = principled('paper', PAL['sheen'], 0.45, coat=0.3, sss=0.1, sss_radius=(1, 0.9, 0.7), sss_scale=0.05)
        L, R = Vector((0.62, -0.88, -0.3)), (math.radians(-8), 0, math.radians(-22))
        out.append(bevel(prim('cube', paper, tuple(L), R, scale=(0.3, 0.03, 0.38), shade=False), 0.02, 3))
        rib = principled('ribbon', PAL['bronze'], 0.35, coat=0.6)
        m = Euler(R).to_matrix()
        out.append(prim('cube', rib, tuple(L + m @ Vector((0, -0.035, 0.12))), R, scale=(0.305, 0.012, 0.05), shade=False))
        for k, z in enumerate((-0.06, -0.15)):
            out.append(prim('cube', paper, tuple(L + m @ Vector((-0.04, -0.035, z))), R, scale=(0.2 - 0.06 * k, 0.008, 0.012), shade=False))
        sl = prim('cylinder', gold(), tuple(L + m @ Vector((0.16, -0.05, -0.24))), (math.radians(90) + R[0], 0, R[2]), vertices=32, radius=0.09, depth=0.04)
        out.append(bevel(sl, 0.01))
    elif kind == 'shieldbadge':
        import bmesh
        me = bpy.data.meshes.new('shield'); bm = bmesh.new()
        vs = [bm.verts.new(p) for p in [(-0.5, 0, 0.5), (0.5, 0, 0.5), (0.5, 0, 0.05), (0.3, 0, -0.35), (0, 0, -0.6), (-0.3, 0, -0.35), (-0.5, 0, 0.05)]]
        bm.faces.new(vs); bm.to_mesh(me); bm.free()
        o = link(bpy.data.objects.new('shield', me)); o.location = (0, -1.02, 0); o.data.materials.append(principled('shieldm', PAL['gold'], 0.3, coat=0.8, coat_rough=0.05))
        so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.16; so.offset = 0; bevel(o, 0.05, 4); out.append(o)
    elif kind == 'magnet':
        mb = principled('magnet', PAL['bronze'], 0.3, coat=0.8, coat_rough=0.05); tip = principled('tip', (0.86, 0.87, 0.9), 0.25, metallic=1.0)
        pts = [(0.38 * math.cos(math.radians(t)), -1.05, 0.05 + 0.38 * math.sin(math.radians(t))) for t in range(0, 181, 15)]
        pts = [(0.38, -1.05, -0.35)] + pts + [(-0.38, -1.05, -0.35)]
        out.append(tube('mag', pts, [0.13] * len(pts), mb))
        for x in (-0.38, 0.38): out.append(cyl_(tip, (x, -1.05, -0.45), 0.135, 0.2))
    elif kind == 'x2':
        bpy.ops.object.text_add(location=(0, -1.0, -0.05), rotation=(math.radians(90), 0, 0)); t = bpy.context.active_object
        t.data.body = '2x'; t.data.size = 0.95; t.data.extrude = 0.08; t.data.bevel_depth = 0.02; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
        t.data.materials.append(gold()); out.append(t)
    elif kind == 'star':
        import bmesh
        me = bpy.data.meshes.new('star'); bm = bmesh.new()
        vs = [bm.verts.new((math.cos(math.pi / 2 + k * math.pi / 5) * (0.9 if k % 2 == 0 else 0.4), 0, math.sin(math.pi / 2 + k * math.pi / 5) * (0.9 if k % 2 == 0 else 0.4))) for k in range(10)]
        bm.faces.new(vs); bm.to_mesh(me); bm.free()
        o = link(bpy.data.objects.new('star', me)); o.data.materials.append(gold())
        so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.28; so.offset = 0
        bevel(o, 0.08, 4); out.append(o)
    elif kind == 'coin':
        out.append(bevel(prim('cylinder', gold(), (0, 0, 0), (math.radians(90), 0, math.radians(-25)), vertices=64, radius=0.8, depth=0.2), 0.04, 4))
        out.append(prim('cylinder', principled('mark', (0.75, 0.45, 0.05), 0.3, metallic=1.0), (0, 0, 0), (math.radians(90), 0, math.radians(-25)), vertices=64, radius=0.55, depth=0.23))
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
        out.append(prim('uv_sphere', gold(), (0.29, 0, 1.37), radius=0.075))
    elif kind == 'slotcoin':
        slot = principled('slot', INK, 0.6)
        out.append(prim('cube', slot, (0, 0, 0.995), scale=(0.24, 0.05, 0.02), shade=False))
        c = prim('cylinder', gold(), (0, 0, 1.15), (0, math.radians(90), 0), vertices=48, radius=0.22, depth=0.06)
        out.append(bevel(c, 0.012))
    elif kind == 'flame':
        outer = principled('flameO', PAL['roomgold'], 0.35, emit=PAL['roomgold'], emit_str=1.2, coat=0.6)
        inner = principled('flameI', PAL['sheen'], 0.35, emit=PAL['sheen'], emit_str=1.5)
        f = prim('uv_sphere', outer, (0, 0, 1.12), scale=(0.2, 0.2, 0.34), radius=1.0, segments=48, ring_count=24)
        tp = f.modifiers.new('tp', 'SIMPLE_DEFORM'); tp.deform_method = 'TAPER'; tp.factor = -1.2; tp.deform_axis = 'Z'
        g = prim('uv_sphere', inner, (0, -0.12, 1.08), scale=(0.1, 0.1, 0.18), radius=1.0, segments=32, ring_count=16)
        tg = g.modifiers.new('tp', 'SIMPLE_DEFORM'); tg.deform_method = 'TAPER'; tg.factor = -1.2; tg.deform_axis = 'Z'
        out += [f, g]
    elif kind == 'cross':
        m = principled('red', PAL['bronze'], 0.3, coat=0.8, coat_rough=0.05)
        p = surf(0, 0.5, 0.0)
        for sc in ((0.16, 0.05, 0.05), (0.05, 0.05, 0.16)):
            c = prim('cube', m, tuple(p), scale=sc, shade=False); on_surface(c, p)
            out.append(bevel(c, 0.015))
    elif kind == 'bag':
        m = principled('bag', PAL['paper'], 0.5, coat=0.3)
        L = Vector((1.0, -0.25, -0.45))
        out.append(bevel(prim('cube', m, tuple(L), (0, 0, math.radians(-20)), scale=(0.2, 0.09, 0.22), shade=False), 0.02))
        h = principled('handle', PAL['bronze'], 0.4)
        d = Vector((math.cos(math.radians(-20)), math.sin(math.radians(-20)), 0))
        pts = [tuple(L + d * (0.1 * math.cos(a)) + Vector((0, 0, 0.21 + 0.12 * math.sin(a)))) for a in [math.radians(t) for t in range(0, 181, 30)]]
        out.append(tube('handle', pts, [0.018] * len(pts), h))
    elif kind == 'sprout':
        st = principled('stem', PAL['bronze'], 0.5); lf = principled('leaf', PAL['gold'], 0.35, coat=0.6)
        out.append(tube('stem', [(0, 0, 0.97), (0.02, 0, 1.12), (0, 0, 1.24)], [0.03, 0.025, 0.02], st))
        for s in (-1, 1):
            l = prim('uv_sphere', lf, (s * 0.17, 0, 1.3), (0, s * math.radians(-35), 0), scale=(0.2, 0.06, 0.09), radius=1.0, segments=32, ring_count=16)
            out.append(l)
    elif kind == 'band':
        m = principled('ribbon', PAL['gold'], 0.3, metallic=0.6, coat=0.6)
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
    if acc == 'continents': continents(body, PAL['gold'])
    face = []
    ball = uv_sphere('ball', 1.0, (0, 0, 0), seg=128, rings=64); ball.data.materials.append(body)
    if opts.get('noball'): bpy.data.objects.remove(ball); ball = None
    for s in ((-1, 1) if opts.get('face', True) and ball else ()):
        p = surf(s * 0.2, -0.1, -0.012)
        e = uv_sphere(f'eye{s}', 0.062, tuple(p), (1, 0.55, 1.15)); e.data.materials.append(feat); on_surface(e, p); face.append(e)
    pts = []
    for k in range(13):
        a = math.radians(-58 + 116 * k / 12); x = 0.13 * math.sin(a); z = -0.31 - 0.055 * math.cos(a) + 0.055
        pts.append(tuple(surf(x, z, 0.004)))
    if opts.get('face', True) and ball: face.append(tube('smile', pts, [0.014, 0.019] + [0.021] * 9 + [0.019, 0.014], feat))
    if acc and acc != 'continents':
        parts = accessory(acc, opts, feat)
        k = opts.get('acc_scale', 1.0 if acc == 'band' or not ball else ACC_SCALE)
        if k != 1.0:  # grow the accessory about the point where it meets the ball, so it stays attached
            bpy.context.view_layer.update()
            c = sum((o.matrix_world @ (sum((Vector(b) for b in o.bound_box), Vector()) / 8) for o in parts), Vector()) / len(parts)
            hub = link(bpy.data.objects.new('acc', None)); hub.location = c.normalized() if c.length > 1e-6 else Vector((0, 0, 1))
            bpy.context.view_layer.update()
            for o in parts:
                mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
            hub.scale = (k, k, k); parts = [hub]
        face += parts
    CAM = Vector((-0.9, -7.6, 0.9))
    # themed icons use LENS (wider than the coin's 110 mm) to leave room for accessories; all of them share it so balls match
    stage(res=res, samples=samples, cam_loc=tuple(CAM), target=(0, 0, 0) if opts.get('lens') == 110 else (0.1, 0, 0.15), lens=opts.get('lens', LENS))
    if opts.get('metal'):  # metals only show what they reflect: give them a soft bright studio sky
        bg = bpy.context.scene.world.node_tree.nodes['Background']; bg.inputs['Strength'].default_value = 0.9
    vs = bpy.context.scene.view_settings; vs.view_transform = 'Standard'; vs.look = 'None'; vs.exposure = -0.2
    pivot = link(bpy.data.objects.new('pivot', None))
    for o in face + ([ball] if ball else []): o.parent = pivot
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
