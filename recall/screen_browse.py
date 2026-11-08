"""Browse, search, edit and delete the cards that exist."""
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from base import Screen, forget_study_card
from forms import Field, SearchEntry
from widgets import Button

STATE_TEXT = {"new": "New", "learning": "Learning", "review": "Review",
              "relearning": "Relearning"}


def due_text(row):
    if row["state"] == "new":
        return "—"
    ts = row["due"] or 0
    delta = ts - time.time()
    if row["state"] in ("learning", "relearning"):
        if delta <= 0:
            return "now"
        mins = delta / 60
        return f"{int(mins)}m" if mins < 60 else f"{mins / 60:.1f}h"
    if delta <= 0:
        return "due now"
    days = delta / 86400
    if days < 1:
        return f"{int(delta / 3600)}h"
    if days < 31:
        return f"in {int(days)}d"
    return datetime.fromtimestamp(ts).strftime("%d %b %Y")


class BrowseScreen(Screen):
    title = "Browse"
    subtitle = "Every card you have. Double-click one to edit it."

    def __init__(self, master, app):
        super().__init__(master, app)
        c = self.theme.c
        self.filter = ""

        bar = tk.Frame(self.body, bg=c["bg"])
        bar.pack(fill="x", pady=(0, 12))
        self.search = SearchEntry(bar, self.theme, "Search prompts, answers, tags…",
                                  width=34, command=self._search)
        self.search.pack(side="left")
        self.deck_box = ttk.Combobox(bar, state="readonly", width=20,
                                     font=self.theme.f_body())
        self.deck_box.pack(side="left", padx=10)
        self.deck_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.count_label = tk.Label(bar, text="", bg=c["bg"], fg=c["muted"],
                                    font=self.theme.f_small())
        self.count_label.pack(side="left", padx=12)

        Button(bar, self.theme, "Add card", command=lambda: self.app.show("add"),
               kind="solid", color=c["accent"], height=38, font_size=10,
               pad_x=16).pack(side="right")

        wrap = tk.Frame(self.body, bg=c["border"], padx=1, pady=1)
        wrap.pack(fill="both", expand=True)
        cols = ("prompt", "answer", "deck", "state", "due", "lapses")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="browse")
        heads = {"prompt": ("Prompt", 380), "answer": ("Answer", 320),
                 "deck": ("Deck", 120), "state": ("State", 100),
                 "due": ("Due", 110), "lapses": ("Lapses", 70)}
        for key, (text, width) in heads.items():
            self.tree.heading(key, text=text, anchor="w")
            self.tree.column(key, width=width, anchor="w", stretch=(key in ("prompt", "answer")))
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.tree.bind("<Return>", lambda e: self.edit_selected())
        self.tree.bind("<Delete>", lambda e: self.delete_selected())

        actions = tk.Frame(self.body, bg=c["bg"])
        actions.pack(fill="x", pady=(12, 0))
        Button(actions, self.theme, "Edit", command=self.edit_selected, kind="outline",
               color=c["text"], height=38, font_size=10, pad_x=18).pack(side="left")
        Button(actions, self.theme, "Delete", command=self.delete_selected, kind="ghost",
               color=c["red"], height=38, font_size=10, pad_x=18).pack(side="left", padx=6)
        Button(actions, self.theme, "Reset progress", command=self.reset_selected,
               kind="outline", color=c["amber"], height=38, font_size=10,
               pad_x=18).pack(side="left")
        tk.Label(actions, text="Tip: Enter edits, Delete removes.", bg=c["bg"],
                 fg=c["faint"], font=self.theme.f_tiny()).pack(side="right")

    # ------------------------------------------------------------------
    def _search(self, value):
        self.filter = value
        self.refresh()

    def refresh(self):
        names = ["All decks"] + [d["name"] for d in self.db.decks()]
        current = self.deck_box.get()
        self.deck_box.configure(values=names)
        if current not in names:
            current = "All decks"
            self.deck_box.set(current)
        deck_id = None
        if current != "All decks":
            row = self.db.deck_by_name(current)
            deck_id = row["id"] if row else None

        self.tree.delete(*self.tree.get_children())
        rows = self.db.items(deck_id, self.filter)
        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["prompt"][:110], r["answer"][:90].replace("\n", " "),
                r["deck_name"], STATE_TEXT.get(r["state"], r["state"]),
                due_text(r), r["lapses"] or 0))
        self.count_label.configure(text=f"{len(rows)} card{'s' if len(rows) != 1 else ''}")

    def _selected_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Nothing selected", "Pick a card in the list first.",
                                parent=self.app.root)
            return None
        return int(sel[0])

    def edit_selected(self):
        item_id = self._selected_item()
        if item_id:
            ItemDialog(self.app, item_id=item_id, on_save=self.refresh)

    def delete_selected(self):
        item_id = self._selected_item()
        if not item_id:
            return
        item = self.db.item(item_id)
        if messagebox.askyesno("Delete card", f"Delete this card?\n\n{item['prompt'][:120]}",
                               parent=self.app.root):
            self.db.delete_item(item_id)
            self.app.sidebar.refresh_counts()
            self.refresh()

    def reset_selected(self):
        """Put one card back to new: no schedule, no history, the card itself stays."""
        item_id = self._selected_item()
        if not item_id:
            return
        item = self.db.item(item_id)
        n = len(self.db.card_ids_for_item(item_id))
        if not messagebox.askyesno(
                "Reset progress",
                f"Reset this card?\n\n{item['prompt'][:140]}\n\n"
                f"{n} card side{'s' if n != 1 else ''} go back to New: schedule, "
                "stability and the whole review history of this card are deleted. "
                "The card itself stays.\n\nThis cannot be undone.",
                parent=self.app.root, icon="warning", default="no"):
            return
        self.db.reset_item(item_id)
        forget_study_card(self.app)
        self.app.toast.show("Card reset — it is new again", "warn")
        self.app.sidebar.refresh_counts()
        self.refresh()


class ItemDialog(tk.Toplevel):
    """Edit one existing item."""

    def __init__(self, app, item_id, on_save=None):
        super().__init__(app.root)
        self.app, self.db, self.theme = app, app.db, app.theme
        self.item_id, self.on_save = item_id, on_save
        c = self.theme.c
        item = self.db.item(item_id)
        self.configure(bg=c["bg"])
        self.title("Edit card")
        self.transient(app.root)
        self.grab_set()
        self.geometry("680x620")
        self.minsize(560, 520)

        head = tk.Frame(self, bg=c["bg"])
        head.pack(fill="x", padx=24, pady=(20, 4))
        tk.Label(head, text="Edit card", bg=c["bg"], fg=c["text"],
                 font=self.theme.f_h2()).pack(side="left")

        wrap = tk.Frame(self, bg=c["bg"])
        wrap.pack(fill="both", expand=True, padx=24, pady=12)

        self.f_prompt = Field(wrap, self.theme, "Prompt (question)", kind="text", height=3,
                              value=item["prompt"])
        self.f_prompt.frame.pack(fill="x", pady=(0, 12))
        self.f_answer = Field(wrap, self.theme, "Answer", kind="text", height=3,
                              value=item["answer"])
        self.f_answer.frame.pack(fill="x", pady=(0, 12))
        self.f_expl = Field(wrap, self.theme, "Explanation (optional)", kind="text",
                            height=2, value=item["explanation"] or "")
        self.f_expl.frame.pack(fill="x", pady=(0, 12))
        row = tk.Frame(wrap, bg=c["bg"])
        row.pack(fill="x", pady=(0, 12))
        self.f_source = Field(row, self.theme, "Source", kind="entry",
                              value=item["source"] or "")
        self.f_source.frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.f_tags = Field(row, self.theme, "Tags", kind="entry",
                            value=item["tags"] or "")
        self.f_tags.frame.pack(side="left", fill="x", expand=True)

        self.error = tk.Label(wrap, text="", bg=c["bg"], fg=c["red"],
                              font=self.theme.f_small())
        self.error.pack(anchor="w")

        foot = tk.Frame(self, bg=c["bg"])
        foot.pack(fill="x", padx=24, pady=(0, 20))
        Button(foot, self.theme, "Save", command=self.save, kind="solid",
               color=c["accent"], height=42, font_size=11, pad_x=30).pack(side="right")
        Button(foot, self.theme, "Cancel", command=self.destroy, kind="outline",
               color=c["muted"], height=42, font_size=11, pad_x=22).pack(side="right", padx=8)

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-Return>", lambda e: self.save())
        self.f_prompt.focus()

    def save(self):
        prompt, answer = self.f_prompt.get(), self.f_answer.get()
        if not prompt or not answer:
            self.error.configure(text="A card needs both a prompt and an answer.")
            return
        self.db.update_item(self.item_id, prompt=prompt, answer=answer,
                            explanation=self.f_expl.get(), source=self.f_source.get(),
                            tags=self.f_tags.get())
        if self.on_save:
            self.on_save()
        self.app.toast.show("Card updated")
        self.destroy()
