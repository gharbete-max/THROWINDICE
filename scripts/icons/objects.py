"""3D object icons in the menu-smiley style: candy plastic with a clear coat, polished gold, same lights and camera.
Objects get the smiley face (black dot eyes, small smile), placed by ray-casting onto the object's front surface.
Flag badges (flag-<cc>) are glossy coins with the flag painted on and no face.
Usage (bpy as a Python package):  python objects.py <name,name|all|list> outdir [res] [samples] [frames] [flagdir]
  -> outdir/<name>/000.png ..  (frame 0 = still; the loop is a turntable spin about the vertical axis, lights fixed)"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Quaternion, Euler, Matrix
from lib import reset, link, uv_sphere, tube, principled, stage, render
import smiley
from smiley import prim, bevel, smooth

FLAGDIR = os.environ.get('FLAGDIR', '')
LENS = 70

def gold():
    # a touch less mirror-like than the smiley accessories' gold, so big gold faces don't go dark under the object lighting
    if smiley.GOLD is None: smiley.GOLD = principled('gold', (1.0, 0.74, 0.22), 0.28, metallic=0.75, coat=0.5, coat_rough=0.05)
    return smiley.GOLD

def plastic(name, col, rough=0.3):
    warm = col[0] >= col[2]
    return principled(name, col, rough, sss=0.04, sss_radius=(1, 0.6, 0.2) if warm else (0.3, 0.6, 1.0), sss_scale=0.15, coat=0.6, coat_rough=0.08)

def ink():
    return principled('feat', (0.012, 0.01, 0.008), 0.25, coat=1.0, coat_rough=0.02)

def box(name, mat, loc, size, rot=(0, 0, 0), bv=0.04):
    o = prim('cube', mat, loc, rot, scale=(size[0] / 2, size[1] / 2, size[2] / 2), shade=False)
    return bevel(o, bv, 3) if bv else o

def cyl(mat, loc, r, depth, rot=(0, 0, 0), v=48, bv=0.02):
    o = prim('cylinder', mat, loc, rot, vertices=v, radius=r, depth=depth)
    return bevel(o, bv, 3) if bv else o

def prism(mat, loc, w, d, h, rot=(0, 0, 0)):
    """triangular roof: ridge along x, width w (x), depth d (y), height h (z), base at loc z"""
    import bmesh
    me = bpy.data.meshes.new('prism'); bm = bmesh.new()
    pts = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, -d / 2 + 0, 0)]
    v = [bm.verts.new(p) for p in [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0), (-w / 2, 0, h), (w / 2, 0, h)]]
    for f in [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]: bm.faces.new([v[i] for i in f])
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new('prism', me)); o.location = loc; o.rotation_euler = rot; o.data.materials.append(mat)
    return bevel(o, 0.02, 2)

# ---------- face by ray cast ----------
def _hit(objs, x, z):
    dg = bpy.context.evaluated_depsgraph_get(); best = None
    for o in objs:
        mi = o.matrix_world.inverted(); org = mi @ Vector((x, -10, z)); d = (mi.to_3x3() @ Vector((0, 1, 0))).normalized()
        ok, loc, n, _ = o.evaluated_get(dg).ray_cast(org, d)
        if ok:
            w = o.matrix_world @ loc; nw = (o.matrix_world.to_3x3().inverted().transposed() @ n).normalized()
            if best is None or w.y < best[0].y: best = (w, nw)
    return best

NOFACE = False
def face(targets, cx, cz, s=1.0):
    """black dot eyes + small smile on the front of `targets`, centred at (cx, cz), scaled by s"""
    if NOFACE: return []
    bpy.context.view_layer.update(); f = ink(); out = []
    for k in (-1, 1):
        h = _hit(targets, cx + k * 0.2 * s, cz - 0.1 * s)
        if not h: continue
        p, n = h; e = uv_sphere(f'eye{k}', 0.062 * s, tuple(p - n * 0.012 * s), (1, 0.55, 1.15)); e.data.materials.append(f)
        e.rotation_euler = (-n).to_track_quat('Y', 'Z').to_euler(); out.append(e)
    pts = []
    for k in range(13):
        a = math.radians(-58 + 116 * k / 12); x = 0.13 * s * math.sin(a); z = (-0.31 - 0.055 * math.cos(a) + 0.055) * s
        h = _hit(targets, cx + x, cz + z)
        if h: pts.append(tuple(h[0] + h[1] * 0.004 * s))
    if len(pts) >= 6:
        r = [0.014, 0.019] + [0.021] * (len(pts) - 4) + [0.019, 0.014]
        out.append(tube('smile', pts, [v * s for v in r], f))
    return out

# ---------- objects: each returns (parts, face parts) ----------
METAL = {'silver': (0.86, 0.87, 0.9), 'bronze': (0.72, 0.47, 0.24)}
def o_coin(metal=None):
    m = principled(metal, METAL[metal], 0.28, metallic=0.75, coat=0.5, coat_rough=0.05) if metal else gold()
    c = cyl(m, (0, 0, 0), 0.95, 0.26, (math.radians(90), 0, 0), 64, 0.05)
    rim = prim('torus', m, (0, -0.12, 0), (math.radians(90), 0, 0), major_radius=0.8, minor_radius=0.035, major_segments=64, minor_segments=12)
    return [c, rim], face([c], 0, 0.05, 1.15)

def glass_grad(name, c0, c1, trans=0.55, emit=0.35, axis=None, k=0.3):
    """tinted glass whose colour runs c0 (bottom left) to c1 (top right), with a soft inner glow"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
    ramp = nt.nodes.new('ShaderNodeValToRGB'); e0, e1 = ramp.color_ramp.elements; e0.position = 0.2; e0.color = (*c0, 1); e1.position = 0.8; e1.color = (*c1, 1)
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY_ADD'; mul.inputs[1].default_value = 0.3; mul.inputs[2].default_value = 0.5
    mul.inputs[1].default_value = k
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    if axis: nt.links.new(sep.outputs[axis], add.inputs[0]); add.inputs[1].default_value = 0.0
    else: nt.links.new(sep.outputs['X'], add.inputs[0]); nt.links.new(sep.outputs['Y'], add.inputs[1])
    nt.links.new(add.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color']); nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = emit; b.inputs['Transmission Weight'].default_value = trans; b.inputs['IOR'].default_value = 1.45
    b.inputs['Roughness'].default_value = 0.08; b.inputs['Coat Weight'].default_value = 1.0; b.inputs['Coat Roughness'].default_value = 0.02
    return m

def o_crypto():
    """translucent lavender-to-violet glass coin (Token World palette), 16-sided edge, a ring of raised pixel tiles round the face"""
    bpy.context.scene.render.film_transparent = True
    try: bpy.context.scene.cycles.film_transparent_glass = True
    except Exception: pass
    P = smiley.PAL; m = glass_grad('cglass', P['lavender'], P['violet'], emit=0.15)
    c = cyl(m, (0, 0, 0), 0.95, 0.26, (math.radians(90), 0, 0), 16, 0.03)
    core = cyl(principled('core', P['periwinkle'], 0.3, emit=P['lavender'], emit_str=0.2), (0, 0, 0), 0.7, 0.1, (math.radians(90), 0, 0), 16, 0)
    cols = [principled('px%d' % k, col, 0.15, emit=col, emit_str=0.25, coat=1.0, coat_rough=0.02) for k, col in
            enumerate((P['gold'], P['lavender'], P['ice'], P['violet']))]
    px, st = [], 0.15
    for i in range(-6, 7):
        for k in range(-6, 7):
            x, z = i * st, k * st; d = math.hypot(x, z)
            if 0.6 < d < 0.83:
                px.append(box('px', cols[(i * 3 + k * 5) % 4], (x, -0.15, z), (st * 0.82, 0.05, st * 0.82), bv=0.008))
    return [c, core] + px, face([c], 0, 0.05, 1.05)

def o_notes():
    g = plastic('note', smiley.PAL['sheen']); dk = plastic('noteDk', smiley.PAL['gold'])
    ps = []
    for k, (dx, dz, rz) in enumerate([(0.12, -0.1, 10), (0.06, -0.05, 4), (0, 0, 0)]):
        ps.append(box('n', g if k == 2 else dk, (dx, 0.12 - 0.06 * k, dz), (1.9, 0.05, 1.0), (0, math.radians(rz), 0), 0.02))
    oval = prim('cylinder', plastic('oval', smiley.PAL['paper']), (0, -0.035, 0), (math.radians(90), 0, 0), vertices=48, radius=0.36, depth=0.02)
    oval.scale = (1.3, 1, 1)
    return ps + [oval], face([oval, ps[2]], 0, 0.06, 0.95)

def o_moneybag():
    tan = plastic('bag', smiley.PAL['bronze'])
    b = uv_sphere('bag', 0.85, (0, 0, -0.2), (1, 0.92, 0.95), 64, 32); b.data.materials.append(tan)
    neck = cyl(tan, (0, 0, 0.62), 0.22, 0.25); top = prim('cone', tan, (0, 0, 0.86), vertices=48, radius1=0.12, radius2=0.42, depth=0.26)
    tie = prim('torus', gold(), (0, 0, 0.66), major_radius=0.25, minor_radius=0.055, major_segments=48, minor_segments=12)
    return [b, neck, top, tie], face([b], 0, -0.1, 1.15)

def o_receipt():
    paper = plastic('paper', smiley.PAL['paper']); line = plastic('line', smiley.PAL['pewter'])
    r = box('rcpt', paper, (0, 0, 0), (1.2, 0.08, 1.75), (0, 0, 0), 0.03)
    ls = [box('l', line, (-0.05 if k % 2 else 0, -0.045, -0.35 - 0.16 * k), (0.8 - 0.25 * (k % 2), 0.01, 0.05), bv=0) for k in range(3)]
    tot = box('t', gold(), (0.25, -0.05, -0.8), (0.4, 0.015, 0.09), bv=0)
    return [r, tot] + ls, face([r], 0, 0.45, 0.95)

def o_tag():
    pink = plastic('tag', smiley.PAL['gold'])
    import bmesh
    me = bpy.data.meshes.new('tag'); bm = bmesh.new()
    vs = [bm.verts.new(p) for p in [(-0.62, 0, -0.8), (0.62, 0, -0.8), (0.62, 0, 0.45), (0, 0, 0.98), (-0.62, 0, 0.45)]]
    bm.faces.new(vs); bm.to_mesh(me); bm.free()
    t = link(bpy.data.objects.new('tag', me)); t.data.materials.append(pink)
    so = t.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.14; so.offset = 0; bevel(t, 0.05, 4)
    t.rotation_euler = (0, math.radians(-12), 0)
    hole = prim('torus', gold(), (0.13, -0.08, 0.6), (math.radians(90), 0, 0), major_radius=0.1, minor_radius=0.03, major_segments=32, minor_segments=10)
    hole.location = Euler((0, math.radians(-12), 0)).to_matrix() @ Vector((0, -0.08, 0.62))
    s = tube('string', [tuple(hole.location + Vector((0, 0, 0.08))), (0.1, -0.1, 1.05), (0.35, -0.1, 1.2)], [0.018] * 3, gold())
    return [t, hole, s], face([t], 0, -0.12, 1.0)

def o_bank():
    st = plastic('stone', smiley.PAL['sheen']); rf = plastic('roof', smiley.PAL['graphite'])
    base = box('base', st, (0, 0, -0.85), (1.9, 1.1, 0.2)); step = box('step', st, (0, -0.05, -0.72), (1.7, 1.0, 0.1))
    cols = [cyl(st, (x, -0.3, -0.25), 0.1, 0.85, v=24, bv=0.01) for x in (-0.6, -0.2, 0.2, 0.6)]
    back = box('back', st, (0, 0.15, -0.25), (1.5, 0.5, 0.85), bv=0.02)
    frieze = box('frieze', st, (0, -0.05, 0.28), (1.8, 1.0, 0.42))
    roof = prism(rf, (0, -0.05, 0.44), 1.95, 1.05, 0.42)
    return [base, step, back, frieze, roof] + cols, face([frieze], 0, 0.42, 0.72)

def o_tower():
    gl = plastic('glass', smiley.PAL['platinum']); win = principled('win', smiley.PAL['graphite'], 0.1, coat=1.0)
    t = box('tower', gl, (0, 0, -0.1), (1.0, 1.0, 1.9), bv=0.06)
    ws = [box('w', win, (x, -0.505, z), (0.18, 0.01, 0.16), bv=0) for x in (-0.3, 0, 0.3) for z in (-0.85, -0.55)]
    top = box('top', plastic('cap', smiley.PAL['pewter']), (0, 0, 0.9), (0.7, 0.7, 0.14))
    ant = tube('ant', [(0.2, 0, 0.96), (0.2, 0, 1.15), (0.2, 0, 1.3)], [0.02] * 3, gold())
    return [t, top, ant] + ws, face([t], 0, 0.4, 1.0)

def o_factory():
    w = plastic('wall', smiley.PAL['bronze']); r = plastic('saw', smiley.PAL['pewter'])
    body = box('body', w, (0, 0, -0.45), (1.9, 1.0, 0.95))
    saws = [prism(r, (x, 0, 0.03), 0.6, 1.0, 0.32, (0, math.radians(18), 0)) for x in (-0.6, 0, 0.6)]
    ch = cyl(plastic('chim', smiley.PAL['graphite']), (0.62, 0.2, 0.45), 0.13, 0.95)
    smoke = [uv_sphere('s', r_, (0.62 + dx, 0.2, z), seg=32, rings=16) for dx, z, r_ in ((0.05, 1.05, 0.16), (0.22, 1.25, 0.12))]
    for s in smoke: s.data.materials.append(plastic('smoke', smiley.PAL['platinum']))
    return [body, ch] + saws + smoke, face([body], -0.2, -0.35, 0.95)

def o_crane():
    y = plastic('yellow', smiley.PAL['gold']); dk = plastic('dark', smiley.PAL['graphite'])
    mast = box('mast', y, (-0.35, 0, -0.2), (0.22, 0.22, 1.8), bv=0.02)
    jib = box('jib', y, (0.2, 0, 0.72), (1.5, 0.16, 0.16), bv=0.02)
    cab = box('cab', y, (-0.35, -0.02, 0.38), (0.55, 0.5, 0.45))
    hook = tube('rope', [(0.75, 0, 0.66), (0.75, 0, 0.3), (0.75, 0, 0.05)], [0.012] * 3, dk)
    blk = box('blk', principled('steel', (0.75, 0.76, 0.8), 0.25, metallic=1.0), (0.75, 0, -0.05), (0.2, 0.2, 0.2))
    base = box('cbase', dk, (-0.35, 0, -1.05), (0.7, 0.6, 0.12))
    return [mast, jib, cab, hook, blk, base], face([cab], -0.35, 0.42, 0.55)

def o_house():
    wl = plastic('hwall', smiley.PAL['sheen']); rf = plastic('hroof', smiley.PAL['bronze'])
    b = box('house', wl, (0, 0, -0.45), (1.5, 1.2, 1.1))
    r = prism(rf, (0, 0, 0.08), 1.75, 1.4, 0.7)
    door = box('door', plastic('door', smiley.PAL['graphite']), (0.45, -0.6, -0.75), (0.3, 0.04, 0.5), bv=0.02)
    ch = box('chim', rf, (0.45, 0.2, 0.55), (0.2, 0.2, 0.45), bv=0.02)
    return [b, r, door, ch], face([b], -0.18, -0.3, 0.95)

def o_castle():
    st = plastic('cstone', smiley.PAL['platinum']); rf = plastic('croof', smiley.PAL['graphite'])
    wall = box('wall', st, (0, 0, -0.45), (1.3, 0.9, 1.0))
    tws = [cyl(st, (x, 0, -0.25), 0.3, 1.45) for x in (-0.75, 0.75)]
    cones = [prim('cone', rf, (x, 0, 0.72), vertices=48, radius1=0.38, radius2=0.0, depth=0.55) for x in (-0.75, 0.75)]
    cren = [box('c', st, (x, 0, 0.12), (0.18, 0.9, 0.18), bv=0.02) for x in (-0.36, 0, 0.36)]
    gate = box('gate', plastic('gate', smiley.PAL['bronze']), (0, -0.46, -0.78), (0.4, 0.04, 0.45), bv=0.04)
    return [wall, gate] + tws + cones + cren, face([wall], 0, -0.15, 0.8)

def o_dome():
    st = plastic('dstone', smiley.PAL['sheen']); dm = plastic('dome', smiley.PAL['gold'])
    base = box('dbase', st, (0, 0, -0.6), (1.7, 1.1, 0.75))
    drum = cyl(st, (0, 0, -0.08), 0.6, 0.3)
    d = uv_sphere('dome', 0.6, (0, 0, 0.05), (1, 1, 1.05), 64, 32); d.data.materials.append(dm)
    sp = tube('spire', [(0, 0, 0.66), (0, 0, 0.85), (0, 0, 1.0)], [0.03, 0.02, 0.012], gold())
    ball = prim('uv_sphere', gold(), (0, 0, 0.72), radius=0.06)
    return [base, drum, d, sp, ball], face([base], 0, -0.48, 0.85)

def o_map():
    pp = [plastic('map%d' % k, c) for k, c in enumerate((smiley.PAL['sheen'], smiley.PAL['paper']))]
    land = plastic('land', smiley.PAL['gold']); sea = plastic('sea', smiley.PAL['platinum'])
    panels = [box('p', pp[k % 2], (-0.6 + 0.6 * k, 0.08 * (k % 2), 0), (0.6, 0.05, 1.5), (0, 0, math.radians(14 if k % 2 else -14)), 0.015) for k in range(3)]
    blobs = [box('b', land, (-0.62, -0.06, 0.35), (0.35, 0.01, 0.4), (0, 0, math.radians(-14)), 0), box('b', land, (0.6, -0.06, -0.45), (0.3, 0.01, 0.35), (0, 0, math.radians(-14)), 0)]
    return panels + blobs, face([panels[1]], 0, 0.05, 0.85)

def o_pin():
    red = plastic('pin', smiley.PAL['bronze'])
    s = uv_sphere('pinball', 0.7, (0, 0, 0.3), seg=64, rings=32); s.data.materials.append(red)
    c = prim('cone', red, (0, 0, -0.45), (math.radians(180), 0, 0), vertices=48, radius1=0.5, radius2=0.02, depth=0.95)
    shadow = cyl(plastic('pinshadow', smiley.PAL['graphite']), (0, 0, -0.95), 0.22, 0.03, bv=0.01)
    return [s, c, shadow], face([s], 0, 0.3, 0.9)

def o_compass():
    body = principled('cbody', smiley.PAL['paper'], 0.3, coat=0.8)
    d = cyl(body, (0, 0, 0), 0.92, 0.22, (math.radians(90), 0, 0), 64, 0.04)
    rim = prim('torus', gold(), (0, -0.1, 0), (math.radians(90), 0, 0), major_radius=0.92, minor_radius=0.07, major_segments=64, minor_segments=16)
    import bmesh
    def needle(col, up):
        me = bpy.data.meshes.new('ndl'); bm = bmesh.new()
        vs = [bm.verts.new(p) for p in [(-0.09, 0, 0), (0, 0, 0.62 * up), (0.09, 0, 0)]]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
        o = link(bpy.data.objects.new('ndl', me)); o.location = (0.0, -0.13, 0.25); o.data.materials.append(principled('n', col, 0.3, coat=0.8))
        so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.03; o.rotation_euler = (0, math.radians(-35), 0); return o
    hub = prim('uv_sphere', gold(), (0, -0.14, 0.25), radius=0.05)
    return [d, rim, needle(smiley.PAL['bronze'], 1), needle(smiley.PAL['pewter'], -0.6), hub], face([d], 0, -0.2, 0.85)

# runner poses. Ground gaits: (stride deg, leg length, bob, lean deg, arm swing deg, knee bend), 8 frames each.
GAITS = {'walk': (22, 0.56, 0.04, 0, 20, 0.04), 'jog': (34, 0.58, 0.07, 8, 38, 0.08), 'run': (54, 0.62, 0.13, 18, 64, 0.17)}
# Air poses, one tuple per frame: (bob, lean, (front leg, back leg) deg, leg length, knee bend, (arm 1, arm 2) deg)
def _air(name, i):
    w = math.sin(2 * math.pi * i / 4)
    if name == 'tko': return [(-0.16, 6, (24, -18), 0.42, 0.22, (-55, -40)), (0.05, 2, (-6, 8), 0.7, 0.0, (125, 150)), (0.1, -4, (44, -24), 0.46, 0.2, (150, 165))][i]
    if name == 'rise': return (0.06, -6, (42 + 10 * w, -12 - 10 * w), 0.48, 0.2, (150 + 14 * w, 160 - 14 * w))
    return (0.0, -10, (-42 + 24 * w, 40 - 24 * w), 0.56, 0.1, (95 + 40 * w, 95 - 40 * w))  # fall: arms windmill, legs kick
AIR = {'tko': 3, 'rise': 4, 'fall': 4}
RUNNER_SKIN = os.environ.get('RUNNER_SKIN', 'gold')   # 'glass' = the powered-up look

def o_runner(gait, frame):
    """game runner: a smiley ball with legs and little arms, turned to face right (the run direction)"""
    P = smiley.PAL
    if RUNNER_SKIN == 'glass':  # powered up: translucent purple-to-red glass with an inner glow
        bpy.context.scene.render.film_transparent = True
        try: bpy.context.scene.cycles.film_transparent_glass = True
        except Exception: pass
        body = glass_grad('rglass', (0.98, 0.06, 0.22), (0.4, 0.05, 0.98), trans=0.6, emit=0.45, axis='Z', k=0.75)  # red underneath -> purple on top
        limb = principled('rlimb', (0.85, 0.05, 0.25), 0.15, emit=(0.9, 0.08, 0.3), emit_str=0.5, coat=1.0, coat_rough=0.02)
        limb.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.4
    else:
        body = plastic('rbody', P['gold']); limb = plastic('rleg', P['bronze'])
    if gait in GAITS:
        st, L, bobA, lean, armA, bend = GAITS[gait]; ph = frame / 8; c = math.sin(2 * math.pi * ph)
        bob = bobA * math.cos(4 * math.pi * ph); legs = (st * c, -st * c); arms = (-armA * c, armA * c)
    else:
        bob, lean, legs, L, bend, arms = _air(gait, frame)
    b = uv_sphere('rb', 0.8, (0, 0, 0.25 + bob), seg=64, rings=32); b.data.materials.append(body)
    parts = [b]
    for k, side in enumerate((-1, 1)):
        a = math.radians(legs[k]); hip = Vector((0.05 * side, side * 0.22, -0.4 + bob))
        knee = hip + Vector((math.sin(a) * L * 0.5 + bend, 0, -math.cos(a) * L * 0.5))
        foot = hip + Vector((math.sin(a) * L, 0, -math.cos(a) * L))
        parts.append(tube('leg', [tuple(hip), tuple(knee), tuple(foot)], [0.09, 0.085, 0.08], limb))
        f = uv_sphere('foot', 0.13, tuple(foot + Vector((0.07, 0, -0.02))), (1.5, 0.9, 0.6), 32, 16); f.data.materials.append(limb); parts.append(f)
        # arm: on the visible left/right side of the ball (clear of the face), raised outward by its angle
        bA = math.radians(abs(arms[k]) * 0.8 + 18); sh = Vector((side * 0.74, 0.05, 0.12 + bob))
        hand = sh + Vector((side * math.sin(bA) * 0.42, -0.06, -math.cos(bA) * 0.42))
        parts.append(tube('arm', [tuple(sh), tuple(sh.lerp(hand, 0.5)), tuple(hand)], [0.07, 0.065, 0.06], limb))
        hd = uv_sphere('hand', 0.1, tuple(hand), seg=24, rings=12); hd.data.materials.append(limb); parts.append(hd)
    fc = face([b], 0, 0.3 + bob, 0.95)
    hub = link(bpy.data.objects.new('turn', None)); bpy.context.view_layer.update()
    for o in parts + fc:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.rotation_mode = 'XYZ'; hub.rotation_euler = (0, math.radians(lean), math.radians(30))
    return [hub], []

def star_mesh(mat, loc=(0, 0, 0), r=0.9):
    import bmesh
    me = bpy.data.meshes.new('star'); bm = bmesh.new()
    vs = [bm.verts.new((math.cos(math.pi / 2 + k * math.pi / 5) * (r if k % 2 == 0 else r * 0.45), 0, math.sin(math.pi / 2 + k * math.pi / 5) * (r if k % 2 == 0 else r * 0.45))) for k in range(10)]
    bm.faces.new(vs); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new('star', me)); o.location = loc; o.data.materials.append(mat)
    so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.3; so.offset = 0
    return bevel(o, 0.09, 4)

def o_star(off=False):
    """UI star (save / profile): gold, or platinum for 'not saved'. No face: it is a control, not a character."""
    m = principled('pstar', (0.86, 0.87, 0.9), 0.3, metallic=0.7, coat=0.6) if off else principled('gstar', smiley.PAL['gold'], 0.28, coat=0.8, coat_rough=0.05)
    return [star_mesh(m)], []

def o_warn():
    """warning sign: rounded gold triangle with a face"""
    import bmesh
    me = bpy.data.meshes.new('tri'); bm = bmesh.new()
    vs = [bm.verts.new(p) for p in [(-0.95, 0, -0.7), (0.95, 0, -0.7), (0, 0, 0.95)]]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
    t = link(bpy.data.objects.new('tri', me)); t.data.materials.append(plastic('warn', smiley.PAL['gold']))
    so = t.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.24; so.offset = 0; bevel(t, 0.14, 5)
    return [t], face([t], 0, -0.12, 0.85)

def o_hook():
    """scam warning: a fishing hook with a coin as bait (the coin has the face)"""
    steel = principled('steel', (0.86, 0.87, 0.9), 0.25, metallic=1.0)
    # a big J: shank down the right, a round bend, the point coming back up on the left
    arc = [(0.55 * math.cos(math.radians(a)), 0.15, -0.35 - 0.55 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    pts = [(0.55, 0.15, 1.1), (0.55, 0.15, 0.4)] + arc + [(-0.55, 0.15, 0.05)]
    hook = tube('hook', pts, [0.1] * len(pts), steel)
    barb = prim('cone', steel, (-0.55, 0.15, 0.12), vertices=24, radius1=0.15, radius2=0.0, depth=0.3)
    eye = prim('torus', steel, (0.55, 0.15, 1.22), (math.radians(90), 0, 0), major_radius=0.13, minor_radius=0.05, major_segments=32, minor_segments=8)
    c = cyl(gold(), (0, -0.25, -0.75), 0.42, 0.14, (math.radians(90), 0, 0), 48, 0.03)
    return [hook, barb, eye, c], face([c], 0, -0.72, 0.55)

def o_moon():
    """theme toggle: a thick gold crescent moon with a face (2D crescent, solidified and rounded)"""
    import bmesh
    R1, C2, R2 = 0.95, Vector((0.5, 0.32)), 0.78
    outer = [(R1 * math.cos(math.radians(a)), R1 * math.sin(math.radians(a))) for a in range(0, 360, 4)]
    keep = [q for q in outer if (Vector(q) - C2).length > R2]
    k0 = max(range(len(outer)), key=lambda i: (Vector(outer[i]) - C2).length > R2 and (Vector(outer[i - 1]) - C2).length <= R2)
    ring = outer[k0:] + outer[:k0]; ring = [q for q in ring if (Vector(q) - C2).length > R2]   # outer arc, in order
    inner = [(C2.x + R2 * math.cos(math.radians(a)), C2.y + R2 * math.sin(math.radians(a))) for a in range(0, 360, 4)]
    inner = [q for q in inner if Vector(q).length < R1]
    a0 = math.atan2(ring[-1][1] - C2.y, ring[-1][0] - C2.x)
    inner.sort(key=lambda q: (a0 - math.atan2(q[1] - C2.y, q[0] - C2.x)) % (2 * math.pi))       # walk the cut arc back to the start
    me = bpy.data.meshes.new('moon'); bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in ring + inner]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new('moon', me)); o.data.materials.append(plastic('moon', smiley.PAL['sheen']))
    so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.4; so.offset = 0; bevel(o, 0.16, 6)
    o.rotation_euler = (0, math.radians(-20), 0)
    return [o], face([o], -0.48, -0.02, 0.55)

def o_pu_shield():
    """power-up: a heater shield, platinum face, gold rim and boss, with a face"""
    import bmesh
    def outline(sc):
        pts = [(-0.75, 0.85), (0.75, 0.85), (0.78, 0.1)] + [(0.78 * math.cos(math.radians(a)) * (1 - t) , -0.15 - 0.85 * t) for t, a in [(0.25, 20), (0.5, 40), (0.75, 65)]] + [(0, -1.0)]
        right = [(0.75, 0.85), (0.78, 0.2), (0.7, -0.25), (0.5, -0.6), (0.25, -0.85), (0, -1.0)]
        full = [(-0.75, 0.85)] + right + [(-x, z) for x, z in reversed(right[1:-1])]
        return [(x * sc, z * sc) for x, z in full]
    def slab(sc, th, mat, y):
        me = bpy.data.meshes.new('sh'); bm = bmesh.new(); vs = [bm.verts.new((x, 0, z)) for x, z in outline(sc)]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
        o = link(bpy.data.objects.new('sh', me)); o.location = (0, y, 0); o.data.materials.append(mat)
        so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = th; so.offset = 0; return bevel(o, 0.05, 4)
    rim = slab(1.0, 0.28, gold(), 0)
    face_ = slab(0.84, 0.3, principled('plat', (0.86, 0.87, 0.9), 0.25, metallic=0.9, coat=0.6), -0.04)
    return [rim, face_], face([face_], 0, 0.05, 0.85)

def o_pu_magnet():
    """power-up: a chunky horseshoe magnet, bronze with platinum poles, with a face on the bend"""
    mb = principled('mag', smiley.PAL['bronze'], 0.3, coat=0.9, coat_rough=0.04); tip = principled('pole', (0.86, 0.87, 0.9), 0.22, metallic=1.0)
    arc = [(0.48 * math.cos(math.radians(a)), 0, 0.15 + 0.48 * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    pts = [(0.48, 0, -0.45)] + arc + [(-0.48, 0, -0.45)]
    body = tube('magnet', pts, [0.22] * len(pts), mb)
    poles = [cyl(tip, (x, 0, -0.62), 0.225, 0.3, bv=0.03) for x in (-0.48, 0.48)]
    return [body] + poles, face([body], 0, 0.72, 0.5)

def o_pu_x2():
    """power-up: a chunky bevelled gold 2x"""
    bpy.ops.object.text_add(location=(0, 0, 0), rotation=(math.radians(90), 0, 0)); t = bpy.context.active_object
    t.data.body = '2x'; t.data.size = 1.35; t.data.extrude = 0.16; t.data.bevel_depth = 0.05; t.data.bevel_resolution = 4
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'; t.data.materials.append(gold())
    return [t], []

OBJECTS = {'coin': (o_coin, -1), 'pu2-shield': (o_pu_shield, 1), 'pu2-magnet': (o_pu_magnet, 1), 'pu2-x2': (o_pu_x2, 1), 'star': (o_star, 1), 'star-off': (lambda: o_star(True), 1), 'warn': (o_warn, -1), 'hook': (o_hook, 1), 'moon': (o_moon, -1), 'coin-silver': (lambda: o_coin('silver'), -1), 'coin-bronze': (lambda: o_coin('bronze'), -1),
           **{'runner-%s-%d' % (g, i): ((lambda g=g, i=i: o_runner(g, i)), 0) for g, n in [*[(g, 8) for g in GAITS], *AIR.items()] for i in range(n)}, 'crypto': (o_crypto, 1), 'notes': (o_notes, -1), 'moneybag': (o_moneybag, 1), 'receipt': (o_receipt, -1),
           'tag': (o_tag, 1), 'bank': (o_bank, -1), 'tower': (o_tower, 1), 'factory': (o_factory, -1), 'crane': (o_crane, 1),
           'house': (o_house, -1), 'castle': (o_castle, 1), 'dome': (o_dome, -1), 'map': (o_map, 1), 'pin': (o_pin, -1), 'compass': (o_compass, 1)}

def flag_badge(cc):
    img = bpy.data.images.load(os.path.join(FLAGDIR, cc + '.png'))
    m = bpy.data.materials.new('flag'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.28; b.inputs['Coat Weight'].default_value = 0.7; b.inputs['Coat Roughness'].default_value = 0.05
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; tx.extension = 'EXTEND'
    mp.inputs['Location'].default_value = (0.5, 0.5, 0); mp.inputs['Scale'].default_value = (0.556, 0.556, 0.556)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tx.inputs['Vector']); nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    disc = cyl(m, (0, 0, 0), 0.9, 0.24, (math.radians(90), 0, 0), 96, 0.06)
    rim = prim('torus', gold(), (0, 0, 0), (math.radians(90), 0, 0), major_radius=0.92, minor_radius=0.08, major_segments=96, minor_segments=16)
    return [disc, rim]

def build(name, out, res, samples, nfr):
    smiley.GOLD = None; reset()
    if name.startswith('flag-'): parts, fc, sign = flag_badge(name[5:]), [], -1
    else:  # '<name>-plain' = the same object without a face (used by the Token World portal coins)
        global NOFACE; NOFACE = name.endswith('-plain')
        fn, sign = OBJECTS[name[:-6] if NOFACE else name]; parts, fc = fn()
    stage(res=res, samples=samples, cam_loc=(-0.9, -7.6, 0.9), target=(0.05, 0, 0.05), lens=LENS)
    bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35  # something for gold to reflect
    vs = bpy.context.scene.view_settings; vs.view_transform = 'Standard'; vs.look = 'None'; vs.exposure = -0.75
    pivot = link(bpy.data.objects.new('pivot', None)); pivot.rotation_mode = 'QUATERNION'
    bpy.context.view_layer.update()
    for o in parts + fc:
        mw = o.matrix_world.copy(); o.parent = pivot; o.matrix_world = mw
    d = os.path.join(out, name); os.makedirs(d, exist_ok=True)
    for i in range(nfr):
        # objects rock +-25 deg instead of a full turn, so the face never turns away; flags turn fully
        ang = sign * 2 * math.pi * i / nfr if name.startswith(('flag-', 'pu2-')) else sign * math.radians(25) * math.sin(2 * math.pi * i / nfr)
        pivot.rotation_quaternion = Quaternion((0, 0, 1), ang)
        render(f'{d}/{i:03d}.png')

if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]
    if which == 'list': print(' '.join(OBJECTS)); sys.exit()
    res = int(sys.argv[3]) if len(sys.argv) > 3 else 192
    samples = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    nfr = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    if len(sys.argv) > 6: FLAGDIR = sys.argv[6]
    names = list(OBJECTS) if which == 'all' else which.split(',')
    for n in names: build(n, out, res, samples, nfr)
