# Nytt lys og etterbehandling med nyeste three.js (versjon 52, 10. nov 2026).
# - Tone mapping (ACES) ble prøvd, men gjorde fargene bleke; den er av (kan slås på med #fx=1.1,...).
# - Bloom: flammen, portalen, glør, øyne og lanterner gløder ut i lufta.
# - Myk refleks fra et innebygd «rom»-miljø, så stål og messing ser ut som metall.
# - Skarpere og større skygge fra månen.
# Alt kan slås av med #lavgrafikk i adressen (for svake telefoner).
from patch import sub

IMPORTS = r"""import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
"""

SETUP = r"""  // ---------- Nytt lys og glød (versjon 52) ----------
  const FX = { on: !/lavgrafikk/.test(location.hash) };
  // Testknapper: #fx=eksponering,miljø,bloom-styrke,bloom-terskel
  const FXK = (location.hash.match(/fx=([\d.,]+)/) || [, '0,0.02,0.5,1.5'])[1].split(',').map(Number);
  if (FX.on) {
    // ACES gjorde de gamle fargene flate og bleke; uten tone mapping beholder spillet kontrasten (FXK[0] > 0 slår ACES på).
    if (FXK[0] > 0) { renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = FXK[0]; }
    const pm = new THREE.PMREMGenerator(renderer);
    // Rommets eget punktlys ville blitt alt for sterkt med den gamle lysdempingen; de lysende panelene holder.
    const room = new THREE.RoomEnvironment(); const ls = []; room.traverse(o => { if (o.isLight) ls.push(o); }); ls.forEach(o => o.parent.remove(o));
    scene.environment = pm.fromScene(room, 0.04).texture;
    scene.environmentIntensity = FXK[1];
    const rt = new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, samples: PHONE ? 2 : 4 });
    FX.composer = new THREE.EffectComposer(renderer, rt);
    FX.composer.addPass(new THREE.RenderPass(scene, camera));
    FX.bloom = new THREE.UnrealBloomPass(new THREE.Vector2(256, 256), FXK[2], 0.45, FXK[3]);
    FX.composer.addPass(FX.bloom);
    FX.composer.addPass(new THREE.OutputPass());
  }
"""

GLOW = r"""// Glød (versjon 52): lysende ting (flammer, øyne, glør, lanterner) tegnes mye sterkere enn 1.0
// bare mens bildet tegnes. Skjermen viser dem likt (alt over 1 er fullt lys), men bloom ser dem og
// lar dem gløde. Vanlige lyse flater (snø, hvite skyer) holder seg under terskelen og gløder ikke.
const lum = c => 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
const glowK = (c, k) => Math.min(6, 2.2 / Math.max(0.05, lum(c) * k));
const tmpC = new T.Color();
THREE.MeshBasicMaterial = class extends T.MeshBasicMaterial {
  get color() {
    const c = this._c;
    if (!drawing || !c || this.depthTest === false || (this.transparent && this.opacity < 0.9) || this.blending !== T.NormalBlending) return c;
    const mx = Math.max(c.r, c.g, c.b), mn = Math.min(c.r, c.g, c.b);
    if (mx < 0.85 || (mx - mn) / mx < 0.15) return c;
    return tmpC.copy(c).multiplyScalar(glowK(c, 1));
  }
  set color(v) { this._c = v; }
};
THREE.MeshStandardMaterial = class extends T.MeshStandardMaterial {
  // Bare ting som er laget for å lyse: mørk overflate med sterk, klar glødfarge (glør, lanterner, vinduer, portal).
  get emissiveIntensity() {
    const e = this._ei, m = this.emissive;
    if (!drawing || e < 0.8 || !m || Math.max(m.r, m.g, m.b) < 0.6 || !this.color || lum(this.color) > 0.3) return e;
    return e * glowK(m, e);
  }
  set emissiveIntensity(v) { this._ei = v; }
};
"""

def apply(s):
    s = sub(s, "window.THREE = THREE;\nfor (const s of", GLOW + "window.THREE = THREE;\nfor (const s of")
    s = sub(s, "import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';\n",
               "import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';\n" + IMPORTS)
    s = sub(s, "const THREE = Object.assign({}, T, { GLTFLoader, SkeletonUtils, ",
               "const THREE = Object.assign({}, T, { GLTFLoader, SkeletonUtils, EffectComposer, RenderPass, UnrealBloomPass, OutputPass, RoomEnvironment, ")
    s = sub(s, """  function resize() {
    const w = view.clientWidth || 1, h = view.clientHeight || 1;
    renderer.setSize(w, h, false);
""", SETUP + """  function resize() {
    const w = view.clientWidth || 1, h = view.clientHeight || 1;
    renderer.setSize(w, h, false);
    if (FX.composer) { FX.composer.setPixelRatio(renderer.getPixelRatio()); FX.composer.setSize(w, h); }
""")
    s = sub(s, "    renderer.render(scene, camera);\n    requestAnimationFrame(frame);",
               "    if (FX.composer) FX.composer.render(); else renderer.render(scene, camera);\n    requestAnimationFrame(frame);")
    # Månen: større og skarpere skyggekart.
    s = sub(s, "renderer.shadowMap.type = THREE.PCFSoftShadowMap;", "renderer.shadowMap.type = THREE.PCFShadowMap;")
    return s
