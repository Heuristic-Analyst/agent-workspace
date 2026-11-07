"""Colours, fonts and ttk styles.

One place decides how the whole app looks.  Both palettes define exactly the same
keys, so every screen is written once and works in light and dark mode.
"""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

# Fonts are picked from what the machine actually has.  The first match wins, so
# the app looks native-ish on macOS, Windows and Linux without shipping a font.
SANS_CANDIDATES = [
    "SF Pro Text", "Segoe UI Variable Text", "Segoe UI", "Helvetica Neue",
    "Inter", "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans",
    "Nimbus Sans", "Arial", "TkDefaultFont",
]
MONO_CANDIDATES = [
    "SF Mono", "Cascadia Mono", "Consolas", "Menlo", "Ubuntu Mono",
    "DejaVu Sans Mono", "Liberation Mono", "Courier New", "TkFixedFont",
]

PALETTES = {
    "light": {
        "bg":          "#F4F6F9",   # app background
        "surface":     "#FFFFFF",   # cards, panels
        "surface_alt": "#FAFBFC",   # zebra rows, inputs
        "sidebar":     "#151A27",
        "sidebar_hi":  "#232B3D",
        "sidebar_tx":  "#AEB5C6",
        "sidebar_tx_hi": "#FFFFFF",
        "text":        "#12161F",
        "muted":       "#5C6472",
        "faint":       "#68707F",
        "border":      "#E3E7ED",
        "border_hi":   "#CFD5DE",
        "accent":      "#4F46E5",
        "accent_hi":   "#4338CA",
        "accent_tx":   "#FFFFFF",
        "accent_soft": "#EEEFFE",
        "green":       "#15803D",
        "green_hi":    "#166534",
        "green_soft":  "#E9F9EF",
        "amber":       "#B45309",
        "amber_hi":    "#92400E",
        "amber_soft":  "#FEF6E7",
        "red":         "#B91C1C",
        "red_hi":      "#991B1B",
        "red_soft":    "#FEECEC",
        "blue":        "#1D4ED8",
        "shadow":      "#E7EAF0",
    },
    "dark": {
        "bg":          "#0F1218",
        "surface":     "#171C26",
        "surface_alt": "#1C222E",
        "sidebar":     "#0A0D13",
        "sidebar_hi":  "#1B2433",
        "sidebar_tx":  "#98A2B6",
        "sidebar_tx_hi": "#FFFFFF",
        "text":        "#E9ECF2",
        "muted":       "#9AA3B2",
        "faint":       "#8A93A3",
        "border":      "#262E3C",
        "border_hi":   "#334054",
        "accent":      "#7C7BF7",
        "accent_hi":   "#908FFA",
        "accent_tx":   "#0F1218",
        "accent_soft": "#232544",
        "green":       "#4ADE80",
        "green_hi":    "#6EE79A",
        "green_soft":  "#16301F",
        "amber":       "#FBBF24",
        "amber_hi":    "#FCD34D",
        "amber_soft":  "#302612",
        "red":         "#F87171",
        "red_hi":      "#FCA5A5",
        "red_soft":    "#331A1C",
        "blue":        "#60A5FA",
        "shadow":      "#0B0E14",
    },
}


class Theme:
    """Holds the active colour set and the resolved font families."""

    def __init__(self, name="light"):
        self.name = name
        self.family = "TkDefaultFont"
        self.mono_family = "TkFixedFont"

    # -- lifecycle -------------------------------------------------------
    def resolve_fonts(self, root):
        families = set(tkfont.families(root))
        self.family = next((f for f in SANS_CANDIDATES if f in families), "TkDefaultFont")
        self.mono_family = next((f for f in MONO_CANDIDATES if f in families), "TkFixedFont")

    @property
    def c(self):
        return PALETTES[self.name]

    def toggle(self):
        self.name = "dark" if self.name == "light" else "light"

    # -- fonts -----------------------------------------------------------
    def font(self, size=11, weight="normal", slant="roman", mono=False):
        style = ""
        if weight != "normal":
            style += weight
        if slant != "roman":
            style += " italic"
        fam = self.mono_family if mono else self.family
        return (fam, size, style.strip()) if style.strip() else (fam, size)

    # display sizes
    def f_display(self):  return self.font(26, "bold")
    def f_h1(self):       return self.font(19, "bold")
    def f_h2(self):       return self.font(14, "bold")
    def f_body(self):     return self.font(11)
    def f_body_b(self):   return self.font(11, "bold")
    def f_small(self):    return self.font(9)
    def f_small_b(self):  return self.font(9, "bold")
    def f_tiny(self):     return self.font(8)
    def f_mono(self):     return self.font(10, mono=True)

    # -- ttk styling -----------------------------------------------------
    def apply(self, root):
        c = self.c
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        root.configure(bg=c["bg"])
        root.option_add("*Font", self.f_body())
        root.option_add("*TCombobox*Listbox.font", self.f_body())
        root.option_add("*TCombobox*Listbox.background", c["surface"])
        root.option_add("*TCombobox*Listbox.foreground", c["text"])
        root.option_add("*TCombobox*Listbox.selectBackground", c["accent"])
        root.option_add("*TCombobox*Listbox.selectForeground", c["accent_tx"])

        style.configure(".", background=c["bg"], foreground=c["text"],
                        fieldbackground=c["surface"], font=self.f_body(),
                        borderwidth=0, focuscolor=c["accent"])
        style.configure("TFrame", background=c["bg"])
        style.configure("Surface.TFrame", background=c["surface"])
        style.configure("TLabel", background=c["bg"], foreground=c["text"])
        style.configure("Surface.TLabel", background=c["surface"], foreground=c["text"])
        style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"])
        style.configure("SurfaceMuted.TLabel", background=c["surface"], foreground=c["muted"])

        # Entry
        style.configure("TEntry", fieldbackground=c["surface"], foreground=c["text"],
                        insertcolor=c["text"], bordercolor=c["border"],
                        lightcolor=c["border"], darkcolor=c["border"],
                        padding=6, relief="flat")
        style.map("TEntry",
                  bordercolor=[("focus", c["accent"])],
                  lightcolor=[("focus", c["accent"])],
                  darkcolor=[("focus", c["accent"])])

        # Combobox
        style.configure("TCombobox", fieldbackground=c["surface"], background=c["surface"],
                        foreground=c["text"], arrowcolor=c["muted"],
                        bordercolor=c["border"], lightcolor=c["surface"],
                        darkcolor=c["surface"], padding=5, relief="flat")
        style.map("TCombobox",
                  fieldbackground=[("readonly", c["surface"])],
                  foreground=[("readonly", c["text"])],
                  bordercolor=[("focus", c["accent"])],
                  arrowcolor=[("hover", c["text"])])

        # Notebook (used by settings tabs)
        style.configure("TNotebook", background=c["bg"], borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background=c["bg"], foreground=c["muted"],
                        padding=(14, 8), borderwidth=0, font=self.f_body_b())
        style.map("TNotebook.Tab",
                  background=[("selected", c["surface"])],
                  foreground=[("selected", c["text"])],
                  expand=[("selected", (0, 0, 0, 0))])

        # Treeview
        style.configure("Treeview", background=c["surface"], fieldbackground=c["surface"],
                        foreground=c["text"], rowheight=34, borderwidth=0,
                        font=self.f_body())
        style.configure("Treeview.Heading", background=c["surface_alt"], foreground=c["muted"],
                        relief="flat", borderwidth=0, font=self.f_small_b(), padding=(8, 9))
        style.map("Treeview.Heading", background=[("active", c["surface_alt"])])
        style.map("Treeview",
                  background=[("selected", c["accent"])],
                  foreground=[("selected", c["accent_tx"])])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        # Scrollbar - thin, unobtrusive
        style.configure("Vertical.TScrollbar", background=c["border"], troughcolor=c["bg"],
                        bordercolor=c["bg"], arrowcolor=c["muted"], relief="flat",
                        arrowsize=0, width=10)
        style.map("Vertical.TScrollbar", background=[("active", c["border_hi"])])
        style.configure("Horizontal.TScrollbar", background=c["border"], troughcolor=c["bg"],
                        bordercolor=c["bg"], arrowcolor=c["muted"], relief="flat", width=10)

        # Separator
        style.configure("TSeparator", background=c["border"])

        # Checkbutton / Radiobutton
        style.configure("TCheckbutton", background=c["bg"], foreground=c["text"],
                        focuscolor=c["bg"], font=self.f_body())
        style.map("TCheckbutton", background=[("active", c["bg"])],
                  indicatorcolor=[("selected", c["accent"]), ("!selected", c["surface"])])
        style.configure("Surface.TCheckbutton", background=c["surface"], foreground=c["text"])
        style.map("Surface.TCheckbutton", background=[("active", c["surface"])])

        # Scale (retention slider)
        style.configure("TScale", background=c["bg"], troughcolor=c["border"],
                        bordercolor=c["border"], lightcolor=c["accent"],
                        darkcolor=c["accent"], gripcount=0)
