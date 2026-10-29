"""Shieldguard (Tier 1) – første menneskefigur laget i Blender.

Kjør: python tools/blender/shieldguard.py UTMAPPE
Lager UTMAPPE/shieldguard.glb (med skjelett og animasjoner) og bilder.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector
import figur as F

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(OUT, exist_ok=True)
sc = F.reset()

navy = F.mat('marine', '#1f2d52', rough=0.85)
white = F.mat('hvit', '#ebe6da', rough=0.7)
steel = F.mat('staal', '#6a6e76', metal=0.9, rough=0.38)
mail = F.mat('brynje', '#5d6168', metal=0.85, rough=0.6)
brass = F.mat('messing', '#c29a45', metal=0.95, rough=0.32)
leather = F.mat('laer', '#5c3b22', rough=0.75)
cloth = F.mat('bukse', '#3e3328', rough=0.9)
skin = F.mat('hud', '#d6a07c', rough=0.65)
beard = F.mat('skjegg', '#5a3a22', rough=0.9)
dark = F.mat('oye', '#1a1512', rough=0.3)
wood = F.mat('tre', '#7b5432', rough=0.8)
glow = F.mat('glo', '#f0a020', metal=0.6, rough=0.35, emit=1.2)

J = F.JOINT
V = Vector

# ----- bein -----
for s, sd in ((1, 'L'), (-1, 'R')):
    hip, knee = J['thigh.' + sd]
    ank = J['shin.' + sd][1]
    F.limb('laar' + sd, hip + V((0, 0, 0.03)), knee, 0.098, 0.074, cloth, 'thigh.' + sd)
    F.sphere('kne' + sd, knee + V((0, -0.035, 0.0)), 0.06, steel, 'shin.' + sd, scale=(1, 0.8, 1.1))
    F.limb('legg' + sd, knee, ank + V((0, 0, 0.12)), 0.072, 0.06, cloth, 'shin.' + sd)
    F.limb('stovel' + sd, ank + V((0, 0, 0.26)), ank + V((0, 0, -0.04)), 0.078, 0.082, leather, 'shin.' + sd)
    F.limb('krage' + sd, ank + V((0, 0, 0.24)), ank + V((0, 0, 0.3)), 0.088, 0.09, leather, 'shin.' + sd)
    F.box('fot' + sd, V((s * 0.11, -0.06, 0.05)), (0.13, 0.26, 0.1), leather, 'foot.' + sd, bevel=0.03)

# ----- kropp -----
F.limb('bekken', (0, 0, 0.84), (0, 0, 1.02), 0.2, 0.205, cloth, 'hips', flat=0.75)
F.limb('brynjeskjort', (0, 0, 0.66), (0, 0, 1.0), 0.245, 0.215, mail, 'hips', flat=0.78)
F.limb('overkropp', (0, 0, 0.98), (0, 0, 1.44), 0.215, 0.275, mail, 'spine', flat=0.72)
F.limb('skulderparti', (0, 0, 1.36), (0, 0, 1.47), 0.275, 0.17, mail, 'chest', flat=0.72)
for fr, nm in ((True, 'foran'), (False, 'bak')):
    F.shell('vapenkjole_' + nm, 0.99, 1.42, 0.226, 0.286, navy, 'spine', flat=0.72, width=0.165, front=fr)
    F.shell('vapenkjole_skjort_' + nm, 0.58, 0.99, 0.262, 0.226, navy, 'hips', flat=0.8, width=0.15, front=fr)
    F.shell('kant_' + nm, 0.58, 0.61, 0.266, 0.262, brass, 'hips', flat=0.8, width=0.152, front=fr, thick=0.016)
F.limb('belte', (0, 0, 0.965), (0, 0, 1.04), 0.272, 0.272, leather, 'hips', flat=0.8)
F.box('spenne', V((0, -0.222, 1.0)), (0.07, 0.02, 0.06), brass, 'hips', bevel=0.008)
F.stag('bryst', V((0, -0.207, 1.22)), 1.05, white, 'spine', glow=glow)
for s in (1, -1):
    F.box('reim%d' % s, V((s * 0.13, -0.18, 1.39)), (0.05, 0.03, 0.12), leather, 'chest', bevel=0.006,
          rot=(0.3, 0, 0))

# ----- hode -----
F.limb('hals', (0, 0, 1.4), (0, 0, 1.53), 0.072, 0.07, skin, 'neck')
F.sphere('hode', (0, -0.01, 1.62), 0.13, skin, 'head', scale=(1, 1.05, 1.12), seg=24)
for s in (1, -1):
    F.sphere('ore%d' % s, (s * 0.127, 0.0, 1.615), 0.03, skin, 'head', scale=(0.5, 1, 1.3))
    F.sphere('oye%d' % s, (s * 0.046, -0.12, 1.612), 0.019, dark, 'head')
    F.box('bryn%d' % s, V((s * 0.047, -0.128, 1.643)), (0.066, 0.022, 0.022), beard, 'head', bevel=0.005,
          rot=(0, s * 0.12, 0))
F.sphere('nese', (0, -0.142, 1.6), 0.028, skin, 'head', scale=(0.85, 1, 1.25))
F.sphere('skjegg', (0, -0.062, 1.528), 0.118, beard, 'head', scale=(1.03, 0.86, 0.8), seg=20)
F.dome('haar', (0, 0.0, 1.61), 0.137, beard, 'head', scale=(1.0, 1.02, 1.1), seg=20, keep=(0, 1, 0))
F.sphere('bart', (0, -0.132, 1.565), 0.034, beard, 'head', scale=(1.9, 0.65, 0.6))
F.dome('hjelm', (0, -0.01, 1.668), 0.147, steel, 'head', scale=(1, 1.05, 1.12), seg=28)
rb = F.ring('hjelmkant', (0, -0.01, 1.672), 0.148, 0.016, brass, 'head')
rb.scale = (1, 1.05, 1)
F.box('neseskinne', V((0, -0.178, 1.635)), (0.024, 0.014, 0.075), steel, 'head', bevel=0.005)
F.limb('hjelmkam', (0, -0.165, 1.69), (0, 0.15, 1.69), 0.012, 0.012, brass, 'head', seg=8)
F.sphere('hjelmknapp', (0, -0.01, 1.835), 0.022, brass, 'head')

# ----- armer -----
for s, sd in ((1, 'L'), (-1, 'R')):
    sh, el = J['upperarm.' + sd]
    wr, hd = J['hand.' + sd]
    F.sphere('skulder' + sd, sh, 0.092, mail, 'upperarm.' + sd)
    F.limb('overarm' + sd, sh, el, 0.078, 0.062, mail, 'upperarm.' + sd)
    F.sphere('albue' + sd, el, 0.064, mail, 'forearm.' + sd)
    F.limb('underarm' + sd, el, el.lerp(wr, 0.35), 0.06, 0.056, mail, 'forearm.' + sd)
    F.limb('armskinn' + sd, el.lerp(wr, 0.3), wr, 0.066, 0.058, leather, 'forearm.' + sd)
    F.sphere('hand' + sd, wr.lerp(hd, 0.45), 0.062, skin, 'hand.' + sd, scale=(0.85, 1.0, 1.2))
# skulderplate på sverdarmen
shR = J['upperarm.R'][0]
F.dome('skulderplate', shR + V((-0.025, 0, 0.03)), 0.125, steel, 'upperarm.R', scale=(1, 1.1, 0.75))
bpy.data.objects['skulderplate'].rotation_euler = (0, -0.45, 0)
F.dome('skulderplate2', shR + V((-0.06, 0, -0.04)), 0.11, steel, 'upperarm.R', scale=(1, 1.05, 0.6))
bpy.data.objects['skulderplate2'].rotation_euler = (0, -0.7, 0)
k = F.ring('skulderkant', shR + V((-0.03, 0, 0.03)), 0.123, 0.011, brass, 'upperarm.R', rot=(0, -0.45, 0))
k.scale = (1, 1.1, 1)

# ----- skjold (venstre underarm) -----
el, wr = J['forearm.L']
mid = el.lerp(wr, 0.5)
grp = bpy.data.objects.new('skjold', None)
sc.collection.objects.link(grp)
parts = [
    F.disc('skjold_tre', (0, 0, 0), 0.3, 0.035, wood, 'forearm.L', rot=(math.pi / 2, 0, 0)),
    F.disc('skjold_flate', (0, -0.02, 0), 0.284, 0.008, navy, 'forearm.L', rot=(math.pi / 2, 0, 0)),
    F.ring('skjold_kant', (0, -0.004, 0), 0.29, 0.02, steel, 'forearm.L', rot=(math.pi / 2, 0, 0)),
]
for i in range(14):
    a = 2 * math.pi * i / 14
    parts.append(F.sphere('nagle%d' % i, (math.cos(a) * 0.258, -0.026, math.sin(a) * 0.258), 0.012, brass,
                          'forearm.L', seg=8))
for i in (-1, 0, 1):
    parts.append(F.box('planke%d' % i, V((i * 0.1, 0.02, 0)), (0.006, 0.004, 0.5 - abs(i) * 0.08), leather,
                       'forearm.L', bevel=0))
parts.append(F.box('handtak', V((0, 0.03, 0)), (0.03, 0.025, 0.2), leather, 'forearm.L', bevel=0.004))
emb = F.stag('skjold', V((0, -0.026, -0.01)), 1.65, white, 'forearm.L', glow=glow)
for p in parts + [emb]:
    p.parent = grp
grp.location = mid + V((0.05, -0.12, 0.0))
grp.rotation_euler = (0, 0, math.radians(28))

# ----- sverd (høyre hånd) -----
hR = J['hand.R'][0].lerp(J['hand.R'][1], 0.45)
sg = bpy.data.objects.new('sverd', None)
sc.collection.objects.link(sg)
sp = [
    F.limb('blad', (0, 0, -0.07), (0, 0, -0.66), 0.05, 0.04, steel, 'hand.R', seg=4, flat=0.22),
    F.limb('odd', (0, 0, -0.66), (0, 0, -0.74), 0.04, 0.002, steel, 'hand.R', seg=4, flat=0.22),
    F.box('parerstang', V((0, 0, -0.06)), (0.2, 0.04, 0.035), brass, 'hand.R', bevel=0.008),
    F.limb('grep', (0, 0, -0.05), (0, 0, 0.07), 0.018, 0.018, leather, 'hand.R', seg=8),
    F.sphere('knapp', (0, 0, 0.09), 0.03, brass, 'hand.R', seg=12),
]
for p in sp:
    p.parent = sg
sg.location = hR
sg.rotation_euler = (math.radians(-18), 0, math.radians(10))

# ----- skjelett og festing -----
arm = F.build_armature('Shieldguard_rig')
F.attach_parts(arm)
bpy.context.view_layer.update()


def fwd_sign(bone):
    """Fortegn på X-rotasjon som flytter beinets hale fremover (-Y)."""
    pb = arm.pose.bones[bone]
    t0 = (arm.matrix_world @ pb.tail).y
    pb.rotation_euler = (math.radians(10), 0, 0)
    bpy.context.view_layer.update()
    t1 = (arm.matrix_world @ pb.tail).y
    pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    return 1 if t1 < t0 else -1


S = {b: fwd_sign(b) for b in ('spine', 'chest', 'thigh.L', 'thigh.R', 'shin.L', 'shin.R',
                              'upperarm.L', 'upperarm.R', 'forearm.L', 'forearm.R', 'root', 'head')}
print('fortegn', S)


def P(**kw):
    """Fremover-grader per bein -> X-rotasjon med riktig fortegn. Tupler gir (x, y, z)."""
    out = {}
    for k, v in kw.items():
        b = k.replace('_L', '.L').replace('_R', '.R')
        if isinstance(v, tuple):
            out[b] = (v[0] * S.get(b, 1), v[1], v[2])
        else:
            out[b] = (v * S.get(b, 1), 0, 0)
    return out


F.action(arm, 'idle', {
    1: P(chest=0, head=0, upperarm_L=0, upperarm_R=0),
    30: P(chest=2.5, head=-2, upperarm_L=2, upperarm_R=-2),
    60: P(chest=0, head=0, upperarm_L=0, upperarm_R=0),
})
F.action(arm, 'walk', {
    1: P(thigh_L=24, thigh_R=-24, shin_L=-6, shin_R=-10, upperarm_R=16, upperarm_L=-5, chest=4),
    7: P(thigh_L=0, thigh_R=0, shin_L=-8, shin_R=-38, upperarm_R=0, upperarm_L=0, chest=5),
    13: P(thigh_L=-24, thigh_R=24, shin_L=-10, shin_R=-6, upperarm_R=-16, upperarm_L=5, chest=4),
    19: P(thigh_L=0, thigh_R=0, shin_L=-38, shin_R=-8, upperarm_R=0, upperarm_L=0, chest=5),
    25: P(thigh_L=24, thigh_R=-24, shin_L=-6, shin_R=-10, upperarm_R=16, upperarm_L=-5, chest=4),
}, loc_keys={1: ('root', (0, -0.02, 0)), 7: ('root', (0, 0.015, 0)), 13: ('root', (0, -0.02, 0)),
             19: ('root', (0, 0.015, 0)), 25: ('root', (0, -0.02, 0))})
F.action(arm, 'attack', {
    1: P(upperarm_R=0, forearm_R=0, upperarm_L=0, chest=(0, 0, 0)),
    7: P(upperarm_R=125, forearm_R=45, upperarm_L=20, chest=(-4, 14, 0)),
    11: P(upperarm_R=35, forearm_R=0, upperarm_L=25, chest=(8, -16, 0)),
    20: P(upperarm_R=0, forearm_R=0, upperarm_L=0, chest=(0, 0, 0)),
})
F.action(arm, 'hit', {
    1: P(chest=0, head=0, upperarm_L=0),
    4: P(chest=-12, head=-10, upperarm_L=25),
    12: P(chest=0, head=0, upperarm_L=0),
})
F.action(arm, 'die', {
    1: P(root=0, chest=0, head=0, thigh_L=0, thigh_R=0, upperarm_R=0, upperarm_L=0),
    8: P(root=-20, chest=12, head=10, thigh_L=25, thigh_R=10, upperarm_R=40, upperarm_L=30),
    20: P(root=-88, chest=-5, head=-15, thigh_L=12, thigh_R=4, upperarm_R=-60, upperarm_L=-50),
})

F.export_glb(os.path.join(OUT, 'shieldguard.glb'))

tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type == 'MESH':
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
print('trekanter', tris)

if '--render' in sys.argv:
    F.studio(sc)
    for nm, az, el in (('front', 0, 6), ('side', 90, 6), ('back', 180, 6), ('tre-kvart', 35, 12)):
        F.render_view(sc, os.path.join(OUT, 'sg_%s.png' % nm), az, el)
    sc.render.resolution_x, sc.render.resolution_y = 900, 900
    F.render_view(sc, os.path.join(OUT, 'sg_portrett.png'), 25, 5, dist=1.6, target_z=1.58, lens=70)
