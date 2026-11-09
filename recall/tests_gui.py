"""GUI smoke test. Needs a display (on a server: xvfb-run -a python3 tests_gui.py).

Builds the window with a temporary database, walks every screen in both themes and
checks that nothing is clipped: no widget outside its parent, no label whose text is
wider or taller than the widget that holds it.

    python3 tests_gui.py            # checks only
    python3 tests_gui.py shots/     # also saves a screenshot of each screen
"""
import os
import sys
import tempfile

os.environ.setdefault("RECALL_DB", os.path.join(tempfile.mkdtemp(), "gui.db"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk            # noqa: E402

import main as appmod           # noqa: E402

SCREENS = ["study", "browse", "add", "import", "stats", "settings"]


def walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from walk(child)


def text_of(widget):
    try:
        return str(widget.cget("text"))
    except Exception:
        return ""


def audit(app):
    """Check the visible screen only: a hidden screen's scroll area keeps its
    children 'mapped' inside a canvas window (a Tk quirk), and they are invisible."""
    problems = []
    screen = app._current if app._current is not None else app.root
    for w in walk(screen):
        if not w.winfo_ismapped() or isinstance(w, (tk.Tk, tk.Toplevel)):
            continue
        if getattr(w, "_is_scroll_content", False):
            continue
        parent = w.master
        if parent is None or isinstance(parent, (tk.Tk, tk.Toplevel)):
            continue
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        x, y = w.winfo_rootx() - px, w.winfo_rooty() - py
        ww, hh = w.winfo_width(), w.winfo_height()
        if x + ww > parent.winfo_width() + 2 or y + hh > parent.winfo_height() + 2:
            problems.append(("outside parent", w.winfo_class(), text_of(w)[:40],
                             x, y, ww, hh))
        if w.winfo_class() in ("Label", "TLabel") and text_of(w).strip():
            if w.winfo_reqwidth() > ww + 2:
                problems.append(("text too wide", w.winfo_class(), text_of(w)[:40]))
            if w.winfo_reqheight() > hh + 2:
                problems.append(("text too tall", w.winfo_class(), text_of(w)[:40]))
    return problems


def screenshot(app, path):
    import subprocess
    from PIL import Image
    root_png = path + ".root.png"
    subprocess.run(["import", "-window", "root", root_png], check=False,
                   capture_output=True)
    x = app.root.winfo_rootx()
    y = app.root.winfo_rooty()
    Image.open(root_png).crop((x, y, x + app.root.winfo_width(),
                               y + app.root.winfo_height())).save(path)
    os.remove(root_png)


def check_reset(app):
    """The reset buttons: one card in Browse, one deck and everything in Settings."""
    from tkinter import messagebox
    yes = lambda *a, **k: True
    messagebox.askyesno = yes
    import screen_browse
    import screen_settings
    screen_browse.messagebox.askyesno = yes
    screen_settings.messagebox.askyesno = yes

    deck = app.db.decks()[0]
    app.show("study")
    app.root.update()
    study = app.screens["study"]
    for _ in range(3):
        if not study.card:
            break
        study.reveal()
        study.grade(3)
        app.root.update()
    assert app.db.review_count() > 0, "nothing to reset"

    # --- one card, from Browse
    app.show("browse")
    app.root.update()
    br = app.screens["browse"]
    learned = [iid for iid in br.tree.get_children()
               if app.db.card(app.db.card_ids_for_item(int(iid))[0])["state"] != "new"]
    assert learned, "the study flow left no learned card"
    br.tree.selection_set(learned[0])
    before = app.db.review_count()
    br.reset_selected()
    app.root.update()
    for cid in app.db.card_ids_for_item(int(learned[0])):
        c = app.db.card(cid)
        assert c["state"] == "new" and c["stability"] is None and c["due"] == 0, dict(c)
    assert app.db.review_count() < before, "history of the card was kept"

    # --- one deck, then everything, from Settings
    app.show("settings")
    app.root.update()
    st = app.screens["settings"]
    st.reset_deck()
    app.root.update()
    assert set(app.db.state_counts(deck["id"])) <= {"new"}
    st.reset_everything()
    app.root.update()
    assert set(app.db.state_counts()) == {"new"} and app.db.review_count() == 0

    folder = os.path.dirname(os.path.abspath(app.db.path))
    baks = [f for f in os.listdir(folder) if f.startswith("before-reset-")]
    assert baks, "no safety backup was written"
    for f in baks:
        os.remove(os.path.join(folder, f))
    print("  reset buttons work: card, deck, everything — with a safety backup")


def check_global_settings(app):
    """'Save for all decks' writes the form to every deck, a single save stays local."""
    from tkinter import messagebox
    yes = lambda *a, **k: True
    messagebox.askyesno = yes
    import screen_settings
    screen_settings.messagebox.askyesno = yes

    db = app.db
    if not db.deck_by_name("Second deck"):
        db.add_deck("Second deck")
    app.show("settings")
    for _ in range(3):
        app.root.update()
    st = app.screens["settings"]
    st.f_new.set("7")
    st.f_maxint.set("365")
    st.retention.set(85)
    st.save_all()
    app.root.update()
    for row in db.decks():
        d = db.deck(row["id"])
        assert d["new_per_day"] == 7, dict(d)
        assert d["max_interval"] == 365, dict(d)
        assert abs((d["desired_retention"] or 0) - 0.85) < 1e-9, dict(d)

    # the single-deck save must still leave the others alone
    selected = st.deck.get()
    st.f_new.set("3")
    st.save()
    app.root.update()
    assert db.deck_by_name(selected)["new_per_day"] == 3
    others = [db.deck(r["id"]) for r in db.decks() if r["name"] != selected]
    assert others and all(d["new_per_day"] == 7 for d in others), "single save leaked"
    print("  global settings: one click writes every deck, single save stays local")


def main():
    shots = sys.argv[1] if len(sys.argv) > 1 else None
    if shots:
        os.makedirs(shots, exist_ok=True)
    app = appmod.App()
    app.root.geometry("1240x810+0+0")
    deck = app.db.decks()[0]
    if app.db.total_cards() == 0:
        for i in range(6):
            app.db.add_item(deck["id"], f"Sample prompt {i} — a question of some length",
                            "A sample answer", "An explanation that shows up after the answer.",
                            "test source", "demo")
    app.root.update()

    problems = 0
    for theme in ("light", "dark"):
        if app.theme.name != theme:
            app.set_theme(theme)
        for key in SCREENS:
            app.show(key)
            # Tk needs two idle cycles before nested scroll/panel geometry settles
            for _ in range(3):
                app.root.update()
                app.root.update_idletasks()
            found = audit(app)
            problems += len(found)
            for f in found[:4]:
                print(f"  [{theme}/{key}] {f}")
            if shots:
                screenshot(app, os.path.join(shots, f"{theme}_{key}.png"))
    # and again at the smallest size the window allows
    app.root.geometry("1020x690")
    for key in SCREENS:
        app.show(key)
        for _ in range(3):
            app.root.update()
            app.root.update_idletasks()
        for f in audit(app)[:3]:
            print(f"  [small/{key}] {f}")
            problems += 1

    # the study flow itself
    app.show("study")
    app.root.update()
    study = app.screens["study"]
    if study.card:
        study.reveal()
        app.root.update()
        assert set(app.sched.preview(study.card)) == {1, 2, 3, 4}
        study.grade(3)
        app.root.update()
    check_reset(app)
    check_global_settings(app)
    print(f"gui check done — {problems} layout problem(s)")
    app.root.destroy()
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
