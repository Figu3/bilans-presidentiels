"""Build bilans.html (published fragment) and preview.html (local preview) from the template and data files.

data/_all.json         S, H, M17, M22: {eng, pop}
data/research/*.json   tags (poids, crise), academic verdicts, second poll series and events, Chirac dossiers
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
R = os.path.join(D, "research")


def load(path, default=None):
    p = os.path.join(R, path)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


META = {
    "C1": {"sub": "promesses retenues", "elu": "52,6 %", "lp": "n.d.", "lpNote": "avant le site", "obs": "aucun tracker de l'époque"},
    "C2": {"sub": "promesses retenues", "elu": "82,2 %", "lp": "n.d.", "lpNote": "avant le site", "obs": "aucun tracker de l'époque"},
    "S": {"sub": "promesses retenues", "elu": "53,1 %", "lp": "n.d.", "lpNote": "le site démarre en 2012", "obs": "47 % réalisées (Institut Thomas More, mars 2012)"},
    "H": {"sub": "engagements officiels", "elu": "51,6 %", "lp": "45 %", "lpNote": "sous-promesses évaluables", "obs": "39 % à mi-mandat (L'Obs)"},
    "M17": {"sub": "promesses retenues", "elu": "66,1 %", "lp": "43 %", "lpNote": "398 engagements suivis", "obs": "56 % sur 25 (LCP)"},
    "M22": {"sub": "promesses, en cours", "elu": "58,5 %", "lp": "aucun", "lpNote": "pas de tracker", "obs": "aucun bilan publié"},
}
ACAD_SRC = "Étude universitaire"
MIDEM = "https://forum-midem.de/wp-content/uploads/2025/04/TUD_MIDEM_PolicyPaper_2025-2-Immigration-Policy-and-Electoral-Mandates.pdf"
CONV = "https://theconversation.com/en-france-tenir-ses-promesses-electorales-ne-rapporte-rien-272193"
ACAD_ROW = {
    "S": '<b>32 %</b> sur 164 <span class="note"><a href="https://doi.org/10.3917/gap.173.0085">Bouillaud, Guinaudeau, Persico</a></span>',
    "H": '<span class="note">pas de chiffre publié</span>',
    "M17": f'plus de 70 % au moins en partie <span class="note"><a href="{CONV}">Partipol</a></span>',
}

allj = json.load(open(os.path.join(D, "_all.json"), encoding="utf-8"))
data = {k: allj[k] for k in ("S", "H", "M17", "M22")}

polls = load("polls.json", {})
for cid, fn in (("C1", "c1995.json"), ("C2", "c2002.json")):
    c = load(fn)
    pop = (polls.get("ifop_chirac") or {}).get(cid)
    if c and pop:
        data[cid] = {"eng": c["eng"], "pop": [[m, v, 0] for m, v in pop], "extra": {"phares": c.get("phares"), "regard": c.get("regard")}}

tags = load("tags.json", {})
acad = load("academic.json", {})
for k, d in data.items():
    t = tags.get(k, {})
    a = acad.get(k) or {}
    amap = {m["n"]: m for m in (a.get("map") or [])}
    h = a.get("headline") or {}
    for e in d["eng"]:
        tg = t.get(str(e["n"]), {})
        e["poids"] = tg.get("poids", 1)
        e["crise"] = tg.get("crise")
        e["crise_note"] = tg.get("crise_note")
        m = amap.get(e["n"])
        if m and k == "H" and e["n"] == 31:
            m = None  # only a search snippet of the RFSP article, not read
        if m and not any(v["src"].startswith(ACAD_SRC) for v in e["verdicts"]):
            if "MIDEM" in m["note"]:
                src, url = "Mendes et Schäller, MIDEM 2025", MIDEM
            else:
                src, url = "Guinaudeau et Costa, RFSP 2018", "https://doi.org/10.3917/rfsp.682.0291"
            e["verdicts"].append({"src": f"{ACAD_SRC} ({src})", "url": url, "statut": m["statut"]})
            sts = {v["statut"] for v in e["verdicts"] if v["statut"]}
            e["flag"] = e["flag"] or len(sts) > 1
    meta = dict(META[k])
    meta["sub"] = f"{len(d['eng'])} {meta['sub']}"
    if k in ACAD_ROW:
        meta["acad"] = ACAD_ROW[k]
    meta.update({x: y for x, y in d.pop("extra", {}).items() if y})
    d["meta"] = meta
    d["pop2"] = [p for p in ((polls.get("series") or {}).get(k) or []) if p[1] is not None]
    d["events"] = [ev if isinstance(ev, dict) else {"m": ev[0], "label": ev[1]} for ev in (polls.get("events") or {}).get(k) or []]

data["meta"] = {"second": {"institut": "Sofres, Kantar puis Verian", "mesure": "cote de confiance du Figaro Magazine"}}

tpl = open(os.path.join(HERE, "bilans.tpl.html"), encoding="utf-8").read()
out = tpl.replace("__DATA__", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
assert "—" not in out, "em dash in output"
open(os.path.join(HERE, "bilans.html"), "w", encoding="utf-8").write(out)
HEAD = '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
open(os.path.join(HERE, "preview.html"), "w", encoding="utf-8").write(HEAD + out + "</html>")
# index.html is the GitHub Pages page; og.png is a 1200x630 headless Chrome screenshot of preview.html
SITE = "https://figu3.github.io/bilans-presidentiels/"
SHARE = (f'<meta property="og:url" content="{SITE}"><meta property="og:image" content="{SITE}og.png">'
         '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
         '<meta name="twitter:card" content="summary_large_image">')
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(HEAD + SHARE + out + "</html>")
print("built", {k: len(v["eng"]) for k, v in data.items() if k != "meta"}, file=sys.stderr)
