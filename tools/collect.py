#!/usr/bin/env python3
"""Suivi des chiffres de kasalma.com — collecte (déterministe, sans IA). Repris de PokerPerf.

Search Console (28 j récents vs 28 j précédents, décalage 3 j), Cloudflare Web Analytics (mêmes périodes)
et nombre d'inscrits à la liste d'attente (Formspree, si configuré).

Réglages : ~/.config/kasalma-report/config.json
  {"gsc_site": "sc-domain:kasalma.com", "cf_site_tag": "<siteTag Cloudflare>", "formspree_form": "<id>"}
Identifiants réutilisés de PokerPerf (même compte Google, même compte Cloudflare) :
  ~/.config/pokerperf-gsc/{client,token}.json · ~/.config/pokerperf-cf/{token,account_id}
Clé API Formspree (facultative) : ~/.config/kasalma-report/formspree_key

Usage : python3 -I tools/collect.py [--out FICHIER]   (sinon imprime le JSON)
Écrit aussi un instantané dans ~/.local/share/kasalma-report/AAAA-MM-JJ.json.
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import date, timedelta

H = os.path.expanduser
CFG_DIR = H("~/.config/kasalma-report")
OUTDIR = H("~/.local/share/kasalma-report")


def config():
    path = os.path.join(CFG_DIR, "config.json")
    return json.load(open(path)) if os.path.exists(path) else {}


def post(url, body, headers):
    req = urllib.request.Request(url, data=body, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=60))


def gsc_token():
    c = json.load(open(H("~/.config/pokerperf-gsc/client.json")))
    c = c.get("installed", c)
    t = json.load(open(H("~/.config/pokerperf-gsc/token.json")))
    body = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
                                   "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", body))["access_token"]


def gsc(site, tok, start, end, dims, limit=250):
    url = "https://www.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query" % urllib.parse.quote(site, safe="")
    b = json.dumps({"startDate": start, "endDate": end, "dimensions": dims, "rowLimit": limit}).encode()
    rows = post(url, b, {"Authorization": "Bearer " + tok, "Content-Type": "application/json"}).get("rows", [])
    return [{"keys": r.get("keys", []), "clicks": r["clicks"], "impressions": r["impressions"],
             "ctr": round(r["ctr"] * 100, 2), "position": round(r["position"], 1)} for r in rows]


def cf(site_tag, start, end, dim, limit=30):
    T = open(H("~/.config/pokerperf-cf/token")).read().strip()
    A = open(H("~/.config/pokerperf-cf/account_id")).read().strip()
    dsel = f"dimensions{{{dim}}}" if dim else ""
    q = ("query($a:String!,$s:Time!,$e:Time!){viewer{accounts(filter:{accountTag:$a}){rumPageloadEventsAdaptiveGroups(limit:%d,"
         "orderBy:[count_DESC],filter:{datetime_geq:$s,datetime_leq:$e,siteTag:\"%s\"}){count sum{visits} %s}}}}") % (limit, site_tag, dsel)
    r = post("https://api.cloudflare.com/client/v4/graphql",
             json.dumps({"query": q, "variables": {"a": A, "s": start + "T00:00:00Z", "e": end + "T23:59:59Z"}}).encode(),
             {"Authorization": "Bearer " + T, "Content-Type": "application/json"})
    if r.get("errors"):
        return {"error": str(r["errors"])[:200]}
    rows = r["data"]["viewer"]["accounts"][0]["rumPageloadEventsAdaptiveGroups"]
    return [{"key": (x.get("dimensions") or {}).get(dim) if dim else "total", "views": x["count"], "visits": x["sum"]["visits"]}
            for x in rows]


def waitlist(form_id):
    """Compte les inscrits (API Formspree, clé facultative). Ne garde que des totaux, jamais les adresses."""
    key_path = os.path.join(CFG_DIR, "formspree_key")
    if not os.path.exists(key_path):
        return {"note": "clé Formspree absente : compter les inscrits dans le tableau de bord Formspree"}
    key = open(key_path).read().strip()
    req = urllib.request.Request(f"https://formspree.io/api/0/forms/{form_id}/submissions?limit=1000",
                                 headers={"Authorization": "Bearer " + key})
    subs = json.load(urllib.request.urlopen(req, timeout=60)).get("submissions", [])
    by_phone, by_source = {}, {}
    for s in subs:
        by_phone[s.get("telephone") or "non dit"] = by_phone.get(s.get("telephone") or "non dit", 0) + 1
        by_source[s.get("source") or "?"] = by_source.get(s.get("source") or "?", 0) + 1
    return {"total": len(subs), "telephone": by_phone, "source": by_source}


def totals(rows):
    c = sum(r["clicks"] for r in rows)
    i = sum(r["impressions"] for r in rows)
    pos = round(sum(r["position"] * r["impressions"] for r in rows) / i, 1) if i else None
    return {"clicks": c, "impressions": i, "ctr": round(100 * c / i, 2) if i else 0, "avg_position": pos}


def main():
    cfg = config()
    end = date.today() - timedelta(days=3)
    cur = (end - timedelta(days=27), end)
    prev = (cur[0] - timedelta(days=28), cur[0] - timedelta(days=1))
    f = lambda d: d.isoformat()
    out = {"generated": date.today().isoformat(),
           "periods": {"current": [f(cur[0]), f(cur[1])], "previous": [f(prev[0]), f(prev[1])]},
           "errors": []}

    if cfg.get("gsc_site"):
        try:
            tok = gsc_token()
            g = {}
            for name, (s, e) in (("current", cur), ("previous", prev)):
                daily = gsc(cfg["gsc_site"], tok, f(s), f(e), ["date"])
                g[name] = {"totals": totals(daily), "daily": daily,
                           "pages": gsc(cfg["gsc_site"], tok, f(s), f(e), ["page"], 100),
                           "queries": gsc(cfg["gsc_site"], tok, f(s), f(e), ["query"], 250),
                           "devices": gsc(cfg["gsc_site"], tok, f(s), f(e), ["device"], 5)}
            pq = {r["keys"][0]: r for r in g["previous"]["queries"]}
            moves = []
            for r in g["current"]["queries"]:
                p = pq.get(r["keys"][0])
                moves.append({"query": r["keys"][0], "impr": r["impressions"], "clicks": r["clicks"], "pos": r["position"],
                              "prev_impr": p["impressions"] if p else 0, "prev_pos": p["position"] if p else None})
            g["query_moves"] = sorted(moves, key=lambda m: -m["impr"])[:60]
            g["near_page1"] = [m for m in moves if m["pos"] and 8 <= m["pos"] <= 20][:20]
            out["gsc"] = g
        except Exception as e:
            out["errors"].append(f"gsc: {e}")
    else:
        out["errors"].append("gsc: propriété non configurée (gsc_site)")

    if cfg.get("cf_site_tag"):
        try:
            out["cloudflare"] = {name: {"total": cf(cfg["cf_site_tag"], f(s), f(e), None),
                                        "paths": cf(cfg["cf_site_tag"], f(s), f(e), "requestPath"),
                                        "referrers": cf(cfg["cf_site_tag"], f(s), f(e), "refererHost"),
                                        "countries": cf(cfg["cf_site_tag"], f(s), f(e), "countryName", 15)}
                                 for name, (s, e) in (("current", cur), ("previous", prev))}
            out["cloudflare"]["note"] = "Trafic faible = échantillonnage (valeurs par paquets de 10)."
        except Exception as e:
            out["errors"].append(f"cloudflare: {e}")
    else:
        out["errors"].append("cloudflare: site non configuré (cf_site_tag)")

    if cfg.get("formspree_form"):
        try:
            out["waitlist"] = waitlist(cfg["formspree_form"])
        except Exception as e:
            out["errors"].append(f"formspree: {e}")

    os.makedirs(OUTDIR, exist_ok=True)
    s = json.dumps(out, ensure_ascii=False, indent=1)
    open(os.path.join(OUTDIR, out["generated"] + ".json"), "w").write(s)
    if "--out" in sys.argv:
        open(sys.argv[sys.argv.index("--out") + 1], "w").write(s)
    else:
        print(s)


if __name__ == "__main__":
    main()
