"""The study screen: one card, four buttons, keyboard shortcuts."""
import time
import tkinter as tk
from tkinter import ttk

from base import Screen
from widgets import Badge, Button, Link, Panel, round_rect

STATE_STYLE = {
    "new":       ("NEW", "accent"),
    "learning":  ("LEARNING", "amber"),
    "review":    ("REVIEW", "green"),
    "relearning": ("RELEARNING", "amber"),
}


class StudyScreen(Screen):
    title = "Study"
    subtitle = "Answer from memory, then check. Forgetting is where the learning happens."

    def __init__(self, master, app):
        super().__init__(master, app)
        c = self.theme.c
        self.card = None
        self.revealed = False
        self.started = time.time()
        self.deck_id = None
        self.session_count = 0
        self.session_start = time.time()

        # ---- top bar -----------------------------------------------------
        top = tk.Frame(self.body, bg=c["bg"])
        top.pack(fill="x")
        tk.Label(top, text="Deck", bg=c["bg"], fg=c["muted"],
                 font=self.theme.f_small_b()).pack(side="left", padx=(0, 8))
        self.deck_box = ttk.Combobox(top, state="readonly", width=24,
                                     font=self.theme.f_body())
        self.deck_box.pack(side="left")
        self.deck_box.bind("<<ComboboxSelected>>", self._deck_changed)

        self.count_new = Badge(top, self.theme, "0 new", parent_bg=c["bg"])
        self.count_learn = Badge(top, self.theme, "0 learning", parent_bg=c["bg"])
        self.count_due = Badge(top, self.theme, "0 due", parent_bg=c["bg"])
        for b in (self.count_due, self.count_learn, self.count_new):
            b.pack(side="right", padx=(8, 0))

        # ---- card --------------------------------------------------------
        self.panel = Panel(self.body, self.theme, pad=28, radius=18)
        self.panel.pack(fill="both", expand=True, pady=(16, 0))
        body = self.panel.body
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=3)   # prompt
        body.grid_rowconfigure(2, weight=0)   # divider
        body.grid_rowconfigure(3, weight=2)   # answer

        meta = tk.Frame(body, bg=c["surface"])
        meta.grid(row=0, column=0, sticky="ew")
        self.state_badge = Badge(meta, self.theme, "NEW", parent_bg=c["surface"])
        self.state_badge.pack(side="left")
        self.deck_label = tk.Label(meta, text="", bg=c["surface"], fg=c["faint"],
                                   font=self.theme.f_small())
        self.deck_label.pack(side="left", padx=(10, 0))
        self.tags_label = tk.Label(meta, text="", bg=c["surface"], fg=c["faint"],
                                   font=self.theme.f_small())
        self.tags_label.pack(side="right")

        self.prompt_zone = tk.Frame(body, bg=c["surface"])
        self.prompt_zone.grid(row=1, column=0, sticky="nsew")
        self.prompt_zone.grid_rowconfigure(0, weight=1)
        self.prompt_zone.grid_rowconfigure(2, weight=1)
        self.prompt_zone.grid_columnconfigure(0, weight=1)
        self.prompt_label = tk.Label(self.prompt_zone, text="", bg=c["surface"],
                                     fg=c["text"], font=self.theme.f_display(),
                                     wraplength=760, justify="center")
        self.prompt_label.grid(row=1, column=0)
        self.prompt_zone.bind("<Configure>", self._resize_text)

        self.divider = tk.Frame(body, bg=c["border"], height=1)
        self.divider.grid(row=2, column=0, sticky="ew", pady=6)

        self.answer_zone = tk.Frame(body, bg=c["surface"])
        self.answer_zone.grid(row=3, column=0, sticky="nsew")
        self.answer_zone.grid_columnconfigure(0, weight=1)
        self.answer_zone.grid_rowconfigure(0, weight=1)
        self.answer_zone.grid_rowconfigure(3, weight=1)
        inner = tk.Frame(self.answer_zone, bg=c["surface"])
        inner.grid(row=1, column=0)
        self.answer_label = tk.Label(inner, text="", bg=c["surface"], fg=c["text"],
                                     font=self.theme.font(15, "bold"),
                                     wraplength=740, justify="center")
        self.answer_label.pack()
        self.expl_label = tk.Label(inner, text="", bg=c["surface"], fg=c["muted"],
                                   font=self.theme.f_body(), wraplength=720,
                                   justify="center")
        self.expl_label.pack(pady=(10, 0))
        self.source_label = tk.Label(inner, text="", bg=c["surface"], fg=c["faint"],
                                     font=self.theme.f_tiny(), wraplength=720,
                                     justify="center")
        self.source_label.pack(pady=(8, 0))

        self.hint = tk.Label(self.answer_zone, text="Answer hidden — recall it first",
                             bg=c["surface"], fg=c["faint"], font=self.theme.f_small())
        self.hint.place(relx=0.5, rely=0.25, anchor="center")

        # ---- buttons -----------------------------------------------------
        self.btn_row = tk.Frame(self.body, bg=c["bg"])
        self.btn_row.pack(fill="x", pady=(16, 0))
        self.footer = tk.Label(self.body, bg=c["bg"], fg=c["faint"],
                               font=self.theme.f_tiny())
        self.footer.pack(pady=(10, 0))
        self._build_buttons()

    # ------------------------------------------------------------- state
    def refresh(self):
        self._reload_decks()
        self.load_next()

    def on_show(self):
        self._reload_decks()
        self._update_counts()
        if not self.card:
            self.load_next()
        self.focus_set()

    def _reload_decks(self):
        names = ["All decks"] + [d["name"] for d in self.db.decks()]
        self.deck_box.configure(values=names)
        if not self.deck_box.get() or self.deck_box.get() not in names:
            self.deck_box.set("All decks")

    def _deck_changed(self, _e=None):
        name = self.deck_box.get()
        if name == "All decks":
            self.deck_id = None
        else:
            row = self.db.deck_by_name(name)
            self.deck_id = row["id"] if row else None
        self.session_count = 0
        self.load_next()

    def _resize_text(self, event):
        width = max(320, event.width - 80)
        self.prompt_label.configure(wraplength=width)
        self.answer_label.configure(wraplength=width)
        self.expl_label.configure(wraplength=width)

    # -------------------------------------------------------------- queue
    def _update_counts(self):
        counts = self.db.counts(self.deck_id)
        c = self.theme.c
        self.count_new.set_text(f"{counts['new']} new")
        self.count_learn.set_text(f"{counts['learning']} learning")
        self.count_due.set_text(f"{counts['due']} due")
        self.count_due.set_colors(c["green_hi"], c["green_soft"])
        self.count_learn.set_colors(c["amber_hi"], c["amber_soft"])
        self.count_new.set_colors(c["accent_hi"], c["accent_soft"])

    def load_next(self):
        self._update_counts()
        card = self.db.next_card(self.deck_id)
        self.card, self.revealed, self.started = card, False, time.time()
        if not card:
            self._show_empty()
            return
        self.panel.pack(fill="both", expand=True, pady=(16, 0))
        self.btn_row.pack(fill="x", pady=(16, 0))
        self.footer.pack(pady=(10, 0))
        if self.empty is not None:
            self.empty.pack_forget()

        c = self.theme.c
        label, colour = STATE_STYLE.get(card["state"], ("CARD", "accent"))
        self.state_badge.set_text(label)
        self.state_badge.set_colors(c[colour + "_hi"], c[colour + "_soft"])
        self.deck_label.configure(text=card["deck_name"])
        tags = card["tags"] or ""
        self.tags_label.configure(text=tags)

        prompt, answer = card["prompt"], card["answer"]
        if card["ordinal"] == 1:
            prompt, answer = answer, prompt
        self._prompt, self._answer = prompt, answer
        # long text gets a smaller size so a card never overflows its panel
        size = 26 if len(prompt) <= 80 else 22 if len(prompt) <= 160 else 18 if len(prompt) <= 300 else 15
        self.prompt_label.configure(text=prompt, font=self.theme.font(size, "bold"))
        asize = 15 if len(answer) <= 60 else 14 if len(answer) <= 160 else 12
        self.answer_label.configure(text=answer, font=self.theme.font(asize, "bold"))
        self.expl_label.configure(text=card["explanation"] or "")
        src = card["source"] or ""
        self.source_label.configure(text=f"Source: {src}" if src else "")
        self.hint.place(relx=0.5, rely=0.25, anchor="center")
        self.answer_label.pack_forget()
        self.expl_label.pack_forget()
        self.source_label.pack_forget()
        self._build_buttons()

    # ------------------------------------------------------------ reveal
    def reveal(self, _e=None):
        if not self.card or self.revealed:
            return
        self.revealed = True
        self.hint.place_forget()
        self.answer_label.pack()
        if self.card["explanation"]:
            self.expl_label.pack(pady=(10, 0))
        if self.card["source"]:
            self.source_label.pack(pady=(8, 0))
        self._build_buttons()

    def _build_buttons(self):
        for w in self.btn_row.winfo_children():
            w.destroy()
        c = self.theme.c
        if not self.card:
            return
        if not self.revealed:
            Button(self.btn_row, self.theme, "Show answer", command=self.reveal,
                   kind="solid", color=c["accent"], height=46, font_size=12,
                   pad_x=48).pack(side="left")
            self.footer.configure(
                text="Space / Enter shows the answer    ·    1-4 grade    ·    Ctrl+Z undoes")
            return

        previews = self.sched.preview(self.card)
        specs = [(1, "Again", c["red"]), (2, "Hard", c["amber"]),
                 (3, "Good", c["green"]), (4, "Easy", c["blue"])]
        for rating, label, colour in specs:
            Button(self.btn_row, self.theme, label, sub=previews.get(rating, ""),
                   command=lambda r=rating: self.grade(r), kind="solid", color=colour,
                   height=48, font_size=12).pack(side="left", fill="x", expand=True,
                                                 padx=(0, 10))
        Button(self.btn_row, self.theme, "Undo", command=self.app.undo_review,
               kind="outline", color=c["muted"], height=48, font_size=11,
               pad_x=18).pack(side="left")
        self.footer.configure(text="1 = Again   2 = Hard   3 = Good   4 = Easy"
                                   "    ·    Ctrl+Z undoes the last answer")

    # ------------------------------------------------------------- grade
    def grade(self, rating):
        if not self.card or not self.revealed:
            return
        took = int((time.time() - self.started) * 1000)
        self.sched.grade(self.card, rating, took)
        self.session_count += 1
        self.app.sidebar.refresh_counts()
        self.load_next()

    # -------------------------------------------------------- empty state
    empty = None

    def _show_empty(self):
        c = self.theme.c
        self.panel.pack_forget()
        self.btn_row.pack_forget()
        self.footer.pack_forget()
        if self.empty is not None:
            self.empty.destroy()
        self.empty = Panel(self.body, self.theme, pad=30, radius=18)
        self.empty.pack(fill="both", expand=True, pady=(16, 0))
        body = self.empty.body
        tk.Label(body, text="Nothing due right now", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(20, "bold")).pack(pady=(30, 8))
        done = self.session_count
        wait = self.db.next_due(self.deck_id)
        if wait is not None and wait < 3600:
            msg = ("Next card in about %d minute%s. The gap is doing the work — "
                   "come back then." % (max(1, round(wait / 60)),
                                        "" if round(wait / 60) == 1 else "s"))
        elif wait is not None and wait < 36 * 3600:
            msg = ("Next card in about %d hours. %d card%s answered here."
                   % (round(wait / 3600), done, "" if done == 1 else "s"))
        else:
            msg = ("You answered %d card%s in this session. Come back when the next ones are "
                   "due — the gap is doing the work." % (done, "" if done == 1 else "s"))
        tk.Label(body, text=msg, bg=c["surface"], fg=c["muted"], font=self.theme.f_body(),
                 wraplength=560, justify="center").pack(pady=(0, 22))
        row = tk.Frame(body, bg=c["surface"])
        row.pack()
        Button(row, self.theme, "Add cards", command=lambda: self.app.show("add"),
               kind="soft", color=c["accent"], height=42, bg=c["surface"]).pack(side="left", padx=6)
        Button(row, self.theme, "Import material", command=lambda: self.app.show("import"),
               kind="soft", color=c["accent"], height=42, bg=c["surface"]).pack(side="left", padx=6)
        Button(row, self.theme, "See stats", command=lambda: self.app.show("stats"),
               kind="outline", color=c["muted"], height=42, bg=c["surface"]).pack(side="left", padx=6)

    # --------------------------------------------------------------- keys
    def on_key(self, event):
        if event.keysym in ("space", "Return"):
            if not self.revealed:
                self.reveal()
            return True
        if event.char in "1234" and self.revealed:
            self.grade(int(event.char))
            return True
        return False
