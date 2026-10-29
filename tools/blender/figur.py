"""Felles byggeklosser for menneskefigurene i Blender (bpy).

Kjøres med Blender som Python-modul (`pip install bpy`). Figuren står på z = 0,
ser mot -Y og er ca. 1,8 m høy. Hver del er en egen mesh som henger på ett bein
i et felles menneskeskjelett (leddet figur, som i askemyr-style-test), så alle
to-beinte units kan dele skjelett og animasjoner.
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

# ---------- scene ----------

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    return sc


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


_mats = {}

def mat(name, hexcol, metal=0.0, rough=0.6, emit=0.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = srgb(hexcol)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = srgb(hexcol)
        b.inputs['Emission Strength'].default_value = emit
    _mats[name] = m
    return m


# ---------- figurdeler ----------

PARTS = []  # (obj, bone)


def _finish(ob, m, bone, smooth=True, bevel=0.0):
    ob.data.materials.append(m)
    if smooth:
        ob.data.polygons.foreach_set('use_smooth', [True] * len(ob.data.polygons))
    if bevel:
        md = ob.modifiers.new('bevel', 'BEVEL')
        md.width = bevel
        md.segments = 2
        md.limit_method = 'ANGLE'
    PARTS.append((ob, bone))
    return ob


def _mesh_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def sphere(name, loc, r, m, bone, scale=(1, 1, 1), seg=16, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    ob = _mesh_obj(name, bm)
    ob.location = loc
    ob.scale = scale
    ob.rotation_euler = rot
    return _finish(ob, m, bone)


def _cut(bm, co, no):
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_inner=True)


def dome(name, loc, r, m, bone, scale=(1, 1, 1), seg=20, keep=(0, 0, 1)):
    """Halvkule (hjelm, skjoldbule, hår): beholder halvdelen mot `keep`."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    _cut(bm, (0, 0, 0), keep)
    ob = _mesh_obj(name, bm)
    ob.location = loc
    ob.scale = scale
    return _finish(ob, m, bone)


def box(name, loc, size, m, bone, bevel=0.012, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    ob = _mesh_obj(name, bm)
    ob.location = loc
    ob.rotation_euler = rot
    return _finish(ob, m, bone, smooth=False, bevel=bevel)


def limb(name, p0, p1, r0, r1, m, bone, seg=14, flat=1.0, bevel=0.0):
    """Avkortet kjegle fra p0 til p1 (armer, bein, skaft, blad)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=d.length)
    for v in bm.verts:
        v.co.y *= flat
    ob = _mesh_obj(name, bm)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = q
    ob.location = (p0 + p1) / 2
    return _finish(ob, m, bone, bevel=bevel)


def shell(name, z0, z1, r0, r1, m, bone, flat=0.75, width=0.17, front=True, seg=28, thick=0.012):
    """Buet stoffpanel (våpenkjole) som følger kroppen: en del av en kjegle,
    bare forsiden (eller baksiden), klippet til bredden `width`."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r0, radius2=r1, depth=z1 - z0)
    for v in bm.verts:
        v.co.y *= flat
    sgn = -1 if front else 1
    _cut(bm, (0, 0, 0), (0, sgn, 0))
    _cut(bm, (width, 0, 0), (-1, 0, 0))
    _cut(bm, (-width, 0, 0), (1, 0, 0))
    ob = _mesh_obj(name, bm)
    ob.location = (0, 0, (z0 + z1) / 2)
    md = ob.modifiers.new('tykk', 'SOLIDIFY')
    md.thickness = thick
    md.offset = 1
    return _finish(ob, m, bone)


def disc(name, loc, r, depth, m, bone, rot=(0, 0, 0), seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth)
    ob = _mesh_obj(name, bm)
    ob.location = loc
    ob.rotation_euler = rot
    return _finish(ob, m, bone, smooth=True, bevel=0.004)


def ring(name, loc, R, r, m, bone, rot=(0, 0, 0), seg=40):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for i in range(seg):
        a = 2 * math.pi * i / seg
        c = Vector((math.cos(a) * R, math.sin(a) * R, 0))
        for j in range(8):
            b = 2 * math.pi * j / 8
            n = Vector((math.cos(a), math.sin(a), 0))
            bm.verts.new(c + n * math.cos(b) * r + Vector((0, 0, math.sin(b) * r)))
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(8):
            a = i * 8 + j
            b = i * 8 + (j + 1) % 8
            c = ((i + 1) % seg) * 8 + (j + 1) % 8
            d = ((i + 1) % seg) * 8 + j
            bm.faces.new((bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]))
    ob = _mesh_obj(name, bm)
    ob.location = loc
    ob.rotation_euler = rot
    return _finish(ob, m, bone)


def stag(prefix, center, s, m, bone, glow=None, rot=(0, 0, 0)):
    """Hjortehodet (folkets emblem), flatt i XZ-planet, ser mot -Y.
    Bygges rundt origo og flyttes/dreies samlet med et tomt objekt."""
    root = bpy.data.objects.new(prefix + '_emb', None)
    bpy.context.collection.objects.link(root)
    obs = []
    obs.append(sphere(prefix + '_hode', (0, 0, -0.01 * s), 0.028 * s, m, bone, scale=(0.75, 0.3, 1.25)))
    obs.append(sphere(prefix + '_mule', (0, 0, -0.045 * s), 0.018 * s, m, bone, scale=(0.8, 0.3, 1.0)))
    for sx in (-1, 1):
        obs.append(sphere(prefix + '_ore%d' % sx, (sx * 0.032 * s, 0, 0.012 * s), 0.014 * s, m, bone,
                          scale=(1.6, 0.3, 0.6), rot=(0, sx * 0.5, 0)))
        a0 = Vector((sx * 0.016 * s, 0, 0.02 * s))
        a1 = Vector((sx * 0.05 * s, 0, 0.075 * s))
        a2 = Vector((sx * 0.06 * s, 0, 0.12 * s))
        obs.append(limb(prefix + '_gevir%da' % sx, a0, a1, 0.006 * s, 0.005 * s, m, bone, seg=6, flat=0.5))
        obs.append(limb(prefix + '_gevir%db' % sx, a1, a2, 0.005 * s, 0.003 * s, m, bone, seg=6, flat=0.5))
        for t, (tx, tz) in enumerate(((0.025, 0.035), (0.03, 0.03))):
            base = a0.lerp(a1, 0.6) if t == 0 else a1.lerp(a2, 0.5)
            tip = base + Vector((-sx * tx * s * 0.3, 0, tz * s))
            obs.append(limb(prefix + '_tind%d%d' % (sx, t), base, tip, 0.004 * s, 0.002 * s, m, bone, seg=6, flat=0.5))
    if glow is not None:
        obs.append(ring(prefix + '_glo', (0, 0.004 * s, 0.01 * s), 0.1 * s, 0.006 * s, glow, bone, rot=(math.pi / 2, 0, 0)))
    for o in obs:
        o.parent = root
    root.location = center
    root.rotation_euler = rot
    return root


# ---------- skjelett ----------

BONES = [
    # navn, hode, hale, forelder
    ('root', (0, 0, 0), (0, 0.0, 0.2), None),
    ('hips', (0, 0, 0.9), (0, 0, 1.02), 'root'),
    ('spine', (0, 0, 1.02), (0, 0, 1.22), 'hips'),
    ('chest', (0, 0, 1.22), (0, 0, 1.42), 'spine'),
    ('neck', (0, 0, 1.42), (0, 0, 1.5), 'chest'),
    ('head', (0, 0, 1.5), (0, 0, 1.78), 'neck'),
]
SH = (0.27, 0.0, 1.37)  # skulder (venstre = +X)
EL = (0.42, 0.02, 1.13)  # albue
WR = (0.53, -0.04, 0.9)  # håndledd
HD = (0.57, -0.07, 0.82)
HIP = (0.1, 0, 0.9)
KN = (0.11, -0.02, 0.5)
AN = (0.11, 0.0, 0.12)
TOE = (0.11, -0.14, 0.04)


def _mx(p):
    return (-p[0], p[1], p[2])


for side, f in (('L', lambda p: p), ('R', _mx)):
    BONES += [
        ('upperarm.' + side, f(SH), f(EL), 'chest'),
        ('forearm.' + side, f(EL), f(WR), 'upperarm.' + side),
        ('hand.' + side, f(WR), f(HD), 'forearm.' + side),
        ('thigh.' + side, f(HIP), f(KN), 'hips'),
        ('shin.' + side, f(KN), f(AN), 'thigh.' + side),
        ('foot.' + side, f(AN), f(TOE), 'shin.' + side),
    ]
JOINT = {b[0]: (Vector(b[1]), Vector(b[2])) for b in BONES}


def build_armature(name='Rig'):
    ad = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, ad)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    for n, h, t, p in BONES:
        b = ad.edit_bones.new(n)
        b.head, b.tail = h, t
        b.roll = 0
        if p:
            b.parent = eb[p]
            b.use_connect = False
        eb[n] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
    return arm


def attach_parts(arm):
    bpy.context.view_layer.update()
    tops = [(o, b) for o, b in PARTS if o.parent is None or o.parent.type != 'EMPTY']
    # emblemer: flytt ut av det tomme objektet først
    for o, b in PARTS:
        if o.parent is not None and o.parent.type == 'EMPTY':
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    bpy.context.view_layer.update()
    for o, b in PARTS:
        mw = o.matrix_world.copy()
        o.parent = arm
        o.parent_type = 'BONE'
        o.parent_bone = b
        bpy.context.view_layer.update()
        o.matrix_world = mw
    for e in [o for o in bpy.data.objects if o.type == 'EMPTY']:
        bpy.data.objects.remove(e)


# ---------- animasjoner ----------

def _key(arm, frame, poses):
    for bn, rot in poses.items():
        pb = arm.pose.bones[bn]
        pb.rotation_euler = [math.radians(a) for a in rot]
        pb.keyframe_insert('rotation_euler', frame=frame)


def _clear(arm):
    for pb in arm.pose.bones:
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)


def action(arm, name, keys, loc_keys=None):
    """keys: {frame: {bone: (x, y, z) grader}}. Lagres som egen action i NLA."""
    arm.animation_data_create()
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for fr in sorted(keys):
        _clear(arm)
        _key(arm, fr, keys[fr])
    if loc_keys:
        for fr, (bn, loc) in loc_keys.items():
            pb = arm.pose.bones[bn]
            pb.location = loc
            pb.keyframe_insert('location', frame=fr)
    tr = arm.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, int(min(keys)), act)
    arm.animation_data.action = None
    _clear(arm)
    return act


def export_glb(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True,
                              export_animation_mode='ACTIONS', export_yup=True)


# ---------- bilder ----------

def studio(sc, res=(900, 1200)):
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = srgb('#3a3632')
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
    sc.world = w

    def light(name, kind, loc, energy, col, rot=None, size=1.0):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = srgb(col)[:3]
        if kind == 'AREA':
            ld.size = size
        lo = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(lo)
        lo.location = loc
        d = Vector((0, 0, 1.1)) - Vector(loc)
        lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return lo
    light('key', 'AREA', (-2.2, -3.0, 3.2), 700, '#ffe2bd', size=2.5)
    light('fill', 'AREA', (3.0, -2.0, 1.6), 180, '#b9c8ff', size=3)
    light('rim', 'AREA', (0.5, 3.2, 2.8), 600, '#ffc070', size=1.5)


def render_view(sc, path, azimuth_deg, elev_deg=8, dist=5.2, target_z=0.95, lens=70):
    cd = bpy.data.cameras.new('cam')
    cd.lens = lens
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    a = math.radians(azimuth_deg)
    e = math.radians(elev_deg)
    t = Vector((0, 0, target_z))
    cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
