// ===== The Last Flame — introfilm (versjon 49) =====
// Sanntids-3D (three.js r128 + bloom), klippet til sangen «Hold porten» (musikk/hold-porten.mp3).
// Spillet kaller LastFlameFilm.play(ferdig) når Start trykkes første gang; «Hopp over» går rett videre.
// Kilde: prototype/intro.html (frittstående). Bygget lages på nytt for hver avspilling og kastes etterpå.
window.LastFlameFilm = (() => {
'use strict';
let songBuf = null;
function prefetch() {
  if (!songBuf) songBuf = fetch('musikk/hold-porten.mp3').then(r => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); }).catch(e => { console.warn('film song', e); return null; });
  return songBuf;
}
function makeFilm(root, onDone, withSound) {
root.innerHTML = '<canvas></canvas><div class="lf-place" aria-hidden="true"><span class="rule"></span><b></b><i></i></div>'
  + '<div class="lf-subs" aria-live="polite"><span></span></div><button type="button" class="lf-skip">Hopp over</button><div class="lf-load">Forbereder introen …</div>';
const V3 = THREE.Vector3, PI = Math.PI;
const C = h => new THREE.Color(h).convertSRGBToLinear();
const HDR = (h, k) => C(h).multiplyScalar(k);
function mulberry32(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
let rnd = mulberry32(1777);
const rr = (a, b) => a + (b - a) * rnd();
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const lerp = (a, b, u) => a + (b - a) * u;
const sm = (a, b, x) => { x = clamp((x - a) / (b - a), 0, 1); return x * x * (3 - 2 * x); };
function hash2(x, y) { let h = (Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967295; }
function vnoise(x, y) { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  const a = hash2(xi, yi), b = hash2(xi + 1, yi), c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1); return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; }
function fbm(x, y, o = 4) { let s = 0, a = .5, f = 1; for (let i = 0; i < o; i++) { s += a * vnoise(x * f, y * f); f *= 2.03; a *= .5; } return s; }
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- renderer and post ----------
const canvas = root.querySelector('canvas');
const R = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
const phone = Math.min(innerWidth, innerHeight) < 600;
R.setPixelRatio(Math.min(devicePixelRatio || 1, phone ? 1.5 : 2));
R.toneMapping = THREE.NoToneMapping;
R.outputEncoding = THREE.LinearEncoding;
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 1200);
const U = { ptScale: { value: 400 }, time: { value: 0 } };
const rt = new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
const composer = new THREE.EffectComposer(R, rt);
const renderPass = new THREE.RenderPass(new THREE.Scene(), camera);
composer.addPass(renderPass);
const bloom = new THREE.UnrealBloomPass(new THREE.Vector2(256, 256), 1.0, 0.6, 0.85);
composer.addPass(bloom);
const FinalShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, fade: { value: 0 }, white: { value: 0 }, bars: { value: 0 }, exposure: { value: 1 },
    tint: { value: new V3(1, 1, 1) }, vign: { value: .7 }, grain: { value: .035 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time,fade,white,bars,exposure,vign,grain; uniform vec3 tint; varying vec2 vUv;
    vec3 aces(vec3 x){ return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.); }
    void main(){ vec2 uv=vUv, d=uv-.5; float k=.006*dot(d,d)*4.;
      vec3 c=vec3(texture2D(tDiffuse,uv+d*k).r, texture2D(tDiffuse,uv).g, texture2D(tDiffuse,uv-d*k).b);
      c=aces(c*tint*exposure); c=pow(c,vec3(1./2.2));
      float v=smoothstep(.95,.25,length(d*vec2(1.05,.95))); c*=mix(1.,v,vign);
      float g=fract(sin(dot(uv*vec2(1273.1,947.7)+fract(time*7.13),vec2(12.9898,78.233)))*43758.5453); c+=(g-.5)*grain;
      c*=fade; c=mix(c,vec3(1.,.96,.88),white);
      if(uv.y<bars||uv.y>1.-bars) c=vec3(0.);
      gl_FragColor=vec4(c,1.); }`
};
const finalPass = new THREE.ShaderPass(FinalShader);
composer.addPass(finalPass);
const FU = finalPass.uniforms;
let W = 1, H = 1;
function resize() {
  W = innerWidth; H = innerHeight;
  R.setSize(W, H, false); composer.setSize(W, H);
  const pr = R.getPixelRatio();
  bloom.setSize(Math.round(W * pr / 2), Math.round(H * pr / 2));
  camera.aspect = W / H;
}
addEventListener('resize', resize); resize();

// ---------- shared GLSL ----------
const NOISE = `float h21(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h21(i),h21(i+vec2(1,0)),f.x),mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 p){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*vn(p);p*=2.03;a*=.5;}return s;}`;
const UV_VS = 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }';

// ---------- materials ----------
function std(hex, o = {}) {
  const m = new THREE.MeshStandardMaterial({ color: C(hex), roughness: o.r ?? .9, metalness: o.m ?? 0, flatShading: o.flat ?? false });
  if (o.e) { m.emissive = C(o.e); m.emissiveIntensity = o.ei ?? 1; }
  if (o.vc) m.vertexColors = true;
  if (o.map) m.map = o.map;
  if (o.side) m.side = o.side;
  return m;
}
const basic = (hex, k = 1) => new THREE.MeshBasicMaterial({ color: HDR(hex, k) });

function glowTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.25, 'rgba(255,255,255,.45)'); gr.addColorStop(.6, 'rgba(255,255,255,.08)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
}
const GLOW = glowTexture();
function glowSprite(hex, k, size) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color: HDR(hex, k), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
  s.scale.setScalar(size); return s;
}
function stoneTexture(base, rows = 8, cols = 6, seed = 3) {
  const c = document.createElement('canvas'); c.width = 512; c.height = 512; const g = c.getContext('2d'); const r = mulberry32(seed);
  g.fillStyle = '#1b1a1a'; g.fillRect(0, 0, 512, 512);
  const bh = 512 / rows;
  for (let y = 0; y < rows; y++) {
    const off = (y % 2) * (512 / cols / 2);
    for (let x = -1; x < cols + 1; x++) {
      const bw = 512 / cols, l = 40 + r() * 22 + base;
      g.fillStyle = `hsl(${28 + r() * 14}, ${6 + r() * 8}%, ${l * .55}%)`;
      g.fillRect(x * bw + off + 3, y * bh + 3, bw - 6, bh - 6);
      for (let k = 0; k < 14; k++) { g.fillStyle = `rgba(0,0,0,${r() * .14})`; g.fillRect(x * bw + off + r() * bw, y * bh + r() * bh, 4 + r() * 22, 2 + r() * 8); }
    }
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.encoding = THREE.sRGBEncoding; t.anisotropy = 4; return t;
}
function veinTexture() {
  const c = document.createElement('canvas'); c.width = 256; c.height = 256; const g = c.getContext('2d'); const r = mulberry32(9);
  g.fillStyle = '#000'; g.fillRect(0, 0, 256, 256); g.lineCap = 'round';
  for (let i = 0; i < 18; i++) {
    g.strokeStyle = `rgba(255,255,255,${.5 + r() * .5})`; g.lineWidth = 1 + r() * 3; g.beginPath();
    let x = r() * 256, y = 0; g.moveTo(x, y);
    while (y < 256) { x += (r() - .5) * 40; y += 14 + r() * 20; g.lineTo(x, y); }
    g.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}

// ---------- particles ----------
const PT_VS = `attribute float size; attribute float alpha; varying float vA; uniform float scale;
  void main(){ vA=alpha; vec4 mv=modelViewMatrix*vec4(position,1.); gl_PointSize=size*scale/max(-mv.z,.1); gl_Position=projectionMatrix*mv; }`;
const PT_FS = `uniform vec3 color; varying float vA; void main(){ float r=length(gl_PointCoord-.5); float a=smoothstep(.5,.0,r); if(a*vA<.003) discard; gl_FragColor=vec4(color,a*vA); }`;
class Particles {
  constructor(n, o) {
    this.n = n; this.o = o; this.emit = o.emit ?? true;
    const g = new THREE.BufferGeometry();
    this.pos = new Float32Array(n * 3); this.vel = new Float32Array(n * 3); this.life = new Float32Array(n); this.max = new Float32Array(n);
    this.size = new Float32Array(n); this.base = new Float32Array(n); this.alpha = new Float32Array(n);
    g.setAttribute('position', new THREE.BufferAttribute(this.pos, 3)); g.setAttribute('size', new THREE.BufferAttribute(this.size, 1)); g.setAttribute('alpha', new THREE.BufferAttribute(this.alpha, 1));
    this.mat = new THREE.ShaderMaterial({ uniforms: { color: { value: o.color }, scale: U.ptScale }, vertexShader: PT_VS, fragmentShader: PT_FS,
      transparent: true, depthWrite: false, blending: o.additive === false ? THREE.NormalBlending : THREE.AdditiveBlending });
    this.points = new THREE.Points(g, this.mat); this.points.frustumCulled = false; this.geo = g;
    this.S = {};
    for (let i = 0; i < n; i++) { this.spawn(i); if (!o.burst) this.life[i] = this.max[i] * rnd(); if (o.burst) { this.life[i] = 0; this.alpha[i] = 0; } }
  }
  spawn(i) {
    const S = this.S; this.o.spawn(S, i);
    const j = i * 3; this.pos[j] = S.x; this.pos[j + 1] = S.y; this.pos[j + 2] = S.z;
    this.vel[j] = S.vx || 0; this.vel[j + 1] = S.vy || 0; this.vel[j + 2] = S.vz || 0;
    this.life[i] = this.max[i] = S.life || 2; this.base[i] = S.size || 1;
  }
  burst(k) { let c = 0; for (let i = 0; i < this.n && c < k; i++) if (this.life[i] <= 0) { this.spawn(i); c++; } }
  update(dt, t) {
    const o = this.o, g = o.g || 0, drag = o.drag ?? 1, sw = o.sway || 0;
    for (let i = 0; i < this.n; i++) {
      if (this.life[i] <= 0) { if (this.emit && !o.burst) this.spawn(i); else { this.alpha[i] = 0; continue; } }
      this.life[i] -= dt; const j = i * 3;
      this.vel[j + 1] += g * dt;
      if (drag !== 1) { const d = Math.pow(drag, dt * 60); this.vel[j] *= d; this.vel[j + 1] *= d; this.vel[j + 2] *= d; }
      this.pos[j] += (this.vel[j] + (sw ? Math.sin(t * 1.3 + i) * sw : 0)) * dt; this.pos[j + 1] += this.vel[j + 1] * dt; this.pos[j + 2] += (this.vel[j + 2] + (sw ? Math.cos(t * 1.1 + i * 1.7) * sw : 0)) * dt;
      if (o.floor !== undefined && this.pos[j + 1] < o.floor) this.life[i] = 0;
      const f = 1 - this.life[i] / this.max[i];
      this.alpha[i] = (o.fade ? o.fade(f) : Math.sin(PI * clamp(f, 0, 1))) * (o.alpha ?? 1);
      this.size[i] = this.base[i] * (o.grow ? 1 + f * o.grow : 1);
    }
    this.geo.attributes.position.needsUpdate = true; this.geo.attributes.alpha.needsUpdate = true; this.geo.attributes.size.needsUpdate = true;
  }
}

// ---------- flame ----------
const FLAME_FS = `uniform float time,power,seed; uniform vec3 cCore,cMid,cEdge; varying vec2 vUv; ${NOISE}
  void main(){ vec2 uv=vUv; float x0=(uv.x-.5)*2.; float y=uv.y; float tt=time+seed;
    float n1=fbm(vec2(x0*2.2+seed, y*2.6-tt*2.1)); float n2=fbm(vec2(x0*4.5-seed, y*5.-tt*3.4));
    float w=(1.-y)*.62+.04; w*=smoothstep(0.,.22,y)*.75+.25;
    float x=abs(x0+(n1-.5)*.7*y);
    float shape=1.-smoothstep(w*.55,w,x+(n2-.5)*.22);
    shape*=1.-smoothstep(.35,1.,y+(n1-.5)*.45);
    shape*=smoothstep(0.,.07,y);
    float core=(1.-smoothstep(0.,w*.5,x))*(1.-smoothstep(.05,.62,y+(n2-.5)*.2));
    vec3 col=mix(cEdge,cMid,smoothstep(.0,.6,shape)); col=mix(col,cCore,core);
    gl_FragColor=vec4(col*power, clamp(shape,0.,1.)); }`;
function makeFlame(o = {}) {
  const h = o.h || 1, g = new THREE.Group(), bb = new THREE.Group(); g.add(bb);
  const mats = [];
  const layers = [[1, 1, 0], [1.45, .55, .3]];
  for (const [s, p, sh] of layers) {
    const m = new THREE.ShaderMaterial({ uniforms: { time: U.time, power: { value: (o.power ?? 2) * p }, seed: { value: rnd() * 20 },
      cCore: { value: HDR(o.core ?? 0xfff3d6, 1) }, cMid: { value: C(o.mid ?? 0xffb43c) }, cEdge: { value: C(o.edge ?? 0xc8400c) } },
      vertexShader: UV_VS, fragmentShader: FLAME_FS, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(h * .62 * s, h * s), m);
    mesh.position.y = h * s * .5 - h * .06 - sh * h * .12; mesh.userData.p = p; bb.add(mesh); mats.push(m);
  }
  const glow = glowSprite(o.mid ?? 0xffb43c, o.glow ?? 1.4, h * 2.6); glow.position.y = h * .32; g.add(glow);
  let light = null;
  if (o.light) { light = new THREE.PointLight(C(0xffa040), o.light, o.dist || h * 12, 1.4); light.position.y = h * .45; g.add(light); }
  const api = { g, bb, mats, glow, light, base: o.power ?? 2, k: 1, billboard: o.billboard !== false, li: o.light || 0, gb: o.glow ?? 1.4, col: o.mid ?? 0xffb43c,
    set(k) { this.k = k; },
    update(t, cam) {
      const fl = 1 + Math.sin(t * 17.3 + this.base) * .05 + Math.sin(t * 7.1) * .06;
      for (const m of this.mats) m.uniforms.power.value = this.base * this.k * (m === this.mats[0] ? 1 : .55) * fl;
      this.glow.material.color.copy(HDR(this.col, this.gb * this.k * fl));
      this.g.visible = this.k > .002;
      if (this.light) this.light.intensity = this.li * this.k * fl;
      if (this.billboard && cam) { this.g.getWorldPosition(TMP); TMP2.copy(cam.position); TMP2.y = TMP.y; this.bb.lookAt(TMP2); }
    } };
  return api;
}
const TMP = new V3(), TMP2 = new V3();
function embers(n, ox, oy, oz, spread, o = {}) {
  return new Particles(n, { color: HDR(o.hex ?? 0xffa040, o.k ?? 3), sway: o.sway ?? .4, drag: .99,
    spawn(S) { S.x = ox + rr(-spread, spread); S.y = oy + rr(0, spread * .5); S.z = oz + rr(-spread, spread); S.vx = rr(-.2, .2); S.vy = rr(o.up ?? .6, (o.up ?? .6) * 2.4); S.vz = rr(-.2, .2); S.life = rr(1.2, o.life ?? 3.2); S.size = rr(.03, .08) * (o.s ?? 1); } });
}

// ---------- sky ----------
function makeSky(o) {
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: { top: { value: C(o.top) }, mid: { value: C(o.mid) }, bot: { value: C(o.bot) },
    sd: { value: new V3(...o.sun).normalize() }, sc: { value: HDR(o.sunCol ?? 0x000000, o.sunK ?? 1) }, sp: { value: o.sunPow ?? 24 }, time: U.time, neb: { value: o.neb ?? 0 } },
    vertexShader: 'varying vec3 vD; void main(){ vD=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform vec3 top,mid,bot,sd,sc; uniform float sp,time,neb; varying vec3 vD; ${NOISE}
      void main(){ vec3 d=normalize(vD); float h=d.y; vec3 c = h>0. ? mix(mid,top,pow(clamp(h,0.,1.),.55)) : mix(mid,bot,pow(clamp(-h,0.,1.),.35));
        float s=max(dot(d,sd),0.); c+=sc*(pow(s,sp)*1.5+.35*pow(s,4.));
        if(neb>0.){ float n=fbm(d.xy*2.3+d.z*1.7+time*.01); float n2=fbm(d.zy*4.1-time*.02); c+=neb*vec3(.28,.12,.45)*pow(n,3.)*1.6+neb*vec3(.08,.18,.4)*pow(n2,4.)*2.; }
        gl_FragColor=vec4(c,1.); }` });
  const s = new THREE.Mesh(new THREE.SphereGeometry(600, 32, 16), m); s.renderOrder = -1; return s;
}
function stars(n, r) {
  const p = new Particles(n, { color: HDR(0xdfe8ff, 1.6), emit: false, alpha: 1, fade: () => 1,
    spawn(S) { const u = rr(-1, 1), a = rr(0, PI * 2), q = Math.sqrt(1 - u * u); S.x = q * Math.cos(a) * r; S.y = Math.abs(u) * r * .9 + 10; S.z = q * Math.sin(a) * r; S.life = 1e9; S.size = rr(.6, 2.6) * r / 300; } });
  for (let i = 0; i < n; i++) { p.alpha[i] = rr(.25, 1); p.size[i] = p.base[i]; }
  p.update = function (dt, t) { for (let i = 0; i < this.n; i++) this.alpha[i] = .45 + .45 * Math.sin(t * (1 + i % 5) + i); this.geo.attributes.alpha.needsUpdate = true; };
  p.geo.attributes.size.needsUpdate = true; return p;
}

// ---------- ground ----------
function makeGround(size, seg, hf, cf, o = {}) {
  const g = new THREE.PlaneGeometry(size, size, seg, seg); g.rotateX(-PI / 2);
  const p = g.attributes.position, col = new Float32Array(p.count * 3), c = new THREE.Color();
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), y = hf(x, z); p.setY(i, y); cf(x, z, y, c); col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; }
  g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.computeVertexNormals();
  return new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, metalness: 0, flatShading: o.flat ?? false }));
}

// ---------- shapes ----------
function taperTube(pts, r, taper = .25, seg = 24, rs = 7) {
  const curve = new THREE.CatmullRomCurve3(pts), g = new THREE.TubeGeometry(curve, seg, r, rs, false), p = g.attributes.position;
  for (let j = 0; j <= seg; j++) {
    const u = j / seg, c = curve.getPointAt(u), k = lerp(1, taper, u);
    for (let i = 0; i <= rs; i++) { const idx = j * (rs + 1) + i; p.setXYZ(idx, c.x + (p.getX(idx) - c.x) * k, c.y + (p.getY(idx) - c.y) * k, c.z + (p.getZ(idx) - c.z) * k); }
  }
  g.computeVertexNormals(); return { g, curve };
}
function twistedTree(h, r, mat, twist) {
  const grp = new THREE.Group(); const pts = []; let x = 0, z = 0;
  for (let i = 0; i <= 6; i++) { pts.push(new V3(x, i / 6 * h, z)); x += rr(-1, 1) * twist; z += rr(-1, 1) * twist; }
  const trunk = taperTube(pts, r, .2); grp.add(new THREE.Mesh(trunk.g, mat));
  const nb = 3 + Math.floor(rnd() * 3);
  for (let b = 0; b < nb; b++) {
    const u = rr(.45, .9), s = trunk.curve.getPointAt(u), a = rr(0, PI * 2), L = h * rr(.25, .5);
    const bp = [s.clone()]; for (let k = 1; k <= 4; k++) bp.push(new V3(s.x + Math.cos(a + k * .4) * L * k / 4, s.y + L * k / 4 * rr(.2, .9), s.z + Math.sin(a + k * .4) * L * k / 4));
    grp.add(new THREE.Mesh(taperTube(bp, r * lerp(1, .2, u) * .8, .1, 12, 5).g, mat));
  }
  return grp;
}

// ---------- creatures ----------
const HG = {
  torso: new THREE.CylinderGeometry(.17, .11, .72, 7).translate(0, .36, 0),
  head: new THREE.SphereGeometry(.15, 8, 6).scale(.9, 1.1, 1.05),
  arm: new THREE.CylinderGeometry(.06, .035, .9, 5).translate(0, -.45, 0),
  leg: new THREE.CylinderGeometry(.08, .045, .95, 5).translate(0, -.47, 0),
  eye: new THREE.SphereGeometry(.028, 6, 4),
  crack: new THREE.BoxGeometry(.028, .34, .02),
  horn: new THREE.ConeGeometry(.04, .22, 5)
};
const M = {};
function initMats() {
  M.ash = std(0x302b28, { r: .95, flat: true });
  M.ashDark = std(0x1c1917, { r: 1, flat: true });
  M.crack = basic(0xff3a14, 1.8);
  M.eye = basic(0xff5a1e, 5);
  M.cyan = basic(0x5ff4ff, 5);
  M.amberEye = basic(0xffb020, 6);
  M.steel = std(0x8a8f98, { r: .38, m: .85 });
  M.darkSteel = std(0x3a3d44, { r: .5, m: .8 });
  M.blue = std(0x274a8c, { r: .8 });
  M.leather = std(0x4a3222, { r: .9 });
  M.wood = std(0x3b2a1c, { r: .9 });
  M.gold = std(0xd8a845, { r: .28, m: 1 });
  M.white = std(0xe4ded0, { r: .45, m: .3 });
  M.cloth = std(0xf2ece0, { r: .8, side: THREE.DoubleSide });
  M.halo = basic(0xffd890, 2.0);
}
function makeHusk(kind = 'husk') {
  const g = new THREE.Group(), hips = new THREE.Group(); hips.position.y = .95; g.add(hips);
  const legL = new THREE.Mesh(HG.leg, M.ash), legR = new THREE.Mesh(HG.leg, M.ash); legL.position.x = -.11; legR.position.x = .11; hips.add(legL, legR);
  const torso = new THREE.Group(); torso.rotation.x = .45; hips.add(torso);
  const body = new THREE.Mesh(HG.torso, M.ash); torso.add(body);
  const head = new THREE.Group(); head.position.set(0, .84, .06); torso.add(head);
  head.add(new THREE.Mesh(HG.head, M.ash));
  const eL = new THREE.Mesh(HG.eye, M.eye), eR = new THREE.Mesh(HG.eye, M.eye); eL.position.set(-.05, .02, .13); eR.position.set(.05, .02, .13); head.add(eL, eR);
  const c1 = new THREE.Mesh(HG.crack, M.crack); c1.position.set(.04, .42, .155); c1.rotation.z = .3; torso.add(c1);
  const armL = new THREE.Group(), armR = new THREE.Group(); armL.position.set(-.23, .64, 0); armR.position.set(.23, .64, 0);
  armL.add(new THREE.Mesh(HG.arm, M.ash)); armR.add(new THREE.Mesh(HG.arm, M.ash)); torso.add(armL, armR);
  const h = { g, hips, legL, legR, torso, head, armL, armR, phase: rnd() * 6.28, kind, speed: 1 };
  if (kind === 'brute') {
    g.scale.setScalar(1.75); body.scale.set(1.7, 1.05, 1.4); armL.position.x = -.34; armR.position.x = .34; armL.scale.set(1.8, 1.05, 1.8); armR.scale.set(1.8, 1.05, 1.8);
    const c2 = new THREE.Mesh(HG.crack, M.crack); c2.position.set(-.12, .36, .2); c2.rotation.z = -.4; torso.add(c2);
    const hl = new THREE.Mesh(HG.horn, M.ashDark), hr = hl.clone(); hl.position.set(-.08, .12, .02); hl.rotation.z = .5; hr.position.set(.08, .12, .02); hr.rotation.z = -.5; head.add(hl, hr);
    h.speed = .7;
  }
  return h;
}
function walk(h, t, amp = 1, rate = 1) {
  const p = t * 4.2 * h.speed * rate + h.phase, s = Math.sin(p);
  h.legL.rotation.x = s * .55 * amp; h.legR.rotation.x = -s * .55 * amp;
  h.armL.rotation.x = -.35 - s * .4 * amp; h.armR.rotation.x = -.35 + s * .4 * amp;
  h.hips.position.y = .95 + Math.abs(Math.cos(p)) * .05 * amp; h.torso.rotation.z = s * .07; h.head.rotation.z = Math.sin(p * .5) * .18;
}
function makeSoldier(o = {}) {
  const g = new THREE.Group(), hips = new THREE.Group(); hips.position.y = .95; g.add(hips);
  const legL = new THREE.Mesh(HG.leg, M.darkSteel), legR = new THREE.Mesh(HG.leg, M.darkSteel); legL.position.x = -.11; legR.position.x = .11; legL.scale.set(1.25, 1, 1.25); legR.scale.set(1.25, 1, 1.25); hips.add(legL, legR);
  const torso = new THREE.Group(); hips.add(torso);
  const body = new THREE.Mesh(new THREE.CylinderGeometry(.2, .17, .74, 8).translate(0, .37, 0), o.armor || M.blue); torso.add(body);
  const chest = new THREE.Mesh(new THREE.CylinderGeometry(.215, .19, .34, 8).translate(0, .55, 0), o.plate || M.steel); torso.add(chest);
  const head = new THREE.Group(); head.position.set(0, .88, 0); torso.add(head);
  head.add(new THREE.Mesh(new THREE.SphereGeometry(.15, 10, 8), o.plate || M.steel));
  const visor = new THREE.Mesh(new THREE.BoxGeometry(.2, .035, .04), M.ashDark); visor.position.set(0, -.01, .13); head.add(visor);
  const armL = new THREE.Group(), armR = new THREE.Group(); armL.position.set(-.27, .66, 0); armR.position.set(.27, .66, 0);
  const aG = new THREE.CylinderGeometry(.075, .055, .78, 6).translate(0, -.39, 0);
  armL.add(new THREE.Mesh(aG, o.plate || M.steel)); armR.add(new THREE.Mesh(aG, o.plate || M.steel)); torso.add(armL, armR);
  const s = { g, hips, legL, legR, torso, head, armL, armR, phase: rnd() * 6.28, speed: 1 };
  if (o.shield) {
    const sh = new THREE.Group(); sh.position.set(-.02, -.62, .14); armL.add(sh);
    const disc = new THREE.Mesh(new THREE.CylinderGeometry(.42, .42, .06, 18).rotateX(PI / 2), M.blue); sh.add(disc);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(.42, .03, 6, 22), M.gold); sh.add(rim);
    const boss = new THREE.Mesh(new THREE.SphereGeometry(.08, 8, 6), M.gold); boss.position.z = .04; sh.add(boss);
    s.shield = sh;
    const sp = new THREE.Mesh(new THREE.CylinderGeometry(.018, .018, 2.2, 5), M.wood); sp.position.set(0, -.7, .5); sp.rotation.x = PI / 2 - .3; armR.add(sp);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(.04, .2, 5), M.steel); tip.position.set(0, 1.15, 0); sp.add(tip);
  }
  if (o.bow) {
    const bow = new THREE.Mesh(new THREE.TorusGeometry(.46, .016, 4, 14, PI), M.wood); bow.rotation.set(0, PI / 2, PI / 2); bow.position.set(0, -.72, .1); armL.add(bow); s.bow = bow;
  }
  return s;
}
function makeWarden() {
  const s = makeSoldier({ armor: M.white, plate: M.white });
  const g = s.g; g.scale.setScalar(1.38);
  const belt = new THREE.Mesh(new THREE.TorusGeometry(.19, .03, 6, 18).rotateX(PI / 2), M.gold); belt.position.y = .32; s.torso.add(belt);
  const collar = new THREE.Mesh(new THREE.TorusGeometry(.17, .035, 6, 18).rotateX(PI / 2), M.gold); collar.position.y = .74; s.torso.add(collar);
  for (const sx of [-1, 1]) { const p = new THREE.Mesh(new THREE.SphereGeometry(.15, 10, 8, 0, PI * 2, 0, PI / 2), M.gold); p.position.set(sx * .27, .7, 0); p.scale.set(1.15, .8, 1.1); s.torso.add(p); }
  const crest = new THREE.Mesh(new THREE.BoxGeometry(.03, .1, .26), M.gold); crest.position.set(0, .14, -.02); s.head.add(crest);
  const halo = new THREE.Mesh(new THREE.TorusGeometry(.3, .018, 8, 40), M.halo); halo.position.set(0, .12, -.2); s.head.add(halo); s.halo = halo;
  const hg = glowSprite(0xffd890, .22, 1.1); hg.position.copy(halo.position); s.head.add(hg);
  // cape
  const cg = new THREE.PlaneGeometry(.62, 1.5, 6, 12).translate(0, -.75, 0);
  const cape = new THREE.Mesh(cg, M.cloth); cape.position.set(0, .74, -.2); s.torso.add(cape);
  s.cape = cape; s.capeBase = Float32Array.from(cg.attributes.position.array);
  // sword
  const sw = new THREE.Group(); sw.position.set(0, -.78, 0); s.armR.add(sw);
  const grip = new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, .22, 6), M.leather); sw.add(grip);
  const guard = new THREE.Mesh(new THREE.BoxGeometry(.32, .04, .06), M.gold); guard.position.y = -.12; sw.add(guard);
  const bladeMat = new THREE.MeshStandardMaterial({ color: C(0xf4efe4), roughness: .18, metalness: .9, emissive: C(0xffc860), emissiveIntensity: 0 });
  const blade = new THREE.Mesh(new THREE.BoxGeometry(.075, 1.35, .022).translate(0, -.8, 0), bladeMat); sw.add(blade);
  const core = new THREE.Mesh(new THREE.BoxGeometry(.018, 1.2, .026).translate(0, -.78, 0), basic(0xffe2a0, 1)); sw.add(core);
  const bglow = glowSprite(0xffc060, 0, 1.6); bglow.position.y = -.8; bglow.scale.set(.9, 2.2, 1); sw.add(bglow);
  s.sword = sw; s.blade = blade; s.bladeMat = bladeMat; s.bladeCore = core; s.bladeGlow = bglow;
  sw.rotation.x = 0;
  // shield with the flame
  const sh = new THREE.Group(); sh.position.set(-.02, -.6, .16); s.armL.add(sh);
  sh.add(new THREE.Mesh(new THREE.CylinderGeometry(.5, .5, .07, 24).rotateX(PI / 2), M.white));
  sh.add(new THREE.Mesh(new THREE.TorusGeometry(.5, .04, 8, 30), M.gold));
  const sf = makeFlame({ h: .55, power: 2.4, billboard: false, glow: .5 }); sf.g.position.set(0, -.26, .05); sh.add(sf.g);
  s.shieldFlame = sf; s.shield = sh;
  return s;
}
function makeCrow() {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(.35, 8, 6).scale(.7, .6, 1.6), M.ashDark); g.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(.2, 8, 6), M.ashDark); head.position.set(0, .12, .58); g.add(head);
  const beak = new THREE.Mesh(new THREE.ConeGeometry(.07, .3, 5).rotateX(PI / 2), M.ash); beak.position.set(0, .1, .82); g.add(beak);
  for (const sx of [-1, 1]) { const e = new THREE.Mesh(HG.eye, M.eye); e.scale.setScalar(1.6); e.position.set(sx * .1, .18, .72); g.add(e); }
  const wg = new THREE.BufferGeometry(); wg.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, .35, 1.7, .05, -.1, 0, 0, -.4, 1.7, .05, -.1, 1.15, 0, -.65, 0, 0, -.4], 3)); wg.computeVertexNormals();
  const wm = std(0x15110f, { r: 1, side: THREE.DoubleSide });
  const wl = new THREE.Group(), wr = new THREE.Group(); wl.add(new THREE.Mesh(wg, wm)); const mr = new THREE.Mesh(wg, wm); mr.scale.x = -1; wr.add(mr); g.add(wl, wr);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(.25, .6, 4).rotateX(-PI / 2), wm); tail.position.z = -.75; tail.scale.y = .2; g.add(tail);
  return { g, wl, wr };
}

// ========== SCENES ==========
const scenes = {};
function newScene(bg) { const s = new THREE.Scene(); s.background = C(bg); s.userData.parts = []; return s; }

// ---- A: one flame in the dark ----
function buildA() {
  const s = newScene(0x020203);
  s.fog = new THREE.FogExp2(C(0x020203), .08);
  s.add(new THREE.HemisphereLight(C(0x2a2030), C(0x050302), .15));
  const pts = []; for (let i = 0; i <= 10; i++) { const u = i / 10; pts.push(new THREE.Vector2(.08 + Math.sin(u * PI * .5) * .42 + (i > 8 ? -.04 * (i - 8) : 0), u * .34)); }
  const bowl = new THREE.Mesh(new THREE.LatheGeometry(pts, 20), std(0x2a2522, { r: .7, m: .4 })); bowl.position.y = .9; s.add(bowl);
  const ped = new THREE.Mesh(new THREE.CylinderGeometry(.16, .3, .9, 10), std(0x1d1a18, { r: .9 })); ped.position.y = .45; s.add(ped);
  const coals = new THREE.Mesh(new THREE.SphereGeometry(.38, 14, 6, 0, PI * 2, 0, PI / 2).scale(1, .25, 1), basic(0xff6a20, .0)); coals.position.y = 1.15; s.add(coals);
  const fl = makeFlame({ h: .75, power: 1.25, light: 2.0, dist: 9, glow: .45 }); fl.g.position.y = 1.16; s.add(fl.g);
  const em = embers(70, 0, 1.4, 0, .18, { up: .5, life: 3.4, s: .45, k: 2 }); s.add(em.points);
  const dust = new Particles(160, { color: HDR(0xffcf90, .35), sway: .05, spawn(S) { S.x = rr(-3, 3); S.y = rr(0, 3); S.z = rr(-3, 2); S.vy = rr(-.02, .02); S.life = rr(4, 9); S.size = rr(.01, .025); } });
  s.add(dust.points);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(8, 32).rotateX(-PI / 2), std(0x141110, { r: 1 })); s.add(floor);
  s.userData.update = (t, dt) => {
    const k = sm(1.4, 2.4, t) * (1 + .25 * sm(5, 7, t)), spark = Math.exp(-Math.pow((t - 1.5) * 6, 2)) * 2;
    fl.set(k + spark * .5); fl.update(t, camera);
    coals.material.color.copy(HDR(0xff5a18, .7 * k));
    em.emit = t > 1.5; em.update(dt, t); dust.update(dt, t);
  };
  scenes.A = s;
}

// ---- B: the fallen worlds go dark ----
function buildB() {
  const s = newScene(0x05060f);
  s.add(makeSky({ top: 0x04050c, mid: 0x0f0d26, bot: 0x030308, sun: [.4, .1, -1], sunCol: 0x4a3080, sunK: .25, sunPow: 6, neb: .55 }));
  const st = stars(900, 280); s.add(st.points);
  s.add(new THREE.HemisphereLight(C(0x8890c0), C(0x100a08), .8));
  const dl = new THREE.DirectionalLight(C(0xd8c0ff), 1.2); dl.position.set(-4, 6, 3); s.add(dl);
  const isl = [];
  const spots = [[-9, 1.5, -14, 2.2], [-3.5, 3.6, -20, 2.6], [3.2, -.4, -11, 1.8], [9, 2.4, -17, 2.4], [-14, -1.6, -22, 2.8], [14, -1.2, -24, 3], [0, -3.2, -8, 1.5], [-6, 6.5, -30, 3.2], [7, 7, -32, 3]];
  const order = [6, 2, 0, 3, 1, 4, 5, 7, 8];
  spots.forEach(([x, y, z, r], i) => {
    const g = new THREE.Group(); g.position.set(x, y, z);
    const rg = new THREE.ConeGeometry(r, r * 1.7, 9, 5).rotateX(PI); const p = rg.attributes.position;
    for (let k = 0; k < p.count; k++) { const vx = p.getX(k), vy = p.getY(k), vz = p.getZ(k), n = fbm(vx * .7 + i * 3, vz * .7 + vy * .5) - .5; p.setXYZ(k, vx * (1 + n * .5), vy, vz * (1 + n * .5)); }
    rg.computeVertexNormals();
    const rockMat = std(0x5a4232, { r: .95, flat: true }), topMat = std([0x4a7a3a, 0x7a4a8a, 0x3a6a7a, 0x8a6a2a][i % 4], { r: .9, flat: true });
    const rock = new THREE.Mesh(rg, rockMat); rock.position.y = -r * .85; g.add(rock);
    const top = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.02, r * .96, r * .22, 9), topMat); g.add(top);
    const treeMat = std(0x2d4a2a, { r: .9, flat: true });
    for (let k = 0; k < 4; k++) { const tr = new THREE.Mesh(new THREE.ConeGeometry(r * .14, r * .5, 5), treeMat); const a = rr(0, 6.28), d = rr(.3, .8) * r; tr.position.set(Math.cos(a) * d, r * .3, Math.sin(a) * d); g.add(tr); }
    const fl = makeFlame({ h: r * .7, power: 1.6, light: 1.6, dist: r * 6, glow: .9 }); fl.g.position.y = r * .1; g.add(fl.g);
    const smoke = new Particles(40, { color: C(0x6a6470), additive: false, alpha: .35, grow: 3, burst: true, sway: .2,
      spawn(S) { S.x = x + rr(-.2, .2) * r; S.y = y + r * .4; S.z = z + rr(-.2, .2) * r; S.vx = rr(-.2, .2); S.vy = rr(.4, 1.1); S.vz = rr(-.2, .2); S.life = rr(1.5, 3); S.size = r * rr(.2, .4); } });
    s.add(g, smoke.points);
    isl.push({ g, fl, rockMat, topMat, treeMat, smoke, out: 8.3 + order.indexOf(i) * .62, done: false, top0: topMat.color.clone(), rock0: rockMat.color.clone(), bob: rnd() * 6 });
  });
  const grey = C(0x3a3836), greyD = C(0x2a2826);
  s.userData.update = (t, dt) => {
    for (const I of isl) {
      const k = 1 - sm(I.out, I.out + .5, t);
      I.fl.set(k); I.fl.update(t, camera);
      const gk = 1 - sm(I.out, I.out + 1.4, t);
      I.topMat.color.copy(greyD).lerp(I.top0, gk); I.rockMat.color.copy(grey).lerp(I.rock0, gk); I.treeMat.color.copy(greyD).lerp(C(0x2d4a2a), gk);
      if (!I.done && t > I.out) { I.done = true; I.smoke.burst(26); }
      if (t < I.out - .1) I.done = false;
      I.smoke.update(dt, t);
      I.g.position.y += Math.sin(t * .6 + I.bob) * .002;
      I.g.rotation.y = t * .04 + I.bob;
    }
    st.update(dt, t);
  };
  scenes.B = s;
}

// ---- C: Askemyr ----
function buildC() {
  const s = newScene(0x1a1c18);
  s.fog = new THREE.FogExp2(C(0x26262a), .045);
  s.add(makeSky({ top: 0x121316, mid: 0x2e2a26, bot: 0x0e0e0c, sun: [0, .05, -1], sunCol: 0x8a3a14, sunK: .28, sunPow: 7 }));
  s.add(new THREE.HemisphereLight(C(0x7a7a70), C(0x1c1a14), .55));
  const back = new THREE.DirectionalLight(C(0xffa070), 1.0); back.position.set(0, 5, -20); s.add(back);
  const hf = (x, z) => (fbm(x * .12, z * .12) - .5) * 3 + (fbm(x * .5, z * .5) - .5) * .5 - (Math.abs(x) < 3 && z > -6 ? .0 : 0);
  const ground = makeGround(140, 140, hf, (x, z, y, c) => { const n = fbm(x * .3 + 9, z * .3); c.copy(C(0x3a3632)).lerp(C(0x22201c), n).lerp(C(0x4e4a44), clamp(y * .3, 0, .6)); });
  s.add(ground);
  const poolMat = new THREE.ShaderMaterial({ uniforms: { time: U.time }, vertexShader: 'varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }',
    fragmentShader: `uniform float time; varying vec3 vW; ${NOISE} void main(){ float n=fbm(vW.xz*.6+vec2(time*.05,-time*.04)); float b=pow(fbm(vW.xz*1.8-time*.1),3.);
      vec3 c=mix(vec3(.01,.04,.01),vec3(.12,.55,.08),n*.6)+vec3(.4,1.6,.2)*b*1.4; gl_FragColor=vec4(c,1.); }` });
  const pool = new THREE.Mesh(new THREE.PlaneGeometry(140, 140).rotateX(-PI / 2), poolMat); pool.position.y = -.55; s.add(pool);
  const pl = new THREE.PointLight(C(0x60ff40), 1.4, 16, 1.5); pl.position.set(-3, .2, 2); s.add(pl);
  const deadMat = std(0x161412, { r: 1, flat: true });
  for (let i = 0; i < 16; i++) { const tr = twistedTree(rr(3, 6), rr(.08, .16), deadMat, .25); const a = rr(0, 6.28), d = rr(7, 28), tx = Math.cos(a) * d, tz = Math.sin(a) * d - 4; if (Math.abs(tx) < 4.5 && tz > -8) continue; tr.position.set(tx, hf(tx, tz) - .2, tz); s.add(tr); }
  const ash = new Particles(1200, { color: C(0xc8c2b8), additive: false, alpha: .8, sway: .4, fade: f => Math.min(1, f * 6) * Math.min(1, (1 - f) * 6),
    spawn(S) { S.x = rr(-14, 14); S.y = rr(0, 9); S.z = rr(-14, 16); S.vx = rr(.1, .4); S.vy = rr(-.7, -.25); S.vz = rr(-.1, .1); S.life = rr(5, 12); S.size = rr(.025, .06); } });
  s.add(ash.points);
  const embersC = new Particles(80, { color: HDR(0xff5a20, 3), sway: .3, spawn(S) { S.x = rr(-8, 8); S.y = rr(0, 3); S.z = rr(-8, 8); S.vy = rr(.2, .6); S.life = rr(2, 5); S.size = rr(.03, .06); } });
  s.add(embersC.points);
  const husks = [];
  const place = [[-1.6, 1.2], [1.3, .4], [-.2, -1.2], [2.8, 2.2], [-3.2, 2.8], [.5, -3.4], [-2.4, -2.8], [3.6, -1.6]];
  place.forEach(([x, z], i) => { const h = makeHusk(i === 5 ? 'brute' : 'husk'); h.x = x; h.z = z; h.y0 = hf(x, z); h.rise = 15.6 + i * .55; h.g.rotation.y = rr(-.3, .3); s.add(h.g); husks.push(h); });
  const dirt = new Particles(160, { color: C(0x4a443c), additive: false, alpha: .9, g: -6, burst: true,
    spawn(S) { const h = husks[Math.floor(rnd() * husks.length)]; S.x = h.x + rr(-.3, .3); S.y = h.y0 + .1; S.z = h.z + rr(-.3, .3); S.vx = rr(-1, 1); S.vy = rr(1.5, 3.5); S.vz = rr(-1, 1); S.life = rr(.6, 1.2); S.size = rr(.04, .09); } });
  s.add(dirt.points);
  s.userData.update = (t, dt) => {
    for (const h of husks) {
      const u = sm(h.rise, h.rise + 1.6, t), walking = t > h.rise + 1.6;
      h.g.position.set(h.x, h.y0 - 1.9 * (1 - u), h.z + (walking ? (t - h.rise - 1.6) * .35 * h.speed : 0));
      h.torso.rotation.x = .45 + (1 - u) * .7;
      h.armL.rotation.x = -2.6 * (1 - u) - .35 * u; h.armR.rotation.x = -2.4 * (1 - u) - .35 * u;
      if (walking) walk(h, t, .8, .6);
      if (Math.abs(t - h.rise - .2) < dt * 1.2) dirt.burst(20);
    }
    ash.update(dt, t); embersC.update(dt, t); dirt.update(dt, t);
    pl.intensity = 1.2 + Math.sin(t * 2.1) * .3;
  };
  scenes.C = s;
}

// ---- D: Vrangheim ----
function buildD() {
  const s = newScene(0x0c0612);
  s.fog = new THREE.FogExp2(C(0x1a0c24), .06);
  s.add(makeSky({ top: 0x07030c, mid: 0x2a0e34, bot: 0x07030a, sun: [0, .15, -1], sunCol: 0x8a2a8a, sunK: .35, sunPow: 5 }));
  s.add(new THREE.HemisphereLight(C(0x6a4a9a), C(0x140a1a), .45));
  const ml = new THREE.PointLight(C(0xff3ad0), 2, 22, 1.4); ml.position.set(0, 3, -6); s.add(ml);
  const hf = (x, z) => (fbm(x * .15, z * .15) - .5) * 2.2;
  s.add(makeGround(120, 110, hf, (x, z, y, c) => { c.copy(C(0x2a1634)).lerp(C(0x140a1a), fbm(x * .4, z * .4)); }));
  const vt = veinTexture(); vt.repeat.set(1, 3);
  const treeMat = new THREE.MeshStandardMaterial({ color: C(0x2a1236), roughness: .85, emissive: HDR(0xff2ad0, 1), emissiveMap: vt, emissiveIntensity: 1.2 });
  const trees = [];
  for (let i = 0; i < 26; i++) {
    const side = i % 2 ? 1 : -1, z = -i * 1.9 + rr(-1, 1) + 6, x = side * rr(2.6, 7.5);
    const tr = twistedTree(rr(4.5, 8), rr(.18, .32), treeMat, .7); tr.position.set(x, hf(x, z) - .1, z); tr.rotation.y = rr(0, 6.28); s.add(tr); trees.push(tr);
  }
  const thorn = std(0x3a2030, { r: .8, flat: true });
  for (let i = 0; i < 40; i++) { const c = new THREE.Mesh(new THREE.ConeGeometry(.08, rr(.5, 1.4), 4), thorn); const x = rr(-9, 9), z = rr(-40, 8); if (Math.abs(x) < 1.2) continue; c.position.set(x, hf(x, z) + .3, z); c.rotation.set(rr(-.6, .6), 0, rr(-.6, .6)); s.add(c); }
  const eyes = [];
  for (let i = 0; i < 26; i++) {
    const g = new THREE.Group(); const n = 3 + Math.floor(rnd() * 3);
    for (let k = 0; k < n; k++) { const e = new THREE.Mesh(HG.eye, M.cyan); e.scale.set(1.4, 1, 1); e.position.set((k - (n - 1) / 2) * .09, (k % 2) * .07, 0); g.add(e); }
    const side = rnd() < .5 ? -1 : 1, z = rr(-30, 2), x = side * rr(1.6, 8);
    g.position.set(x, hf(x, z) + rr(.4, 2.6), z); g.lookAt(0, 1.5, 9); g.scale.setScalar(rr(1, 1.8)); g.userData.t0 = 23.6 + rnd() * 4.6; g.userData.bl = rnd() * 10;
    s.add(g); eyes.push(g);
  }
  const spores = new Particles(500, { color: HDR(0xff4ae0, 2.2), sway: .35, spawn(S) { S.x = rr(-9, 9); S.y = rr(0, 6); S.z = rr(-30, 8); S.vy = rr(.02, .18); S.life = rr(3, 8); S.size = rr(.025, .06); } });
  s.add(spores.points);
  const motes = new Particles(160, { color: HDR(0x60f0ff, 1.6), sway: .5, spawn(S) { S.x = rr(-7, 7); S.y = rr(.2, 3); S.z = rr(-20, 8); S.life = rr(2, 5); S.size = rr(.02, .04); } });
  s.add(motes.points);
  s.userData.update = (t, dt) => {
    treeMat.emissiveIntensity = .7 + .6 * Math.pow(.5 + .5 * Math.sin(t * 2.2), 2);
    vt.offset.y = -t * .08;
    for (const e of eyes) { const o = sm(e.userData.t0, e.userData.t0 + .25, t); const bl = Math.pow(Math.abs(Math.sin(t * .7 + e.userData.bl)), 40); e.scale.y = Math.max(.02, o * (1 - bl)) * e.scale.x; e.visible = o > .01; }
    spores.update(dt, t); motes.update(dt, t);
    ml.intensity = 1.6 + Math.sin(t * 2.2) * .6;
  };
  scenes.D = s;
}

// ---- E: Urheim ----
function buildE() {
  const s = newScene(0x2a1606);
  s.fog = new THREE.FogExp2(C(0x3a200c), .011);
  s.add(makeSky({ top: 0x1e0e06, mid: 0x7a3e12, bot: 0x1e1208, sun: [-.3, .1, -1], sunCol: 0xff9030, sunK: .8, sunPow: 10 }));
  s.add(new THREE.HemisphereLight(C(0xffb060), C(0x2a1a0a), .35));
  const back = new THREE.DirectionalLight(C(0xffa040), 2.2); back.position.set(0, 8, -30); s.add(back);
  const fill = new THREE.DirectionalLight(C(0x506040), .35); fill.position.set(6, 3, 10); s.add(fill);
  const hf = (x, z) => (fbm(x * .1, z * .1) - .5) * 2.5;
  s.add(makeGround(160, 120, hf, (x, z, y, c) => { c.copy(C(0x3a3018)).lerp(C(0x1e1a0c), fbm(x * .3, z * .3)); }));
  // volcano
  const vol = new THREE.Mesh(new THREE.ConeGeometry(38, 30, 18, 3, true), std(0x2a1a10, { r: 1, flat: true })); vol.position.set(-30, 10, -110); s.add(vol);
  const lava = new THREE.Mesh(new THREE.CircleGeometry(5, 16).rotateX(-PI / 2), basic(0xff6a10, 4)); lava.position.set(-30, 24.9, -110); s.add(lava);
  const vs = new Particles(140, { color: C(0x3a2a20), additive: false, alpha: .55, grow: 4, sway: .6, spawn(S) { S.x = -30 + rr(-3, 3); S.y = 26; S.z = -110 + rr(-3, 3); S.vx = rr(.5, 1.5); S.vy = rr(2, 4); S.life = rr(5, 9); S.size = rr(3, 6); } });
  s.add(vs.points);
  // ferns
  const fernMat = std(0x1e2a12, { r: .9, side: THREE.DoubleSide, flat: true });
  for (let i = 0; i < 70; i++) {
    const g = new THREE.Group(); const L = rr(1.2, 3.2), n = 6 + Math.floor(rnd() * 4);
    for (let k = 0; k < n; k++) { const leaf = new THREE.Mesh(new THREE.PlaneGeometry(L * .28, L, 1, 4).translate(0, L / 2, 0), fernMat);
      const p = leaf.geometry.attributes.position; for (let j = 0; j < p.count; j++) { const y = p.getY(j); p.setZ(j, Math.pow(y / L, 2) * L * .5); } leaf.geometry.computeVertexNormals();
      leaf.rotation.set(-.4, k / n * PI * 2, 0); g.add(leaf); }
    const side = rnd() < .5 ? -1 : 1, x = side * rr(5, 18), z = rr(-40, 4); g.position.set(x, hf(x, z), z); g.scale.setScalar(rr(.8, 1.8)); s.add(g);
  }
  const trunkMat = std(0x1a120a, { r: 1 });
  for (let i = 0; i < 18; i++) { const tr = twistedTree(rr(8, 14), rr(.25, .45), trunkMat, .5); const side = rnd() < .5 ? -1 : 1, x = side * rr(8, 24), z = rr(-50, 0); tr.position.set(x, hf(x, z), z); s.add(tr); }
  // tyrant
  const T = { g: new THREE.Group() }, skin = std(0x2a2418, { r: .85, flat: true }), plate = std(0x8a7a5a, { r: .6, flat: true });
  const body = new THREE.Mesh(new THREE.SphereGeometry(1.6, 12, 10).scale(1, 1.05, 2), skin); body.position.y = 3.7; T.g.add(body);
  T.neck = new THREE.Group(); T.neck.position.set(0, 4.4, 2.6); T.g.add(T.neck);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(.75, 1.1, 2.2, 10).rotateX(-1.0), skin); neck.position.set(0, .3, .5); T.neck.add(neck);
  T.head = new THREE.Group(); T.head.position.set(0, .9, 1.4); T.neck.add(T.head);
  const skull = new THREE.Mesh(new THREE.BoxGeometry(1.1, .9, 2.0), skin); skull.position.set(0, .2, .7); T.head.add(skull);
  const snout = new THREE.Mesh(new THREE.BoxGeometry(.9, .55, 1.1), skin); snout.position.set(0, .05, 1.9); T.head.add(snout);
  T.jaw = new THREE.Group(); T.jaw.position.set(0, -.25, .1); T.head.add(T.jaw);
  const jaw = new THREE.Mesh(new THREE.BoxGeometry(.95, .32, 2.4), skin); jaw.position.set(0, -.12, 1.15); T.jaw.add(jaw);
  const toothMat = std(0xe8dcc0, { r: .5 });
  for (let k = 0; k < 9; k++) for (const sx of [-1, 1]) { const tt = new THREE.Mesh(new THREE.ConeGeometry(.05, .22, 4), toothMat); tt.position.set(sx * .38, -.22, .9 + k * .17); tt.rotation.x = PI; T.head.add(tt); const bt = tt.clone(); bt.rotation.x = 0; bt.position.set(sx * .36, .1, .5 + k * .17); T.jaw.add(bt); }
  const mouth = new THREE.PointLight(C(0xff7020), 0, 6, 2); mouth.position.set(0, -.2, 1.8); T.head.add(mouth);
  for (const sx of [-1, 1]) { const e = new THREE.Mesh(HG.eye, M.amberEye); e.scale.setScalar(2.4); e.position.set(sx * .5, .45, .9); T.head.add(e); }
  for (let k = 0; k < 9; k++) { const p = new THREE.Mesh(new THREE.ConeGeometry(.3 - k * .02, .8 - k * .04, 4), plate); p.position.set(0, 5.35 - k * .06, 2 - k * .75); p.rotation.x = -.3; T.g.add(p); }
  const tailPts = [new V3(0, 3.8, -2.8), new V3(0, 3.6, -5), new V3(.6, 3.2, -7.5), new V3(1.4, 2.8, -10)];
  T.g.add(new THREE.Mesh(taperTube(tailPts, 1.05, .08, 20, 9).g, skin));
  T.legs = [];
  for (const sx of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(sx * 1.15, 3.2, -.2); T.g.add(hip);
    const th = new THREE.Mesh(new THREE.CylinderGeometry(.7, .45, 2.2, 8).translate(0, -1.1, 0), skin); hip.add(th);
    const kn = new THREE.Group(); kn.position.y = -2.1; hip.add(kn); kn.rotation.x = -.6;
    const sh = new THREE.Mesh(new THREE.CylinderGeometry(.38, .3, 1.6, 7).translate(0, -.8, 0), skin); kn.add(sh);
    const ft = new THREE.Mesh(new THREE.BoxGeometry(.7, .25, 1.2), skin); ft.position.set(0, -1.55, .35); kn.add(ft);
    hip.rotation.x = .3; T.legs.push(hip);
    const arm = new THREE.Mesh(new THREE.CylinderGeometry(.12, .08, .8, 5), skin); arm.position.set(sx * .9, 3.6, 2.6); arm.rotation.x = .9; T.g.add(arm);
  }
  T.g.position.set(-3.5, hf(-3.5, -7), -7); T.g.rotation.y = 1.2; s.add(T.g);
  const steam = new Particles(260, { color: C(0xd8b890), additive: false, alpha: .22, grow: 3, sway: .3, spawn(S) { S.x = rr(-16, 16); S.y = rr(0, 1); S.z = rr(-30, 10); S.vy = rr(.3, .8); S.life = rr(4, 8); S.size = rr(1, 2.4); } });
  s.add(steam.points);
  const dust = new Particles(240, { color: C(0x8a6a40), additive: false, alpha: .6, grow: 2.5, burst: true, drag: .97, spawn(S) { S.x = rr(-4, 4); S.y = rr(0, .5); S.z = -8 + rr(-3, 5); S.vx = rr(-3, 3); S.vy = rr(.5, 2); S.vz = rr(0, 4); S.life = rr(1.5, 3); S.size = rr(.4, 1); } });
  s.add(dust.points);
  const motes = new Particles(300, { color: HDR(0xffc070, 1.5), sway: .3, spawn(S) { S.x = rr(-10, 10); S.y = rr(0, 6); S.z = rr(-20, 10); S.life = rr(3, 7); S.size = rr(.02, .045); } });
  s.add(motes.points);
  const steps = [29.6, 30.35, 31.1];
  s.userData.update = (t, dt) => {
    const roar = sm(31.3, 31.7, t) * (1 - sm(33.4, 34.2, t));
    const walkU = clamp((t - 29.2) / 2.2, 0, 1);
    T.g.position.z = -7 + walkU * 2.4 * Math.cos(1.2); T.g.position.x = -3.5 + walkU * 2.4 * Math.sin(1.2);
    T.legs[0].rotation.x = .3 + Math.sin(walkU * PI * 2) * .25 * (1 - roar); T.legs[1].rotation.x = .3 - Math.sin(walkU * PI * 2) * .25 * (1 - roar);
    T.neck.rotation.x = -roar * .35 + Math.sin(t * 1.3) * .03; T.head.rotation.x = -roar * .25;
    T.jaw.rotation.x = roar * .75 + Math.sin(t * 40) * .02 * roar;
    T.g.position.y = hf(0, T.g.position.z) + Math.abs(Math.sin(walkU * PI * 2)) * .12;
    mouth.intensity = roar * 3;
    for (const st of steps) if (Math.abs(t - st) < dt * .6) { dust.burst(30); shake(.18); }
    if (Math.abs(t - 31.5) < dt * .6) { dust.burst(120); shake(.7); }
    steam.update(dt, t); dust.update(dt, t); motes.update(dt, t); vs.update(dt, t);
    lava.material.color.copy(HDR(0xff6a10, 3 + Math.sin(t * 3) * .8));
  };
  scenes.E = s;
}

// ---- F: the gate, the city and the last flame ----
const F = {};
const hillY = (x, z) => z < -2 ? 12 * sm(-2, -44, z) + (fbm(x * .1, z * .1) - .5) * 1.4 * sm(-2, -10, z) : 0;
function domeZ(x, y) { return -26 + 28 * Math.sqrt(Math.max(0, 1 - (x / 46) ** 2 - (y / 44) ** 2)); }
function buildF() {
  const s = newScene(0x0b0c12);
  s.fog = new THREE.FogExp2(C(0x1c1416), .0085);
  F.sky = makeSky({ top: 0x05070f, mid: 0x1e1418, bot: 0x0a0807, sun: [0, .03, 1], sunCol: 0x8a2408, sunK: .4, sunPow: 14 }); s.add(F.sky);
  F.stars = stars(500, 300); s.add(F.stars.points);
  s.add(new THREE.HemisphereLight(C(0x4a5a88), C(0x22160e), .55));
  const moon = new THREE.DirectionalLight(C(0x9fb4e8), .65); moon.position.set(-30, 50, -40); s.add(moon);
  const rim = new THREE.DirectionalLight(C(0xff6a30), .35); rim.position.set(10, 8, 60); s.add(rim);
  // ground: battlefield out front, the hill with the city behind
  const g = makeGround(360, 200, (x, z) => {
    if (z < -2) return hillY(x, z);
    const road = Math.exp(-x * x / 18);
    return (fbm(x * .06, z * .06) - .5) * 2.4 * (1 - road * .8) * sm(2, 14, z) + (fbm(x * .4, z * .4) - .5) * .25;
  }, (x, z, y, c) => {
    if (z < -2) { c.copy(C(0x2a2622)).lerp(C(0x3a3228), fbm(x * .3, z * .3)); return; }
    const road = Math.exp(-x * x / 10);
    c.copy(C(0x221c16)).lerp(C(0x302618), fbm(x * .2, z * .2)).lerp(C(0x3e342a), road * .7);
  });
  s.add(g);
  // wall, gate, towers
  const stone = stoneTexture(6), stoneMat = new THREE.MeshStandardMaterial({ map: stone, roughness: .92, color: C(0xb8b0a4) });
  const wallMat = (rx, ry) => { const m = stoneMat.clone(); m.map = stone.clone(); m.map.needsUpdate = true; m.map.repeat.set(rx, ry); return m; };
  for (const sx of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(31.5, 10, 3), wallMat(10, 3)); w.position.set(sx * 24.25, 5, 0); s.add(w);
    const tw = new THREE.Mesh(new THREE.BoxGeometry(5, 16, 5), wallMat(1.6, 5)); tw.position.set(sx * 6, 8, .4); s.add(tw);
    const tr = new THREE.Mesh(new THREE.ConeGeometry(4, 4.5, 4).rotateY(PI / 4), std(0x3a1e16, { r: .8, flat: true })); tr.position.set(sx * 6, 18.2, .4); s.add(tr);
    const ct = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 4.2, 14, 14), wallMat(4, 4)); ct.position.set(sx * 41, 7, 0); s.add(ct);
    const cr = new THREE.Mesh(new THREE.ConeGeometry(4.4, 6, 14), std(0x3a1e16, { r: .8 })); cr.position.set(sx * 41, 17, 0); s.add(cr);
    const ban = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 5, 1, 6), std(0x1e3a7a, { r: .8, side: THREE.DoubleSide })); ban.position.set(sx * 6, 11, 2.95); s.add(ban);
    const bs = new THREE.Mesh(new THREE.PlaneGeometry(.5, 3.6), new THREE.MeshStandardMaterial({ color: C(0xd8a845), metalness: .8, roughness: .3, side: THREE.DoubleSide })); bs.position.set(sx * 6, 11.3, 2.97); s.add(bs);
  }
  const lintel = new THREE.Mesh(new THREE.BoxGeometry(7, 2.6, 3), wallMat(2, 1)); lintel.position.set(0, 8.7, 0); s.add(lintel);
  const doors = new THREE.Mesh(new THREE.BoxGeometry(7, 7.5, .6), std(0x2a1c12, { r: .85 })); doors.position.set(0, 3.75, .2); s.add(doors);
  for (let k = 0; k < 4; k++) { const band = new THREE.Mesh(new THREE.BoxGeometry(7, .18, .1), M.darkSteel); band.position.set(0, 1 + k * 1.8, .55); s.add(band); }
  const seam = new THREE.Mesh(new THREE.BoxGeometry(.06, 7.4, .1), basic(0xffb040, 2.5)); seam.position.set(0, 3.75, .52); s.add(seam);
  // crenellations
  const cren = new THREE.InstancedMesh(new THREE.BoxGeometry(.8, 1, 3.05), stoneMat, 64); let ci = 0; const m4 = new THREE.Matrix4();
  for (let x = -39.5; x <= 39.5; x += 1.6) { if (Math.abs(x) < 8.6) continue; m4.makeTranslation(x, 10.5, 0); cren.setMatrixAt(ci++, m4); if (ci >= 64) break; }
  cren.count = ci; s.add(cren);
  // gate braziers
  F.braziers = [];
  for (const sx of [-1, 1]) {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(.2, .3, 2.2, 8), M.darkSteel); post.position.set(sx * 4.3, 1.1, 3.3); s.add(post);
    const bowl = new THREE.Mesh(new THREE.CylinderGeometry(.55, .3, .4, 10), M.darkSteel); bowl.position.set(sx * 4.3, 2.3, 3.3); s.add(bowl);
    const fl = makeFlame({ h: 1.3, power: 3, light: 2.4, dist: 20 }); fl.g.position.set(sx * 4.3, 2.45, 3.3); s.add(fl.g); F.braziers.push(fl);
  }
  // city on the hill
  const NH = 170, houses = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1).translate(0, .5, 0), std(0x8a7a66, { r: .9 }), NH);
  const roofs = new THREE.InstancedMesh(new THREE.ConeGeometry(.78, .7, 4).rotateY(PI / 4).translate(0, .35, 0), std(0x5a2a1c, { r: .8, flat: true }), NH);
  const winPts = []; const q = new THREE.Quaternion(), sc = new V3(), ps = new V3(), col = new THREE.Color();
  let hi = 0;
  for (let k = 0; hi < NH && k < 2000; k++) {
    const x = rr(-36, 36), z = rr(-46, -5); if (Math.abs(x) < 6 && z < -38) continue; if (Math.abs(x) < 2.2) continue;
    const y = hillY(x, z), w = rr(1.6, 3), d = rr(1.6, 3), hh = rr(1.6, 3.6);
    q.setFromAxisAngle(new V3(0, 1, 0), rr(-.2, .2)); ps.set(x, y - .2, z); sc.set(w, hh, d); m4.compose(ps, q, sc); houses.setMatrixAt(hi, m4);
    col.copy(C(0x8a7a66)).lerp(C(0x5e544a), rnd()); houses.setColorAt(hi, col);
    ps.set(x, y - .2 + hh, z); sc.set(w * .95, rr(.9, 1.5), d * .95); m4.compose(ps, q, sc); roofs.setMatrixAt(hi, m4);
    if (rnd() < .8) winPts.push([x + rr(-.4, .4) * w, y + hh * rr(.35, .7), z + d * .51]);
    if (rnd() < .5) winPts.push([x + w * .51, y + hh * rr(.35, .7), z + rr(-.4, .4) * d]);
    hi++;
  }
  houses.count = roofs.count = hi; s.add(houses, roofs);
  const wins = new Particles(winPts.length, { color: HDR(0xffb050, 2.6), emit: false, fade: () => 1, spawn(S, i) { const p = winPts[i] || [0, -99, 0]; S.x = p[0]; S.y = p[1]; S.z = p[2]; S.life = 1e9; S.size = rr(.16, .26); } });
  wins.update = function (dt, t) { for (let i = 0; i < this.n; i++) this.alpha[i] = .7 + .3 * Math.sin(t * 3 + i * 7.1) * Math.sin(t * 1.3 + i); this.geo.attributes.alpha.needsUpdate = true; };
  for (let i = 0; i < wins.n; i++) wins.size[i] = wins.base[i]; wins.geo.attributes.size.needsUpdate = true;
  s.add(wins.points); F.wins = wins;
  // citadel and the last flame
  const cy = hillY(0, -46);
  const keep = new THREE.Mesh(new THREE.CylinderGeometry(4, 5, 12, 12), wallMat(5, 4)); keep.position.set(0, cy + 6, -46); s.add(keep);
  const kc = new THREE.Mesh(new THREE.CylinderGeometry(4.4, 4.4, 1.2, 12), wallMat(5, .5)); kc.position.set(0, cy + 12.6, -46); s.add(kc);
  const spire = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 2, 8, 10), wallMat(2, 3)); spire.position.set(0, cy + 17, -46); s.add(spire);
  const bowl = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 1.2, 1.1, 14), M.gold); bowl.position.set(0, cy + 21.5, -46); s.add(bowl);
  F.flameY = cy + 22; F.flamePos = new V3(0, F.flameY, -46);
  F.flame = makeFlame({ h: 6.5, power: 3.4, light: 3.4, dist: 120, glow: 1.6 }); F.flame.g.position.copy(F.flamePos); F.flame.g.position.y -= .2; s.add(F.flame.g);
  F.flameEmbers = embers(160, 0, F.flameY + 1, -46, 1.5, { up: 1.5, life: 4, s: 3 }); s.add(F.flameEmbers.points);
  // dome
  F.domeMat = new THREE.ShaderMaterial({ uniforms: { time: U.time, hitT: { value: -1 }, hitP: { value: new V3() }, glow: { value: 0 }, col: { value: HDR(0xff8a2a, 1) } },
    vertexShader: 'varying vec3 vN,vW; void main(){ vec4 w=modelMatrix*vec4(position,1.); vW=w.xyz; vN=normalize(mat3(modelMatrix)*normal); gl_Position=projectionMatrix*viewMatrix*w; }',
    fragmentShader: `uniform float time,hitT,glow; uniform vec3 hitP,col; varying vec3 vN,vW; ${NOISE}
      void main(){ vec3 V=normalize(cameraPosition-vW); float f=pow(1.-abs(dot(normalize(vN),V)),2.5);
        float d=distance(vW,hitP); float ring=hitT<0.?0.:exp(-pow((d-hitT*20.)*.35,2.))*exp(-hitT*1.1);
        float n=fbm(vec2(vW.x*.25+vW.z*.18,vW.y*.3)-time*.3);
        float hex=ring*(.4+1.4*n) + glow*(.25+f*1.2)*(.5+n) + f*.015;
        gl_FragColor=vec4(col*hex,1.); }`, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24, 0, PI * 2, 0, PI / 2), F.domeMat); dome.scale.set(46, 44, 28); dome.position.set(0, 0, -26); s.add(dome);
  // portal
  F.portal = new THREE.Group(); F.portal.position.set(0, 7.2, 68); s.add(F.portal);
  const rg = new THREE.TorusGeometry(7.4, 1, 7, 28); const rp = rg.attributes.position;
  for (let k = 0; k < rp.count; k++) { const n = hash2(Math.round(rp.getX(k) * 3), Math.round(rp.getY(k) * 3 + rp.getZ(k) * 5)) - .5; rp.setXYZ(k, rp.getX(k) * (1 + n * .1), rp.getY(k) * (1 + n * .1), rp.getZ(k) * (1 + n * .6)); }
  rg.computeVertexNormals();
  const ring = new THREE.Mesh(rg, std(0x1e1614, { r: .95, flat: true, e: 0x5a0e04, ei: 1 })); F.portal.add(ring); F.ringMat = ring.material;
  for (let k = 0; k < 9; k++) { const sp = new THREE.Mesh(new THREE.ConeGeometry(.5, rr(2, 4), 5), ring.material); const a = k / 9 * PI * 2 + .2; sp.position.set(Math.cos(a) * 8.2, Math.sin(a) * 8.2, 0); sp.rotation.z = a - PI / 2; F.portal.add(sp); }
  F.portalMat = new THREE.ShaderMaterial({ uniforms: { time: U.time, open: { value: 0 } }, vertexShader: UV_VS, transparent: true, depthWrite: false, side: THREE.DoubleSide,
    fragmentShader: `uniform float time,open; varying vec2 vUv; ${NOISE}
      void main(){ vec2 p=vUv*2.-1.; float r=length(p); float a=atan(p.y,p.x); float o=open*.98;
        float sw=fbm(vec2(a*1.6+r*5.-time*1.4, r*3.-time*.8)); float sw2=fbm(vec2(a*3.-time*.6, r*8.+time));
        float inside=1.-smoothstep(o-.03,o,r);
        vec3 red=vec3(1.25,.16,.04);
        vec3 c=vec3(.03,0.,0.)+red*pow(sw,2.6)*1.6*smoothstep(0.,o,r)+red*.6*pow(sw2,4.);
        float edge=exp(-pow((r-o)*16.,2.))*step(.01,open);
        c=c*inside+red*edge*2.2;
        gl_FragColor=vec4(c,clamp(inside+edge,0.,1.)); }` });
  const disc = new THREE.Mesh(new THREE.PlaneGeometry(15.4, 15.4), F.portalMat); F.portal.add(disc);
  F.portalLight = new THREE.PointLight(C(0xff2a0a), 0, 70, 1.3); F.portalLight.position.set(0, 7, 62); s.add(F.portalLight);
  const lg = new THREE.BufferGeometry(); F.boltPos = new Float32Array(16 * 2 * 3 * 4); lg.setAttribute('position', new THREE.BufferAttribute(F.boltPos, 3));
  F.bolts = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: HDR(0xff6040, 4), transparent: true, blending: THREE.AdditiveBlending })); F.bolts.frustumCulled = false; F.portal.add(F.bolts);
  F.portalSparks = new Particles(220, { color: HDR(0xff4020, 3), burst: true, drag: .97, g: -2,
    spawn(S) { const a = rr(0, 6.28), r = 7.4; S.x = Math.cos(a) * r; S.y = 7.2 + Math.sin(a) * r; S.z = 67.5; S.vx = Math.cos(a) * rr(1, 5); S.vy = Math.sin(a) * rr(1, 5); S.vz = rr(-4, -1); S.life = rr(.6, 1.6); S.size = rr(.08, .18); } });
  s.add(F.portalSparks.points);
  // horde from the portal
  F.horde = [];
  for (let i = 0; i < 26; i++) {
    const h = makeHusk(i % 6 === 3 ? 'brute' : 'husk'); h.spawn = 47.1 + i * .17 + rr(0, .2); h.lane = rr(-6.5, 6.5) + (i % 2 ? .5 : -.5); h.v = (h.kind === 'brute' ? 1.7 : 2.5) * rr(.9, 1.1);
    h.g.visible = false; s.add(h.g); F.horde.push(h);
  }
  // shield line, second row, archers on the wall, the Warden
  F.guards = []; F.archers = [];
  for (let i = 0; i < 12; i++) { const sd = makeSoldier({ shield: true }); sd.g.position.set(-7.7 + i * 1.4, 0, 9 + (i % 2) * .15); s.add(sd.g); F.guards.push(sd); }
  for (let i = 0; i < 6; i++) { const sd = makeSoldier({ shield: true }); sd.g.position.set(-6 + i * 2.4, 0, 7.4); s.add(sd.g); F.guards.push(sd); }
  for (let i = 0; i < 12; i++) { const side = i < 6 ? -1 : 1, x = side * (10.5 + (i % 6) * 3.2); const a = makeSoldier({ bow: true }); a.g.position.set(x, 10, .6); s.add(a.g); F.archers.push(a); }
  F.warden = makeWarden(); F.warden.g.position.set(0, 0, 12.2); s.add(F.warden.g);
  F.wardenLight = new THREE.PointLight(C(0xffd890), .4, 7, 1.5); F.wardenLight.position.set(0, 3.4, 12.6); s.add(F.wardenLight);
  // the charge that hits the shield line
  F.charge = [];
  for (let i = 0; i < 7; i++) { const h = makeHusk(i === 3 ? 'brute' : 'husk'); h.x = 2.4 + i * .95; h.z0 = 21 + rr(0, 2.5); h.g.visible = false; s.add(h.g); F.charge.push(h); }
  F.clashSparks = new Particles(260, { color: HDR(0xffc060, 4), burst: true, g: -9, drag: .985,
    spawn(S) { S.x = rr(2.2, 9); S.y = rr(.6, 1.6); S.z = rr(9.4, 10); S.vx = rr(-3, 3); S.vy = rr(1, 5); S.vz = rr(-1, 4); S.life = rr(.3, .9); S.size = rr(.015, .035); } });
  s.add(F.clashSparks.points);
  // fire arrows
  F.arrows = []; F._tp = new V3();
  const arrowGeo = new THREE.BoxGeometry(.05, .05, .9), arrowMat = basic(0xffa040, 4);
  for (let v = 0; v < 2; v++) for (let i = 0; i < F.archers.length; i++) {
    const a = F.archers[i], m = new THREE.Mesh(arrowGeo, arrowMat); m.visible = false; s.add(m);
    const gl = glowSprite(0xff8a30, 1.2, 1.1); m.add(gl);
    F.arrows.push({ m, t0: 63.55 + v * 1.0 + rr(0, .25), dur: rr(1.3, 1.6), p0: new V3(a.g.position.x + .3, 11.6, 1.2), p1: new V3(rr(-7, 7), 0, rr(24, 38)), hit: false });
  }
  F.trail = new Particles(500, { color: HDR(0xff7a28, 2.6), emit: false, burst: true, spawn(S) { S.x = F._tp.x + rr(-.05, .05); S.y = F._tp.y; S.z = F._tp.z; S.vy = rr(.1, .5); S.life = rr(.2, .5); S.size = rr(.05, .12); } });
  s.add(F.trail.points);
  F.impacts = new Particles(240, { color: HDR(0xff8a30, 4), burst: true, g: -6, spawn(S) { S.x = F._tp.x; S.y = F._tp.y + .2; S.z = F._tp.z; S.vx = rr(-2, 2); S.vy = rr(1, 4); S.vz = rr(-2, 2); S.life = rr(.3, .8); S.size = rr(.06, .14); } });
  s.add(F.impacts.points);
  // crow
  F.crow = makeCrow(); F.crow.g.scale.setScalar(1.4); s.add(F.crow.g);
  F.hitP = new V3(-5, 20, domeZ(-5, 20)); F.domeMat.uniforms.hitP.value.copy(F.hitP);
  F.crowA = new V3(-30, 27, 36);
  F.feathers = new Particles(80, { color: HDR(0xff9a40, 3), burst: true, g: -3, drag: .97, spawn(S) { S.x = F.hitP.x; S.y = F.hitP.y; S.z = F.hitP.z + .4; S.vx = rr(-4, 4); S.vy = rr(-2, 4); S.vz = rr(0, 5); S.life = rr(.5, 1.4); S.size = rr(.12, .3); } });
  s.add(F.feathers.points);
  // atmosphere
  F.ash = new Particles(1400, { color: C(0xb8aea4), additive: false, alpha: .6, sway: .5, fade: f => Math.min(1, f * 6) * Math.min(1, (1 - f) * 6),
    spawn(S) { const c = camera.position; S.x = c.x + rr(-22, 22); S.y = c.y + rr(-6, 14); S.z = c.z + rr(-28, 14); S.vx = rr(.2, .6); S.vy = rr(-.8, -.3); S.vz = rr(-.2, .2); S.life = rr(4, 9); S.size = rr(.03, .07); } });
  s.add(F.ash.points);
  F.embersAir = new Particles(260, { color: HDR(0xff7a30, 2.4), sway: .6, spawn(S) { const c = camera.position; S.x = c.x + rr(-14, 14); S.y = c.y + rr(-4, 6); S.z = c.z + rr(-24, 2); S.vy = rr(.3, .9); S.life = rr(2, 5); S.size = rr(.03, .06); } });
  s.add(F.embersAir.points);
  s.userData.update = updateF;
  scenes.F = s;
}
function updateF(t, dt) {
  const end = t >= 74;
  // flame and the dome
  const flare = sm(68.4, 72.8, t) * (end ? 0 : 1);
  F.flame.set(1 + flare * 1.5); F.flame.g.scale.setScalar(1 + flare * .9); F.flame.update(t, camera);
  F.flameEmbers.update(dt, t);
  for (const b of F.braziers) b.update(t, camera);
  F.domeMat.uniforms.glow.value = flare * 1.6 + (end ? .05 : 0);
  F.domeMat.uniforms.col.value.copy(HDR(flare > .01 ? 0xffb040 : 0xff8a2a, 1));
  F.wins.update(dt, t); F.stars.update(dt, t);
  // crow hits the dome at 41.2
  const cu = clamp((t - 38.5) / 2.7, 0, 1);
  const crow = F.crow;
  crow.g.visible = t > 38.4 && t < 43.2;
  if (t < 41.2) {
    crow.g.position.lerpVectors(F.crowA, F.hitP, cu); crow.g.lookAt(F.hitP);
    const fl = Math.sin(t * 16) * .6; crow.wl.rotation.z = fl; crow.wr.rotation.z = -fl;
    F.domeMat.uniforms.hitT.value = -1;
  } else {
    const k = t - 41.2; crow.g.position.set(F.hitP.x - k * 1.5, F.hitP.y - 4.9 * k * k, F.hitP.z + k * 4); crow.g.rotation.x += dt * 6; crow.g.rotation.z += dt * 4;
    crow.wl.rotation.z = .9; crow.wr.rotation.z = -.9;
    F.domeMat.uniforms.hitT.value = k;
    if (k < dt * 1.2) { F.feathers.burst(70); shake(.15); }
  }
  F.feathers.update(dt, t);
  // portal opens 44.6 → 47.1
  const open = end ? 0 : sm(44.6, 47.1, t);
  F.portalMat.uniforms.open.value = open * (1 + Math.sin(t * 9) * .01);
  F.portalLight.intensity = open * 3 + (open > 0 && open < 1 ? Math.random() * 3 : 0);
  F.ringMat.emissiveIntensity = .15 + open * .7;
  const boltOn = t > 44.5 && t < 48.2 && !end;
  F.bolts.visible = boltOn;
  if (boltOn && Math.random() < .5) {
    let j = 0;
    for (let b = 0; b < 4; b++) { let a = rr(0, 6.28), r = 7.4 * Math.max(open, .2), x = Math.cos(a) * r, y = Math.sin(a) * r;
      for (let k = 0; k < 16; k++) { const nx = x + rr(-1.2, 1.2), ny = y + rr(-1.2, 1.2); F.boltPos.set([x, y, .3, nx, ny, .3], j); j += 6; x = nx; y = ny; } }
    F.bolts.geometry.attributes.position.needsUpdate = true;
  }
  if (Math.abs(t - 47.1) < dt * .6) { F.portalSparks.burst(200); shake(.5); }
  if (t > 44.6 && t < 47 && Math.random() < .3) F.portalSparks.burst(4);
  F.portalSparks.update(dt, t);
  // horde
  for (const h of F.horde) {
    const k = t - h.spawn; h.g.visible = k > 0 && !end;
    if (!h.g.visible) continue;
    const z = 67 - h.v * k;
    h.g.position.set(h.lane + Math.sin(k * .7 + h.phase) * .3, 0, z); h.g.position.y = groundF(h.g.position.x, z); h.g.rotation.y = PI;
    walk(h, t, 1);
    const emerge = sm(0, .6, k); h.g.scale.setScalar((h.kind === 'brute' ? 1.75 : 1) * emerge);
  }
  // guards and archers
  const lock = sm(56.8, 57.6, t);
  for (const sd of F.guards) {
    sd.armL.rotation.x = lerp(-.25, -1.35, lock); sd.armL.rotation.z = lerp(0, -.5, lock);
    sd.armR.rotation.x = lerp(-.3, -.9, lock);
    sd.hips.position.y = .95 + Math.sin(t * 2 + sd.phase) * .01 - lock * .08;
    sd.legL.rotation.x = -lock * .35; sd.legR.rotation.x = lock * .25;
  }
  for (let i = 0; i < F.archers.length; i++) {
    const a = F.archers[i], draw = sm(57.5, 58.5, t) * (1 - sm(63.5, 63.6, t)) + sm(63.8, 64.3, t) * (1 - sm(64.5, 64.6, t)) + sm(64.8, 65.4, t);
    a.armL.rotation.x = -1.45; a.armL.rotation.z = -.15; a.armR.rotation.x = -1.3 - draw * .25; a.armR.rotation.z = draw * .9; a.torso.rotation.x = -.15;
  }
  // the Warden
  const w = F.warden, raise = sm(55.6, 56.5, t), swing = sm(67.0, 67.22, t);
  w.armR.rotation.x = lerp(-.25, -2.75, raise) + swing * 2.2; w.armR.rotation.z = -.1;
  w.sword.rotation.x = lerp(-1.1, 0, raise);
  w.armL.rotation.x = lerp(-.55, -1.25, sm(56.8, 57.6, t)); w.armL.rotation.z = -.35;
  w.hips.position.y = .95 + Math.sin(t * 1.6) * .012;
  w.torso.rotation.y = Math.sin(t * .7) * .03 - swing * .4;
  const lit = sm(55.9, 56.6, t) * (end ? 0 : 1);
  w.bladeMat.emissiveIntensity = lit * 2.6 * (1 + .15 * Math.sin(t * 13));
  w.bladeCore.material.color.copy(HDR(0xffe2a0, .3 + lit * 6));
  w.bladeGlow.material.color.copy(HDR(0xffc060, lit * 1.8));
  w.halo.rotation.z = t * .3;
  w.shieldFlame.update(t, null);
  const cp = w.cape.geometry.attributes.position, cb = w.capeBase;
  for (let i = 0; i < cp.count; i++) { const y = cb[i * 3 + 1], u = -y / 1.5; cp.setZ(i, cb[i * 3 + 2] - u * u * (.35 + .12 * Math.sin(t * 2.4 + u * 3 + cb[i * 3] * 4))); cp.setX(i, cb[i * 3] * (1 + u * .3)); }
  cp.needsUpdate = true; w.cape.geometry.computeVertexNormals();
  F.wardenLight.intensity = .3 + lit * 1.4;
  // the charge
  for (const h of F.charge) {
    const k = t - 61.0; h.g.visible = k > -.1 && t < 74;
    if (!h.g.visible) continue;
    const zc = 9.95 + (h.kind === 'brute' ? .35 : 0);
    let z = h.z0 - Math.max(0, k) * 11.5; let stag = 0;
    if (z < zc) { const over = (zc - z) / 11.5; z = zc + Math.sin(Math.min(over * 6, PI)) * .45; stag = 1; }
    h.g.position.set(h.x, 0, z); h.g.rotation.y = PI;
    walk(h, t, stag ? .5 : 1.4, stag ? .7 : 2.2);
    if (stag) { h.armR.rotation.x = -2.2 + Math.sin(t * 9 + h.phase) * .8; h.torso.rotation.x = .3; }
  }
  if (Math.abs(t - 62.0) < dt * .6) { F.clashSparks.burst(240); shake(.8); }
  F.clashSparks.update(dt, t);
  // arrows
  for (const a of F.arrows) {
    const u = (t - a.t0) / a.dur; a.m.visible = u > 0 && u < 1 && !end;
    if (u <= 0) { a.hit = false; continue; }
    if (u >= 1) { if (!a.hit) { a.hit = true; F._tp.copy(a.p1); F.impacts.burst(14); } continue; }
    const p = arrowAt(a, u), p2 = arrowAt(a, Math.min(1, u + .01)); a.m.position.copy(p); a.m.lookAt(p2);
    F._tp.copy(p); F.trail.burst(2);
  }
  F.trail.update(dt, t); F.impacts.update(dt, t);
  F.ash.update(dt, t); F.embersAir.update(dt, t);
}
const _ap = new V3();
function arrowAt(a, u) { _ap.lerpVectors(a.p0, a.p1, u); _ap.y = lerp(a.p0.y, a.p1.y + .3, u) + Math.sin(u * PI) * 9; return _ap.clone(); }
function groundF(x, z) { if (z < -2) return hillY(x, z); const road = Math.exp(-x * x / 18); return (fbm(x * .06, z * .06) - .5) * 2.4 * (1 - road * .8) * sm(2, 14, z) + (fbm(x * .4, z * .4) - .5) * .25; }

// ========== camera, shake ==========
let shakeAmp = 0;
function shake(a) { shakeAmp = Math.max(shakeAmp, reduced ? a * .25 : a); }
const ease = { io: u => u * u * (3 - 2 * u), o: u => 1 - Math.pow(1 - u, 2.2), i: u => u * u, l: u => u };
function curve(pts) { return pts.length === 1 ? { getPoint: () => pts[0].clone() } : new THREE.CatmullRomCurve3(pts); }
const v = (x, y, z) => new V3(x, y, z);

// ========== shot list ==========
// t0/t1 seconds, scene, camera path, look path, fov, bloom, grade, fade in/out.
const SHOTS = [
  { t0: 0, t1: 6.5, sc: 'A', pos: [v(.0, 1.55, 4.2), v(.15, 1.45, 2.4)], look: [v(0, 1.45, 0), v(0, 1.5, 0)], fov: [32, 30], e: 'o', bl: [.8, .5, .55], ex: 1.0, tint: [1.08, 1, .9], fi: 1.2, fo: .6 },
  { t0: 6.5, t1: 13.5, s0: 7.2, sc: 'B', pos: [v(-2, 1.5, 9), v(2.5, 3, 5)], look: [v(0, .5, -14), v(0, 1.5, -20)], fov: [48, 44], bl: [1.1, .6, .25], ex: 1.05, tint: [.92, .96, 1.1], fi: .6, fo: .6 },
  { t0: 13.5, t1: 23, s0: 35.2, rate: .9, sc: 'F', pos: [v(11, 1.6, 23), v(6, 6, 32), v(0, 22, 52)], look: [v(0, 6, 0), v(0, 10, -10), v(0, 17, -36)], fov: [38, 42], bl: [1.0, .55, .35], ex: 1.05, tint: [1, .98, 1.02], fi: .8, fo: .5 },
  { t0: 23, t1: 27, s0: 16.6, sc: 'C', pos: [v(.3, 1.0, 11), v(-.2, 1.25, 8.6)], look: [v(0, 1.1, 0), v(0, 1.2, 0)], fov: [38, 36], bl: [.9, .5, .3], ex: 1.05, tint: [.96, 1.02, .92], fi: .5, fo: .35 },
  { t0: 27, t1: 31, s0: 24, sc: 'D', pos: [v(0, 1.6, 9), v(0, 1.8, 4)], look: [v(0, 1.8, -10), v(0, 2.0, -18)], fov: [44, 40], roll: .04, bl: [1.3, .5, .2], ex: 1.1, tint: [1.02, .92, 1.1], fi: .35, fo: .35 },
  { t0: 31, t1: 36, s0: 28.4, sc: 'E', pos: [v(2.5, .8, 11), v(1.8, .6, 8.5)], look: [v(-1.5, 4.4, -6), v(-.5, 5.0, -5)], fov: [46, 50], bl: [.6, .55, .7], ex: .95, tint: [1.08, .98, .86], fi: .35, fo: .5 },
  { t0: 36, t1: 41, s0: 44, rate: .9, sc: 'F', pos: [v(7, 2.6, 45), v(4, 3, 50)], look: [v(0, 7, 68), v(0, 7.2, 68)], fov: [44, 40], bl: [1.2, .6, .3], ex: 1.05, tint: [1.06, .96, .94], fi: .4 },
  { t0: 41, t1: 48, s0: 47.6, sc: 'F', pos: [v(-15, 13, 1.4), v(-10, 12.4, 4.5)], look: [v(-2, 3, 40), v(0, 3, 42)], fov: [40, 38], bl: [1.0, .55, .35], ex: 1.05, tint: [1.02, .97, 1] },
  { t0: 48, t1: 58, s0: 54.6, rate: .8, sc: 'F', pos: [v(2.2, 1.0, 18), v(4.4, 1.6, 14.4), v(2.3, 2.6, 8.6)], look: [v(0, 2.5, 12.2), v(0, 2.6, 12.4), v(-1, .8, 40)], fov: [32, 40], bl: [1.15, .55, .3], ex: 1.05, tint: [1.02, 1, .98] },
  { t0: 58, t1: 61, s0: 61.2, rate: .8, sc: 'F', pos: [v(13, 1.7, 16), v(12, 1.8, 15)], look: [v(4.5, 1.2, 10), v(3.5, 1.2, 10)], fov: [38, 40], bl: [1.1, .5, .3], ex: 1.05, tint: [1.02, .98, .98] },
  { t0: 61, t1: 65, s0: 63.3, rate: .85, sc: 'F', pos: [v(-15.3, 12.7, -2.8), v(-15, 13, -2.2)], look: [v(-7, 9, 26), v(-6, 8, 30)], fov: [46, 44], bl: [1.2, .55, .3], ex: 1.05, tint: [1.04, .98, .96] },
  { t0: 65, t1: 69, s0: 64.2, rate: .7, sc: 'F', pos: [v(-2, 8.5, 4.5), v(0, 10.5, 6.5)], look: [v(0, 1, 22), v(0, 1, 28)], fov: [44, 42], bl: [1.1, .55, .3], ex: 1.05, tint: [1.02, .98, .98] },
  { t0: 69, t1: 73.5, s0: 64.9, rate: .6, sc: 'F', pos: [v(1.25, 3.0, 13.6), v(.9, 3.25, 13.3)], look: 'blade', fov: [30, 26], bl: [1.4, .6, .25], ex: 1.05, tint: [1.04, 1, .95], fo: .2 },
  { t0: 73.5, t1: 80, s0: 58, rate: .42, sc: 'F', pos: [v(-4, 1.2, 22), v(-3, 2.6, 30)], look: [v(0, 2.8, 10), v(0, 5, 0)], fov: [30, 38], bl: [1.1, .55, .3], ex: 1.05, tint: [1.02, 1, .98], fi: .3, fo: .2 },
  { t0: 80, t1: 87, s0: 66.4, sc: 'F', pos: [v(11, 0, 15), v(5, 0, 7)], rel: 'flame', look: 'flame', fov: [40, 46], bl: [1.2, .7, .2], ex: 1.05, tint: [1.05, 1, .92], fi: .3 },
  { t0: 87, t1: 1e9, s0: 74, sc: 'F', pos: [v(-30, 16, 46), v(-22, 18, 40)], look: [v(0, 13, -24), v(0, 14, -26)], span: 30, fov: [40, 40], bl: [1.0, .6, .35], ex: .85, tint: [1, .98, 1] }
];
for (const s of SHOTS) { if (Array.isArray(s.pos)) s.cp = curve(s.pos); if (Array.isArray(s.look)) s.cl = curve(s.look); }
// the song's own lyrics and timings (Hold Porten)
const SUBS = [
  [2.5, 9.8, 'Når mørket presser mot murene, står én port igjen.'],
  [10.1, 14.9, 'Bak den ligger alt vi har lovet å beskytte.'],
  [14.9, 20.4, 'Et hjem. Et håp. En morgen vi ennå ikke har sett.'],
  [29.3, 33.4, 'De sier at flammen snart vil slukne.'],
  [33.4, 36.2, 'Men den trenger ikke være stor.'],
  [36.2, 41.0, 'Den trenger bare å leve i én hånd, og finne veien til den neste.'],
  [48.2, 56.5, 'Så hold linjen. Hold fast ved hverandre.'],
  [73.6, 83.8, 'Når natten krever alt, skal vi svare med det eneste den ikke kan ta:'],
  [84.1, 87.2, 'Vi står her.'],
  [87.2, 90.2, 'Vi holder porten.']
];
const PLACES = [[14.2, 19.6, 'DEN SISTE BYEN', 'Der flammen brenner'], [23.3, 26.7, 'ASKEMYR', 'Den første verdenen'], [27.3, 30.8, 'VRANGHEIM', 'Den andre verdenen'], [31.3, 35.4, 'URHEIM', 'Den tredje verdenen']];
const END_T = 90.4;
const sceneT = (sh, t) => (sh.s0 ?? sh.t0) + (t - sh.t0) * (sh.rate ?? 1);

function shotAt(t) { for (let i = SHOTS.length - 1; i >= 0; i--) if (t >= SHOTS[i].t0) return SHOTS[i]; return SHOTS[0]; }
const _look = new V3(), _wp = new V3();
function applyShot(sh, t, dt, st) {
  const span = sh.span || (sh.t1 - sh.t0), u0 = clamp((t - sh.t0) / span, 0, 1), u = (ease[sh.e] || ease.io)(u0);
  if (sh.rel === 'flame') { _wp.copy(F.flamePos); camera.position.copy(sh.cp.getPoint(u)).add(_wp); }
  else camera.position.copy(sh.cp.getPoint(u));
  if (sh.look === 'blade') { F.warden.blade.getWorldPosition(_look); _look.y += .2; }
  else if (sh.look === 'flame') { _look.copy(F.flamePos); _look.y += 2.5 + sm(68, 72, st) * 4; }
  else _look.copy(sh.cl.getPoint(u));
  // handheld drift and shake
  const hd = .02 + (sh.sc === 'F' ? .02 : 0);
  camera.position.x += Math.sin(t * .9) * hd + (Math.random() - .5) * shakeAmp * .3;
  camera.position.y += Math.sin(t * 1.3 + 1) * hd + (Math.random() - .5) * shakeAmp * .3;
  camera.lookAt(_look);
  if (sh.roll) camera.rotateZ(Math.sin(t * .5) * sh.roll);
  camera.rotateZ((Math.random() - .5) * shakeAmp * .02);
  shakeAmp *= Math.pow(.02, dt);
  // fov adapts to tall phone screens
  const vf = lerp(sh.fov[0], sh.fov[1], u), asp = camera.aspect, k = asp < 1.6 ? Math.pow(1.6 / asp, .62) : 1;
  camera.fov = 2 * Math.atan(Math.tan(vf * PI / 360) * k) * 180 / PI; camera.updateProjectionMatrix();
  U.ptScale.value = H * R.getPixelRatio() / (2 * Math.tan(camera.fov * PI / 360));
  // grade
  bloom.strength = sh.bl[0]; bloom.radius = sh.bl[1]; bloom.threshold = sh.bl[2];
  FU.exposure.value = sh.ex; FU.tint.value.set(...sh.tint);
  const fi = sh.fi ?? 0, fo = sh.fo ?? 0;
  let f = 1; if (fi > 0) f = Math.min(f, sm(sh.t0, sh.t0 + fi, t)); if (fo > 0) f = Math.min(f, 1 - sm(sh.t1 - fo, sh.t1, t));
  FU.fade.value = f;
  // flare to white, then back to the city at night
  FU.white.value = sh.sc === 'F' ? sm(71.6, 73.4, st) * (1 - sm(74.2, 76.2, st)) : 0;
  if (sh.sc === 'F' && st > 68 && st < 74) bloom.strength = sh.bl[0] + sm(70, 73, st) * 1.0;
  FU.bars.value = camera.aspect > 1.25 ? clamp((1 - camera.aspect / 2.39) / 2, 0, .12) : 0;
  renderPass.scene = scenes[sh.sc];
}

// ========== sound (Web Audio, all synthesized) ==========
const A = { on: false };
function initAudio() {
  const Ctx = window.AudioContext || window.webkitAudioContext; if (!Ctx) return false;
  const c = new Ctx(); A.ctx = c;
  const comp = c.createDynamicsCompressor(); comp.threshold.value = -10; comp.knee.value = 10; comp.ratio.value = 3; comp.attack.value = .005; comp.release.value = .25; comp.connect(c.destination);
  A.master = c.createGain(); A.master.gain.value = 1; A.master.connect(comp);
  const len = c.sampleRate * 4, ir = c.createBuffer(2, len, c.sampleRate);
  for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.8); }
  A.rev = c.createConvolver(); A.rev.buffer = ir; const wet = c.createGain(); wet.gain.value = .55; A.rev.connect(wet); wet.connect(A.master);
  const mkBus = () => { const b = c.createGain(); b.connect(A.master); const sd = c.createGain(); sd.gain.value = .6; b.connect(sd); sd.connect(A.rev); return b; };
  A.intro = mkBus(); A.intro.gain.value = .5; A.bus = A.intro;
  A.songGain = c.createGain(); A.songGain.connect(A.master);
  const nb = c.createBuffer(1, c.sampleRate * 3, c.sampleRate), nd = nb.getChannelData(0); for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1; A.noise = nb;
  A.on = false; return true;
}
function loadSong() {
  return fetch('musikk/hold-porten.mp3').then(r => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
    .then(b => new Promise((ok, no) => A.ctx.decodeAudioData(b, ok, no))).then(buf => { A.song = buf; }).catch(e => console.warn('song', e));
}
function playSong(at, offset = 0, fadeIn = 0) {
  if (!A.song) return;
  if (A.src) { try { A.src.stop(); } catch (e) {} }
  const src = A.ctx.createBufferSource(); src.buffer = A.song; src.connect(A.songGain);
  A.songGain.gain.cancelScheduledValues(at); A.songGain.gain.setValueAtTime(fadeIn ? .0001 : 1, at); if (fadeIn) A.songGain.gain.linearRampToValueAtTime(1, at + fadeIn);
  src.start(at, offset); A.src = src;
}
function env(p, t, a, peak, h, r) { p.setValueAtTime(.0001, t); p.linearRampToValueAtTime(peak, t + a); if (h > 0) p.setValueAtTime(peak, t + a + h); p.exponentialRampToValueAtTime(.0001, t + a + h + r); }
function osc(type, f, t, vol, o = {}) {
  const c = A.ctx, s = c.createOscillator(), g = c.createGain(); s.type = type; s.frequency.setValueAtTime(f, t);
  if (o.f2) s.frequency.exponentialRampToValueAtTime(o.f2, t + (o.gl ?? .3)); if (o.det) s.detune.value = o.det;
  const a = o.a ?? .01, h = o.h ?? 0, r = o.r ?? .5; env(g.gain, t, a, vol, h, r);
  let n = s; if (o.lp || o.bp) { const fl = c.createBiquadFilter(); fl.type = o.bp ? 'bandpass' : 'lowpass'; fl.frequency.setValueAtTime(o.lp || o.bp, t); if (o.lp2) fl.frequency.exponentialRampToValueAtTime(o.lp2, t + a + h + r); fl.Q.value = o.q ?? .7; s.connect(fl); n = fl; }
  n.connect(g); g.connect(o.dest || A.bus); s.start(t); s.stop(t + a + h + r + .05);
}
function nz(t, vol, o = {}) {
  const c = A.ctx, s = c.createBufferSource(), fl = c.createBiquadFilter(), g = c.createGain(); s.buffer = A.noise; s.loop = true;
  fl.type = o.type || 'lowpass'; fl.frequency.setValueAtTime(o.f || 800, t); fl.Q.value = o.q ?? .7;
  const a = o.a ?? .005, h = o.h ?? 0, r = o.r ?? .4; if (o.f2) fl.frequency.exponentialRampToValueAtTime(o.f2, t + a + h + r * .8);
  env(g.gain, t, a, vol, h, r); s.connect(fl); fl.connect(g); g.connect(o.dest || A.bus); s.start(t, Math.random() * 2); s.stop(t + a + h + r + .05);
}
const NOTE = n => 440 * Math.pow(2, (n - 69) / 12);
function pad(notes, t, dur, vol, o = {}) {
  const c = A.ctx, a = o.a ?? 1.8, r = o.r ?? 2;
  for (const n of notes) for (const det of [-11, 0, 9]) {
    const s = c.createOscillator(); s.type = 'sawtooth'; s.frequency.value = NOTE(n); s.detune.value = det + (Math.random() - .5) * 4;
    const f1 = c.createBiquadFilter(), f2 = c.createBiquadFilter(), g = c.createGain(); f1.type = f2.type = 'bandpass'; f1.frequency.value = o.f1 ?? 760; f2.frequency.value = o.f2 ?? 1180; f1.Q.value = 5; f2.Q.value = 7;
    const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = o.lp ?? 2200;
    s.connect(lp); lp.connect(f1); lp.connect(f2); f1.connect(g); f2.connect(g); env(g.gain, t, a, vol, Math.max(0, dur - a - r), r); g.connect(o.dest || A.bus);
    s.start(t); s.stop(t + dur + .1);
  }
}
function drone(t, dur) { osc('sawtooth', NOTE(26), t, .16, { lp: 160, a: 4, h: dur - 8, r: 4 }); osc('sawtooth', NOTE(26), t, .14, { det: 9, lp: 190, a: 5, h: dur - 9, r: 4 }); osc('sine', NOTE(38), t, .1, { a: 5, h: dur - 9, r: 4 }); nz(t, .03, { type: 'bandpass', f: 380, q: .5, a: 4, h: dur - 8, r: 4 }); }
function boom(t, k = 1) { osc('sine', 62, t, .9 * k, { f2: 30, gl: 1, r: 3.2 }); nz(t, .5 * k, { f: 500, f2: 50, r: 1.6 }); osc('triangle', 45, t, .3 * k, { r: 2.5 }); }
function drum(t, k = .6) { osc('sine', 140, t, k, { f2: 46, gl: .16, r: .8 }); nz(t, .28 * k, { f: 1100, f2: 160, r: .16 }); }
function ignite(t) { nz(t, .3, { type: 'bandpass', f: 250, f2: 2800, q: 1.4, a: .2, r: .9 }); osc('sine', 880, t + .1, .045, { r: 3 }); osc('sine', 1318, t + .15, .03, { r: 3 }); }
function puff(t) { nz(t, .26, { f: 700, f2: 120, a: .02, r: .9 }); osc('sine', 220, t, .05, { f2: 98, gl: 1.2, r: 1.3 }); }
function groan(t) { osc('sawtooth', 74, t, .1, { f2: 52, gl: 1.4, lp: 340, a: .35, h: .3, r: 1 }); osc('sawtooth', 77, t, .08, { f2: 55, gl: 1.4, lp: 300, a: .4, h: .2, r: 1 }); nz(t, .06, { type: 'bandpass', f: 300, q: 2, a: .3, r: 1 }); }
function tick(t) { osc('sine', 2200 + Math.random() * 1400, t, .03, { r: .35 }); osc('sine', 3300 + Math.random() * 900, t + .02, .015, { r: .4 }); }
function buzz(t, dur) { osc('square', 196, t, .012, { a: 1, h: dur - 2, r: 1, lp: 900 }); osc('square', 199.5, t, .012, { a: 1, h: dur - 2, r: 1, lp: 900 }); }
function thud(t, k = 1) { osc('sine', 70, t, .7 * k, { f2: 28, gl: .5, r: 1 }); nz(t, .35 * k, { f: 260, f2: 60, r: .5 }); }
function roar(t) {
  osc('sawtooth', 150, t, .32, { f2: 70, gl: 2.4, lp: 1400, lp2: 400, q: 2, a: .12, h: 1.1, r: 1.3 });
  osc('sawtooth', 157, t, .26, { f2: 66, gl: 2.4, lp: 1200, lp2: 380, q: 2, a: .14, h: 1.1, r: 1.3 });
  osc('square', 48, t, .18, { a: .2, h: 1, r: 1.3, lp: 300 });
  nz(t, .34, { type: 'bandpass', f: 900, f2: 280, q: 1.2, a: .1, h: 1, r: 1.4 });
}
function caw(t) { for (const d of [0, .32]) osc('sawtooth', 1050, t + d, .07, { f2: 640, gl: .22, bp: 1500, q: 3, r: .26 }); }
function shimmer(t, k = 1) { for (let i = 0; i < 7; i++) osc('sine', 900 + Math.random() * 3600, t + i * .015, .03 * k, { r: 1.2 + Math.random() * 1.4 }); nz(t, .06 * k, { type: 'highpass', f: 5000, r: 1.2 }); }
function tear(t, dur) { nz(t, .32, { type: 'bandpass', f: 140, f2: 2200, q: 2.2, a: dur * .85, r: .5 }); for (let i = 0; i < 26; i++) nz(t + Math.random() * dur, .09, { type: 'highpass', f: 2500, r: .05 + Math.random() * .08 }); osc('sawtooth', 55, t, .14, { f2: 110, gl: dur, lp: 600, a: dur * .8, r: .6 }); }
function horn(t, n, dur, vol = .11) { osc('sawtooth', NOTE(n), t, vol, { lp: 1100, a: .3, h: dur, r: .9 }); osc('sawtooth', NOTE(n) * 1.004, t, vol * .8, { lp: 900, a: .35, h: dur, r: .9 }); osc('sine', NOTE(n - 12), t, vol * .6, { a: .3, h: dur, r: .9 }); }
function shing(t) { nz(t, .22, { type: 'highpass', f: 4000, r: .6 }); osc('sine', 2637, t, .05, { r: 2 }); osc('sine', 3951, t, .03, { r: 1.5 }); osc('triangle', 1318, t, .04, { r: 1.8 }); }
function clash(t) { nz(t, .55, { type: 'bandpass', f: 2600, q: .9, r: .3 }); for (const f of [880, 1320, 2093, 2794]) osc('sine', f * (1 + Math.random() * .02), t, .05, { r: .5 }); thud(t, .8); }
function whoosh(t, k = .12) { nz(t, k, { type: 'bandpass', f: 700, f2: 2600, q: 1.5, a: .15, r: .45 }); }
function swish(t) { nz(t, .32, { type: 'bandpass', f: 400, f2: 3400, q: 1.2, a: .05, r: .3 }); }
function rumble(t, dur, k = .12) { nz(t, k, { f: 140, a: 1.5, h: dur - 3, r: 1.5 }); }

const EVENTS = [];
const ev = (t, fn) => EVENTS.push({ t, fn });
// sound effects on top of the song, in film time
function buildScore() {
  EVENTS.length = 0;
  ev(1.5, ignite);
  for (let k = 0; k < 9; k++) ev(7.6 + k * .62, puff);
  ev(17.6, caw); ev(18.7, caw); ev(20.2, w => shimmer(w, 1.2));
  [23.3, 24.0, 24.9, 25.8].forEach(x => ev(x, groan));
  for (let x = 27.3; x < 30.8; x += .35 + Math.random() * .3) ev(x, tick);
  [32.2, 32.95, 33.7].forEach(x => ev(x, w => thud(w, .8)));
  ev(33.95, roar); ev(34.1, w => thud(w, 1));
  ev(36.55, w => tear(w, 2.9));
  ev(49.6, shing); ev(51.1, w => clash(w));
  ev(59.0, clash);
  [61.3, 61.5, 61.7, 62.5, 62.7, 62.9].forEach(x => ev(x, w => whoosh(w, .14)));
  ev(72.5, swish); ev(72.55, w => shimmer(w, 1));
}

// ========== player ==========
const ui = { sub: root.querySelector('.lf-subs span'), place: root.querySelector('.lf-place'), placeName: root.querySelector('.lf-place b'), placeSub: root.querySelector('.lf-place i'),
  skip: root.querySelector('.lf-skip'), load: root.querySelector('.lf-load') };
let paused = false, playing = false, clock0 = 0, audio0 = 0, evI = 0, last = 0, T = 0, endShown = false, curSub = -1, curPlace = -1, built = false;
function now() { return A.on ? A.ctx.currentTime - audio0 : performance.now() / 1000 - clock0; }
function start(withSound) {
  rnd = mulberry32(1777);
  if (A.ctx && withSound) { A.on = true; A.ctx.resume(); const c = A.ctx.currentTime; A.intro.gain.setValueAtTime(.5, c); audio0 = c + .15; playSong(audio0); }
  else A.on = false;
  clock0 = performance.now() / 1000 + .15; evI = 0; endShown = false; curSub = -1; curPlace = -1;
  playing = true; last = -1;
}
let dead = false, raf = 0;
function done(cb = true) {
  if (dead) return; dead = true; cancelAnimationFrame(raf);
  removeEventListener('resize', resize); removeEventListener('keydown', onKey);
  if (A.ctx) { const c = A.ctx.currentTime, ctx = A.ctx; A.master.gain.cancelScheduledValues(c); A.master.gain.setValueAtTime(A.master.gain.value, c); A.master.gain.linearRampToValueAtTime(.0001, c + .5); setTimeout(() => { try { ctx.close(); } catch (e) {} }, 700); }
  setTimeout(() => { try { R.dispose(); R.forceContextLoss(); } catch (e) {} }, 650);
  if (cb) onDone();
}
function showEnd() { if (endShown) return; endShown = true; done(); }
function skip() { done(); }
const onKey = e => { if (e.key === 'Escape') skip(); };
ui.skip.addEventListener('click', skip);
addEventListener('keydown', onKey);

function step(t, dt) {
  T = t; U.time.value = t;
  const sh = shotAt(t), st = sceneT(sh, t);
  U.time.value = st;
  scenes[sh.sc].userData.update(st, dt * (sh.rate ?? 1));
  applyShot(sh, t, dt, st);
  FU.time.value = t;
}
function loop() {
  if (dead) return;
  raf = requestAnimationFrame(loop);
  if (!built || paused) return;
  let t, dt;
  if (playing) {
    t = now(); if (t < 0) t = 0;
    dt = last < 0 ? 1 / 60 : clamp(t - last, 0, .06); last = t;
    if (A.on) { const ahead = t + 1.0; while (evI < EVENTS.length && EVENTS[evI].t <= ahead) { const e = EVENTS[evI++]; if (e.t >= t - .05) e.fn(audio0 + e.t); } }
    if (t >= END_T) showEnd();
    // subtitles and place names
    let si = SUBS.findIndex(s => t >= s[0] && t < s[1]);
    if (si !== curSub) { curSub = si; if (si >= 0) { ui.sub.textContent = SUBS[si][2]; ui.sub.classList.add('on'); } else ui.sub.classList.remove('on'); }
    let pi = PLACES.findIndex(s => t >= s[0] && t < s[1]);
    if (pi !== curPlace) { curPlace = pi; if (pi >= 0) { ui.placeName.textContent = PLACES[pi][2]; ui.placeSub.textContent = PLACES[pi][3]; ui.place.classList.add('on'); } else ui.place.classList.remove('on'); }
  } else { t = 1.1 + (performance.now() / 1000) * 0; dt = 1 / 60; }
  if (!playing) { // behind the start card: the single ember, barely lit
    step(2.6, dt); FU.fade.value = .55;
  } else step(t, dt);
  composer.render();
}
const evSort = () => EVENTS.sort((a, b) => a.t - b.t);
// sound must be unlocked inside the tap that started the film
if (withSound) { initAudio(); if (A.ctx) A.ctx.resume(); }
setTimeout(() => {
  try {
    initMats(); buildA(); buildB(); buildC(); buildD(); buildE(); buildF(); buildScore(); evSort();
    for (const k in scenes) { const sh = SHOTS.find(s => s.sc === k); if (sh && sh.cp) { camera.position.copy(sh.cp.getPoint(0)); camera.lookAt(sh.cl ? sh.cl.getPoint(0) : F.flamePos); } R.compile(scenes[k], camera); }
  } catch (e) { console.error(e); done(); return; }
  const go = () => { if (dead) return; built = true; ui.load.hidden = true; start(withSound && !!A.ctx); raf = requestAnimationFrame(loop); };
  if (withSound && A.ctx) prefetch().then(b => b && new Promise((ok, no) => A.ctx.decodeAudioData(b.slice(0), ok, no)).then(x => { A.song = x; }).catch(e => console.warn('film decode', e))).then(go);
  else go();
}, 60);
window.__film = { seek(t, frames = 20) { paused = true; playing = true; built = true; ui.load.hidden = true; for (let i = 0; i < frames; i++) step(t - (frames - i) / 60, 1 / 60); step(t, 1 / 60); composer.render(); }, get t() { return T; } };
return { skip, kill: () => done(false) };
}

let cur = null;
return {
  prefetch,
  get playing() { return !!cur; },
  play(onDone, withSound = true) {
    if (cur) return;
    const root = document.createElement('div'); root.className = 'lf-film'; document.body.appendChild(root);
    window.__filmOn = true;
    cur = makeFilm(root, () => {
      cur = null; window.__filmOn = false;
      try { localStorage.setItem('lf-intro-seen', '1'); } catch (e) {}
      root.classList.add('out'); setTimeout(() => root.remove(), 600);
      if (onDone) onDone();
    }, withSound);
  },
  stop() { if (!cur) return; const c = cur; cur = null; window.__filmOn = false; c.kill(); document.querySelectorAll('.lf-film').forEach(n => n.remove()); }
};
})();
