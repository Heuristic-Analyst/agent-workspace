"""Recall — a small spaced-repetition app.

Run it with:   python3 main.py
Everything is standard library (tkinter + sqlite3); nothing to install.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import DB                                    # noqa: E402
from sched import Scheduler                          # noqa: E402
from theme import Theme                              # noqa: E402
from widgets import Badge, Button, Toast, round_rect, set_dpi_awareness  # noqa: E402

from screen_study import StudyScreen                 # noqa: E402
from screen_browse import BrowseScreen               # noqa: E402
from screen_add import AddScreen                     # noqa: E402
from screen_import import ImportScreen               # noqa: E402
from screen_stats import StatsScreen                 # noqa: E402
from screen_settings import SettingsScreen           # noqa: E402

SCREENS = {
    "study": StudyScreen,
    "browse": BrowseScreen,
    "add": AddScreen,
    "import": ImportScreen,
    "stats": StatsScreen,
    "settings": SettingsScreen,
}
NAV = [("study", "Study"), ("browse", "Browse"), ("add", "Add card"),
       ("import", "Import"), ("stats", "Stats"), ("settings", "Settings")]

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("RECALL_DB") or os.path.join(APP_DIR, "learning.db")


class NavItem(tk.Frame):
    def __init__(self, master, app, key, text):
        self.app = app
        self.key = key
        c = app.theme.c
        super().__init__(master, bg=c["sidebar"], height=42)
        self.pack_propagate(False)
        self.bar = tk.Frame(self, bg=c["sidebar"], width=3)
        self.bar.pack(side="left", fill="y")
        self.label = tk.Label(self, text=text, bg=c["sidebar"], fg=c["sidebar_tx"],
                              font=app.theme.font(11, "bold"), anchor="w")
        self.label.pack(side="left", fill="both", expand=True, padx=(16, 0))
        for w in (self, self.bar, self.label):
            w.bind("<Button-1>", lambda e: app.show(self.key))
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
        self.active = False

    def _enter(self, _e):
        if not self.active:
            self.configure(bg=self.app.theme.c["sidebar_hi"])
            self.label.configure(bg=self.app.theme.c["sidebar_hi"])

    def _leave(self, _e):
        if not self.active:
            self.configure(bg=self.app.theme.c["sidebar"])
            self.label.configure(bg=self.app.theme.c["sidebar"])

    def set_active(self, active):
        c = self.app.theme.c
        self.active = active
        bg = c["sidebar_hi"] if active else c["sidebar"]
        self.configure(bg=bg)
        self.label.configure(bg=bg, fg=c["sidebar_tx_hi"] if active else c["sidebar_tx"])
        self.bar.configure(bg=c["accent"] if active else bg)


class Sidebar(tk.Frame):
    def __init__(self, master, app):
        c = app.theme.c
        super().__init__(master, bg=c["sidebar"], width=214)
        self.app = app
        self.pack_propagate(False)

        brand = tk.Frame(self, bg=c["sidebar"])
        brand.pack(fill="x", padx=18, pady=(24, 22))
        mark = tk.Canvas(brand, width=34, height=34, bg=c["sidebar"],
                         highlightthickness=0)
        mark.pack(side="left")
        round_rect(mark, 1, 1, 33, 33, 10, fill=c["accent"], outline="")
        mark.create_text(17, 18, text="R", fill=c["accent_tx"],
                         font=app.theme.font(16, "bold"))
        titles = tk.Frame(brand, bg=c["sidebar"])
        titles.pack(side="left", padx=(10, 0))
        tk.Label(titles, text="Recall", bg=c["sidebar"], fg="#FFFFFF",
                 font=app.theme.font(14, "bold")).pack(anchor="w")
        tk.Label(titles, text="spaced repetition", bg=c["sidebar"], fg=c["sidebar_tx"],
                 font=app.theme.font(8)).pack(anchor="w")

        self.items = {}
        for key, label in NAV:
            item = NavItem(self, app, key, label)
            item.pack(fill="x", padx=10, pady=1)
            self.items[key] = item

        spacer = tk.Frame(self, bg=c["sidebar"])
        spacer.pack(fill="both", expand=True)

        foot = tk.Frame(self, bg=c["sidebar"])
        foot.pack(fill="x", padx=18, pady=(0, 20))
        tk.Frame(foot, bg=c["sidebar_hi"], height=1).pack(fill="x", pady=(0, 14))
        self.due_badge = Badge(foot, app.theme, "0 due", fg=c["accent_tx"],
                               bg=c["accent"], parent_bg=c["sidebar"], height=24)
        self.due_badge.pack(anchor="w")
        self.new_label = tk.Label(foot, text="", bg=c["sidebar"], fg=c["sidebar_tx"],
                                  font=app.theme.font(8), anchor="w")
        self.new_label.pack(anchor="w", pady=(8, 0))
        tk.Label(foot, text="FSRS-4.5 scheduler", bg=c["sidebar"], fg="#5A6478",
                 font=app.theme.font(8), anchor="w").pack(anchor="w", pady=(2, 0))

    def set_active(self, key):
        for k, item in self.items.items():
            item.set_active(k == key)

    def refresh_counts(self):
        counts = self.app.db.counts()
        due = counts["due"] + counts["learning"]
        self.due_badge.set_text(f"{due} due")
        self.new_label.configure(text=f"{counts['new']} new waiting")


class App:
    def __init__(self):
        set_dpi_awareness()
        self.root = tk.Tk()
        self.root.title("Recall — spaced repetition")
        self.root.geometry("1240x810")
        self.root.minsize(1020, 690)
        self.db = DB(DB_PATH)
        self.theme = Theme(self.db.get_meta("theme", "light"))
        self.theme.resolve_fonts(self.root)
        self.sched = Scheduler(self.db)
        self.screens = {}
        self.current_key = "study"
        self._current = None
        self.sidebar = None
        self.toast = None
        self.build()

    # ------------------------------------------------------------------
    def build(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.theme.apply(self.root)
        c = self.theme.c
        self.root.configure(bg=c["bg"])
        self.sidebar = Sidebar(self.root, self)
        self.sidebar.pack(side="left", fill="y")
        self.main = tk.Frame(self.root, bg=c["bg"])
        self.main.pack(side="left", fill="both", expand=True)
        self.toast = Toast(self.main, self.theme)
        self.screens = {}
        self._current = None
        self.sidebar.refresh_counts()
        self.show(self.current_key)
        self.root.bind_all("<Key>", self._on_key)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def show(self, key):
        if key not in self.screens:
            self.screens[key] = SCREENS[key](self.main, self)
        screen = self.screens[key]
        if self._current is not None and self._current is not screen:
            self._current.pack_forget()
        screen.pack(fill="both", expand=True)
        self._current = screen
        self.current_key = key
        self.sidebar.set_active(key)
        self.sidebar.refresh_counts()
        screen.on_show()
        self.root.title(f"Recall — {key.capitalize()}")

    # ------------------------------------------------------------------
    def set_theme(self, name):
        if name == self.theme.name:
            return
        self.theme.name = name
        self.db.set_meta("theme", name)
        self.build()

    def undo_review(self):
        card_id = self.db.undo_last_review()
        if card_id is None:
            self.toast.show("Nothing to undo", "warn")
            return
        self.toast.show("Undid the last answer")
        self.sidebar.refresh_counts()
        if hasattr(self._current, "load_next"):
            self._current.load_next()
        elif hasattr(self._current, "refresh"):
            self._current.refresh()

    def _on_key(self, event):
        widget = self.root.focus_get()
        typing = isinstance(widget, (tk.Entry, tk.Text, ttk.Entry, ttk.Combobox,
                                     tk.Spinbox))
        if event.state & 0x4 and event.keysym.lower() == "z" and not typing:
            self.undo_review()
            return "break"
        if typing:
            return
        if self._current is not None:
            if self._current.on_key(event):
                return "break"

    def on_close(self):
        self.db.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    App().run()


if __name__ == "__main__":
    main()
