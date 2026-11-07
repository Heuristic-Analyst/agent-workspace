"""Bring notes, lecture files or exports in as cards."""
import os
import tkinter as tk
from tkinter import filedialog, ttk

import importer
from base import Screen
from forms import Field
from widgets import Button, Panel

NEW_DECK = "＋ New deck…"


class ImportScreen(Screen):
    title = "Import"
    subtitle = "Markdown, text, JSON or CSV — a preview is shown before anything is saved."

    def __init__(self, master, app):
        super().__init__(master, app)
        c = self.theme.c
        self.items = []
        self.file_path = None

        # --- drop zone / file picker ------------------------------------
        self.zone = Panel(self.body, self.theme, pad=24, radius=16,
                          fill=c["surface_alt"], shadow=False)
        self.zone.pack(fill="x")
        zb = self.zone.body
        self.zone_title = tk.Label(zb, text="No file chosen yet", bg=c["surface_alt"],
                                   fg=c["text"], font=self.theme.font(13, "bold"))
        self.zone_title.pack(anchor="w")
        self.zone_sub = tk.Label(
            zb, text="Supported: .md / .txt (Q:/A: blocks or  prompt :: answer),  "
                     ".json,  .csv / .tsv", bg=c["surface_alt"], fg=c["muted"],
            font=self.theme.f_small(), justify="left")
        self.zone_sub.pack(anchor="w", pady=(4, 12))
        row = tk.Frame(zb, bg=c["surface_alt"])
        row.pack(anchor="w")
        Button(row, self.theme, "Choose file…", command=self.choose_file, kind="solid",
               color=c["accent"], height=40, font_size=10, pad_x=20,
               bg=c["surface_alt"]).pack(side="left")
        Button(row, self.theme, "Load example", command=self.load_example, kind="outline",
               color=c["muted"], height=40, font_size=10, pad_x=16,
               bg=c["surface_alt"]).pack(side="left", padx=8)

        # --- options ------------------------------------------------------
        self.options = tk.Frame(self.body, bg=c["bg"])
        self.options.pack(fill="x", pady=(16, 0))
        self.deck = Field(self.options, self.theme, "Import into deck", kind="combo", value=[])
        self.deck.frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.deck.widget.bind("<<ComboboxSelected>>", lambda e: self._deck_changed())
        self.new_deck = Field(self.options, self.theme, "New deck name", kind="entry")
        self.new_deck.frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.new_deck.frame.pack_forget()

        self.skip_dupes = ttk.Checkbutton(self.options, text="Skip duplicates",
                                          style="TCheckbutton")
        self.skip_dupes.state(["selected"])
        self.skip_dupes.pack(side="left", pady=(18, 0))

        # --- preview ------------------------------------------------------
        wrap = tk.Frame(self.body, bg=c["border"], padx=1, pady=1)
        wrap.pack(fill="both", expand=True, pady=(16, 0))
        self.tree = ttk.Treeview(wrap, columns=("n", "prompt", "answer", "status"),
                                 show="headings")
        for key, text, width, stretch in (("n", "#", 44, False),
                                          ("prompt", "Prompt", 420, True),
                                          ("answer", "Answer", 380, True),
                                          ("status", "Status", 90, False)):
            self.tree.heading(key, text=text, anchor="w")
            self.tree.column(key, width=width, anchor="w", stretch=stretch)
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        foot = tk.Frame(self.body, bg=c["bg"])
        foot.pack(fill="x", pady=(14, 0))
        self.summary = tk.Label(foot, text="", bg=c["bg"], fg=c["muted"],
                                font=self.theme.f_small())
        self.summary.pack(side="left")
        self.import_btn = Button(foot, self.theme, "Import cards", command=self.do_import,
                                 kind="solid", color=c["accent"], height=44,
                                 font_size=11, pad_x=28, state="disabled")
        self.import_btn.pack(side="right")
        Button(foot, self.theme, "Clear", command=self.reset, kind="outline",
               color=c["muted"], height=44, font_size=11, pad_x=18).pack(side="right", padx=8)

    # ------------------------------------------------------------------
    def refresh(self):
        names = [d["name"] for d in self.db.decks()]
        self.deck.widget.configure(values=names + [NEW_DECK])
        if self.deck.get() not in names + [NEW_DECK]:
            self.deck.widget.set(names[0] if names else "")

    def _deck_changed(self):
        if self.deck.get() == NEW_DECK:
            self.new_deck.frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
            self.new_deck.focus()
        else:
            self.new_deck.frame.pack_forget()

    def choose_file(self):
        path = filedialog.askopenfilename(
            parent=self.app.root, title="Choose a file to import",
            filetypes=[("Cards", "*.md *.txt *.json *.csv *.tsv"),
                       ("Markdown", "*.md"), ("JSON", "*.json"),
                       ("CSV", "*.csv *.tsv"), ("All files", "*.*")])
        if path:
            self.load(path)

    def load_example(self):
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "docs", "sample-content.json")
        if os.path.exists(path):
            self.load(path)
        else:
            self.app.toast.show("Example file not found", "warn")

    def load(self, path):
        try:
            deck_guess, items = importer.parse_file(path)
        except Exception as exc:
            self.app.toast.show(f"Could not read that file: {exc}", "err", 4000)
            return
        self.file_path = path
        self.items = importer.mark_duplicates(self.db, items)
        self.tree.delete(*self.tree.get_children())
        dups = 0
        for i, it in enumerate(self.items, 1):
            if it["duplicate"]:
                dups += 1
            self.tree.insert("", "end", values=(
                i, it["prompt"][:120], it["answer"][:100],
                "exists" if it["duplicate"] else "new"),
                tags=("dup",) if it["duplicate"] else ())
        self.tree.tag_configure("dup", foreground=self.theme.c["faint"])
        self.zone_title.configure(text=os.path.basename(path))
        self.zone_sub.configure(
            text=f"{len(self.items)} cards found · {len(self.items) - dups} new · "
                 f"{dups} already in the collection")
        self.summary.configure(
            text=f"Ready to import {len(self.items) - (dups if self._skip() else 0)} cards")
        names = [d["name"] for d in self.db.decks()]
        if deck_guess:
            if deck_guess in names:
                self.deck.widget.set(deck_guess)
            else:
                self.deck.widget.set(NEW_DECK)
                self._deck_changed()
                self.new_deck.set(deck_guess)
        self.import_btn.set_state("normal" if self.items else "disabled")

    def _skip(self):
        return bool(self.skip_dupes.instate(["selected"]))

    def reset(self):
        self.items, self.file_path = [], None
        self.tree.delete(*self.tree.get_children())
        self.zone_title.configure(text="No file chosen yet")
        self.zone_sub.configure(text="Supported: .md / .txt (Q:/A: blocks or  prompt :: answer),  "
                                     ".json,  .csv / .tsv")
        self.summary.configure(text="")
        self.import_btn.set_state("disabled")

    def do_import(self):
        if not self.items:
            return
        if self.deck.get() == NEW_DECK:
            name = self.new_deck.get().strip()
            if not name:
                self.app.toast.show("Give the new deck a name", "warn")
                return
            deck_row = self.db.deck_by_name(name) or None
            deck_id = deck_row["id"] if deck_row else self.db.add_deck(name)
        else:
            row = self.db.deck_by_name(self.deck.get())
            if not row:
                self.app.toast.show("Pick a deck", "warn")
                return
            deck_id = row["id"]
        result = importer.import_into(self.db, deck_id, self.items, self._skip())
        self.app.sidebar.refresh_counts()
        self.app.toast.show(f"Added {result['added']} cards"
                            + (f", skipped {result['skipped']} duplicates"
                               if result["skipped"] else ""), "ok", 3000)
        self.reset()
        self.refresh()
