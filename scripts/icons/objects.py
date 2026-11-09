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
SHADES = os.environ.get('RUNNER_PROP') == 'shades'   # all-in: big black sunglasses instead of eyes
DOLLAR = 0.0   # > 0: eyes are gold $ signs at this scale (2x power-up form)
LOVE = os.environ.get('RUNNER_FACE', '').startswith('love')   # smitten face: big glossy popped-out eyes with white shines, a hard smile, pink cheeks
NOEYES = os.environ.get('RUNNER_FACE') == 'love-noeyes'     # same, but the eyes are left out: the game draws huge heart eyes there (positions exported per frame)
def face(targets, cx, cz, s=1.0):
    """black dot eyes + small smile on the front of `targets`, centred at (cx, cz), scaled by s"""
    if NOFACE: return []
    bpy.context.view_layer.update(); f = ink(); out = []
    for k in (-1, 1):
        h = _hit(targets, cx + k * 0.2 * s, cz - 0.1 * s)
        if not h: continue
        p, n = h
        if DOLLAR:
            bpy.ops.object.text_add(location=tuple(p + n * 0.03), rotation=(math.radians(90), 0, 0)); e = bpy.context.active_object
            e.data.body = '$'; e.data.size = 0.36 * s * DOLLAR; e.data.extrude = 0.035; e.data.bevel_depth = 0.012
            e.data.align_x = 'CENTER'; e.data.align_y = 'CENTER'; e.data.materials.append(principled('dollar', (1.0, 0.74, 0.18), 0.22, metallic=0.85, coat=0.8, emit=(1.0, 0.7, 0.15), emit_str=0.6))
            out.append(e); continue
        if LOVE and NOEYES:  # an invisible marker where the eye would be; build() exports its pixel position
            a_ = link(bpy.data.objects.new(f'eyeanchor{k}', None)); a_.location = tuple(p + n * 0.04 * s); out.append(a_)
        if LOVE:  # puppy eyes: bigger glossy black balls that pop out, each with a big and a small white shine
            r = 0.15 * s; e = uv_sphere(f'eye{k}', r, tuple(p + n * 0.035 * s), (1, 0.8, 1.1)); e.data.materials.append(f)
            if NOEYES: bpy.data.objects.remove(e)
            else: e.rotation_euler = (-n).to_track_quat('Y', 'Z').to_euler(); out.append(e)
            shine = principled('shine', (0.85, 0.86, 0.9), 0.2, emit=(0.85, 0.86, 0.9), emit_str=0.5)  # a soft catch-light, not a white blob
            for dx, dz, rr in (() if NOEYES else ((-0.38, 0.4, 0.26), (0.32, -0.3, 0.12))):
                q = p + n * (0.035 * s + r * 0.85) + Vector((dx * r, 0, dz * r)); sh = uv_sphere('shine', rr * r, tuple(q)); sh.data.materials.append(shine); out.append(sh)
            ch = _hit(targets, cx + k * 0.4 * s, cz - 0.27 * s)  # blush below each eye
            if ch:
                cp_, cn = ch; bl = uv_sphere('blush', 0.12 * s, tuple(cp_ + cn * 0.005), (1.5, 0.25, 0.8)); bl.data.materials.append(principled('blush', (1.0, 0.35, 0.45), 0.5, emit=(1.0, 0.3, 0.4), emit_str=0.3))
                bl.rotation_euler = (-cn).to_track_quat('Y', 'Z').to_euler(); out.append(bl)
            continue
        if SHADES:  # a big glossy black lens over each eye, bridged across the nose
            gl = principled('shades', (0.01, 0.01, 0.015), 0.04, coat=1.0, coat_rough=0.0, metallic=0.3)
            ln = uv_sphere(f'lens{k}', 0.215 * s, tuple(p + n * 0.035 * s + Vector((0, 0, 0.02 * s))), (1.4, 0.28, 1.0)); ln.data.materials.append(gl)
            ln.rotation_euler = (-n).to_track_quat('Y', 'Z').to_euler(); out.append(ln)
            if k == 1:
                hb = _hit(targets, cx, cz - 0.04 * s)
                if hb: out.append(tube('bridge', [tuple(lp + ln_ * 0.05 * s) for lp, ln_ in ((pl, nl), hb, (p, n))], [0.028 * s] * 3, gl))
            pl, nl = p, n; continue
        e = uv_sphere(f'eye{k}', 0.062 * s, tuple(p - n * 0.012 * s), (1, 0.55, 1.15)); e.data.materials.append(f)
        e.rotation_euler = (-n).to_track_quat('Y', 'Z').to_euler(); out.append(e)
    pts = []
    for k in range(13):
        a = math.radians(-58 + 116 * k / 12); W_, D_ = (0.27, 0.15) if LOVE else (0.13, 0.055)
        x = W_ * s * math.sin(a); z = (-0.31 - D_ * math.cos(a) + D_) * s
        h = _hit(targets, cx + x, cz + z)
        if h: pts.append(tuple(h[0] + h[1] * 0.004 * s))
    if len(pts) >= 6:
        r = [0.014, 0.019] + [0.021] * (len(pts) - 4) + [0.019, 0.014]
        if LOVE: r = [v * 1.9 for v in r]
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
def _lerp_pose(a, b, u):
    if isinstance(a, tuple): return tuple(_lerp_pose(x, y, u) for x, y in zip(a, b))
    return a + (b - a) * u

TKO_KEYS = [(-0.16, 6, (24, -18), 0.42, 0.22, (-55, -40)), (0.05, 2, (-6, 8), 0.7, 0.0, (125, 150)), (0.1, -4, (44, -24), 0.46, 0.2, (150, 165))]

def _air(name, i):
    w = math.sin(2 * math.pi * i / AIR[name])
    if name == 'tko':  # AIR['tko'] frames blended through the three key poses (eased)
        u = i / (AIR['tko'] - 1) * 2; k = min(1, int(u)); f = u - k; f = f * f * (3 - 2 * f)
        return _lerp_pose(TKO_KEYS[k], TKO_KEYS[k + 1], f)
    if name == 'rise': return (0.06, -6, (42 + 10 * w, -12 - 10 * w), 0.48, 0.2, (150 + 14 * w, 160 - 14 * w))
    return (0.0, -10, (-42 + 24 * w, 40 - 24 * w), 0.56, 0.1, (95 + 40 * w, 95 - 40 * w))  # fall: arms windmill, legs kick
GAIT_N = 24   # frames per walk/jog/run cycle (was 8): the game steps them by distance, 30-75 fps
AIR = {'tko': 9, 'rise': 12, 'fall': 12}   # was 3/4/4
RUNNER_PROP = os.environ.get('RUNNER_PROP', '')   # 'case' = going to cash (carries a briefcase), 'shades' = all in (strut + sunglasses)
RUNNER_SKIN = os.environ.get('RUNNER_SKIN', 'gold')   # 'glass' = the powered-up look

def rainbow_glass(name):
    """translucent glass whose hue runs in a spiral round the body (angle around z + height); the game also rotates the hues over time"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    at = nt.nodes.new('ShaderNodeMath'); at.operation = 'ARCTAN2'; nt.links.new(sep.outputs['Y'], at.inputs[0]); nt.links.new(sep.outputs['X'], at.inputs[1])
    zk = nt.nodes.new('ShaderNodeMath'); zk.operation = 'MULTIPLY'; zk.inputs[1].default_value = 0.55; nt.links.new(sep.outputs['Z'], zk.inputs[0])
    turn = nt.nodes.new('ShaderNodeMath'); turn.operation = 'MULTIPLY_ADD'; turn.inputs[1].default_value = 2 / (2 * math.pi); nt.links.new(at.outputs[0], turn.inputs[0])
    nt.links.new(zk.outputs[0], turn.inputs[2])  # two hue turns per lap + a slow climb with height: bands wind round as a spiral
    fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'; nt.links.new(turn.outputs[0], fr.inputs[0])
    hsv = nt.nodes.new('ShaderNodeCombineColor'); hsv.mode = 'HSV'; hsv.inputs[1].default_value = 0.85; hsv.inputs[2].default_value = 1.0
    nt.links.new(fr.outputs[0], hsv.inputs[0])
    nt.links.new(hsv.outputs[0], b.inputs['Base Color']); nt.links.new(hsv.outputs[0], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 0.45; b.inputs['Transmission Weight'].default_value = 0.6; b.inputs['IOR'].default_value = 1.45
    b.inputs['Roughness'].default_value = 0.08; b.inputs['Coat Weight'].default_value = 1.0; b.inputs['Coat Roughness'].default_value = 0.02
    return m

GLASS = os.environ.get('GLASS_STYLE', '1') == '1'   # glass family: see-through bodies with a glowing core

def glass_on():
    bpy.context.scene.render.film_transparent = True
    try: bpy.context.scene.cycles.film_transparent_glass = True
    except Exception: pass

POS_SK = {'lgreen': ((0.22, 0.82, 0.36), (0.1, 0.48, 0.2), False), 'ggreen': ((0.05, 0.95, 0.3), (0.02, 0.6, 0.18), True),
          'lred': ((1.0, 0.3, 0.32), (0.62, 0.14, 0.16), False), 'gred': ((1.0, 0.06, 0.12), (0.7, 0.02, 0.08), True)}

def runner_mats():
    """body + limb materials for the current RUNNER_SKIN"""
    P = smiley.PAL
    if RUNNER_SKIN in POS_SK:  # market position: light = 1x (opaque, soft), strong = 2x (deep translucent glass)
        c, cl, strong = POS_SK[RUNNER_SKIN]
        if strong:
            bpy.context.scene.render.film_transparent = True
            try: bpy.context.scene.cycles.film_transparent_glass = True
            except Exception: pass
            body = glass_grad('pglass', tuple(x * 0.55 for x in c), c, trans=0.7, emit=0.5, axis='Z', k=0.75)
            limb = principled('plimb', cl, 0.15, emit=cl, emit_str=0.45, coat=1.0, coat_rough=0.02)
            limb.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.4
        elif GLASS:
            glass_on(); body = glass_grad('lglass', tuple(0.7 * x for x in c), c, trans=0.3, emit=0.35, axis='Z', k=0.75)
            limb = principled('pleg', cl, 0.15, coat=1.0, coat_rough=0.02)
        else:
            body = principled('pbody', c, 0.22, coat=1.0, coat_rough=0.05); limb = principled('pleg', cl, 0.3, coat=0.6)
    elif GLASS:  # honey glass: amber body, polished gold limbs
        glass_on(); body = glass_grad('amber', (0.62, 0.3, 0.03), (1.0, 0.72, 0.22), trans=0.72, emit=0.32, axis='Z', k=0.75)
        limb = gold()
    else:
        body = plastic('rbody', P['gold']); limb = plastic('rleg', P['bronze'])
    return body, limb

def coin_heart(x, z, rock=0.0, sz=1.0):
    """the runner's signature: a glowing gold $ coin floating inside the glass body. rock = small turn (rad) so it never goes edge-on; sz squashes it vertically (goo)"""
    if not GLASS: return []
    m = principled('heart', (1.0, 0.72, 0.18), 0.2, metallic=0.6, coat=1.0, coat_rough=0.03, emit=(1.0, 0.62, 0.12), emit_str=1.6)
    hub = link(bpy.data.objects.new('coinhub', None)); hub.location = (x, -0.05, z)
    c = cyl(m, (0, 0, 0), 0.3, 0.08, (math.radians(90), 0, 0), 48, 0.02)
    bpy.ops.object.text_add(location=(0, -0.045, -0.01), rotation=(math.radians(90), 0, 0)); d = bpy.context.active_object
    d.data.body = '$'; d.data.size = 0.42; d.data.extrude = 0.012; d.data.align_x = 'CENTER'; d.data.align_y = 'CENTER'; d.data.materials.append(gold())
    for o in (c, d): o.parent = hub
    hub.rotation_euler = (0, 0, rock); hub.scale = (1, 1, sz); return [hub]

def briefcase(hand, swing=0.0):
    """a small leather briefcase hanging from `hand` (handle up), swinging by `swing` rad about the hand"""
    leather = plastic('leather', (0.07, 0.03, 0.012), 0.35); g_ = gold()
    piv = link(bpy.data.objects.new('casepiv', None)); piv.location = tuple(hand)
    ps = [box('case', leather, (hand.x, hand.y - 0.02, hand.z - 0.3), (0.56, 0.17, 0.4), bv=0.05),
          prim('torus', g_, (hand.x, hand.y - 0.02, hand.z - 0.08), (math.radians(90), 0, 0), major_radius=0.08, minor_radius=0.022, major_segments=24, minor_segments=8)]
    for x in (-0.16, 0.16): ps.append(box('latch', g_, (hand.x + x, hand.y - 0.11, hand.z - 0.16), (0.07, 0.03, 0.05), bv=0.01))
    bpy.context.view_layer.update()
    for o in ps:
        mw = o.matrix_world.copy(); o.parent = piv; o.matrix_world = mw
    piv.rotation_euler = (0, swing, 0); return [piv]

def o_runner(gait, frame):
    """game runner: a smiley ball with legs and little arms, turned to face right (the run direction)"""
    P = smiley.PAL
    body, limb = runner_mats()
    if gait in GAITS:
        st, L, bobA, lean, armA, bend = GAITS[gait]; ph = frame / GAIT_N; c = math.sin(2 * math.pi * ph)
        bob = bobA * math.cos(4 * math.pi * ph); legs = (st * c, -st * c); arms = (-armA * c, armA * c)
    else:
        bob, lean, legs, L, bend, arms = _air(gait, frame)
    b = uv_sphere('rb', 0.8, (0, 0, 0.25 + bob), seg=64, rings=32); b.data.materials.append(body)
    parts = [b] + coin_heart(0, 0.25 + bob, 0.35 * math.sin(2 * math.pi * frame / (GAIT_N if gait in GAITS else AIR[gait])))
    for k, side in enumerate((-1, 1)):
        a = math.radians(legs[k]); hip = Vector((0.05 * side, side * 0.22, -0.4 + bob))
        knee = hip + Vector((math.sin(a) * L * 0.5 + bend, 0, -math.cos(a) * L * 0.5))
        foot = hip + Vector((math.sin(a) * L, 0, -math.cos(a) * L))
        parts.append(tube('leg', [tuple(hip), tuple(knee), tuple(foot)], [0.09, 0.085, 0.08], limb))
        f = uv_sphere('foot', 0.13, tuple(foot + Vector((0.07, 0, -0.02))), (1.5, 0.9, 0.6), 32, 16); f.data.materials.append(limb); parts.append(f)
        # arm: on the visible left/right side of the ball (clear of the face), raised outward by its angle
        bA = math.radians(abs(arms[k]) * 0.8 + 18); sh = Vector((side * 0.74, 0.05, 0.12 + bob))
        if RUNNER_PROP == 'case' and side == -1: bA = math.radians(14 + 0.25 * arms[k])  # the trailing arm hangs down, carrying the case
        hand = sh + Vector((side * math.sin(bA) * 0.42, -0.06, -math.cos(bA) * 0.42))
        parts.append(tube('arm', [tuple(sh), tuple(sh.lerp(hand, 0.5)), tuple(hand)], [0.07, 0.065, 0.06], limb))
        hd = uv_sphere('hand', 0.1, tuple(hand), seg=24, rings=12); hd.data.materials.append(limb); parts.append(hd)
        if RUNNER_PROP == 'case' and side == -1: parts += briefcase(hand, math.radians(0.6 * arms[k]))
    global DOLLAR
    fc = face([b], 0, 0.3 + bob, 0.95 * (1.12 if LOVE else 1))
    hub = link(bpy.data.objects.new('turn', None)); bpy.context.view_layer.update()
    for o in parts + fc:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.rotation_mode = 'XYZ'; hub.rotation_euler = (0, math.radians(lean), math.radians(14 if LOVE else 30))  # love frames turn toward the camera so the whole happy face shows
    return [hub], []

TRICK_N = 24   # frames per trick row (24 = ~40 fps over a 0.6 s trick)

def _keys(vals, u):
    """evenly spaced keyframes, eased between: lets hand-keyed poses render at any frame count"""
    x = max(0.0, min(1.0, u)) * (len(vals) - 1); i = min(int(x), len(vals) - 2); f = x - i; f = f * f * (3 - 2 * f)
    return vals[i] + (vals[i + 1] - vals[i]) * f
def _ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def _rest_limbs():
    """the runner's 'fall' frame 0 in body space (before the hub's yaw/lean): the pose every trick starts and ends on"""
    bob, lean, legs, L, bend, arms = _air('fall', 0); out = {'legs': [], 'arms': [], 'lean': lean}
    for k, side in enumerate((-1, 1)):
        a = math.radians(legs[k]); hip = Vector((0.05 * side, side * 0.22, -0.4 + bob))
        knee = hip + Vector((math.sin(a) * L * 0.5 + bend, 0, -math.cos(a) * L * 0.5)); foot = hip + Vector((math.sin(a) * L, 0, -math.cos(a) * L))
        out['legs'].append((hip, knee, foot, Vector((1.5, 0.9, 0.6))))
        bA = math.radians(abs(arms[k]) * 0.8 + 18); sh = Vector((side * 0.74, 0.05, 0.12 + bob))
        out['arms'].append((sh, sh + Vector((side * math.sin(bA) * 0.42, -0.06, -math.cos(bA) * 0.42))))
    return out

def o_trick(kind, i, n=TRICK_N):
    """flick tricks as real 3D frame sequences; frame 0 and n-1 are the runner's fall pose, so the game cuts in/out without a fade.
    cork:  off-axis 360 (spin axis tilted 45 deg toward the run direction), knees tucked, arms hugging
    spin:  flat 360 about the vertical axis, arms flung wide, legs together and pointed
    split: turns to face the camera and opens into a side split with arms in a V, holds, closes
    goo:   0-3 melt into a rippling pancake, 4-7 pancake loop (seamless), 8-11 land: splat on the floor and spring back"""
    global DOLLAR
    body, limb = runner_mats(); R0 = _rest_limbs(); u = i / (n - 1)
    yaw, lean, bob, rot = math.radians(30), math.radians(R0['lean']), 0.0, Quaternion()
    sq, ctr, rip, legs, arms = 0.0, 0.25, 0.0, [], []
    L = lambda a, b, t: a.lerp(b, t)
    if kind in ('cork', 'spin'):
        e = _ss(0, 1, u); env = math.sin(math.pi * u) ** 0.7
        if kind == 'cork':
            rot = Quaternion(Vector((0.7, 0, 0.7)).normalized(), 2 * math.pi * e)
            for k, side in enumerate((-1, 1)):
                hip, kn, ft, fs = R0['legs'][k]; y = side * 0.2
                legs.append((hip, L(kn, Vector((0.42, y, -0.3)), env), L(ft, Vector((0.12, y, -0.62)), env), fs))
                sh, hd = R0['arms'][k]; arms.append((sh, L(hd, Vector((side * 0.55, -0.42, -0.25)), env)))
        else:
            rot = Quaternion(Vector((0, 0, 1)), -2 * math.pi * e)
            for k, side in enumerate((-1, 1)):
                hip, kn, ft, fs = R0['legs'][k]; y = side * 0.1
                legs.append((hip, L(kn, Vector((0.03, y, -0.72)), env), L(ft, Vector((0.0, y, -1.02)), env), L(fs, Vector((0.7, 0.9, 1.4)), env)))
                sh, hd = R0['arms'][k]; arms.append((sh, L(hd, sh + Vector((side * 0.5, 0.0, 0.08)), env)))
            lean *= 1 - env
    elif kind == 'split':
        env = _ss(0, 0.32, u) * (1 - _ss(0.68, 1, u)); pulse = math.sin(2 * math.pi * _ss(0.32, 0.68, u)) * env
        yaw *= 1 - env; lean *= 1 - env
        for k, side in enumerate((-1, 1)):
            hip0, kn0, ft0, fs0 = R0['legs'][k]; a = math.radians(84 + 6 * pulse)
            hip = Vector((side * 0.26, 0, -0.42)); ft = hip + Vector((side * math.sin(a) * 0.92, 0, -math.cos(a) * 0.92)); kn = L(hip, ft, 0.5) + Vector((0, -0.04, -0.05))
            legs.append((L(hip0, hip, env), L(kn0, kn, env), L(ft0, ft, env), L(fs0, Vector((0.7, 0.9, 1.45)), env)))
            sh, hd = R0['arms'][k]; bA = math.radians(140 + 10 * pulse * side)
            arms.append((sh, L(hd, sh + Vector((side * math.sin(bA) * 0.46, -0.06, -math.cos(bA) * 0.46)), env)))
    else:  # goo
        n4 = n // 3
        if i < n4: sq = _ss(0, 1, (i + 1) / n4); ph = 0                                # melt in
        elif i < 2 * n4: sq = 1.0; ph = 2 * math.pi * (i - n4) / n4                   # loop (period = n4 frames)
        else:                                                                          # land: splat, then spring back with overshoot
            t = (i - 2 * n4) / (n4 - 1); sq = _keys([1.0, 0.5, -0.18, 0.0], t); ph = 0   # splat, spring back with overshoot
            ctr = 0.25 + (-0.3 - 0.25) * (1 - _ss(0, 1, t)) * (1 if t < 1 else 0); ctr = 0.25 if t >= 1 else ctr
        rip = 0.07 * max(0.0, min(1.0, sq)) if i < 2 * n4 or sq > 0.9 else 0.0
        yaw *= 1 - 0.6 * max(0.0, min(1.0, sq)); lean *= 1 - max(0.0, min(1.0, sq))
        flat = max(0.0, min(1.2, sq)); wide = 1 + 0.5 * flat; hz = 0.8 * (1 - 0.62 * flat) if sq >= 0 else 0.8 * (1 - 0.3 * sq)
        for k, side in enumerate((-1, 1)):
            hip, kn, ft, fs = R0['legs'][k]; t_ = max(0.0, min(1.0, sq))
            rim = Vector((side * 0.5 * wide, -0.15, ctr - 0.25 - hz * 0.5)); out = Vector((side * 0.8 * wide, -0.3, ctr - 0.25 - hz * 0.6))
            legs.append((L(hip, rim, t_), L(kn, L(rim, out, 0.5) + Vector((0, 0, 0.04)), t_), L(ft, out, t_), L(fs, Vector((1.2, 1.2, 0.45)), t_)))
            sh, hd = R0['arms'][k]; sh2 = Vector((side * 0.55 * wide, -0.2, ctr - 0.25 + hz * 0.15))
            arms.append((L(sh, sh2, t_), L(hd, sh2 + Vector((side * 0.32, -0.3, -0.05)), t_)))
    if not legs: legs = R0['legs']
    if not arms: arms = R0['arms']
    b = uv_sphere('rb', 0.8, (0, 0, 0.25), seg=64, rings=32); b.data.materials.append(body)
    if kind == 'goo':  # deform the mesh itself: flatten, widen, ripple round the rim
        flat = max(0.0, min(1.2, sq)); wide = 1 + 0.5 * flat if sq >= 0 else 1 + 0.25 * sq; tall = 1 - 0.62 * flat if sq >= 0 else 1 - 0.3 * sq
        for v in b.data.vertices:
            x, y, z = v.co; r = math.hypot(x, y) / 0.8; th = math.atan2(y, x)
            v.co = Vector((x * wide, y * wide, z * tall + rip * r * r * math.sin(5 * th + ph) + 0.03 * flat * (z < 0) * r))
        b.location = (0, 0, ctr)
    parts = [b] + coin_heart(0, b.location.z, 0, tall if kind == 'goo' else 1.0)
    for hip, kn, ft, fs in legs:
        parts.append(tube('leg', [tuple(hip), tuple(kn), tuple(ft)], [0.09, 0.085, 0.08], limb))
        d = (ft - kn).normalized(); w_ = min(1.0, (fs - Vector((1.5, 0.9, 0.6))).length / 0.5); f = uv_sphere('foot', 0.13, tuple(ft + Vector((0.07, 0, -0.02)).lerp(d * 0.07, w_)), tuple(fs), 32, 16); f.data.materials.append(limb); parts.append(f)  # at rest: the same foot as o_runner
    for sh, hd in arms:
        parts.append(tube('arm', [tuple(sh), tuple(sh.lerp(hd, 0.5)), tuple(hd)], [0.07, 0.065, 0.06], limb))
        h_ = uv_sphere('hand', 0.1, tuple(hd), seg=24, rings=12); h_.data.materials.append(limb); parts.append(h_)
    if kind == 'goo' and sq > 0:  # tip the pancake's top toward the camera so its face and splayed limbs read
        tilt = link(bpy.data.objects.new('tilt', None)); tilt.location = (0, 0, ctr); bpy.context.view_layer.update()
        for o in parts:
            mw = o.matrix_world.copy(); o.parent = tilt; o.matrix_world = mw
        tilt.rotation_euler = (math.radians(42) * min(1.0, sq) * (0.6 if i >= 2 * n4 else 1), 0, 0); bpy.context.view_layer.update(); parts = [tilt]
    gs = 1 - 0.15 * max(0.0, min(1.0, sq)); fz = ctr + 0.12 * max(0.0, min(1.0, sq)) + 0.05 * (1 - max(0.0, min(1.0, sq))) if kind == 'goo' else 0.3
    fc = face([b], 0, fz, 0.95 * gs)
    hub = link(bpy.data.objects.new('turn', None)); hub.rotation_mode = 'QUATERNION'; bpy.context.view_layer.update()
    for o in parts + fc:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.rotation_quaternion = Euler((0, lean, yaw)).to_quaternion() @ rot
    return [hub], []

DANCE_N = 54   # 0.9 s loop at 60 fps

def o_dance(frame, n=DANCE_N):
    """game-over dance, a seamless loop: facing the camera, feet planted, the body sways side to side and dips
    into a crouch at each side while the arms pump up and down in turn"""
    body, limb = runner_mats()
    ph = 2 * math.pi * frame / n; sw = math.sin(ph)
    bob = -0.05 + 0.05 * math.cos(2 * ph)          # 0 in the middle, lowest (crouched) at each side
    up = link(bpy.data.objects.new('upper', None)); up.location = (0.17 * sw, 0, bob)
    b = uv_sphere('rb', 0.8, (0.17 * sw, 0, 0.25 + bob), seg=64, rings=32); b.data.materials.append(body)
    fc = face([b], 0.17 * sw, 0.3 + bob, 0.95)
    parts = [b] + coin_heart(0.17 * sw, 0.25 + bob, 0.3 * sw)
    for side in (-1, 1):  # arms: one rises while the other falls
        bA = math.radians(35 + 120 * (0.5 + 0.5 * sw * side)); sh = Vector((side * 0.74 + 0.17 * sw, 0.05, 0.12 + bob))
        hand = sh + Vector((side * math.sin(bA) * 0.42, -0.06, -math.cos(bA) * 0.42))
        parts.append(tube('arm', [tuple(sh), tuple(sh.lerp(hand, 0.5)), tuple(hand)], [0.07, 0.065, 0.06], limb))
        hd = uv_sphere('hand', 0.1, tuple(hand), seg=24, rings=12); hd.data.materials.append(limb); parts.append(hd)
    bpy.context.view_layer.update()
    for o in parts + fc:  # the upper body tilts into the sway
        mw = o.matrix_world.copy(); o.parent = up; o.matrix_world = mw
    up.rotation_euler = (0, math.radians(-10 * sw), 0); bpy.context.view_layer.update()
    legs = []
    for side in (-1, 1):  # feet stay planted; legs bend to follow the hips
        hip = up.matrix_world @ (Vector((side * 0.28 + 0.17 * sw, 0, -0.42 + bob)) - up.location)
        foot = Vector((side * 0.34, 0, -1.02)); knee = hip.lerp(foot, 0.5) + Vector((side * (0.08 - 3 * bob), -0.06, 0))
        legs.append(tube('leg', [tuple(hip), tuple(knee), tuple(foot)], [0.09, 0.085, 0.08], limb))
        f = uv_sphere('foot', 0.13, tuple(foot + Vector((0, -0.07, -0.02))), (0.9, 1.5, 0.6), 32, 16); f.data.materials.append(limb); legs.append(f)
    return [up] + legs, []

def o_heart():
    """a glossy pink heart, front-facing: two lobes and a point, solidified and rounded"""
    import bmesh
    pts = []
    for a in range(0, 360, 6):  # classic heart curve
        t = math.radians(a); x = 16 * math.sin(t) ** 3; z = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 17, z / 17))
    me = bpy.data.meshes.new('heart'); bm = bmesh.new(); vs = [bm.verts.new((x, 0, z)) for x, z in pts]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new('heart', me))
    o.data.materials.append(principled('heart', (0.85, 0.01, 0.2), 0.12, coat=1.0, coat_rough=0.02, emit=(1.0, 0.1, 0.35), emit_str=0.12))
    bpy.context.view_layer.objects.active = o; bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.poke(); bpy.ops.mesh.subdivide(number_cuts=3); bpy.ops.object.mode_set(mode='OBJECT')   # grid the flat face so it can bulge
    so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.3; so.offset = 0
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = 2; sub.render_levels = 2
    cast = o.modifiers.new('puff', 'CAST'); cast.cast_type = 'SPHERE'; cast.factor = 0.55; cast.use_x = False; cast.use_z = False   # inflate front and back
    o.rotation_euler = (0, math.radians(-12), math.radians(16))  # turned a little so the puff and gloss read
    return [o], []

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
    if GLASS: glass_on()
    face_ = slab(0.84, 0.3, glass_grad('shg', (0.55, 0.75, 1.0), (0.92, 0.97, 1.0), trans=0.85, emit=0.2) if GLASS else principled('plat', (0.86, 0.87, 0.9), 0.25, metallic=0.9, coat=0.6), -0.04)
    return [rim, face_], face([face_], 0, 0.05, 0.85)

def o_pu_magnet():
    """power-up: a chunky horseshoe magnet, bronze with platinum poles, with a face on the bend"""
    if GLASS: glass_on()
    mb = glass_grad('mag', (0.05, 0.25, 0.85), (0.35, 0.7, 1.0), trans=0.75, emit=0.3, axis='Z', k=0.9) if GLASS else principled('mag', smiley.PAL['bronze'], 0.3, coat=0.9, coat_rough=0.04); tip = principled('pole', (0.86, 0.87, 0.9), 0.22, metallic=1.0)
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

def o_dividend():
    """DIVIDEND power-up: a little money plant (your money grows) — a glass pot, a green glass stem, gold coin leaves, a face on the pot"""
    glass_on()
    pot_m = glass_grad('pot', (0.55, 0.75, 1.0), (0.92, 0.97, 1.0), trans=0.85, emit=0.2)
    stem_m = principled('stem', (0.1, 0.75, 0.3), 0.15, coat=1.0, emit=(0.1, 0.8, 0.3), emit_str=0.4)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.42, radius2=0.58, depth=0.7, location=(0, 0, -0.55)); pot = bpy.context.active_object
    pot.data.materials.append(pot_m); pot = bevel(pot, 0.04, 3); smooth(pot)
    soil = cyl(gold(), (0, 0, -0.22), 0.52, 0.06, bv=0.02)
    stem = tube('stem', [(0, 0, -0.2), (0.05, 0, 0.25), (-0.04, 0, 0.6), (0, 0, 0.85)], [0.06, 0.055, 0.05, 0.045], stem_m)
    parts = [pot, soil, stem]
    for (x, z, ry) in ((0.36, 0.38, 35), (-0.36, 0.62, -35), (0.0, 1.05, 0)):  # coin leaves, tilted toward the camera
        parts.append(cyl(gold(), (x, -0.05, z), 0.24, 0.06, (math.radians(80), math.radians(ry), 0), 48, 0.02))
    return parts, face([pot], 0, -0.55, 0.5)

def o_hero(i, n=24):
    """site hero: a rising glass candle chart, the gold glass runner leaping over it, the diamond bull at the top.
    Frame i of n turns the whole scene from -20 to +20 degrees (the page scrubs it on scroll)."""
    parts = []
    def place(objs, loc, s=1.0, rz=None):
        hub = link(bpy.data.objects.new('place', None)); bpy.context.view_layer.update()
        for o in objs:
            mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
        hub.location = loc; hub.scale = (s, s, s)
        if rz is not None: hub.rotation_euler = (0, 0, rz)
        parts.append(hub)
    # candles: x, height level, red?
    C = [(-2.6, -0.9, False), (-1.9, -0.55, True), (-1.2, -0.45, False), (-0.5, 0.0, False), (0.2, -0.1, True), (0.9, 0.45, False), (1.6, 0.9, False)]
    for k, (x, z, red) in enumerate(C):
        objs, fc = o_tick(1 if red else (3 if k == len(C) - 1 else 2), red)
        for o in objs: o.rotation_euler = (0, 0, 0)
        place(objs + fc, (x, 0.0, z - 0.6), 0.62)
    r, rf = o_runner('rise', 2); place(r + rf, (-0.45, -0.35, 1.05), 0.7, math.radians(-12))
    bl, _ = o_bull(0); bl[0].rotation_euler = (math.radians(8), 0, math.radians(-35)); place(bl, (2.6, 0.35, 0.95), 0.82)
    root = link(bpy.data.objects.new('hero', None)); bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy(); o.parent = root; o.matrix_world = mw
    root.scale = (0.62, 0.62, 0.62); root.location = (0, 0, -0.05)
    root.rotation_euler = (0, 0, math.radians(-20 + 40 * i / (n - 1)))
    return [root], []

def o_logo3d():
    """the throwindice mark in 3D (app icon / share image): a smoked-glass price-tag bracket with its hole,
    and a gold honey-glass die (two pips) tumbling into it. Mark units: the 100 x 76 SVG viewBox."""
    glass_on()
    M = lambda x, y, d=0.0: ((x - 50) / 30, d, (38 - y) / 30)
    ink = principled('ink', (0.035, 0.035, 0.04), 0.12, coat=1.0, coat_rough=0.02)
    br = [(58, 8), (16, 8), (11, 8), (9, 10), (9, 14), (9, 52), (9, 56), (11, 58), (16, 58), (58, 58)]
    tag = tube('tag', [M(x, y) for x, y in br], [0.115] * len(br), ink, res=32)
    hole = uv_sphere('hole', 0.16, M(20, 38)); hole.data.materials.append(ink)
    die_m = glass_grad('die', (0.5, 0.26, 0.02), (1.0, 0.68, 0.16), trans=0.38, emit=0.3, axis='Z', k=0.8)
    hub = link(bpy.data.objects.new('diehub', None)); hub.location = M(62, 36, -0.15)
    d = box('die', die_m, (0, 0, 0), (1.4, 1.4, 1.4), bv=0.36)
    pip_m = principled('pip', (1.0, 0.98, 0.94), 0.25, coat=1.0, emit=(1, 0.97, 0.9), emit_str=0.25)
    pips = []
    for (px, pz) in ((-0.3, 0.3), (0.3, -0.3)):
        s = uv_sphere('pip', 0.16, (px, -0.66, pz), (1, 0.45, 1)); s.data.materials.append(pip_m); pips.append(s)
    for o in [d] + pips: o.parent = hub
    hub.rotation_euler = (math.radians(14), math.radians(45), math.radians(-18))
    return [tag, hole, hub], []

def o_bull(i, n=96):
    """checkpoint: a faceted, see-through diamond bull, turning slowly (frame i of n, one full turn)"""
    bpy.context.scene.render.film_transparent = True
    try: bpy.context.scene.cycles.film_transparent_glass = True
    except Exception: pass
    dia = principled('diamond', (0.82, 0.93, 1.0), 0.0, coat=1.0, coat_rough=0.0, emit=(0.55, 0.85, 1.0), emit_str=0.25)
    bsdf = dia.node_tree.nodes['Principled BSDF']; bsdf.inputs['Transmission Weight'].default_value = 0.85; bsdf.inputs['IOR'].default_value = 2.4
    def gem(name, loc, scale, rot=(0, 0, 0)):  # low-poly flat-shaded ico = diamond facets
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc, rotation=rot); o = bpy.context.active_object
        o.name = name; o.scale = scale; o.data.materials.append(dia); return o
    def cone(loc, rot, r1, r2, d, v=6):
        bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot); o = bpy.context.active_object
        o.data.materials.append(dia); return o
    parts = [gem('body', (0, 0, 0), (1.05, 0.58, 0.55)), gem('hump', (0.35, 0, 0.22), (0.5, 0.48, 0.42)),
             gem('head', (1.08, 0, 0.22), (0.38, 0.34, 0.36), (0, math.radians(20), 0)), gem('snout', (1.36, 0, 0.08), (0.2, 0.24, 0.19))]
    for x, y in ((0.62, 0.28), (0.62, -0.28), (-0.62, 0.28), (-0.62, -0.28)): parts.append(cone((x, y, -0.62), (0, 0, 0), 0.12, 0.17, 0.75))
    for sd in (-1, 1): parts.append(cone((1.0, sd * 0.42, 0.52), (sd * math.radians(-55), math.radians(-15), 0), 0.09, 0.03, 0.55))  # horns
    parts.append(cone((-1.12, 0, 0.0), (0, math.radians(-125), 0), 0.05, 0.01, 0.6, 5))  # tail
    hub = link(bpy.data.objects.new('turn', None)); bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.scale = (0.8, 0.8, 0.8); hub.rotation_euler = (math.radians(8), 0, 2 * math.pi * i / n)
    return [hub], []

def o_dolla():
    """the Dolla: the game's currency note (Washington-bill layout with a smiley portrait; texture from dolla_texture.py), gently curled"""
    tex = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dolla_tex.png')
    m = bpy.data.materials.new('dolla'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(tex); hs = nt.nodes.new('ShaderNodeHueSaturation'); hs.inputs['Value'].default_value = 0.42; hs.inputs['Saturation'].default_value = 1.25
    nt.links.new(t.outputs['Color'], hs.inputs['Color']); nt.links.new(hs.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.55; b.inputs['Coat Weight'].default_value = 0.25
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); o = bpy.context.active_object; o.scale = (3.3, 1.4, 1)
    bpy.ops.object.transform_apply(scale=True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=24); bpy.ops.object.mode_set(mode='OBJECT')
    for v in o.data.vertices: v.co.z += 0.12 * math.sin(v.co.x * 1.6) + 0.05 * v.co.y * v.co.x   # a gentle S-curl
    so = o.modifiers.new('th', 'SOLIDIFY'); so.thickness = 0.012; o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); o.rotation_euler = (math.radians(78), 0, math.radians(-6)); return [o], []

def o_bill():
    """a single green banknote with a dark seal, slightly tilted, for the cash trail"""
    note = plastic('note', (0.05, 0.42, 0.12), 0.45); ink_ = plastic('ink', (0.02, 0.2, 0.05), 0.5)
    b = box('bill', note, (0, 0, 0), (1.6, 0.02, 0.75), (0, math.radians(8), math.radians(-25)), bv=0.01)
    c = uv_sphere('seal', 0.18, (0, -0.02, 0), (1, 0.12, 1)); c.data.materials.append(ink_); c.rotation_euler = (0, math.radians(8), math.radians(-25))
    return [b, c], []

def o_tick(tier=1, red=False):
    """currency: a glossy candle. green = +1/+3/+10% (tier 1-3, bigger and brighter), red = -2/-5% (tier 1-2, a down-candle)"""
    c = (0.9, 0.08, 0.12) if red else (0.05, 0.8, 0.3)
    k = [0, 0.8, 1.0, 1.2][tier]
    if GLASS:  # clear tinted glass shell, a bright core bar inside
        glass_on(); m = glass_grad('tick', tuple(0.45 * x for x in c), tuple(min(1, 0.35 + x) for x in c), trans=0.8, emit=0.25, axis='Z', k=0.6)
        core = principled('core', c, 0.2, emit=c, emit_str=1.2 + 0.5 * tier)
        body = box('body', m, (0, 0, 0), (0.62 * k, 0.62 * k, 1.15 * k), bv=0.14 * k)
        wick = tube('wick', [(0, 0, -1.0 * k), (0, 0, 1.0 * k)], [0.05 * k, 0.05 * k], core)
        parts = [body, wick, box('corebar', core, (0, 0, 0), (0.26 * k, 0.26 * k, 0.8 * k), bv=0.08 * k)]
    else:
        m = principled('tick', c, 0.12, coat=1.0, coat_rough=0.02, emit=c, emit_str=0.25 + 0.2 * tier)
        m.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.35
        body = box('body', m, (0, 0, 0), (0.62 * k, 0.62 * k, 1.15 * k), bv=0.12 * k)
        wick = tube('wick', [(0, 0, -1.0 * k), (0, 0, 1.0 * k)], [0.06 * k, 0.06 * k], m)
        parts = [body, wick]
    if tier == 3 and not red:  # the big one: a gold band and a sparkle
        parts.append(box('band', gold(), (0, 0, 0.3 * k), (0.66 * k, 0.66 * k, 0.12 * k), bv=0.03))
        star = prim('ico_sphere', principled('spark', (1, 1, 0.9), 0.1, emit=(1, 0.95, 0.7), emit_str=3.0), (0.32 * k, -0.3, 1.0 * k), subdivisions=1, radius=0.12)
        star.scale = (0.4, 0.4, 1.6); parts.append(star)
    fc = face([body], 0, 0.05, 0.62 * k)
    hub = link(bpy.data.objects.new('turn', None)); bpy.context.view_layer.update()
    for o in parts + fc:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.rotation_euler = (0, math.radians(10 if red else -10), math.radians(25)); return [hub], []

def _rug_mat():
    """a woven crypto rug: purple base with cyan/pink stripes (wave texture, so it reads as woven)"""
    m = principled('rug', (0.3, 0.08, 0.6), 0.75); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    w = nt.nodes.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value = 3.0; w.inputs['Distortion'].default_value = 1.5
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (0.32, 0.06, 0.62, 1); r.color_ramp.elements[1].color = (0.1, 0.85, 1.0, 1)
    e = r.color_ramp.elements.new(0.7); e.color = (1.0, 0.25, 0.65, 1)
    nt.links.new(w.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color']); return m

def o_rug(rolled=False):
    """rugpull: a flat crypto rug strip tipped toward the camera (tile), or the same rug half rolled up as it gets yanked"""
    m = _rug_mat(); fr = plastic('fringe', (0.95, 0.9, 0.75), 0.6); parts = []
    if rolled:
        parts.append(prim('cylinder', m, (0.55, 0, 0.22), (math.radians(90), 0, 0), vertices=48, radius=0.32, depth=1.3))
        parts.append(box('flat', m, (-0.45, 0, -0.08), (1.6, 1.3, 0.05), (0, math.radians(-8), 0), bv=0.01))
        for y in [i * 0.13 - 0.585 for i in range(10)]: parts.append(box('tassel', fr, (-1.3, y, -0.12), (0.18, 0.03, 0.02), bv=0))
    else:
        parts.append(box('flat', m, (0, 0, 0), (2.8, 1.3, 0.06), bv=0.01))
        for x in (-1.45, 1.45):
            for y in [i * 0.13 - 0.585 for i in range(10)]: parts.append(box('tassel', fr, (x, y, 0), (0.18, 0.03, 0.02), bv=0))
    hub = link(bpy.data.objects.new('tilt', None)); bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.rotation_euler = (math.radians(30), 0, 0); return [hub], []

def o_rocket():
    """a pump token: a chunky cartoon rocket with a coin porthole and a flame"""
    body = principled('rkt', (0.92, 0.92, 0.96), 0.2, coat=1.0); red = plastic('fin', (0.9, 0.12, 0.25), 0.25)
    fl = principled('flame', (1.0, 0.55, 0.1), 0.5, emit=(1.0, 0.5, 0.08), emit_str=6.0)
    hull = uv_sphere('hull', 0.42, (0, 0, 0), (1, 1, 2.1)); hull.data.materials.append(body)
    nose = prim('cone', red, (0, 0, 0.95), vertices=32, radius1=0.3, radius2=0.0, depth=0.4)
    port = prim('cylinder', gold(), (0, -0.38, 0.2), (math.radians(90), 0, 0), vertices=32, radius=0.17, depth=0.08)
    parts = [hull, nose, port]
    for a in (0, 120, 240):
        f = box('fin', red, (0.38 * math.cos(math.radians(a)), 0.38 * math.sin(math.radians(a)), -0.62), (0.32, 0.06, 0.42), (0, 0, math.radians(a)), bv=0.03); parts.append(f)
    fla = uv_sphere('flame', 0.2, (0, 0, -1.05), (1, 1, 2.0)); fla.data.materials.append(fl); parts.append(fla)
    hub = link(bpy.data.objects.new('turn', None)); bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.rotation_euler = (0, math.radians(35), math.radians(20)); return [hub], []

def o_devwallet():
    """rugpull tell: a shady brown wallet with a sly face and sunglasses, a gold 'DEV' tag"""
    global SHADES
    leather = plastic('wallet', (0.16, 0.08, 0.04), 0.4)
    w = box('wallet', leather, (0, 0, 0), (1.5, 0.3, 1.05), bv=0.1)
    flap = box('flap', leather, (0, -0.1, 0.32), (1.52, 0.18, 0.45), (math.radians(-6), 0, 0), bv=0.08)
    bpy.ops.object.text_add(location=(0.42, -0.21, 0.32), rotation=(math.radians(90), 0, 0)); t = bpy.context.active_object
    t.data.body = 'DEV'; t.data.size = 0.22; t.data.extrude = 0.02; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'; t.data.materials.append(gold())
    SHADES = True; fc = face([w], -0.1, -0.05, 0.85); SHADES = os.environ.get('RUNNER_PROP') == 'shades'
    return [w, flap, t], fc

def o_sign100x():
    """pump tell: a neon '100x' sign"""
    neon = principled('neon', (1.0, 0.2, 0.7), 0.3, emit=(1.0, 0.15, 0.65), emit_str=1.4)
    bpy.ops.object.text_add(location=(0, 0, 0), rotation=(math.radians(90), 0, 0)); t = bpy.context.active_object
    t.data.body = '100x'; t.data.size = 0.9; t.data.extrude = 0.08; t.data.bevel_depth = 0.02; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    t.data.materials.append(neon); t.rotation_euler = (math.radians(90), 0, math.radians(-12)); return [t], []

def o_bear(i=-1, n=96):
    """bear market: a faceted ruby bear, the bull's counterpart. i >= 0: frame i of n of one slow turn (the bear-market checkpoint); i < 0: the static icon"""
    bpy.context.scene.render.film_transparent = True
    try: bpy.context.scene.cycles.film_transparent_glass = True
    except Exception: pass
    ruby = principled('ruby', (1.0, 0.3, 0.35), 0.0, coat=1.0, emit=(0.9, 0.1, 0.2), emit_str=0.3)
    b_ = ruby.node_tree.nodes['Principled BSDF']; b_.inputs['Transmission Weight'].default_value = 0.85; b_.inputs['IOR'].default_value = 1.77
    def gem(loc, sc):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc); o = bpy.context.active_object; o.scale = sc; o.data.materials.append(ruby); return o
    parts = [gem((0, 0, 0), (1.0, 0.62, 0.62)), gem((0.95, 0, 0.25), (0.45, 0.42, 0.42)), gem((1.3, 0, 0.15), (0.18, 0.2, 0.16)),
             gem((0.85, -0.25, 0.62), (0.13, 0.08, 0.13)), gem((0.85, 0.25, 0.62), (0.13, 0.08, 0.13))]
    for x, y in ((0.55, 0.3), (0.55, -0.3), (-0.55, 0.3), (-0.55, -0.3)):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.2, radius2=0.22, depth=0.6, location=(x, y, -0.62)); o = bpy.context.active_object; o.data.materials.append(ruby); parts.append(o)
    hub = link(bpy.data.objects.new('turn', None)); bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
    hub.scale = (0.8, 0.8, 0.8); hub.rotation_euler = (math.radians(8), 0, 2 * math.pi * i / n if i >= 0 else math.radians(-30)); return [hub], []

# ---------- ALL IN: the skateboard ----------
SKATE_PITCH = (-30, -15, 0, 15, 30)   # ride frames are rendered per terrain slope (deg, + = uphill to the right)
SKATE_SEQ = {'ollie': 12, 'kick': 16, 'shove': 20, 'tre': 20, 'indy': 20, 'jesus': 20}   # doubled for smooth playback
SKATE_RIDE_N = 12

def skateboard():
    """deck with kicktails, black grip, green underside, silver trucks, cream wheels; built along +x, wheels touching z = -0.95"""
    grip = plastic('grip', (0.03, 0.03, 0.035), 0.9); under = principled('deck', (0.05, 0.75, 0.3), 0.25, coat=1.0)
    metal = principled('truck', (0.75, 0.77, 0.8), 0.25, metallic=1.0); wheel = plastic('wheel', (0.96, 0.9, 0.72), 0.35)
    z = -0.69; ps = [box('deck', under, (0, 0, z), (1.25, 0.44, 0.05), bv=0.02), box('gripc', grip, (0, 0, z + 0.03), (1.22, 0.42, 0.012), bv=0.005)]
    for sx in (-1, 1):  # kicktails
        t = box('tail', under, (sx * 0.78, 0, z + 0.06), (0.36, 0.44, 0.05), (0, sx * math.radians(-20), 0), bv=0.02); ps.append(t)
        t2 = box('gript', grip, (sx * 0.775, 0, z + 0.088), (0.34, 0.42, 0.012), (0, sx * math.radians(-20), 0), bv=0.005); ps.append(t2)
        ps.append(box('truck', metal, (sx * 0.45, 0, z - 0.09), (0.12, 0.5, 0.08), bv=0.02))
        for sy in (-1, 1): ps.append(prim('cylinder', wheel, (sx * 0.45, sy * 0.27, -0.85), (math.radians(90), 0, 0), vertices=24, radius=0.1, depth=0.09))
    return ps

def o_skate(kind, i):
    """ALL IN rider. kind 'ride-<pitch>': 4-frame crouch loop on a slope; else a trick sequence (frames 0 and n-1 = the flat ride pose).
    ollie: pop the tail, board rises with tucked legs, land. kick: the board rolls 360 under tucked feet. shove: the board spins 360 flat.
    tre: spin + roll (360 flip). indy: knees up, back hand grabs the toe edge. jesus: board in the right (front) hand, arms out wide like a cross, legs together."""
    body, limb = runner_mats(); pitch = 0.0; n = 4
    if kind.startswith('ride'):
        pitch = float(kind.split('_')[1]); n = SKATE_RIDE_N; ph = 2 * math.pi * i / n; crouch = 0.5 + 0.18 * math.sin(ph); u = 0.0
    else:
        n = SKATE_SEQ[kind]; u = i / (n - 1); crouch = 0.5; ph = 0.0
    env = math.sin(math.pi * u)                       # 0 at both ends: tricks start and end on the ride pose
    e = _ss(0, 1, u); hold = _ss(0, 0.3, u) * (1 - _ss(0.7, 1, u))
    lift, tuck = 0.0, 0.0                              # body rise above the board, feet off the deck
    bd = dict(dx=0.0, dz=0.0, roll=0.0, yaw=0.0, pit=0.0)
    arms = [Vector((-0.98, -0.05, -0.05)), Vector((0.98, -0.05, -0.05))]   # balancing, slightly down
    grab = None; legs_together = 0.0
    if kind == 'ollie':
        crouch = _keys([1.0, 0.25, 0.55, 0.6, 0.4, 0.75], u); bd['pit'] = _keys([0, 24, 8, 0, -4, 0], u); bd['dz'] = _keys([0, 0.05, 0.2, 0.22, 0.1, 0], u)
        lift = _keys([0, 0.12, 0.25, 0.26, 0.12, 0], u); bd['dx'] = _keys([0, -0.05, 0, 0, 0, 0], u)
    elif kind in ('kick', 'shove', 'tre'):
        tuck = env; lift = 0.28 * env; bd['dz'] = 0.36 * env; crouch = 0.5 + 0.3 * env   # the board rises with the tucked feet
        if kind in ('kick', 'tre'): bd['roll'] = 360 * e
        if kind in ('shove', 'tre'): bd['yaw'] = 360 * e * (-1 if kind == 'shove' else 1)
    elif kind == 'indy':
        tuck = 0.0; lift = 0.34 * env; bd['dz'] = 0.6 * env; crouch = 0.5 + 0.5 * env; bd['pit'] = 26 * hold   # knees to the chest, nose tipped up
        grab = (-1, hold)                              # back hand to the toe edge
    elif kind == 'jesus':
        lift = 0.3 * env; crouch = 0.5 - 0.5 * hold; legs_together = hold; grab = (1, hold)
    bob = 0.55 - 0.16 * crouch + lift
    # body (ball, face, arms) in its own hub, pitched a third as much as the board so it stays balanced over it
    b = uv_sphere('rb', 0.8, (0, 0, bob), seg=64, rings=32); b.data.materials.append(body); bparts = [b] + coin_heart(0, bob, 0.2)
    for k_, side in enumerate((-1, 1)):
        sh = Vector((side * 0.74, 0.05, bob - 0.13)); tgt = sh + arms[k_] * 0.5
        if kind == 'jesus': tgt = sh.lerp(Vector((side * 1.55, -0.05, bob - 0.08)), hold) if True else tgt   # arms straight out, cross
        if grab and grab[0] == side and kind == 'indy': tgt = tgt.lerp(Vector((0.05, -0.32, -0.62 + bd['dz'] + 0.05)), grab[1])
        bparts.append(tube('arm', [tuple(sh), tuple(sh.lerp(tgt, 0.5) + Vector((0, 0, 0.03))), tuple(tgt)], [0.07, 0.065, 0.06], limb))
        h_ = uv_sphere('hand', 0.1, tuple(tgt), seg=24, rings=12); h_.data.materials.append(limb); bparts.append(h_)
    fc = face([b], 0, bob + 0.05, 0.98)
    bodyhub = link(bpy.data.objects.new('bodyhub', None)); bodyhub.location = (0, 0, -0.95); bpy.context.view_layer.update()
    for o in bparts + fc:
        mw = o.matrix_world.copy(); o.parent = bodyhub; o.matrix_world = mw
    yaw = math.radians(20)
    bodyhub.rotation_euler = (0, math.radians(-pitch * 0.35), yaw)
    # board in its own hub, pivoting at the ground contact under its centre
    bparts2 = skateboard(); boardhub = link(bpy.data.objects.new('boardhub', None)); boardhub.location = (0, 0, -0.95); bpy.context.view_layer.update()
    for o in bparts2:
        mw = o.matrix_world.copy(); o.parent = boardhub; o.matrix_world = mw
    boardhub.rotation_mode = 'QUATERNION'; bpy.context.view_layer.update()
    held = kind == 'jesus' and hold > 0.02
    if held:  # the board hangs vertically from the right (front) hand, wheels toward the camera-right
        hand = (bodyhub.matrix_world @ Vector((0, 0, 0.95)).to_4d()).to_3d() if False else None
        hw = bodyhub.matrix_world @ (Vector((1.55, -0.05, bob - 0.08 + 0.95)) * 1)
        q = Euler((0, 0, yaw)).to_quaternion() @ Quaternion(Vector((0, 1, 0)), math.radians(-90 * hold)) @ Quaternion(Vector((1, 0, 0)), math.radians(-25 * hold))
        rest = Vector((0, 0, -0.95)) + Vector((bd['dx'], 0, bd['dz']))
        boardhub.location = tuple(rest.lerp(hw + Vector((0.25, -0.1, -0.15)), hold))
        boardhub.rotation_quaternion = q
    else:
        boardhub.location = (bd['dx'], 0, -0.95 + bd['dz'])
        boardhub.rotation_quaternion = Euler((0, 0, yaw)).to_quaternion() @ Quaternion(Vector((0, 1, 0)), math.radians(-pitch - bd['pit'])) \
            @ Quaternion(Vector((0, 0, 1)), math.radians(bd['yaw'])) @ Quaternion(Vector((1, 0, 0)), math.radians(bd['roll']))
    bpy.context.view_layer.update()
    # legs, built in world space: hips from the body hub to feet on the deck (or tucked up while the board flips / is held)
    parts = [bodyhub, boardhub]
    for side in (-1, 1):
        hip = bodyhub.matrix_world @ Vector((side * 0.24, 0, bob - 0.6 + 0.95))
        on = boardhub.matrix_world @ Vector((side * 0.38, 0.0, 0.32))         # deck top, above the trucks (hub sits at the wheels)
        if held or legs_together > 0:
            free = hip + Vector((side * 0.06, 0, -0.62)); ft = on.lerp(free, legs_together if held else 0)
        else:
            tk = hip + Vector((side * 0.32, -0.05, -0.22)); ft = on.lerp(tk, tuck) if tuck else on
        kn = hip.lerp(ft, 0.5) + Vector((side * 0.12 * (1 - legs_together), -0.14 * (1 - legs_together), 0.05 * (crouch + tuck)))
        parts.append(tube('leg', [tuple(hip), tuple(kn), tuple(ft)], [0.09, 0.085, 0.08], limb))
        f = uv_sphere('foot', 0.13, tuple(ft + Vector((0.04, 0, 0.03))), (1.4, 0.9, 0.6), 32, 16); f.data.materials.append(limb); parts.append(f)
    return parts, []

def o_hat(kind):
    """purchasable hats, built with the brim/base at the origin (the head anchor) and rendered alone at the runner's scale.
    top: Wall Street top hat (black silk, green dollar band); crown: gold bull-market crown with gems; prop: propeller beanie"""
    a = link(bpy.data.objects.new('eyeanchor0', None)); a.location = (0, 0, 0); ps = []
    if kind == 'top':
        silk = principled('silk', (0.02, 0.02, 0.025), 0.25, coat=1.0, coat_rough=0.1); band = plastic('band', (0.05, 0.6, 0.25), 0.35)
        ps += [prim('cylinder', silk, (0, 0, 0.03), vertices=48, radius=0.72, depth=0.06), prim('cylinder', silk, (0, 0, 0.45), vertices=48, radius=0.46, depth=0.8),
               prim('cylinder', band, (0, 0, 0.16), vertices=48, radius=0.475, depth=0.16)]
        bpy.ops.object.text_add(location=(0, -0.47, 0.16), rotation=(math.radians(90), 0, 0)); t = bpy.context.active_object
        t.data.body = '$'; t.data.size = 0.2; t.data.extrude = 0.02; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'; t.data.materials.append(gold()); ps.append(t)
    elif kind == 'crown':
        g_ = gold(); ps.append(prim('cylinder', g_, (0, 0, 0.12), vertices=64, radius=0.55, depth=0.24))
        for k in range(8):
            ang = 2 * math.pi * k / 8
            ps.append(prim('cone', g_, (0.5 * math.cos(ang), 0.5 * math.sin(ang), 0.42), vertices=4, radius1=0.16, radius2=0.0, depth=0.42))
            gem = principled('gem', [(0.1, 0.9, 0.4), (0.9, 0.1, 0.2), (0.2, 0.5, 1.0)][k % 3], 0.05, coat=1.0, emit=[(0.1, 0.9, 0.4), (0.9, 0.1, 0.2), (0.2, 0.5, 1.0)][k % 3], emit_str=0.6)
            ps.append(prim('ico_sphere', gem, (0.56 * math.cos(ang), 0.56 * math.sin(ang), 0.12), subdivisions=1, radius=0.07, shade=False))
    else:
        f1 = plastic('bean1', (0.05, 0.7, 0.3), 0.6); f2 = plastic('bean2', (1.0, 0.35, 0.4), 0.6); stem = plastic('stem', (0.95, 0.85, 0.3), 0.3)
        dome = uv_sphere('dome', 0.62, (0, 0, -0.05), (1, 1, 0.75)); dome.data.materials.append(f1); ps.append(dome)
        bm = bpy.data.objects.get('dome'); ps.append(prim('torus', f2, (0, 0, 0.0), major_radius=0.6, minor_radius=0.07, major_segments=48, minor_segments=12))
        ps.append(prim('cylinder', stem, (0, 0, 0.5), vertices=16, radius=0.035, depth=0.2))
        for k in (0, 1):
            ps.append(box('blade', [f2, stem][k], (0, 0, 0.6), (0.9, 0.16, 0.025), (math.radians(10), 0, math.radians(30 + 90 * k)), bv=0.01))
    return ps + [a], []

OBJECTS = {'coin': (o_coin, -1), **{'trick-%s-%d' % (k, i): ((lambda k=k, i=i: o_trick(k, i)), 0) for k in ('cork', 'spin', 'split', 'goo') for i in range(TRICK_N)}, 'heart': (o_heart, 1), **{'bull-%d' % i: ((lambda i=i: o_bull(i)), 0) for i in range(96)}, **{'bearcp-%d' % i: ((lambda i=i: o_bear(i)), 0) for i in range(96)}, 'dolla': (o_dolla, 0), **{'skate-ride_%d-%d' % (p_, i): ((lambda p_=p_, i=i: o_skate('ride_%d' % p_, i)), 0) for p_ in SKATE_PITCH for i in range(SKATE_RIDE_N)}, **{'skate-%s-%d' % (k, i): ((lambda k=k, i=i: o_skate(k, i)), 0) for k, n_ in SKATE_SEQ.items() for i in range(n_)}, 'hat-top': (lambda: o_hat('top'), 0), 'hat-crown': (lambda: o_hat('crown'), 0), 'hat-prop': (lambda: o_hat('prop'), 0), 'bill': (o_bill, 0), **{'tick-%d' % t: ((lambda t=t: o_tick(t)), 0) for t in (1, 2, 3)}, **{'tick-r%d' % t: ((lambda t=t: o_tick(t, True)), 0) for t in (1, 2)}, 'rug': (o_rug, 0), 'rug-roll': (lambda: o_rug(True), 0), 'rocket': (o_rocket, 0), 'devwallet': (o_devwallet, 0), 'sign-100x': (o_sign100x, 0), 'bear': (o_bear, 0),  **{'dance-%d' % i: ((lambda i=i: o_dance(i)), 0) for i in range(DANCE_N)}, 'pu2-shield': (o_pu_shield, 1), 'pu2-magnet': (o_pu_magnet, 1), 'pu2-x2': (o_pu_x2, 1), 'pu2-dividend': (o_dividend, 1), 'logo3d': (o_logo3d, 0), **{'hero-%d' % i: ((lambda i=i: o_hero(i)), 0) for i in range(24)}, 'star': (o_star, 1), 'star-off': (lambda: o_star(True), 1), 'warn': (o_warn, -1), 'hook': (o_hook, 1), 'moon': (o_moon, -1), 'coin-silver': (lambda: o_coin('silver'), -1), 'coin-bronze': (lambda: o_coin('bronze'), -1),
           **{'runner-%s-%d' % (g, i): ((lambda g=g, i=i: o_runner(g, i)), 0) for g, n in [*[(g, GAIT_N) for g in GAITS], *AIR.items()] for i in range(n)}, 'crypto': (o_crypto, 1), 'notes': (o_notes, -1), 'moneybag': (o_moneybag, 1), 'receipt': (o_receipt, -1),
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
        rb = bpy.data.objects.get('rb')
        if rb is not None:  # hats sit on this: the ball's top pole and its up direction, in render px
            from bpy_extras.object_utils import world_to_camera_view
            sc = bpy.context.scene; bpy.context.view_layer.update(); R_ = sc.render.resolution_x
            zt = max(v.co.z for v in rb.data.vertices if abs(v.co.x) < 0.05 and abs(v.co.y) < 0.05)
            pr = lambda z: world_to_camera_view(sc, sc.camera, rb.matrix_world @ Vector((0, 0, z)))
            a, b_ = pr(zt), pr(zt + 0.4)
            import json; json.dump([round(a.x * R_, 1), round((1 - a.y) * R_, 1), round(b_.x * R_, 1), round((1 - b_.y) * R_, 1)], open(f'{d}/head.json', 'w'))
        anchors = sorted((o for o in bpy.data.objects if o.name.startswith('eyeanchor')), key=lambda o: o.name)
        if anchors:
            from bpy_extras.object_utils import world_to_camera_view
            sc = bpy.context.scene; bpy.context.view_layer.update(); R_ = sc.render.resolution_x
            px = [[round(c.x * R_, 1), round((1 - c.y) * R_, 1)] for c in (world_to_camera_view(sc, sc.camera, a.matrix_world.translation) for a in anchors)]
            import json; json.dump(px, open(f'{d}/eyes.json', 'w'))

if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]
    if which == 'list': print(' '.join(OBJECTS)); sys.exit()
    res = int(sys.argv[3]) if len(sys.argv) > 3 else 192
    samples = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    nfr = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    if len(sys.argv) > 6: FLAGDIR = sys.argv[6]
    names = list(OBJECTS) if which == 'all' else which.split(',')
    for n in names: build(n, out, res, samples, nfr)
