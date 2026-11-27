#!/usr/bin/env python3
"""IndexNow : prévient Bing / Yandex (et ce qui s'appuie dessus : ChatGPT Search, Copilot, DuckDuckGo)
des pages modifiées. Repris de PokerPerf. Google n'utilise pas IndexNow (lui = Search Console).

Usage (depuis la racine du dépôt, APRÈS que GitHub Pages a publié) :
  python3 -I tools/indexnow.py --since HEAD~1     # pages modifiées depuis ce commit
  python3 -I tools/indexnow.py --all              # toutes les URL du sitemap en ligne
  python3 -I tools/indexnow.py URL [URL…]         # URL précises
Ajoute --dry pour afficher sans envoyer.
La clé (publique par conception) est servie à la racine : https://kasalma.com/<clé>.txt
"""
import glob, json, os, re, subprocess, sys, urllib.error, urllib.request

HOST = "kasalma.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
KEY = next(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(DOCS, "*.txt"))
           if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(p)))


def url_of(rel):
    """docs/cgu/index.html -> https://kasalma.com/cgu/"""
    rel = rel[len("docs/"):]
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return f"https://{HOST}/{rel}"


def changed_since(ref):
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", ref, "HEAD"],
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted({url_of(f) for f in out
                   if f.startswith("docs/") and f.endswith(".html") and not f.endswith("404.html")
                   and os.path.exists(os.path.join(ROOT, f))})


def all_urls():
    sm = urllib.request.urlopen(f"https://{HOST}/sitemap.xml", timeout=30).read().decode()
    return re.findall(r"<loc>(.*?)</loc>", sm)


def main(argv):
    dry = "--dry" in argv
    args = [a for a in argv if a != "--dry"]
    if args[:1] == ["--all"]:
        urls = all_urls()
    elif args[:1] == ["--since"]:
        urls = changed_since(args[1])
    else:
        urls = [a for a in args if a.startswith("https://")]
    if not urls:
        print("Aucune URL à envoyer.")
        return 0
    print(f"{len(urls)} URL :")
    for u in urls:
        print("  ", u)
    if dry:
        return 0
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow :", r.status, "(200/202 = reçu)")
    except urllib.error.HTTPError as e:
        print("IndexNow : erreur", e.code, e.read()[:200].decode(errors="replace"))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
