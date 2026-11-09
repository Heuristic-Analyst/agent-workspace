"""Settings: scheduling per deck, appearance, data."""
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from base import Screen, forget_study_card
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
        Button(btns, self.theme, "Save for all decks", command=self.save_all,
               kind="outline", color=c["accent"], height=40, font_size=10, pad_x=18,
               bg=c["surface"]).pack(side="left", padx=8)
        Button(btns, self.theme, "Reset FSRS parameters", command=self.reset_params,
               kind="outline", color=c["muted"], height=40, font_size=10, pad_x=18,
               bg=c["surface"]).pack(side="left")
        tk.Label(b, text="\u201cSave settings\u201d writes the deck selected above. "
                         "\u201cSave for all decks\u201d writes the same values to every "
                         "deck at once \u2014 handy when all your decks should behave alike.",
                 bg=c["surface"], fg=c["faint"], font=self.theme.f_tiny(),
                 wraplength=620, justify="left").pack(anchor="w", pady=(8, 0))

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

        # ------------------------------------------------- reset progress
        tk.Label(b3, text="Reset progress", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(11, "bold")).pack(anchor="w", pady=(20, 4))
        reset_note = tk.Label(b3, text="Cards go back to New and lose their schedule and "
                                        "review history. The cards, the decks and the settings "
                                        "stay. A backup is written next to the database first.",
                              bg=c["surface"], fg=c["muted"], font=self.theme.f_small(),
                              wraplength=620, justify="left")
        reset_note.pack(anchor="w")
        row4 = tk.Frame(b3, bg=c["surface"])
        row4.pack(anchor="w", pady=(10, 0))
        Button(row4, self.theme, "Reset this deck", command=self.reset_deck,
               kind="outline", color=c["amber"], height=38, font_size=10, pad_x=18,
               bg=c["surface"]).pack(side="left", padx=(0, 8))
        Button(row4, self.theme, "Reset everything", command=self.reset_everything,
               kind="ghost", color=c["red"], height=38, font_size=10, pad_x=14,
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

    def _form_values(self):
        """The scheduling values as deck fields; None if the form holds no numbers."""
        try:
            new_per_day = max(0, int(self.f_new.get()))
            reviews_per_day = max(0, int(self.f_reviews.get()))
            max_interval = max(1, int(self.f_maxint.get()))
            learn = [float(x) for x in self.f_learn.get().replace(" ", "").split(",") if x]
            relearn = [float(x) for x in self.f_relearn.get().replace(" ", "").split(",") if x]
        except ValueError:
            self.app.toast.show("Those numbers are not all numbers", "err")
            return None
        if not learn:
            learn = [1.0, 10.0]
        if not relearn:
            relearn = [10.0]
        return {"desired_retention": self.retention.get() / 100.0,
                "new_per_day": new_per_day, "reviews_per_day": reviews_per_day,
                "max_interval": max_interval,
                "learn_steps": json.dumps(learn),
                "relearn_steps": json.dumps(relearn)}

    def save(self):
        row = self._deck_row()
        if not row:
            return
        values = self._form_values()
        if values is None:
            return
        self.db.update_deck(row["id"], **values)
        self.app.toast.show("Settings saved")
        self.load_deck()
        self.app.sidebar.refresh_counts()

    def save_all(self):
        """The values above, written to every deck at once."""
        values = self._form_values()
        if values is None:
            return
        decks = self.db.decks()
        if len(decks) < 2:
            self.save()
            return
        if not messagebox.askyesno(
                "Save for all decks",
                f"Write these values to all {len(decks)} decks?\n\n"
                "Desired retention, new cards per day, max reviews per day, max interval "
                "and the learning steps are overwritten in every deck, including the one "
                "selected above. The FSRS parameters, the cards and your progress are not "
                "touched.\n\n"
                "Any deck can be changed back on its own afterwards.",
                parent=self.app.root, default="no"):
            return
        done = self.db.update_all_decks(**values)
        self.app.toast.show(f"Same settings written to {done} decks", "warn")
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

    # ------------------------------------------------------- reset progress
    def _safety_backup(self):
        """A free copy of the database before anything is forgotten."""
        folder = os.path.dirname(os.path.abspath(self.db.path)) or "."
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        path = os.path.join(folder, f"before-reset-{stamp}.db")
        try:
            self.db.backup(path)
            return path
        except Exception:
            return None

    def reset_deck(self):
        row = self._deck_row()
        if not row:
            return
        n = self.db.total_cards(row["id"])
        if not n:
            self.app.toast.show("This deck has no cards", "info")
            return
        if not messagebox.askyesno(
                "Reset deck",
                f"Reset all {n} cards of \u201c{row['name']}\u201d?\n\n"
                "They all go back to New. Schedule, stability and the entire review "
                "history of these cards are deleted, so they count as new cards again. "
                "Prompts, answers and deck settings stay.\n\n"
                "This cannot be undone.",
                parent=self.app.root, icon="warning", default="no"):
            return
        bak = self._safety_backup()
        done = self.db.reset_deck(row["id"])
        self._after_reset(done, bak)

    def reset_everything(self):
        n = self.db.total_cards()
        decks = len(self.db.decks())
        if not n:
            self.app.toast.show("There is nothing to reset", "info")
            return
        if not messagebox.askyesno(
                "Reset everything",
                f"Reset all {n} cards in {decks} deck{'s' if decks != 1 else ''}?\n\n"
                "Every card goes back to New and the complete review history is deleted. "
                "Cards, decks and settings stay, but all statistics start from zero and "
                "every card has to be learned again.\n\n"
                "This cannot be undone.",
                parent=self.app.root, icon="warning", default="no"):
            return
        bak = self._safety_backup()
        done = self.db.reset_all()
        self._after_reset(done, bak)

    def _after_reset(self, done, backup_path):
        msg = f"{done} card{'s' if done != 1 else ''} reset"
        if backup_path:
            msg += f" \u2014 backup: {os.path.basename(backup_path)}"
        self.app.toast.show(msg, "warn")
        forget_study_card(self.app)
        self.app.sidebar.refresh_counts()
        self.refresh()
