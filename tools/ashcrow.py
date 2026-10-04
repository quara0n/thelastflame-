"""Ash Crow (askekråke): the first flyer, wave 5 in Askemyr. Many and fragile, flies over the army straight to the
gate, so only shooters and wall archers reach it in the air (flying rules live in world3.py).
Applied last by build_v2.py (needs world3's flyer code, versus' SEND table and the sound tables)."""
from patch import sub

TYPE = "  ashcrow:     { name: 'Ash Crow', side: 'e', kind: 'bird', flies: true, swarm: true, role: 'Flyr over hæren rett mot porten. Bare skyttere og bueskyttere på muren når den i lufta', hp: 45, armor: 0, dmg: 4, interval: 0.9, range: 0.35, speed: 4.0, radius: 0.35, aggro: 8 },\n"

MATS = """  Object.assign(mats, { crow: M(0x1b1719, { roughness: 0.85 }), crowAsh: M(0x4a4446, { roughness: 1 }),
    crowWing: new THREE.MeshStandardMaterial({ color: 0x221d1f, roughness: 0.9, side: THREE.DoubleSide }), crowBeak: M(0x3a3230, { roughness: 0.6 }) });
"""

MODEL = """      case 'ashcrow': {
        const fl = new THREE.Group(); rig.add(fl); anim(rig, fl, 'float', 3.4, 0.18);
        const body = mesh(new THREE.SphereGeometry(0.22, 10, 8), mats.crow, 0, 0.55, 0); body.scale.set(0.85, 0.8, 1.5); fl.add(body);
        fl.add(mesh(new THREE.SphereGeometry(0.15, 10, 8), mats.crow, 0, 0.68, 0.32));
        const beak = mesh(new THREE.ConeGeometry(0.05, 0.22, 6), mats.crowBeak, 0, 0.66, 0.5); beak.rotation.x = Math.PI / 2; fl.add(beak);
        fl.add(mesh(GEO.eye, mats.eye, -0.07, 0.72, 0.42), mesh(GEO.eye, mats.eye, 0.07, 0.72, 0.42));
        const tail = mesh(new THREE.BoxGeometry(0.22, 0.03, 0.3), mats.crowAsh, 0, 0.56, -0.42); tail.rotation.x = 0.2; fl.add(tail);
        [-1, 1].forEach(k => { const w = new THREE.Group(); w.position.set(k * 0.12, 0.62, 0.02);
          const p = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.32), mats.crowWing); p.position.x = k * 0.38; p.rotation.x = -Math.PI / 2; w.add(p);
          const tip = new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.26), mats.crowAsh); tip.position.set(k * 0.8, 0.005, -0.04); tip.rotation.x = -Math.PI / 2; w.add(tip);
          fl.add(w); anim(rig, w, 'flap', 9, k); });
        rig.scale.setScalar(1.5); height = 1.3; break;
      }
"""

CALL = "    bird: t => { [0, 0.22].forEach(d => { voice(t + d, { type: 'sawtooth', f: [[0, 620], [0.06, 820], [0.18, 480]], dur: 0.2, v: 0.12, bp: 1400, q: 3, a: 0.01 }); noise(sfxBus, t + d, 0.16, { ftype: 'bandpass', f: 1800, q: 2, v: 0.06 }); }); },\n"
DIE = "    bird: t => { voice(t, { type: 'sawtooth', f: [[0, 900], [0.35, 260]], dur: 0.38, v: 0.12, bp: 1200, q: 3 }); noise(sfxBus, t + 0.05, 0.25, { ftype: 'highpass', f: 2500, v: 0.08 }); },\n"


def apply(s):
    s = sub(s, "  spitter:     { name: 'Bile Spitter',", TYPE + "  spitter:     { name: 'Bile Spitter',")
    s = sub(s, "const BOUNTY = { husk: 1, brute: 3, spider: 1,", "const BOUNTY = { husk: 1, brute: 3, spider: 1, ashcrow: 1,")
    s = sub(s, "const SEND = { husk: 3, spider: 3,", "const SEND = { husk: 3, spider: 3, ashcrow: 4,")
    s = sub(s, "  // Hjelpere for vridde skapninger.\n", MATS + "  // Hjelpere for vridde skapninger.\n")
    s = sub(s, "      case 'stalker': {", MODEL + "      case 'stalker': {")
    s = sub(s, "    insect: t => { voice(t, { f: [[0, 205]", CALL + "    insect: t => { voice(t, { f: [[0, 205]")
    s = sub(s, "    insect: t => { for (let i = 0; i < 5; i++)", DIE + "    insect: t => { for (let i = 0; i < 5; i++)")
    # Locusts fly too (wave 15 is the World 2 flyer wave): same flyer rules as the crows.
    s = sub(s, "  locust:      { name: 'Locust Swarm', side: 'e', kind: 'insect', swarm: true, role: 'Hundrevis av små munner',",
               "  locust:      { name: 'Locust Swarm', side: 'e', kind: 'insect', flies: true, swarm: true, role: 'Hundrevis av små munner som flyr over hæren. Bare skyttere når dem i lufta',")
    return s
