"""Common frame for every screen: title block, action slot, body area."""
import tkinter as tk


class Screen(tk.Frame):
    title = ""
    subtitle = ""

    def __init__(self, master, app, title=None, subtitle=None):
        super().__init__(master, bg=app.theme.c["bg"])
        self.app = app
        self.theme = app.theme
        self.db = app.db
        self.sched = app.sched
        c = self.theme.c

        head = tk.Frame(self, bg=c["bg"])
        head.pack(fill="x", padx=34, pady=(26, 10))
        left = tk.Frame(head, bg=c["bg"])
        left.pack(side="left", anchor="w")
        tk.Label(left, text=title if title is not None else self.title, bg=c["bg"],
                 fg=c["text"], font=self.theme.f_h1(), anchor="w").pack(anchor="w")
        sub = subtitle if subtitle is not None else self.subtitle
        if sub:
            tk.Label(left, text=sub, bg=c["bg"], fg=c["muted"],
                     font=self.theme.f_body(), anchor="w").pack(anchor="w", pady=(3, 0))
        self.actions = tk.Frame(head, bg=c["bg"])
        self.actions.pack(side="right", anchor="e")

        self.body = tk.Frame(self, bg=c["bg"])
        self.body.pack(fill="both", expand=True, padx=34, pady=(6, 26))

    # override as needed
    def on_show(self):
        self.refresh()

    def refresh(self):
        pass

    def on_key(self, event):
        return False

    def card_panel(self, parent, pad=22, radius=16, fill=None):
        from widgets import Panel
        return Panel(parent, self.theme, pad=pad, radius=radius, fill=fill)


def forget_study_card(app):
    """The queue changed: the study screen should reload instead of a stale card."""
    screen = app.screens.get("study")
    if screen is not None:
        screen.card = None
