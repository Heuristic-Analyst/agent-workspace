# Recall

A small spaced-repetition app: cards, an FSRS scheduler, and nothing else.
Pure Python + tkinter + SQLite — no packages to install.

> Learning science behind it: retrieval practice, spaced repetition and honest
> self-grading. The scheduler is FSRS-4.5 with Anki-style learning steps.

## Run it

```
python3 main.py          # macOS / Linux      (Windows:  python main.py)
```

Needs Python 3.8 or newer with tkinter. tkinter ships with the python.org installers on macOS and
Windows. On Debian/Ubuntu: `sudo apt install python3-tk`.

On first start it creates `learning.db` next to `main.py` and one deck called *Default*.
Your cards live in that file — copy it to back it up.

## The four screens you will use

- **Study** — one card at a time. Think of the answer, press **Space**, then grade yourself.
- **Add card** — write a card by hand; the right side previews it.
- **Import** — bring in a `.json`, `.md`, `.txt`, `.csv` file. You see a preview and duplicate
  detection before anything is saved.
- **Stats** — due counts, retention, forecast, and a review heatmap.

**Browse** lists everything (double-click to edit). **Settings** holds scheduling per deck, the
light/dark switch, backups and JSON export.

### Keyboard

| Key | Does |
|---|---|
| `Space` / `Enter` | show the answer |
| `1` `2` `3` `4` | Again / Hard / Good / Easy |
| `Ctrl+Z` | undo the last answer (outside text fields) |
| `Ctrl+Enter` | save the card you are writing |

## How it schedules

FSRS-4.5 — the modern replacement for SuperMemo's SM-2, the algorithm Anki now uses — with
Anki-style learning steps for brand-new cards:

- New cards go through 1 min → 10 min steps, then graduate with a first interval of ~4 days.
- Each review updates two numbers per card: **difficulty** (1–10) and **stability** (the interval at
  which your recall probability is 90%). Forgetting follows a power curve, so a card you keep
  answering `Good` moves ~4 d → 15 d → 51 d → 146 d → 395 d…
- **Desired retention** (default 90%) is the main dial. Raise it and intervals shorten and reviews
  multiply: at 95% you do roughly twice the reviews for five points more recall.
- A lapse (`Again`) drops stability but keeps a fraction of it — a card you knew for months recovers
  much faster than a new one.
- Ten lapses and the card is a **leech** in Anki. Here it is flagged in Browse by its lapse count:
  rewrite it or delete it, don't keep reviewing it.

Defaults per deck: 20 new cards/day, 200 reviews/day, max interval 2 years, steps 1/10 min.
All of it is editable in Settings.

## Importing your own material

`docs/IMPORT-FORMAT.md` has the three formats with examples; `docs/sample-content.json` is a
ready-to-import example. Typical minimum is one line per card:

```
What is the capacity of short-term memory? :: About 4 chunks, not 7
```

or

```
Q: Why does spacing beat massing?
A: Each review at a delay re-consolidates the memory and slows later forgetting.
```

`docs/CONTENT-GUIDE.md` explains how notes, slides and exam sheets get turned into cards.

## Files

```
main.py            window, navigation, keyboard, theme switching
db.py              SQLite schema and queries (item / card / review)
sched.py           FSRS-4.5 + learning steps: the whole scheduler
importer.py        md / txt / json / csv parsing, duplicate detection
theme.py           two colour palettes, fonts, ttk styles
widgets.py         rounded panels, pill buttons, badges, scroll areas, toasts
forms.py           form fields, search box
screen_*.py        study, browse, add, import, stats, settings
tests.py           scheduler / database / importer tests  (python3 tests.py)
docs/              import format, content guide, sample deck
```

## If something looks wrong

- **No window / `ModuleNotFoundError: tkinter`** → install python3-tk (Linux) or use the
  python.org installer (macOS/Windows).
- **Text is tiny or huge** → the app follows your OS display scaling; Tk multiplies point sizes by
  the detected DPI.
- **A card comes back after seconds** → it is a learning card still inside its 1/10 min steps.
- **Nothing due, but stats show cards** → they are scheduled for later days; that is the spacing
  working.
