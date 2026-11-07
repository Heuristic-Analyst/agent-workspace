"""Settings: scheduling per deck, appearance, data."""
import json
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from base import Screen
from db import DEFAULT_PARAMS
from forms import Field
from widgets import Button, Panel, ScrollFrame


class SettingsScreen(Screen):
    title = "Settings"
    subtitle = "Scheduling is per deck. The defaults are good; change one thing at a time."

    def __init__(self, master, app):
        super().__init__(master, app)
        c = self.theme.c
        self.scroll = ScrollFrame(self.body, c["bg"])
        self.scroll.pack(fill="both", expand=True)
        root = self.scroll.inner

        # ---------------------------------------------------- scheduling
        p = Panel(root, self.theme, pad=20, radius=16)
        p.pack(fill="x")
        b = p.body
        tk.Label(b, text="Scheduling", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(12, "bold")).pack(anchor="w")
        tk.Label(b, text="FSRS with Anki-style learning steps (comma separated minutes). "
                         "Desired retention is the main dial: higher means shorter intervals "
                         "and more reviews.",
                 bg=c["surface"], fg=c["muted"], font=self.theme.f_small(),
                 wraplength=620, justify="left").pack(anchor="w", pady=(3, 14))

        row = tk.Frame(b, bg=c["surface"])
        row.pack(fill="x")
        self.deck = Field(row, self.theme, "Deck", kind="combo", value=[])
        self.deck.frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.deck.widget.bind("<<ComboboxSelected>>", lambda e: self.load_deck())
        self.retention = Field(row, self.theme, "Desired retention", kind="scale")
        self.retention.frame.pack(side="left", fill="x", expand=True)
        self.retention.widget.configure(from_=70, to=97, resolution=1, length=240)

        grid = tk.Frame(b, bg=c["surface"])
        grid.pack(fill="x", pady=(14, 0))
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="s")
        self.f_new = Field(grid, self.theme, "New cards / day", kind="entry")
        self.f_new.frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.f_reviews = Field(grid, self.theme, "Max reviews / day", kind="entry")
        self.f_reviews.frame.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.f_maxint = Field(grid, self.theme, "Max interval", kind="entry", unit="days")
        self.f_maxint.frame.grid(row=0, column=2, sticky="ew")
        self.f_learn = Field(grid, self.theme, "Learning steps", kind="entry",
                             unit="minutes")
        self.f_learn.frame.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(12, 0))
        self.f_relearn = Field(grid, self.theme, "Relearning steps", kind="entry",
                               unit="minutes")
        self.f_relearn.frame.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(12, 0))
        self.f_retention_note = Field(grid, self.theme, "Retention", kind="entry")
        self.f_retention_note.frame.grid(row=1, column=2, sticky="ew", pady=(12, 0))
        self.f_retention_note.widget.configure(state="disabled")

        btns = tk.Frame(b, bg=c["surface"])
        btns.pack(fill="x", pady=(16, 0))
        Button(btns, self.theme, "Save settings", command=self.save, kind="solid",
               color=c["accent"], height=40, font_size=10, pad_x=22,
               bg=c["surface"]).pack(side="left")
        Button(btns, self.theme, "Reset FSRS parameters", command=self.reset_params,
               kind="outline", color=c["muted"], height=40, font_size=10, pad_x=18,
               bg=c["surface"]).pack(side="left", padx=8)

        # ---------------------------------------------------- appearance
        p2 = Panel(root, self.theme, pad=20, radius=16)
        p2.pack(fill="x", pady=(16, 0))
        b2 = p2.body
        tk.Label(b2, text="Appearance", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(12, "bold")).pack(anchor="w")
        row2 = tk.Frame(b2, bg=c["surface"])
        row2.pack(anchor="w", pady=(12, 0))
        for name in ("light", "dark"):
            active = self.theme.name == name
            Button(row2, self.theme, name.capitalize(),
                   command=lambda n=name: self.app.set_theme(n),
                   kind="solid" if active else "outline",
                   color=c["accent"] if active else c["muted"],
                   height=38, font_size=10, pad_x=20,
                   bg=c["surface"]).pack(side="left", padx=(0, 8))

        # ---------------------------------------------------------- data
        p3 = Panel(root, self.theme, pad=20, radius=16)
        p3.pack(fill="x", pady=(16, 0))
        b3 = p3.body
        tk.Label(b3, text="Your data", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(12, "bold")).pack(anchor="w")
        tk.Label(b3, text=self.db.path, bg=c["surface"], fg=c["muted"],
                 font=self.theme.f_mono(), wraplength=700, justify="left").pack(anchor="w",
                                                                                pady=(6, 12))
        row3 = tk.Frame(b3, bg=c["surface"])
        row3.pack(anchor="w")
        Button(row3, self.theme, "Back up database", command=self.backup, kind="soft",
               color=c["accent"], height=38, font_size=10, pad_x=18,
               bg=c["surface"]).pack(side="left", padx=(0, 8))
        Button(row3, self.theme, "Export deck to JSON", command=self.export_deck,
               kind="soft", color=c["accent"], height=38, font_size=10, pad_x=18,
               bg=c["surface"]).pack(side="left", padx=(0, 8))
        Button(row3, self.theme, "Delete deck", command=self.delete_deck, kind="ghost",
               color=c["red"], height=38, font_size=10, pad_x=14,
               bg=c["surface"]).pack(side="left")

    # ------------------------------------------------------------------
    def refresh(self):
        names = [d["name"] for d in self.db.decks()]
        self.deck.widget.configure(values=names)
        if self.deck.get() not in names:
            self.deck.widget.set(names[0] if names else "")
        self.load_deck()

    def _deck_row(self):
        return self.db.deck_by_name(self.deck.get())

    def load_deck(self):
        row = self._deck_row()
        if not row:
            return
        self.retention.set(round((row["desired_retention"] or 0.9) * 100))
        self.f_new.set(str(row["new_per_day"]))
        self.f_reviews.set(str(row["reviews_per_day"]))
        self.f_maxint.set(str(row["max_interval"]))
        self.f_learn.set(", ".join(str(int(float(x))) for x in
                                   json.loads(row["learn_steps"] or "[1,10]")))
        self.f_relearn.set(", ".join(str(int(float(x))) for x in
                                     json.loads(row["relearn_steps"] or "[10]")))
        self.f_retention_note.set(f"{(row['desired_retention'] or 0.9) * 100:.0f}% — "
                                  f"review right before you would forget")

    def save(self):
        row = self._deck_row()
        if not row:
            return
        try:
            new_per_day = max(0, int(self.f_new.get()))
            reviews_per_day = max(0, int(self.f_reviews.get()))
            max_interval = max(1, int(self.f_maxint.get()))
            learn = [float(x) for x in self.f_learn.get().replace(" ", "").split(",") if x]
            relearn = [float(x) for x in self.f_relearn.get().replace(" ", "").split(",") if x]
        except ValueError:
            self.app.toast.show("Those numbers are not all numbers", "err")
            return
        if not learn:
            learn = [1.0, 10.0]
        if not relearn:
            relearn = [10.0]
        self.db.update_deck(row["id"], desired_retention=self.retention.get() / 100.0,
                            new_per_day=new_per_day, reviews_per_day=reviews_per_day,
                            max_interval=max_interval,
                            learn_steps=json.dumps(learn),
                            relearn_steps=json.dumps(relearn))
        self.app.toast.show("Settings saved")
        self.load_deck()
        self.app.sidebar.refresh_counts()

    def reset_params(self):
        row = self._deck_row()
        if not row:
            return
        self.db.update_deck(row["id"], params=json.dumps(DEFAULT_PARAMS))
        self.app.toast.show("FSRS parameters reset to the published defaults")

    def backup(self):
        name = f"recall-backup-{datetime.now():%Y-%m-%d}.db"
        path = filedialog.asksaveasfilename(parent=self.app.root, initialfile=name,
                                            defaultextension=".db",
                                            filetypes=[("SQLite database", "*.db")])
        if path:
            self.db.backup(path)
            self.app.toast.show("Backup saved")

    def export_deck(self):
        row = self._deck_row()
        if not row:
            return
        items = self.db.items(row["id"])
        data = {"deck": row["name"], "items": [
            {"prompt": i["prompt"], "answer": i["answer"],
             "explanation": i["explanation"], "source": i["source"],
             "tags": i["tags"]} for i in items]}
        path = filedialog.asksaveasfilename(
            parent=self.app.root, initialfile=f"{row['name']}.json",
            defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            self.app.toast.show(f"Exported {len(items)} cards")

    def delete_deck(self):
        row = self._deck_row()
        if not row:
            return
        n = self.db.total_cards(row["id"])
        if messagebox.askyesno(
                "Delete deck",
                f"Delete “{row['name']}” and its {n} cards, with all review history?\n\n"
                "This cannot be undone.", parent=self.app.root):
            self.db.delete_deck(row["id"])
            self.app.toast.show("Deck deleted", "warn")
            self.refresh()
            self.app.sidebar.refresh_counts()
