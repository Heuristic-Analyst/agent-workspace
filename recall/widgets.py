"""Small widget kit: rounded panels, pill buttons, badges, scroll areas, toasts.

Plain tkinter looks dated.  Everything here is built from Canvas + Label so it
renders the same on macOS, Windows and Linux, without images or extra packages.
"""
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont


# ---------------------------------------------------------------- geometry
def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Draw a rounded rectangle on a canvas (the classic smooth-polygon trick)."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, splinesteps=24, **kw)


# ---------------------------------------------------------------- panel
class Panel(tk.Canvas):
    """A rounded surface with an optional soft shadow. Put children in `.body`."""

    def __init__(self, master, theme, radius=16, fill=None, border=None,
                 pad=18, shadow=True, bg=None, width=10, height=None,
                 autosize=None):
        self.theme = theme
        self.fill = fill or theme.c["surface"]
        self.border = border
        self.radius = radius
        self.pad = pad
        self.shadow = shadow
        # With no explicit height a panel grows to fit its content.  Without
        # this, a panel packed with fill="x" keeps its 10px default height.
        self.autosize = (height is None) if autosize is None else autosize
        height = height or 10
        outer = bg or theme.c["bg"]
        super().__init__(master, bg=outer, highlightthickness=0, bd=0,
                         width=width, height=height, takefocus=0)
        self.body = tk.Frame(self, bg=self.fill)
        self.bind("<Configure>", self._redraw)
        self.body.bind("<Configure>", self._fit)

    def _fit(self, _e=None):
        if not self.autosize:
            return
        need = self.body.winfo_reqheight() + 2 * self.pad + (3 if self.shadow else 0)
        if abs(need - int(self["height"])) > 2:
            self.configure(height=need)

    def _redraw(self, _e=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 2 or h <= 2:
            return
        if self.shadow:
            off = 3
            round_rect(self, 1, off, w - 1, h - 1, self.radius,
                       fill=self.theme.c["shadow"], outline="")
            round_rect(self, 0, 0, w - 2, h - off - 1, self.radius,
                       fill=self.fill, outline=self.border or self.fill,
                       width=1 if self.border else 0)
            self.body.place(x=self.pad, y=self.pad,
                            width=w - 2 * self.pad - 2,
                            height=h - 2 * self.pad - off)
        else:
            round_rect(self, 0, 0, w, h, self.radius,
                       fill=self.fill, outline=self.border or self.fill,
                       width=1 if self.border else 0)
            self.body.place(x=self.pad, y=self.pad,
                            width=w - 2 * self.pad, height=h - 2 * self.pad)
        self.tag_lower("all")
        self.body.lift()

    def configure_fill(self, fill, border=None):
        self.fill = fill
        if border is not None:
            self.border = border
        self.body.configure(bg=fill)
        self._redraw()


# ---------------------------------------------------------------- button
class Button(tk.Canvas):
    """Rounded pill button with a main label and an optional small sub-label."""

    def __init__(self, master, theme, text="", command=None, kind="solid", sub="",
                 color=None, text_color=None, width=None, height=40,
                 font_size=11, radius=None, pad_x=20, bg=None, state="normal"):
        self.theme = theme
        self._text = text
        self._sub = sub
        self.command = command
        self.kind = kind
        self.color = color or theme.c["accent"]
        self.text_color = text_color
        self.h = height
        self.font_size = font_size
        self.radius = radius if radius is not None else height // 2
        self.pad_x = pad_x
        self._state = state
        self._hover = False
        self._pressed = False
        self._fixed_w = width
        outer = bg or theme.c["bg"]
        super().__init__(master, bg=outer, highlightthickness=0, bd=0,
                         height=height, cursor="hand2", takefocus=0)
        self._measure()
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    # -- size ------------------------------------------------------------
    def _measure(self):
        f = self.theme.font(self.font_size, "bold")
        fs = self.theme.font(max(7, self.font_size - 2))
        w1 = tkfont.Font(font=f).measure(self._text) if self._text else 0
        w2 = tkfont.Font(font=fs).measure(self._sub) if self._sub else 0
        w = max(w1, w2) + 2 * self.pad_x
        if self._fixed_w:
            w = self._fixed_w
        self.configure(width=w, height=self.h)

    def set_text(self, text=None, sub=None):
        if text is not None:
            self._text = text
        if sub is not None:
            self._sub = sub
        self._measure()
        self._draw()

    def set_state(self, state):
        self._state = state
        self.configure(cursor="hand2" if state == "normal" else "arrow")
        self._draw()

    # -- colours ---------------------------------------------------------
    def _colors(self):
        c = self.theme.c
        if self.kind == "soft":
            base = self.color
            bg = c["surface_alt"]
            fg = base
        elif self.kind == "ghost":
            bg = c["bg"]
            fg = self.color
        elif self.kind == "outline":
            bg = c["surface"]
            fg = self.color if self.text_color is None else self.text_color
        else:
            bg = self.color
            fg = self.text_color or "#FFFFFF"
        if self.kind in ("solid",) and self._state == "disabled":
            bg = c["border_hi"]
            fg = c["faint"]
        elif self._state == "disabled":
            fg = c["faint"]
        elif self._hover:
            if self.kind == "solid":
                bg = self._shade(bg, -0.10)
            elif self.kind == "soft":
                bg = c["border"]
            else:
                bg = c["surface_alt"]
        if self._pressed:
            bg = self._shade(bg, -0.06)
        return bg, fg

    @staticmethod
    def _shade(hex_color, amount):
        try:
            h = hex_color.lstrip("#")
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        except Exception:
            return hex_color
        f = 1 + amount
        r, g, b = (max(0, min(255, int(v * f))) for v in (r, g, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    # -- drawing ---------------------------------------------------------
    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 2:
            w = self.winfo_reqwidth()
        if h <= 2:
            h = self.h
        bg, fg = self._colors()
        c = self.theme.c
        outline = ""
        width = 0
        if self.kind == "outline":
            outline = c["border_hi"]
            width = 1
        round_rect(self, 1, 1, w - 1, h - 1, self.radius, fill=bg,
                   outline=outline, width=width)
        cy = h / 2
        if self._sub:
            self.create_text(w / 2, cy - 7, text=self._text, fill=fg,
                             font=self.theme.font(self.font_size, "bold"))
            self.create_text(w / 2, cy + 8, text=self._sub,
                             fill=fg if self.kind == "solid" else c["muted"],
                             font=self.theme.font(max(7, self.font_size - 2)))
        else:
            self.create_text(w / 2, cy, text=self._text, fill=fg,
                             font=self.theme.font(self.font_size, "bold"))

    # -- events ----------------------------------------------------------
    def _on_enter(self, _e):
        if self._state == "normal":
            self._hover = True
            self._draw()

    def _on_leave(self, _e):
        self._hover = self._pressed = False
        self._draw()

    def _on_press(self, _e):
        if self._state == "normal":
            self._pressed = True
            self._draw()

    def _on_release(self, _e):
        was = self._pressed
        self._pressed = False
        self._draw()
        if was and self._state == "normal" and self.command:
            self.command()


class Link(tk.Label):
    """Flat text that acts like a link."""

    def __init__(self, master, theme, text, command, color=None, bg=None,
                 size=10, weight="normal"):
        self.theme = theme
        self._color = color or theme.c["accent"]
        self._bg = bg or theme.c["bg"]
        super().__init__(master, text=text, fg=self._color, bg=self._bg,
                         font=theme.font(size, weight), cursor="hand2")
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", lambda e: self.configure(fg=theme.c["text"]))
        self.bind("<Leave>", lambda e: self.configure(fg=self._color))


class Badge(tk.Canvas):
    """Small rounded count/label chip."""

    def __init__(self, master, theme, text="", fg=None, bg=None, height=22,
                 pad=9, font_size=9, parent_bg=None):
        self.theme = theme
        self._text = text
        self.fg = fg or theme.c["muted"]
        self.bgc = bg or theme.c["surface_alt"]
        self.h = height
        self.pad = pad
        self.font_size = font_size
        super().__init__(master, bg=parent_bg or theme.c["bg"],
                         highlightthickness=0, bd=0, height=height, width=10)
        self.bind("<Configure>", lambda e: self._draw())
        self.set_text(text)

    def set_text(self, text):
        self._text = text
        f = self.theme.font(self.font_size, "bold")
        w = tkfont.Font(font=f).measure(str(text)) + 2 * self.pad
        self.configure(width=w)
        self._draw()

    def set_colors(self, fg, bg):
        self.fg, self.bgc = fg, bg
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width() or self.winfo_reqwidth()
        h = self.h
        round_rect(self, 0, 0, w, h, h / 2, fill=self.bgc, outline="")
        self.create_text(w / 2, h / 2, text=str(self._text), fill=self.fg,
                         font=self.theme.font(self.font_size, "bold"))


# ---------------------------------------------------------------- scrolling
class ScrollFrame(tk.Frame):
    """A vertically scrollable area; put your content in `.inner`."""

    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self._on_scroll)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.inner._is_scroll_content = True
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._resize)
        self.canvas.bind("<Configure>", self._width)
        self.canvas.bind("<Enter>", lambda e: self._bind_wheel(True))
        self.canvas.bind("<Leave>", lambda e: self._bind_wheel(False))

    def _on_scroll(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.vsb.pack_forget()
        else:
            if not self.vsb.winfo_ismapped():
                self.vsb.pack(side="right", fill="y")
        self.vsb.set(first, last)

    def _resize(self, _e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _width(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)

    def _bind_wheel(self, on):
        if on:
            self.canvas.bind_all("<MouseWheel>", self._wheel)
            self.canvas.bind_all("<Button-4>", self._wheel)
            self.canvas.bind_all("<Button-5>", self._wheel)
        else:
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.canvas.unbind_all(seq)

    def _wheel(self, e):
        if str(e.num) == "4":
            step = -1
        elif str(e.num) == "5":
            step = 1
        else:
            step = -1 if e.delta > 0 else 1
            if abs(e.delta) >= 120:
                step = -int(e.delta / 120)
        self.canvas.yview_scroll(step, "units")


# ---------------------------------------------------------------- misc
class Divider(tk.Frame):
    def __init__(self, master, color, pady=0):
        super().__init__(master, bg=color, height=1)
        self.pack_propagate(False)


class Toast(tk.Frame):
    """A short message that fades away on its own."""

    def __init__(self, master, theme):
        super().__init__(master)
        self.theme = theme
        self._job = None

    def show(self, message, kind="ok", ms=2200):
        c = self.theme.c
        colour = {"ok": c["green"], "warn": c["amber"], "err": c["red"],
                  "info": c["accent"]}.get(kind, c["green"])
        for w in self.winfo_children():
            w.destroy()
        f = tk.Frame(self.master, bg=colour)
        self._panel = f
        tk.Label(f, text=message, bg=colour, fg="#FFFFFF",
                 font=self.theme.font(10, "bold"), padx=16, pady=9).pack()
        f.place(relx=0.5, rely=1.0, anchor="s", y=-24)
        f.lift()
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(ms, self._hide)

    def _hide(self):
        try:
            self._panel.destroy()
        except Exception:
            pass
        self._job = None


def label(master, theme, text="", size=11, weight="normal", fg=None, bg=None,
          wrap=0, justify="left", anchor="w"):
    """Convenience label with theme defaults."""
    return tk.Label(master, text=text, font=theme.font(size, weight),
                    fg=fg or theme.c["text"], bg=bg or theme.c["bg"],
                    wraplength=wrap, justify=justify, anchor=anchor)


def set_dpi_awareness():
    """Crisp text on high-DPI Windows screens."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
