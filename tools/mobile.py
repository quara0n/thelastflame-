"""Phone layout for The Last Flame prototype: a compact HUD, an order bar docked to the bottom of the screen,
and a camera pulled back far enough to show the battlefield on a narrow screen. Applied by build_v2.py."""
from patch import sub

PHONE_CSS = """
/* Telefon: kompakt HUD, ordrelinjen festet nederst på skjermen, og mer av slagmarken synlig. */
@media (max-width: 600px) {
  .stage { height: 68vh; min-height: 380px; }
  .hud { top: 6px; left: 6px; right: 6px; gap: 4px; }
  .hud-l .res-grid { gap: 3px; }
  .hud-l .res { min-width: 0; padding: 3px 5px 2px; }
  .hud-l .res .rn { font-size: 8.5px; }
  .hud-l .res b { font-size: 12.5px; }
  .hud-l .res em, .hud-l .res-foot { display: none; }
  .hud-r { gap: 3px; }
  .hud-main, .hud-sub { gap: 3px; }
  .pill, .pill.big { padding: 3px 8px; font-size: 11px; gap: 5px; }
  .pill.big b { font-size: 12px; }
  .gatebar { width: 40px; }
  .camjump button { padding: 2px 7px; font-size: 11px; }
  #cam-village, #cam-flame, #snd-music { display: none; }
  .ordermenu { position: fixed; left: 0; right: 0; bottom: 0; top: auto; transform: none; width: auto; max-height: 55vh; overflow-y: auto;
    border-radius: 12px 12px 0 0; padding: 8px 10px calc(8px + env(safe-area-inset-bottom, 0px)); gap: 6px; z-index: 20; }
  .om-head { min-width: 0; flex: 1 1 100%; flex-direction: row; flex-wrap: wrap; gap: 2px 8px; align-items: baseline; }
  .om-tip { display: none; }
  .om-orders { flex: 1 1 100%; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px; }
  .om-orders button { padding: 6px; font-size: 12px; gap: 5px; min-width: 0; }
  .om-orders span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .om-orders kbd { display: none; }
  .om-up { flex-wrap: wrap; gap: 4px 8px; }
  .om-up button { flex: 1 1 100%; justify-content: center; }
  .om-up button .cost span { color: var(--flame-ink); font-weight: 600; }
  .om-up span { flex: 1 1 100%; }
  .om-foot { flex-wrap: wrap; gap: 6px; }
  .om-dl { flex: 1 1 100%; }
  .om-foot button { flex: 1 1 0; }
  .toast { top: 96px; font-size: 12px; }
  .bpop { top: 96px; max-height: calc(100% - 110px); }
}
"""


def apply(s):
    s = sub(s, "@media (max-width: 380px) { .palette, .foes { grid-template-columns: 1fr; } }",
               "@media (max-width: 380px) { .palette, .foes { grid-template-columns: 1fr; } }" + PHONE_CSS)
    s = sub(s, "Hold ut i tjue waves gjennom to verdener.", "Hold ut i tretti waves gjennom tre verdener.")
    # Portrait screens show less of the field sideways; pull the camera back.
    s = sub(s, "  const cam = { tx: 0, tz: -3, yaw: 0, pitch: 0.8, dist: 56 };",
               "  const PHONE = window.matchMedia('(max-width: 600px)').matches;\n  const FIELD_DIST = PHONE ? 72 : 56, FIELD_TZ = PHONE ? 1 : -3;\n  const cam = { tx: 0, tz: FIELD_TZ, yaw: 0, pitch: 0.8, dist: FIELD_DIST };")
    s = sub(s, "  $('#cam-field').onclick = () => camGoto(0, -3, 56, 0.8);", "  $('#cam-field').onclick = () => camGoto(0, FIELD_TZ, FIELD_DIST, 0.8);")
    return s
