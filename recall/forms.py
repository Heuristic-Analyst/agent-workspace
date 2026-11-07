"""Form fields shared by the add / edit / settings screens."""
import tkinter as tk
from tkinter import ttk


class Field:
    """Label above an input widget, with uniform spacing."""

    def __init__(self, master, theme, label, kind="entry", height=3,
                 value="", hint="", width=4, unit=""):
        self.theme = theme
        self.frame = tk.Frame(master, bg=master["bg"])
        head = tk.Frame(self.frame, bg=master["bg"])
        head.pack(fill="x", pady=(0, 5))
        tk.Label(head, text=label, bg=master["bg"], fg=theme.c["muted"],
                 font=theme.f_small_b(), anchor="w").pack(side="left")
        if unit:
            tk.Label(head, text=unit, bg=master["bg"], fg=theme.c["faint"],
                     font=theme.f_small(), anchor="w").pack(side="left", padx=(6, 0))
        if hint:
            tk.Label(head, text=hint, bg=master["bg"], fg=theme.c["faint"],
                     font=theme.f_tiny(), anchor="e").pack(side="right")

        box = tk.Frame(self.frame, bg=theme.c["border"], padx=1, pady=1)
        box.pack(fill="x")
        if kind == "entry":
            self.widget = tk.Entry(box, bg=theme.c["surface"], fg=theme.c["text"],
                                   insertbackground=theme.c["text"], relief="flat",
                                   font=theme.f_body(), width=width)
            self.widget.pack(fill="x", ipady=7, ipadx=8)
        elif kind == "text":
            self.widget = tk.Text(box, bg=theme.c["surface"], fg=theme.c["text"],
                                  insertbackground=theme.c["text"], relief="flat",
                                  font=theme.f_body(), height=height, width=4,
                                  wrap="word", padx=8, pady=7, undo=True)
            self.widget.pack(fill="both", expand=True)
        elif kind == "combo":
            self.widget = ttk.Combobox(box, values=value if isinstance(value, list) else [],
                                       state="readonly", font=theme.f_body())
            self.widget.pack(fill="x", ipady=3, ipadx=2)
            if isinstance(value, str) and value:
                self.widget.set(value)
        elif kind == "scale":
            self.widget = tk.Scale(box, from_=70, to=97, orient="horizontal",
                                   bg=theme.c["surface"], fg=theme.c["text"],
                                   troughcolor=theme.c["border"], highlightthickness=0,
                                   bd=0, sliderrelief="flat", font=theme.f_small(),
                                   activebackground=theme.c["accent"],
                                   showvalue=True, sliderlength=18)
            self.widget.pack(fill="x", padx=6, pady=4)
        if kind in ("entry", "text") and value:
            self.set(value)

    # -- value access ----------------------------------------------------
    def get(self):
        w = self.widget
        if isinstance(w, tk.Text):
            return w.get("1.0", "end-1c").strip()
        if isinstance(w, tk.Scale):
            return w.get()
        return w.get().strip()

    def set(self, value):
        w = self.widget
        if isinstance(w, tk.Text):
            w.delete("1.0", "end")
            w.insert("1.0", value)
        elif isinstance(w, tk.Scale):
            w.set(value)
        elif isinstance(w, ttk.Combobox):
            w.set(value)
        else:
            w.delete(0, "end")
            w.insert(0, value)

    def focus(self):
        self.widget.focus_set()
        if isinstance(self.widget, tk.Text):
            self.widget.mark_set("insert", "1.0")


class SearchEntry(tk.Frame):
    """Entry with a muted placeholder."""

    def __init__(self, master, theme, placeholder="Search", width=32, command=None):
        super().__init__(master, bg=theme.c["border"], padx=1, pady=1)
        self.theme = theme
        self.placeholder = placeholder
        self.command = command
        self.entry = tk.Entry(self, bg=theme.c["surface"], fg=theme.c["faint"],
                              insertbackground=theme.c["text"], relief="flat",
                              font=theme.f_body(), width=width)
        self.entry.pack(fill="x", ipady=7, ipadx=8)
        self.entry.insert(0, placeholder)
        self.entry.bind("<FocusIn>", self._in)
        self.entry.bind("<FocusOut>", self._out)
        self.entry.bind("<KeyRelease>", self._typed)
        self.entry.bind("<Return>", self._typed)
        self.entry.bind("<Escape>", lambda e: self.clear())

    def _in(self, _e):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=self.theme.c["text"])

    def _out(self, _e):
        if not self.entry.get().strip():
            self.entry.delete(0, "end")
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.theme.c["faint"])

    def _typed(self, _e=None):
        if self.command:
            self.command(self.value())

    def value(self):
        v = self.entry.get()
        return "" if v == self.placeholder else v.strip()

    def clear(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, self.placeholder)
        self.entry.configure(fg=self.theme.c["faint"])
        if self.command:
            self.command("")
