"""Create new cards by hand, with a live preview of what you will be asked."""
import tkinter as tk
from tkinter import ttk

from base import Screen
from forms import Field
from widgets import Button, Panel, ScrollFrame

GOOD_CARD_TIPS = [
    "One fact per card. If the answer has an “and”, split it.",
    "Write it in your own words — the wording you would actually say.",
    "Ask “why” and “how” where you can; it beats “what is”.",
    "Add the source, so you can check it again later.",
]


class AddScreen(Screen):
    title = "Add card"
    subtitle = "Small, specific cards are the ones that survive."

    def __init__(self, master, app):
        super().__init__(master, app)
        c = self.theme.c
        scroll = ScrollFrame(self.body, c["bg"])
        scroll.pack(fill="both", expand=True)
        wrap = scroll.inner

        right = tk.Frame(wrap, bg=c["bg"], width=350)
        right.pack(side="right", fill="y", padx=(24, 0))
        right.pack_propagate(False)
        left = tk.Frame(wrap, bg=c["bg"])
        left.pack(side="left", fill="both", expand=True)

        top = tk.Frame(left, bg=c["bg"])
        top.pack(fill="x", pady=(0, 12))
        self.deck = Field(top, self.theme, "Deck", kind="combo", value=[])
        self.deck.frame.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.reverse = ttk.Checkbutton(top, text="Also make the reverse card",
                                       style="TCheckbutton")
        self.reverse.pack(side="left", pady=(18, 0))

        self.f_prompt = Field(left, self.theme, "Prompt", kind="text", height=3,
                              hint="the question")
        self.f_prompt.frame.pack(fill="x", pady=(0, 12))
        self.f_answer = Field(left, self.theme, "Answer", kind="text", height=3,
                              hint="short and exact")
        self.f_answer.frame.pack(fill="x", pady=(0, 12))
        self.f_expl = Field(left, self.theme, "Explanation", kind="text", height=2,
                            hint="optional, shown after the answer")
        self.f_expl.frame.pack(fill="x", pady=(0, 12))
        row = tk.Frame(left, bg=c["bg"])
        row.pack(fill="x", pady=(0, 12))
        self.f_source = Field(row, self.theme, "Source", kind="entry")
        self.f_source.frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.f_tags = Field(row, self.theme, "Tags", kind="entry")
        self.f_tags.frame.pack(side="left", fill="x", expand=True)

        self.error = tk.Label(left, text="", bg=c["bg"], fg=c["red"],
                              font=self.theme.f_small())
        self.error.pack(anchor="w", pady=(2, 0))

        actions = tk.Frame(left, bg=c["bg"])
        actions.pack(fill="x", pady=(12, 0))
        Button(actions, self.theme, "Add card", command=self.save, kind="solid",
               color=c["accent"], height=44, font_size=11, pad_x=30).pack(side="left")
        Button(actions, self.theme, "Clear", command=self.clear, kind="outline",
               color=c["muted"], height=44, font_size=11, pad_x=20).pack(side="left", padx=8)
        tk.Label(actions, text="Ctrl+Enter saves", bg=c["bg"], fg=c["faint"],
                 font=self.theme.f_tiny()).pack(side="right")

        # ---- right column: preview + tips ------------------------------
        tk.Label(right, text="PREVIEW", bg=c["bg"], fg=c["faint"],
                 font=self.theme.f_small_b()).pack(anchor="w", pady=(0, 6))
        self.preview = Panel(right, self.theme, pad=20, radius=16)
        self.preview.pack(fill="x")
        pb = self.preview.body
        self.prev_prompt = tk.Label(pb, text="Your question appears here", bg=c["surface"],
                                    fg=c["text"], font=self.theme.font(15, "bold"),
                                    wraplength=250, justify="center")
        self.prev_prompt.pack(expand=True, pady=(14, 6))
        self.prev_answer = tk.Label(pb, text="", bg=c["surface"], fg=c["muted"],
                                    font=self.theme.f_body(), wraplength=250,
                                    justify="center")
        self.prev_answer.pack(expand=True, pady=(0, 14))

        tips = Panel(right, self.theme, pad=18, radius=16, fill=c["surface_alt"],
                     shadow=False)
        tips.pack(fill="x", pady=(16, 0))
        tk.Label(tips.body, text="What makes a card work", bg=c["surface_alt"],
                 fg=c["text"], font=self.theme.font(10, "bold")).pack(anchor="w")
        for t in GOOD_CARD_TIPS:
            tk.Label(tips.body, text="·  " + t, bg=c["surface_alt"], fg=c["muted"],
                     font=self.theme.f_small(), wraplength=270, justify="left",
                     anchor="w").pack(anchor="w", pady=(6, 0))

        self.f_prompt.widget.bind("<KeyRelease>", lambda e: self._update_preview())
        self.f_answer.widget.bind("<KeyRelease>", lambda e: self._update_preview())

    # ------------------------------------------------------------------
    def refresh(self):
        names = [d["name"] for d in self.db.decks()]
        self.deck.widget.configure(values=names)
        if self.deck.get() not in names and names:
            self.deck.widget.set(names[0])
        self.f_prompt.focus()

    def _update_preview(self):
        prompt = self.f_prompt.get() or "Your question appears here"
        answer = self.f_answer.get()
        self.prev_prompt.configure(text=prompt[:300])
        self.prev_answer.configure(text=("Answer: " + answer[:200]) if answer else "")

    def clear(self):
        for f in (self.f_prompt, self.f_answer, self.f_expl, self.f_source, self.f_tags):
            f.set("")
        self.error.configure(text="")
        self._update_preview()
        self.f_prompt.focus()

    def save(self):
        prompt, answer = self.f_prompt.get(), self.f_answer.get()
        if not prompt or not answer:
            self.error.configure(text="A card needs both a prompt and an answer.")
            return
        deck_row = self.db.deck_by_name(self.deck.get())
        if not deck_row:
            self.error.configure(text="Pick a deck first.")
            return
        if self.db.item_exists(prompt, answer):
            self.error.configure(text="That card already exists — not added again.")
            return
        self.db.add_item(deck_row["id"], prompt, answer, self.f_expl.get(),
                         self.f_source.get(), self.f_tags.get(),
                         reverse=bool(self.reverse.instate(["selected"])))
        self.app.sidebar.refresh_counts()
        self.app.toast.show("Card added")
        self.clear()

    def on_key(self, event):
        if event.keysym == "Return" and event.state & 0x4:   # Ctrl+Enter
            self.save()
            return True
        return False
