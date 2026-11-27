#!/usr/bin/env python3
"""Hook PreToolUse du rapport mensuel : n'autorise un envoi Gmail QUE vers l'adresse de Rémy,
avec un objet « Rapport Kasalma ». Bloque (exit 2) tout autre destinataire, cc/bcc, pièce jointe,
brouillon existant, réponse dans un fil ou outil inattendu. Repris de PokerPerf."""
import json, os, sys

ALLOWED = open(os.path.expanduser("~/.config/pokerperf-veille/email")).read().strip().lower()


def block(msg):
    print(f"Envoi bloqué par le garde-fou du rapport Kasalma : {msg}", file=sys.stderr)
    sys.exit(2)


ev = json.load(sys.stdin)
if ev.get("tool_name") != "mcp__claude_ai_Gmail__send_message":
    block("outil inattendu " + str(ev.get("tool_name")))
ti = ev.get("tool_input") or {}
to = [str(x).strip().lower() for x in ti.get("to") or []]
if to != [ALLOWED]:
    block(f"destinataire non autorisé {to}")
for k in ("cc", "bcc", "attachments", "draftId", "replyThreadId", "replyToMessageId"):
    if ti.get(k):
        block(f"champ interdit : {k}")
if not str(ti.get("subject", "")).startswith("Rapport Kasalma"):
    block("objet inattendu")
sys.exit(0)
