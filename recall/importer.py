"""Reading material into the app.

Three formats are supported, detected from the file extension and content:

  JSON  {"deck": "Biology", "items": [{"prompt": ..., "answer": ...}]}
  MD    Q:/A:/E: blocks, or one-liners  prompt :: answer
  CSV   prompt,answer,explanation,source,tags   (header optional)

`parse_file` only reads; `import_into` writes and reports what happened, so the
import screen can show a preview before anything is committed.
"""
import csv
import io
import json
import os
import re

MAX_PREVIEW = 400


def _clean(text):
    if text is None:
        return ""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


# --------------------------------------------------------------------- JSON
def parse_json(text):
    data = json.loads(text)
    deck = None
    if isinstance(data, dict):
        deck = data.get("deck") or data.get("name")
        items = data.get("items") or data.get("cards") or []
    else:
        items = data
    out = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        prompt = raw.get("prompt") or raw.get("question") or raw.get("front") or ""
        answer = raw.get("answer") or raw.get("back") or ""
        tags = raw.get("tags") or ""
        if isinstance(tags, (list, tuple)):
            tags = ", ".join(str(t) for t in tags)
        out.append({
            "prompt": _clean(prompt),
            "answer": _clean(answer),
            "explanation": _clean(raw.get("explanation") or raw.get("extra") or ""),
            "source": _clean(raw.get("source") or ""),
            "tags": _clean(tags),
        })
    return deck, [o for o in out if o["prompt"] and o["answer"]]


# ----------------------------------------------------------------------- MD
MD_PREFIX = {
    "q": ("q:", "q.", "question:", "front:"),
    "a": ("a:", "a.", "answer:", "back:"),
    "e": ("e:", "explanation:", "note:", "extra:"),
    "t": ("tags:", "tag:"),
    "s": ("source:",),
}


def _prefix_kind(line):
    low = line.lower()
    for kind, prefixes in MD_PREFIX.items():
        for p in prefixes:
            if low.startswith(p):
                return kind, line[len(p):].strip()
    return None, line


def parse_md(text, default_source=""):
    deck = None
    section_tags = ""
    items, cur = [], None

    def flush():
        nonlocal cur
        if cur and cur.get("prompt") and cur.get("answer"):
            items.append(cur)
        cur = None

    for raw_line in text.replace("\r\n", "\n").split("\n"):
        line = raw_line.rstrip()
        if not line.strip():
            continue

        # headings
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            title = re.sub(r"^(deck|topic|deck:)\s*", "", title, flags=re.I)
            if level == 1:
                if deck is None and not items:
                    deck = title
                else:
                    section_tags = title
            else:
                section_tags = title
            continue

        # one-line cards
        if "::" in line and not line.startswith(("Q:", "A:")):
            parts = [p.strip() for p in line.split("::")]
            if len(parts) >= 2 and parts[0] and parts[1]:
                flush()
                items.append({
                    "prompt": _clean(parts[0]), "answer": _clean(parts[1]),
                    "explanation": _clean(parts[2]) if len(parts) > 2 else "",
                    "source": default_source, "tags": section_tags,
                })
                continue
        if ";;" in line:
            front, _, back = line.partition(";;")
            if front.strip() and back.strip():
                flush()
                items.append({
                    "prompt": _clean(front), "answer": _clean(back),
                    "explanation": "", "source": default_source, "tags": section_tags,
                })
                continue

        kind, rest = _prefix_kind(line)
        if kind == "q":
            flush()
            cur = {"prompt": _clean(rest), "answer": "", "explanation": "",
                   "source": default_source, "tags": section_tags}
        elif kind == "a" and cur is not None:
            cur["answer"] = _clean(rest)
        elif kind == "e" and cur is not None:
            cur["explanation"] = (_clean(cur["explanation"]) + "\n" + _clean(rest)).strip()
        elif kind == "t" and cur is not None:
            cur["tags"] = ", ".join(t for t in (cur["tags"], _clean(rest)) if t)
        elif kind == "s" and cur is not None:
            cur["source"] = _clean(rest)
        elif cur is not None:
            # continuation of the last field (multi-line answers)
            if cur["answer"]:
                cur["answer"] = (cur["answer"] + "\n" + _clean(line)).strip()
            else:
                cur["prompt"] = (cur["prompt"] + " " + _clean(line)).strip()
    flush()
    return deck, [i for i in items if i["prompt"] and i["answer"]]


# ---------------------------------------------------------------------- CSV
CSV_ALIASES = {
    "prompt": ("prompt", "question", "front", "q", "term", "concept"),
    "answer": ("answer", "back", "a", "definition", "explanation_answer"),
    "explanation": ("explanation", "extra", "note", "notes", "detail"),
    "source": ("source", "reference", "from"),
    "tags": ("tags", "tag", "topic", "deck"),
}


def parse_csv(text):
    sample = text[:2000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return None, []
    header = [c.strip().lower() for c in rows[0]]
    mapping, start = {}, 0
    if any(h in sum(CSV_ALIASES.values(), ()) for h in header):
        for key, aliases in CSV_ALIASES.items():
            for i, h in enumerate(header):
                if h in aliases:
                    mapping[key] = i
                    break
        start = 1
    else:
        mapping = {"prompt": 0, "answer": 1, "explanation": 2, "source": 3, "tags": 4}
    out = []
    for row in rows[start:]:
        get = lambda k: row[mapping[k]].strip() if k in mapping and mapping[k] < len(row) else ""
        p, a = get("prompt"), get("answer")
        if p and a:
            tags = get("tags")
            out.append({"prompt": _clean(p), "answer": _clean(a),
                        "explanation": _clean(get("explanation")),
                        "source": _clean(get("source")),
                        "tags": _clean(tags) if not tags.startswith("{") else ""})
    deck = os.path.splitext(os.path.basename(""))[0] or None
    return None, out


# ------------------------------------------------------------------- entry
def parse_file(path):
    """Returns (deck_name_or_None, [item dicts])."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        text = fh.read()
    ext = os.path.splitext(path)[1].lower()
    stem = os.path.splitext(os.path.basename(path))[0]
    if ext == ".json":
        deck, items = parse_json(text)
        return (deck or stem), items
    if ext in (".csv", ".tsv"):
        deck, items = parse_csv(text)
        return deck or stem, items
    # markdown / text / unknown: sniff
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            deck, items = parse_json(text)
            return deck or stem, items
        except Exception:
            pass
    if re.search(r"^[^\n]*,[^\n]*$", text, re.M) and "::" not in text and "Q:" not in text:
        try:
            deck, items = parse_csv(text)
            if items:
                return deck or stem, items
        except Exception:
            pass
    deck, items = parse_md(text)
    return deck or stem, items


def mark_duplicates(db, items):
    for it in items:
        it["duplicate"] = db.item_exists(it["prompt"], it["answer"])
    return items


def import_into(db, deck_id, items, skip_duplicates=True):
    added = skipped = 0
    for it in items:
        if skip_duplicates and it.get("duplicate"):
            skipped += 1
            continue
        db.add_item(deck_id, it["prompt"], it["answer"], it.get("explanation", ""),
                    it.get("source", ""), it.get("tags", ""))
        added += 1
    return {"added": added, "skipped": skipped}
