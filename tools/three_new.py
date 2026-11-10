# Nyeste three.js (versjon 51, 10. nov 2026). Rune: «I want newest three.js».
# Spillet var skrevet for three.js r128 (2021) som et globalt THREE-objekt. Nå hentes three som
# ES-modul fra jsdelivr (import map), og en liten modul lager det samme globale THREE-objektet
# (med GLTFLoader og SkeletonUtils) før spillkoden kjøres. Spillkoden ligger i
# <script type="text/x-flame"> og startes av modulen, i samme rekkefølge som før.
# For at spillet skal se likt ut som før, gjør modulen tre ting:
#  1. ColorManagement av (fargene i koden er valgt slik r128 viste dem).
#  2. Lys-styrke × π (r155+ fjernet den gamle «legacy»-lysmodellen).
#  3. Gammel avstandsdemping for punktlys (myk til 0 ved distance), som i r128.
# Bedre lys og tone mapping kommer i look_new.py oppå dette.
from patch import sub

VERSION = '0.187.0'
CDN = f'https://cdn.jsdelivr.net/npm/three@{VERSION}/'

BOOT = """<script type="importmap">{"imports": {"three": "%sbuild/three.module.js", "three/addons/": "%sexamples/jsm/"}}</script>
<script type="module">
import * as T from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
const THREE = Object.assign({}, T, { GLTFLoader, SkeletonUtils, REVISION_NEW: T.REVISION });
THREE.ColorManagement.enabled = false;
// Lysstyrke som i r128: den gamle modellen ganget direkte lys med π. Spillkoden ser og setter
// de gamle tallene; bare mens bildet tegnes gir intensity π-verdien.
let drawing = false;
for (const k of ['HemisphereLight', 'DirectionalLight', 'PointLight', 'AmbientLight', 'SpotLight']) {
  THREE[k] = class extends T[k] {
    get intensity() { return drawing ? this._li * Math.PI : this._li; }
    set intensity(v) { this._li = v; }
  };
}
THREE.WebGLRenderer = class extends T.WebGLRenderer {
  constructor(o) {
    super(o); this.outputColorSpace = T.SRGBColorSpace;
    const render = this.render;   // render er satt i konstruktøren, ikke på prototypen
    this.render = (scene, cam) => { drawing = true; try { render.call(this, scene, cam); } finally { drawing = false; } };
  }
};
THREE.ShaderChunk.lights_pars_begin = THREE.ShaderChunk.lights_pars_begin.replace(
  /float getDistanceAttenuation\\([\\s\\S]*?\\n\\}/,
  `float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	if ( cutoffDistance > 0.0 && decayExponent > 0.0 ) return pow( saturate( - lightDistance / cutoffDistance + 1.0 ), decayExponent );
	return 1.0;
}`);
window.THREE = THREE;
for (const s of document.querySelectorAll('script[type="text/x-flame"]')) {
  const n = document.createElement('script'); n.textContent = s.textContent; s.replaceWith(n);
}
</script>
""" % (CDN, CDN)

def apply(s):
    s = sub(s, '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
               '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>\n'
               '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/utils/SkeletonUtils.js"></script>\n', '')
    # Spillkoden (det store skriptet etter modelldataene) startes av modulen.
    i = s.index('<script>window.GLB_DATA')
    j = s.index('<script>\n', i)
    s = s[:j] + '<script type="text/x-flame">\n' + s[j + len('<script>\n'):]
    s = s[:i] + BOOT + s[i:]
    s = sub(s, "  renderer.outputEncoding = THREE.sRGBEncoding;\n", "")
    s = sub(s, " pr.outputEncoding = THREE.sRGBEncoding;", "")
    return s
