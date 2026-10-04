"""Wave line-up, 4 Oct 2026: 30 creatures per wave, and the new species is the clear majority, with only a few
of earlier kinds. Giants (Colossus, Treant, Urdragon, Tyrant, Earthshaker) and carriers (Broodmother) count heavier:
6–10 of them plus smaller creatures. Boss waves: the boss + 29 escorts. Applied by build_v2.py after world3.py."""
import re
from patch import sub

# (stil, [(type, antall, rolle)], ekstra)
W = [
  # World 1 – Askemyr
  ("Horde",      [("husk", 30, "front")], {}),
  ("Sverm",      [("spider", 22, "front"), ("husk", 8, "back")], {}),
  ("Spytt",      [("spitter", 20, "back"), ("husk", 10, "front")], {}),
  ("Kile",       [("brute", 18, "front"), ("husk", 8, "back"), ("spitter", 4, "back")], {}),
  ("Askekråker", [("ashcrow", 16, "front"), ("serpent", 10, "flank"), ("husk", 4, "front")], {"flyers": True}),
  ("Skall",      [("beetle", 18, "front"), ("spitter", 6, "back"), ("husk", 6, "back")], {}),
  ("Rede",       [("broodmother", 10, "front"), ("spider", 8, "flank"), ("husk", 12, "back")], {}),
  ("Skygger",    [("stalker", 20, "flank"), ("brute", 4, "front"), ("husk", 6, "front")], {}),
  ("Kjemper",    [("colossus", 6, "front"), ("beetle", 6, "front"), ("husk", 18, "back")], {"heavy": True}),
  ("Boss",       [("fallenWarden", 1, "boss"), ("serpent", 10, "flank"), ("spitter", 8, "back"), ("husk", 11, "front")], {"boss": True}),
  # World 2 – Vrangheim
  ("Flokk",      [("wolf", 22, "front"), ("serpent", 4, "flank"), ("spitter", 4, "back")], {"world": 2}),
  ("Stampede",   [("boar", 16, "front"), ("wolf", 14, "flank")], {"world": 2}),
  ("Sverm",      [("locust", 22, "front"), ("boar", 2, "front"), ("wolf", 6, "flank")], {"world": 2}),
  ("Ljåer",      [("mantis", 18, "front"), ("locust", 12, "flank")], {"world": 2}),
  ("Tornkratt",  [("thornling", 20, "front"), ("locust", 6, "flank"), ("mantis", 4, "back")], {"world": 2}),
  ("Råtne røtter", [("treant", 6, "boss"), ("thornling", 18, "front"), ("wolf", 6, "flank")], {"world": 2, "heavy": True}),
  ("Skall",      [("crab", 20, "front"), ("thornling", 6, "back"), ("locust", 4, "flank")], {"world": 2}),
  ("Sang",       [("siren", 18, "back"), ("crab", 10, "front"), ("boar", 2, "front")], {"world": 2}),
  ("Prosesjon",  [("acolyte", 18, "back"), ("crab", 8, "front"), ("mantis", 4, "front")], {"world": 2}),
  ("Boss",       [("warden2", 1, "boss"), ("seraph", 6, "front"), ("acolyte", 8, "back"), ("crab", 15, "front")], {"world": 2, "boss": True}),
  # World 3 – Urheim
  ("Flokkjakt",  [("raptor", 22, "flank"), ("wolf", 4, "front"), ("spitter", 4, "back")], {"world": 3}),
  ("Horn",       [("hornback", 16, "front"), ("raptor", 14, "flank")], {"world": 3}),
  ("Sverm",      [("snapper", 22, "front"), ("hornback", 2, "front"), ("raptor", 6, "flank")], {"world": 3}),
  ("Panser",     [("clubtail", 18, "front"), ("snapper", 12, "flank")], {"world": 3}),
  ("Urdrager",   [("urdragon", 6, "front"), ("clubtail", 6, "front"), ("snapper", 18, "flank")], {"world": 3, "flyers": True}),
  ("Tyrant",     [("tyrant", 6, "front"), ("raptor", 16, "flank"), ("clubtail", 8, "front")], {"world": 3, "heavy": True}),
  ("Spytt",      [("frillspitter", 20, "back"), ("raptor", 6, "flank"), ("clubtail", 4, "front")], {"world": 3}),
  ("Jordskjelv", [("earthshaker", 6, "front"), ("frillspitter", 10, "back"), ("raptor", 14, "flank")], {"world": 3, "heavy": True}),
  ("Gjengangere", [("revenant", 20, "front"), ("frillspitter", 6, "back"), ("raptor", 4, "flank")], {"world": 3}),
  ("Boss",       [("tyrantKing", 1, "boss"), ("revenant", 12, "front"), ("raptor", 10, "flank"), ("frillspitter", 7, "back")], {"world": 3, "boss": True}),
]
for st, g, ex in W:
    assert sum(n for _, n, _ in g) == 30, st

def js(st, g, ex):
    groups = ", ".join(f"['{t}', {n}, '{r}']" for t, n, r in g)
    extra = "".join(f", {k}: {('true' if v is True else v)}" for k, v in ex.items())
    return f"  {{ style: '{st}', groups: [{groups}]{extra} }},"

def apply(s):
    a = s.index("const WAVES = [\n") + len("const WAVES = [\n")
    b = s.index("].map((w, i) => Object.assign(w, { n: i + 1", a)
    old = s[a:b]
    assert old.count("style:") == 30, old.count("style:")
    s = s[:a] + "  // 30 skapninger per wave; den nye arten er flertallet (kjemper teller tyngre). 4. okt 2026.\n" + "\n".join(js(*w) for w in W) + "\n" + s[b:]
    return s
