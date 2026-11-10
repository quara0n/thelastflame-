# Ekte 3D-modeller (GLB) i spillet, versjon 50 (10. nov 2026).
# Modellene i prototype/models/ bakes inn i siden som base64 (artifacts tar ikke .glb-filer).
# GLTFLoader og SkeletonUtils for three r128 hentes fra jsdelivr. Mangler de, eller modellen
# ikke laster, bruker spillet de gamle klossfigurene, så ingenting går i stykker.
# Legg til en ny figur: legg glb-en i MODELS under, og en linje i buildUnit-patchen (se 'husk').
import base64, pathlib
from patch import sub

HERE = pathlib.Path(__file__).parent
# type -> (fil, skala, ekstra dreining)
MODELS = {
    'husk': ('hollow-husk.glb', 0.82, 0.0),
}

LOADERS = """<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/utils/SkeletonUtils.js"></script>
"""

RUNTIME = r"""
  // ---------- Ekte 3D-modeller (versjon 50) ----------
  const MODEL3D = {};
  (function loadModels() {
    if (!THREE.GLTFLoader || !THREE.SkeletonUtils || !window.GLB_DATA) return;
    const loader = new THREE.GLTFLoader();
    for (const k in GLB_DATA) {
      try {
        const bin = Uint8Array.from(atob(GLB_DATA[k].data), c => c.charCodeAt(0));
        loader.parse(bin.buffer, '', gl => {
          gl.scene.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = false; o.frustumCulled = false;
            if (o.material) { o.material.side = THREE.FrontSide; o.material.envMapIntensity = 0.6; } } });
          MODEL3D[k] = { gl, scale: GLB_DATA[k].scale, rot: GLB_DATA[k].rot };
        }, e => console.warn('modell', k, e));
      } catch (e) { console.warn('modell', k, e); }
    }
  })();
  function addModel(rig, k) {
    const M = MODEL3D[k];
    const obj = THREE.SkeletonUtils.clone(M.gl.scene);
    obj.scale.setScalar(M.scale); obj.rotation.y = M.rot;
    rig.add(obj);
    const mixer = new THREE.AnimationMixer(obj), acts = {};
    M.gl.animations.forEach(c => { acts[c.name] = mixer.clipAction(c); });
    rig.userData.model = { mixer, acts, cur: null, busy: 0 };
    mixer.update(Math.random() * 2);
  }
  function modelPlay(m, name, once, fade) {
    if (m.cur === name || !m.acts[name]) return;
    const a = m.acts[name], prev = m.cur && m.acts[m.cur];
    a.reset(); a.setLoop(once ? THREE.LoopOnce : THREE.LoopRepeat); a.clampWhenFinished = !!once;
    a.fadeIn(fade || 0.15).play();
    if (prev) prev.fadeOut(fade || 0.15);
    m.cur = name;
    if (once && name !== 'die') m.busy = a.getClip().duration * 0.9;
  }
  function modelTick(v, u, dt) {
    const m = v.rig.userData.model; if (!m) return;
    v.rig.position.y = v.fy || 0; v.rig.position.z = 0;
    if (v.lunge > 0.1 && m.cur !== 'attack') { m.cur = null; modelPlay(m, 'attack', true, 0.08); }
    m.busy -= dt;
    if (m.busy <= 0) modelPlay(m, u.moving ? 'walk' : 'idle', false, 0.2);
    m.mixer.update(dt);
  }
  function modelDead(v, u, dt) {
    const m = v.rig.userData.model; if (!m) return false;
    modelPlay(m, 'die', true, 0.1); m.mixer.update(dt);
    v.rig.rotation.x = 0; v.g.position.y = -Math.max(0, v.deadT - 1.4) * 0.8;
    v.g.userData.ring.visible = false; if (v.bar) v.bar.visible = false;
    if (v.deadT > 2.6) v.g.visible = false;
    return true;
  }
"""

def apply(s):
    s = sub(s, '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n' + LOADERS)
    data = ',\n'.join(f'{k}: {{ scale: {sc}, rot: {r}, data: "{base64.b64encode((HERE / "../prototype/models" / f).read_bytes()).decode()}" }}'
                      for k, (f, sc, r) in MODELS.items())
    s = sub(s, LOADERS, LOADERS + '<script>window.GLB_DATA = {' + data + '};</script>\n')
    s = sub(s, "  const heroMats = { cape:", RUNTIME + "  const heroMats = { cape:")
    # Husk: ekte modell når den finnes.
    s = sub(s, "      case 'husk': {\n", "      case 'husk': {\n        if (MODEL3D.husk) { addModel(rig, 'husk'); height = 1.6; break; }\n")
    # Gå/stå/slå/dø-animasjon i alle visninger av enheter (egen bane, rivalens bane, lagkamerater).
    s = sub(s, "      if (v.rig.userData.anim && !u.staged) runAnim(v, animT);",
               "      if (v.rig.userData.anim && !u.staged) runAnim(v, animT);\n      modelTick(v, u, dt);")
    s = sub(s, "\n      if (v.rig.userData.anim) runAnim(v, animT);", "\n      if (v.rig.userData.anim) runAnim(v, animT);\n      modelTick(v, u, dt);")
    s = sub(s, "        if (v.rig.userData.anim) runAnim(v, animT);", "        if (v.rig.userData.anim) runAnim(v, animT);\n        modelTick(v, u, dt);")
    s = sub(s, "        v.deadT += dt;\n", "        v.deadT += dt;\n        if (modelDead(v, u, dt)) continue;\n")
    s = sub(s, "if (!u.alive) { v.deadT += dt; v.rig.rotation.x", "if (!u.alive) { v.deadT += dt; if (modelDead(v, u, dt)) continue; v.rig.rotation.x", count=2)
    return s
