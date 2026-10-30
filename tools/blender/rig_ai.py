"""Gjør en AI-generert figur (.glb fra Hunyuan3D o.l.) klar for spillet.

Kjør: python tools/blender/rig_ai.py INN.glb UT_PREFIKS FIGUR [--render]
FIGUR er en nøkkel i LEDD under (ledd målt på figuren, 1,8 m høy, ser mot -Y, venstre = +X).

Steg: skaler til 1,8 m og sett føttene på bakken, senk til ca. 12 000 trekanter,
krymp teksturene til 1024 px, lag menneskeskjelettet etter leddene, vekt hver flate
til de nærmeste beina, legg på bevegelser (idle, walk, attack, hit, die) og eksporter .glb.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line
import figur as F

# Ledd per figur (venstre side; høyre speiles). Målt med probe på den skalerte modellen.
LEDD = {
    'husk': dict(hips=(0, 0.05, 0.92), spine=(0, 0.07, 1.2), chest=(0, 0.06, 1.42), neck=(0, 0.0, 1.5),
                 head=(0, -0.09, 1.58), top=(0, -0.08, 1.8),
                 sh=(0.22, 0.07, 1.36), el=(0.40, 0.05, 1.0), wr=(0.44, -0.07, 0.7), hd=(0.45, -0.06, 0.48),
                 hip=(0.12, 0.05, 0.9), kn=(0.21, 0.05, 0.5), an=(0.26, 0.14, 0.13), toe=(0.32, -0.02, 0.03)),
}

src, out, key = sys.argv[1], sys.argv[2], sys.argv[3]
J = LEDD[key]
TRIS = 12000
sc = F.reset()
bpy.ops.import_scene.gltf(filepath=src)
ob = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()


def bounds():
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (Vector([min(v[i] for v in bb) for i in range(3)]), Vector([max(v[i] for v in bb) for i in range(3)]))


mn, mx = bounds()
s = 1.8 / (mx.z - mn.z)
ob.scale = [x * s for x in ob.scale]
bpy.context.view_layer.update()
mn, mx = bounds()
ob.location -= Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
n0 = sum(len(p.vertices) - 2 for p in ob.data.polygons)
if n0 > TRIS:
    d = ob.modifiers.new('dec', 'DECIMATE')
    d.ratio = TRIS / n0
    bpy.ops.object.modifier_apply(modifier='dec')
print('trekanter', n0, '->', sum(len(p.vertices) - 2 for p in ob.data.polygons))
for im in bpy.data.images:
    if im.size[0] > 1024:
        im.scale(1024, 1024)

# ----- skjelett -----
def m(p):
    return (-p[0], p[1], p[2])

F.BONES = [
    ('root', (0, 0, 0), (0, 0, 0.2), None),
    ('hips', J['hips'], J['spine'], 'root'),
    ('spine', J['spine'], J['chest'], 'hips'),
    ('chest', J['chest'], J['neck'], 'spine'),
    ('neck', J['neck'], J['head'], 'chest'),
    ('head', J['head'], J['top'], 'neck'),
]
for sd, f in (('L', lambda p: p), ('R', m)):
    F.BONES += [
        ('upperarm.' + sd, f(J['sh']), f(J['el']), 'chest'),
        ('forearm.' + sd, f(J['el']), f(J['wr']), 'upperarm.' + sd),
        ('hand.' + sd, f(J['wr']), f(J['hd']), 'forearm.' + sd),
        ('thigh.' + sd, f(J['hip']), f(J['kn']), 'hips'),
        ('shin.' + sd, f(J['kn']), f(J['an']), 'thigh.' + sd),
        ('foot.' + sd, f(J['an']), f(J['toe']), 'shin.' + sd),
    ]
arm = F.build_armature(key + '_rig')

# ----- vekter: hver flate følger de nærmeste beina -----
segs = [(n, Vector(h), Vector(t)) for n, h, t, p in F.BONES if n != 'root']
groups = {n: ob.vertex_groups.new(name=n) for n, _, _ in segs}
for v in ob.data.vertices:
    p = v.co
    ds = []
    for n, h, t in segs:
        q, f = intersect_point_line(p, h, t)
        f = min(max(f, 0.0), 1.0)
        ds.append(((p - (h + (t - h) * f)).length, n))
    ds.sort()
    near = ds[:2]
    w = [1 / max(d, 0.01) ** 4 for d, _ in near]
    tot = sum(w)
    for (d, n), wi in zip(near, w):
        groups[n].add([v.index], wi / tot, 'REPLACE')
ob.parent = arm
md = ob.modifiers.new('rig', 'ARMATURE')
md.object = arm
bpy.context.view_layer.update()


def fwd_sign(bone):
    pb = arm.pose.bones[bone]
    t0 = (arm.matrix_world @ pb.tail).y
    pb.rotation_euler = (math.radians(10), 0, 0)
    bpy.context.view_layer.update()
    t1 = (arm.matrix_world @ pb.tail).y
    pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    return 1 if t1 < t0 else -1


S = {b: fwd_sign(b) for b in ('spine', 'chest', 'head', 'root', 'thigh.L', 'thigh.R', 'shin.L', 'shin.R',
                              'upperarm.L', 'upperarm.R', 'forearm.L', 'forearm.R')}


def P(**kw):
    out = {}
    for k, v in kw.items():
        b = k.replace('_L', '.L').replace('_R', '.R')
        out[b] = (v[0] * S.get(b, 1), v[1], v[2]) if isinstance(v, tuple) else (v * S.get(b, 1), 0, 0)
    return out


# Husk: krokete, slepende gange og et klor med begge armer.
F.action(arm, 'idle', {
    1: P(chest=0, head=0, upperarm_L=0, upperarm_R=0),
    30: P(chest=3, head=4, upperarm_L=-3, upperarm_R=3),
    60: P(chest=0, head=0, upperarm_L=0, upperarm_R=0),
})
F.action(arm, 'walk', {
    1: P(thigh_L=22, thigh_R=-20, shin_L=-5, shin_R=-12, upperarm_L=-12, upperarm_R=14, chest=(4, 0, 4), head=-3),
    7: P(thigh_L=0, thigh_R=0, shin_L=-8, shin_R=-35, upperarm_L=0, upperarm_R=0, chest=(6, 0, 0), head=0),
    13: P(thigh_L=-20, thigh_R=22, shin_L=-12, shin_R=-5, upperarm_L=14, upperarm_R=-12, chest=(4, 0, -4), head=-3),
    19: P(thigh_L=0, thigh_R=0, shin_L=-35, shin_R=-8, upperarm_L=0, upperarm_R=0, chest=(6, 0, 0), head=0),
    25: P(thigh_L=22, thigh_R=-20, shin_L=-5, shin_R=-12, upperarm_L=-12, upperarm_R=14, chest=(4, 0, 4), head=-3),
}, loc_keys={1: ('root', (0, -0.02, 0)), 7: ('root', (0, 0.012, 0)), 13: ('root', (0, -0.02, 0)),
             19: ('root', (0, 0.012, 0)), 25: ('root', (0, -0.02, 0))})
F.action(arm, 'attack', {
    1: P(upperarm_L=0, upperarm_R=0, forearm_L=0, forearm_R=0, chest=0, head=0),
    8: P(upperarm_L=95, upperarm_R=95, forearm_L=35, forearm_R=35, chest=-10, head=-8),
    12: P(upperarm_L=20, upperarm_R=20, forearm_L=0, forearm_R=0, chest=18, head=10),
    22: P(upperarm_L=0, upperarm_R=0, forearm_L=0, forearm_R=0, chest=0, head=0),
})
F.action(arm, 'hit', {
    1: P(chest=0, head=0),
    4: P(chest=-14, head=-12),
    12: P(chest=0, head=0),
})
F.action(arm, 'die', {
    1: P(root=0, chest=0, head=0, thigh_L=0, thigh_R=0, upperarm_L=0, upperarm_R=0),
    8: P(root=8, chest=15, head=15, thigh_L=-20, thigh_R=-10, upperarm_L=-20, upperarm_R=-30),
    20: P(root=85, chest=5, head=10, thigh_L=-10, thigh_R=-4, upperarm_L=60, upperarm_R=50),
})

bpy.ops.export_scene.gltf(filepath=out + '.glb', export_format='GLB', export_image_format='JPEG',
                          export_jpeg_quality=85, export_animation_mode='ACTIONS', export_yup=True)

if '--render' in sys.argv:
    F.studio(sc, res=(700, 1000))
    sc.cycles.samples = 24
    for name, frame in (('walk', 1), ('attack', 8), ('attack', 12), ('die', 20)):
        for tr in arm.animation_data.nla_tracks:
            tr.mute = tr.name != name
        sc.frame_set(frame)
        F.render_view(sc, f'{out}_{name}{frame}.png', 30, 6)
