# Introfilmen på startskjermen (versjon 49). Rune: «yes. allow to skip it too».
# - Første gang Start trykkes, spilles filmen (tools/intro_film.js, kilde prototype/intro.html) med sangen «Hold porten».
#   Når den er ferdig eller «Hopp over» trykkes, starter spillet som før.
# - Etterpå går Start rett inn i spillet; «Se introfilmen» i startboksen spiller den igjen.
# - Spillets egen tegning står stille mens filmen går (window.__filmOn), så telefonen bare tegner én ting.
# - musikk/hold-porten.mp3 må publiseres sammen med siden (Artifact files).
# Bruk: python3 tools/intro_film.py inn.html ut.html  (inn = siste versjon av Kamptest II)
import os, sys
from patch import sub

HERE = os.path.dirname(os.path.abspath(__file__))

PP = ''.join(f'<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/{p}"></script>\n' for p in [
    'shaders/CopyShader.js', 'shaders/LuminosityHighPassShader.js', 'postprocessing/EffectComposer.js',
    'postprocessing/RenderPass.js', 'postprocessing/ShaderPass.js', 'postprocessing/UnrealBloomPass.js'])

CSS = """/* Introfilmen (versjon 49). */
.lf-film { position: fixed; inset: 0; z-index: 80; background: #07080b; transition: opacity .55s ease; font-family: 'Cormorant Garamond', 'Iowan Old Style', Georgia, serif; }
.lf-film.out { opacity: 0; pointer-events: none; }
.lf-film canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.lf-subs { position: absolute; left: 0; right: 0; bottom: calc(9vh + env(safe-area-inset-bottom, 0px)); text-align: center; pointer-events: none; padding: 0 max(20px, env(safe-area-inset-right, 0px)) 0 max(20px, env(safe-area-inset-left, 0px)); }
.lf-subs span { display: inline-block; max-width: 30ch; font-style: italic; font-weight: 500; font-size: clamp(21px, 3.4vw, 34px); line-height: 1.25; color: #efe6d2;
  text-shadow: 0 2px 14px rgba(0, 0, 0, .9), 0 0 2px rgba(0, 0, 0, .9); opacity: 0; transition: opacity .9s ease; text-wrap: balance; }
.lf-subs span.on { opacity: 1; }
.lf-place { position: absolute; top: calc(11vh + env(safe-area-inset-top, 0px)); left: max(24px, env(safe-area-inset-left, 0px)); display: flex; flex-direction: column; gap: 8px; pointer-events: none; opacity: 0; transition: opacity 1.2s ease; }
.lf-place.on { opacity: 1; }
.lf-place b { font-family: var(--display); font-weight: 600; font-size: clamp(15px, 2vw, 20px); letter-spacing: .42em; color: #ecc970; text-shadow: 0 0 16px rgba(0, 0, 0, .8); }
.lf-place i { font-style: italic; font-size: clamp(14px, 1.7vw, 17px); color: #9c938a; letter-spacing: .04em; }
.lf-place .rule { width: 56px; height: 1px; background: linear-gradient(90deg, #e2a23b, transparent); }
.lf-skip { position: absolute; top: calc(14px + env(safe-area-inset-top, 0px)); right: calc(14px + env(safe-area-inset-right, 0px)); z-index: 2; font: 600 12px/1 var(--display); letter-spacing: .16em; text-transform: uppercase;
  color: #efe6d2; background: rgba(7, 8, 11, .5); border: 1px solid rgba(236, 201, 112, .45); border-radius: 999px; padding: 11px 18px; cursor: pointer; }
.lf-skip:hover, .lf-skip:focus-visible { border-color: #ecc970; outline: none; }
.lf-load { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #9c938a; font-style: italic; font-size: 19px; }
.intro-film { background: none; border: 0; color: var(--muted); font: italic 15px var(--body); text-decoration: underline; text-underline-offset: 3px; padding: 4px; cursor: pointer; }
.intro-film:hover, .intro-film:focus-visible { color: var(--fg); outline: none; }

/* Startskjerm (versjon 46). */"""


def patch(s):
    film = open(os.path.join(HERE, 'intro_film.js')).read()
    s = sub(s, 'family=IBM+Plex+Mono:wght@400;500&display=swap">',
            'family=IBM+Plex+Mono:wght@400;500&family=Cormorant+Garamond:ital,wght@1,500&display=swap">')
    s = sub(s, '/* Startskjerm (versjon 46). */', CSS)
    s = sub(s, '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n<script>',
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n' + PP + '<script>\n' + film + '</script>\n<script>')
    # the game stands still while the film plays
    s = sub(s, """  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);""", """  function frame(now) {
    if (window.__filmOn) { last = now; requestAnimationFrame(frame); return; }
    const dt = Math.min(0.05, (now - last) / 1000);""")
    s = sub(s, """    <button type="button" class="intro-go" id="intro-go">Start</button></div>`;""",
            """    <button type="button" class="intro-go" id="intro-go">Start</button>
    <button type="button" class="intro-film" id="intro-film">Se introfilmen</button></div>`;""")
    s = sub(s, """  function closeIntro() {
    if (!state.intro) return;""", """  function closeIntro() {
    if (!state.intro) return;
    if (window.LastFlameFilm && LastFlameFilm.playing) LastFlameFilm.stop();""")
    s = sub(s, """  introEl.addEventListener('click', e => { if (e.target.closest('#intro-go')) closeIntro(); });""",
            """  // Første Start spiller introfilmen, så går spillet i gang. «Hopp over» hopper rett inn.
  const film = () => window.LastFlameFilm;
  introEl.addEventListener('click', e => {
    if (e.target.closest('#intro-film')) { if (film()) film().play(null); return; }
    if (e.target.closest('#intro-go')) { if (film() && !store.get('lf-intro-seen')) film().play(closeIntro); else closeIntro(); }
  });
  if (state.intro && !store.get('lf-intro-seen')) setTimeout(() => film() && film().prefetch(), 1500);""")
    return s


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    s = open(src).read()
    # an artifact read comes wrapped in the publish skeleton; publish the page body only
    if s.startswith('<!doctype html><html><head>') and '<body>\n' in s:
        s = s.split('<body>\n', 1)[1]
        s = s.rsplit('</body></html>', 1)[0]
    open(out, 'w').write(patch(s))
    print('ok', out, len(s))
