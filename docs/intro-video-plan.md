# The Last Flame – intro video plan (14 Oct 2026)

Goal: a 60–90 second cinematic in the style of LOTR / Diablo / Game of Thrones openings. It plays on its own when the game opens, inside the start box from version 46 (`.intro-media`), and ends on the logo and the Start button.

## 1. Four ways to make it

| Route | What it is | Look | Cost / effort |
|---|---|---|---|
| **A. AI video (recommended)** | Generate concept stills of each shot, animate them into 5–10 s clips with an image-to-video model (Kling, Veo, Seedance and similar), add narration and music, cut it together. Higgsfield is already connected in this project, so Claude can do the whole thing from here. | Closest to real Diablo/GoT trailers. Weak spot: the same character can drift between shots, so keep faces small and use the Warden reference sheet. | Credits only, roughly the price of 15–25 clips (a few dozen dollars). A day or two of back-and-forth to pick the good takes. |
| B. In-engine (three.js) | A scripted camera flight through the real game scene: portal opening, creatures marching, the gate, the flame. Runs live in the page, no video file. | Looks like the game, not like a movie. Far from LOTR quality with today's simple models. | Free. Claude can build it. Grows better as the models get better. |
| C. Commission | A 3D/motion artist or studio on Fiverr, Upwork or ArtStation. | Can be very good, but real Blizzard-level is out of reach. | About 500–3,000 USD for 60 s of decent 3D animation; 5,000+ for high-end. Weeks. |
| D. Hybrid | AI video for the big "myth" shots (the fallen worlds, the flame), then a cut into the real game camera at the end, flying down to the gate as the Start button appears. | Movie feel plus a clear "this is the game". | Route A's cost plus a small three.js piece. |

**Recommendation:** start with A, and finish it as D later. AI video gives the epic feel now, and the last shot (camera dives to the gate, the start box appears) can move into the engine when the real models are in.

## 2. Draft storyboard (about 75 s)

Look: "detailed stylized". The flame's side is warm gold and white; the enemies glow dull red and ashy. Narration in Norwegian, a deep, calm voice (Galadriel in the LOTR prologue is the reference).

| # | Time | Picture | Narration (Norwegian) |
|---|---|---|---|
| 1 | 0–6 s | Black. One small golden flame lights up in the dark. Low drum. | «Før verdenene falt, fantes det tusen flammer.» |
| 2 | 6–14 s | Wide shot: many worlds as floating islands, each with a flame. One by one they go out and turn grey. | «Én etter én slukket de.» |
| 3 | 14–22 s | Askemyr: ash falling over a poison swamp, husks rising from the mud, red cracks in their skin. | «Askemyr ble til aske og gift.» |
| 4 | 22–28 s | Vrangheim: a twisted forest, purple skin, magenta veins, too many cyan eyes in the dark. | «Vrangheim ble vill.» |
| 5 | 28–34 s | Urheim: a tyrant roars in steaming amber jungle, fossil plates on its back. | «I Urheim brast tiden.» |
| 6 | 34–42 s | The last city on a cliff, the huge gate and towers (Helm's Deep feel), and the flame in the citadel. The dome shimmers orange as an ash crow hits it. | «Men én flamme brenner fortsatt.» |
| 7 | 42–50 s | The portal tears open in front of the gate. Thirty creatures pour out. Wide, slow, scary. | «Og alt som falt, kommer for å slukke den.» |
| 8 | 50–60 s | The Warden: white and gold, halo, the flame's sword and shield. He turns toward the portal. Behind him: Shieldguards lock shields, archers draw on the wall. Music swells. | «Hold porten.» |
| 9 | 60–68 s | Fast cuts: shield wall meets the charge, fire arrows, the sword glowing gold. | «Vokt flammen.» |
| 10 | 68–75 s | The flame flares, everything goes white, then the logo «The Last Flame» and the Start button. | (silence, one deep hit) |

## 3. How it plugs into the game

- The video goes into the start box (`.intro-media` in `tools/intro.py`), replacing the shield. The CSS for `video` is already there.
- **Autoplay rules:** browsers, and phones most of all, only autoplay video that is muted (`autoplay muted playsinline`). So: the video starts silent on its own, with a small "🔊 Lyd" button. Tapping it turns sound on (the first tap also unlocks the game music, same trick as in version 8).
- Alternative: show a big «Spill av» first, so the video starts with sound after one tap. That gives the best first impression, and the video is half the experience without the narration. **I lean towards this** for a narrated intro.
- **Skip:** «Hopp over» in the corner from the first second, and tapping Start skips too. After the first time, the game remembers it and shows only the logo and Start (with a «Se intro» link).
- **Phone size:** 1080p, H.264 MP4, about 1.5–2.5 Mbps, so 75 s ≈ 15–25 MB. Also a 720p version for phones (≈ 8–12 MB), chosen by screen size. A poster image (the first frame) shows while it loads, and the game does not wait for the video.
- The artifact limit is 16 MB per page and 15 MB per file, so the video is published as a separate file next to the page (like the music in `musikk/`), and the phone version should stay under 15 MB.
- Shape: the start box is narrow on a phone. Film in 16:9 for desktop and crop a 9:16 or 4:5 version for phones, or make the box full screen while the video plays (recommended: full screen, the box comes in at the end).

## 4. Next steps if Rune says go

1. Agree on the storyboard (cut or add shots, change the narration).
2. Make a still for each shot (Claude, Higgsfield) and let Rune pick.
3. Animate the chosen stills, two or three takes each, and pick the best.
4. Narration (AI voice in Norwegian, or Rune's own voice) and music (one of the existing tracks or a new epic one).
5. Cut it together (ffmpeg), make the phone version, and add it to the start screen with sound button, skip and "seen before".
