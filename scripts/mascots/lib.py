"""Shared Blender helpers: organic metaball bodies, materials, simple rig with computed skin weights, studio lights."""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix, Euler

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def link(obj):
    bpy.context.scene.collection.objects.link(obj); return obj

def bake(obj, name):
    """Evaluate modifiers / metaball into a plain mesh object."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    new = link(bpy.data.objects.new(name, me))
    new.matrix_world = obj.matrix_world.copy()
    bpy.data.objects.remove(obj)
    return new

def blob(name, elements, res=0.018, voxel=0.011, smooth=6, threshold=0.6):
    """elements: list of (co, radius, (sx,sy,sz), stiffness, negative). Returns a smooth organic mesh."""
    mb = bpy.data.metaballs.new(name + '_mb'); mb.resolution = res; mb.render_resolution = res; mb.threshold = threshold
    for co, r, size, stiff, neg in elements:
        e = mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = r
        e.size_x, e.size_y, e.size_z = size; e.stiffness = stiff; e.use_negative = neg
    o = link(bpy.data.objects.new(name + '_mbo', mb))
    o = bake(o, name)
    m = o.modifiers.new('rm', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = voxel; m.use_smooth_shade = True
    s = o.modifiers.new('sm', 'SMOOTH'); s.iterations = smooth; s.factor = 0.6
    o = bake(o, name)
    for p in o.data.polygons: p.use_smooth = True
    return o

def E(co, r, size=(1, 1, 1), stiff=2.0, neg=False):
    return (co, r, size, stiff, neg)

def chain(a, b, r0, r1, n=6, stiff=2.0, squash=(1, 1, 1)):
    """Metaball 'capsule' from a to b with tapering radius."""
    a, b = Vector(a), Vector(b)
    return [E(tuple(a.lerp(b, i / (n - 1))), r0 + (r1 - r0) * i / (n - 1), squash, stiff) for i in range(n)]

def uv_sphere(name, r, loc, scale=(1, 1, 1), seg=64, rings=32):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = link(bpy.data.objects.new(name, me)); o.location = loc; o.scale = scale; return o

def tube(name, pts, radii, mat=None, res=24):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 8
    cu.use_fill_caps = True; sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, (x, y, z), r in zip(sp.points, pts, radii): p.co = (x, y, z, 1); p.radius = r
    sp.use_endpoint_u = True; sp.order_u = min(4, len(pts)); sp.resolution_u = res
    o = link(bpy.data.objects.new(name, cu))
    o = bake(o, name)
    for p in o.data.polygons: p.use_smooth = True
    if mat: o.data.materials.append(mat)
    return o

def subsurf(o, lv=1):
    m = o.modifiers.new('ss', 'SUBSURF'); m.levels = lv; m.render_levels = lv; return o

# ---------- materials ----------
def principled(name, color, rough=0.5, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    names = {'sss': 'Subsurface Weight', 'sss_radius': 'Subsurface Radius', 'sss_scale': 'Subsurface Scale', 'sheen': 'Sheen Weight',
             'sheen_rough': 'Sheen Roughness', 'sheen_tint': 'Sheen Tint', 'coat': 'Coat Weight', 'coat_rough': 'Coat Roughness',
             'spec': 'Specular IOR Level', 'emit': 'Emission Color', 'emit_str': 'Emission Strength', 'transmission': 'Transmission Weight', 'ior': 'IOR', 'alpha': 'Alpha'}
    for k, v in kw.items():
        inp = b.inputs[names[k]]
        inp.default_value = (*v, 1) if (isinstance(v, tuple) and len(v) == 3 and k in ('sheen_tint', 'emit')) else v
    return m

def fur_bump(mat, scale=600, strength=0.12, stretch=3.0):
    """Fine anisotropic noise bump so short fur reads as fur instead of plastic."""
    nt = mat.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale / stretch)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Detail'].default_value = 8; nz.inputs['Roughness'].default_value = 0.7
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = strength; bp.inputs['Distance'].default_value = 0.002
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return mat

def region_mix(mat, color2, expr):
    """Blend Base Color toward color2 where a smooth object-space mask is high. expr(nt, xyz)->mask socket."""
    nt = mat.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sx.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = b.inputs['Base Color'].default_value[:]; mix.inputs['B'].default_value = (*color2, 1)
    nt.links.new(expr(nt, sx), mix.inputs['Factor']); nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    return mat

def smooth_mask(nt, socket, lo, hi):
    """smoothstep(lo, hi, socket) via Map Range."""
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
    nt.links.new(socket, mr.inputs['Value']); return mr.outputs['Result']

def mult(nt, a, b):
    m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; nt.links.new(a, m.inputs[0]); nt.links.new(b, m.inputs[1]); return m.outputs[0]

def eye_mat(name, iris=(0.12, 0.07, 0.04), r=1.0):
    """Big glossy cartoon eye: dark iris ring around a black pupil under a clear coat."""
    m = principled(name, (0, 0, 0), 0.4, coat=1.0, coat_rough=0.0, spec=0.0)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); g = nt.nodes.new('ShaderNodeTexGradient'); g.gradient_type = 'SPHERICAL'
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (0, 1 / 1.05, 0)  # centre on the eye's front (-Y) in units of eye radius
    mp.inputs['Scale'].default_value = (1 / (1.05 * r),) * 3
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], g.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); r = ramp.color_ramp
    r.elements[0].position = 0.0; r.elements[0].color = (0.004, 0.003, 0.003, 1)
    r.elements[1].position = 0.2; r.elements[1].color = (*iris, 1)
    e = r.elements.new(0.36); e.color = (*[c * 1.8 for c in iris], 1)
    e = r.elements.new(0.42); e.color = (0.006, 0.004, 0.004, 1)
    nt.links.new(g.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    return m

# ---------- rig ----------
def make_rig(bones):
    """bones: list of (name, head, tail, parent). Returns armature object."""
    arm = bpy.data.armatures.new('rig'); ob = link(bpy.data.objects.new('rig', arm))
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.mode_set(mode='EDIT')
    for n, h, t, p in bones:
        eb = arm.edit_bones.new(n); eb.head = h; eb.tail = t
        if p: eb.parent = arm.edit_bones[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in ob.pose.bones: pb.rotation_mode = 'XYZ'
    return ob

def seg_dist(P, a, b, limb=False):
    a, b = np.array(a), np.array(b); ab = b - a
    t = (P - a) @ ab / (ab @ ab); tc = np.clip(t, 0, 1)
    d = np.linalg.norm(P - (a + tc[:, None] * ab), axis=1)
    if limb: d = np.where(t < 0.08, d + 10 * (0.08 - t), d)  # limbs only own what lies past the shoulder/hip joint
    return d

def skin(obj, rig, bones, power=4.0, only=None):
    """Smooth automatic weights from distance to each bone segment (robust replacement for bone-heat)."""
    P = np.array([v.co for v in obj.data.vertices]) @ np.array(obj.matrix_world.to_3x3()).T + np.array(obj.matrix_world.translation)
    names = [b[0] for b in bones if (only is None or b[0] in only)]
    D = np.stack([seg_dist(P, b[1], b[2], b[0].startswith(('arm.', 'leg.'))) for b in bones if b[0] in names], 1) + 1e-4
    W = D ** -power
    W[D > np.sort(D, 1)[:, [2]] + 1e-9] = 0  # at most three nearest bones per vertex
    W /= W.sum(1, keepdims=True)
    for j, n in enumerate(names):
        vg = obj.vertex_groups.new(name=n)
        for i in np.nonzero(W[:, j] > 0.01)[0]: vg.add([int(i)], float(W[i, j]), 'REPLACE')
    m = obj.modifiers.new('arm', 'ARMATURE'); m.object = rig; m.use_deform_preserve_volume = True
    obj.modifiers.move(len(obj.modifiers) - 1, 0)  # deform before fur so the hair follows
    return obj

def attach(obj, rig, bone):
    """Rigidly parent an object to a bone, keeping its world transform."""
    mw = obj.matrix_world.copy(); obj.parent = rig; obj.parent_type = 'BONE'; obj.parent_bone = bone
    bpy.context.view_layer.update(); obj.matrix_world = mw

# ---------- stage ----------
def stage(res=480, samples=48, cam_loc=(0, -7.2, 1.55), target=(0, 0, 1.25), lens=60, ortho=None, exposure=0.45):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = samples; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transparent_max_bounces = 16
    sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.view_settings.exposure = exposure
    sc.render.threads_mode = 'AUTO'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.75, 0.72, 0.85, 1); bg.inputs['Strength'].default_value = 0.12
    cam = link(bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))); sc.camera = cam
    cam.location = cam_loc
    if ortho: cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else: cam.data.lens = lens
    d = Vector(target) - Vector(cam_loc); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    def area(name, loc, energy, size, color=(1, 1, 1)):
        L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size; L.color = color
        o = link(bpy.data.objects.new(name, L)); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
    area('key', (-3.2, -4.5, 5.0), 1700, 1.6, (1.0, 0.97, 0.94))
    area('fill', (4.5, -3.5, 2.2), 300, 4.0, (0.85, 0.88, 1.0))
    area('rim', (2.5, 4.0, 4.0), 1100, 2.0, (0.85, 0.8, 1.0))
    area('rim2', (-3.0, 3.5, 2.5), 350, 2.5, (1.0, 0.9, 0.95))
    area('catch', (cam_loc[0] * 0.8 - 0.6, cam_loc[1] * 0.8, cam_loc[2] + 1.2), 120, 0.5)  # small light for eye catchlights
    return cam

def shadow_catcher():
    bpy.ops.mesh.primitive_plane_add(size=12)
    p = bpy.context.active_object; p.is_shadow_catcher = True; p.visible_glossy = False; return p

def render(path):
    bpy.context.scene.render.filepath = path; bpy.ops.render.render(write_still=True)

# ---------- fur ----------
def hair_mat(name, melanin=0.9, redness=0.3, rough=0.32, color=None, region=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    h = nt.nodes.new('ShaderNodeBsdfHairPrincipled'); h.model = 'CHIANG'
    h.parametrization = 'COLOR' if color else 'MELANIN'
    if color: h.inputs['Color'].default_value = (*color, 1)
    else: h.inputs['Melanin'].default_value = melanin; h.inputs['Melanin Redness'].default_value = redness
    h.inputs['Roughness'].default_value = rough; h.inputs['Radial Roughness'].default_value = 0.45; h.inputs['Coat'].default_value = 0.15
    h.inputs['Random Roughness'].default_value = 0.2
    if 'Random Color' in h.inputs: h.inputs['Random Color'].default_value = 0.08
    nt.links.new(h.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    if region:  # region = (color2, mask_fn) blends hair colour by object-space mask (needs COLOR mode)
        c2, fn = region; tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sx.inputs[0])
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['A'].default_value = (*color, 1); mix.inputs['B'].default_value = (*c2, 1)
        nt.links.new(fn(nt, sx), mix.inputs['Factor']); nt.links.new(mix.outputs['Result'], h.inputs['Color'])
    return m

def fur(obj, mat, count=9000, length=0.035, children=14, clump=0.15, rough=0.004, droop=(0, 0, -0.35), avoid=(), short=(), kink=0.0, radius=0.0035):
    """Particle-hair fur. avoid: [(centre, r)] bald zones (eyes/nose); short: [(centre, r, factor)] shorter fur zones."""
    P = np.array([v.co for v in obj.data.vertices]) @ np.array(obj.matrix_world.to_3x3()).T + np.array(obj.matrix_world.translation)
    dens = np.ones(len(P)); ln = np.ones(len(P))
    for c, r in avoid: d = np.linalg.norm(P - np.array(c), axis=1); dens *= np.clip((d - r) / (0.35 * r), 0, 1)
    for c, r, f in short: d = np.linalg.norm(P - np.array(c), axis=1); ln *= 1 - (1 - f) * np.clip(1 - d / r, 0, 1)
    for nm, w in (('fur_density', dens), ('fur_length', ln)):
        vg = obj.vertex_groups.new(name=nm)
        for i in np.nonzero(w > 0.01)[0]: vg.add([int(i)], float(w[i]), 'REPLACE')
    obj.data.materials.append(mat); slot = len(obj.data.materials)
    obj.modifiers.new('fur', 'PARTICLE_SYSTEM'); ps = obj.particle_systems[-1]; s = ps.settings
    s.type = 'HAIR'; s.count = count; s.hair_length = length; s.use_advanced_hair = True
    s.normal_factor = length; s.object_align_factor = tuple(d * length for d in droop)  # advanced hair: length comes from these
    s.hair_step = 5; s.display_step = 3; s.render_step = 4
    s.material = slot; s.child_type = 'INTERPOLATED'; s.rendered_child_count = children; s.child_percent = 2
    s.clump_factor = clump; s.clump_shape = 0.3; s.roughness_1 = rough; s.roughness_1_size = 1.0; s.roughness_endpoint = rough * 0.6
    s.length_random = 0.35; s.child_length = 1.0
    if kink: s.kink = 'CURL'; s.kink_amplitude = kink; s.kink_frequency = 2
    s.root_radius = 1.0; s.tip_radius = 0.0; s.radius_scale = radius; s.use_close_tip = True
    ps.vertex_group_density = 'fur_density'; ps.vertex_group_length = 'fur_length'
    s.emit_from = 'FACE'; s.use_even_distribution = True; s.distribution = 'JIT'
    return ps

def surf(obj, x, z, y0=-5.0):
    """Front surface y of obj at (x, z), found by casting a ray toward +Y."""
    ok, loc, n, i = obj.ray_cast(obj.matrix_world.inverted() @ Vector((x, y0, z)), Vector((0, 1, 0)))
    return (obj.matrix_world @ loc).y if ok else None

def flap(name, base, tip, normal, w, l, t, mat):
    """Thin rounded flap (ear) from base toward tip, lying flat against a surface with the given normal."""
    o = uv_sphere(name, 1.0, (0, 0, 0)); base, tip, n = Vector(base), Vector(tip), Vector(normal).normalized()
    y = (base - tip).normalized(); z = (n - y * n.dot(y)).normalized(); x = y.cross(z)
    M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = (base + tip) / 2
    me = o.data  # taper toward the tip so it is triangular, not oval
    for v in me.vertices: v.co.x *= 0.55 + 0.45 * (v.co.y + 1) / 2
    me.transform(M @ Matrix.Diagonal((w, l, t, 1)))  # bake transform so fur lengths stay in world units
    o.data.materials.append(mat); return o

def normal_at(obj, x, z, y0=-5.0):
    ok, loc, n, i = obj.ray_cast(obj.matrix_world.inverted() @ Vector((x, y0, z)), Vector((0, 1, 0)))
    return (obj.matrix_world @ loc), (obj.matrix_world.to_3x3() @ n).normalized()
