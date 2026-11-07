"""Statistics: how much is due, how much you did, and how well you remember."""
import tkinter as tk
from datetime import datetime

from base import Screen
from widgets import Panel, ScrollFrame, round_rect


def _mix(c1, c2, t):
    """Blend two #rrggbb colours."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


class BarChart(tk.Canvas):
    def __init__(self, master, theme, height=190):
        self.theme = theme
        super().__init__(master, bg=theme.c["surface"], highlightthickness=0,
                         bd=0, height=height)
        self.data = []
        self.bind("<Configure>", lambda e: self.draw())

    def set_data(self, data):
        self.data = list(data)
        self.draw()

    def draw(self):
        self.delete("all")
        c = self.theme.c
        w, h = self.winfo_width(), self.winfo_height()
        if w < 40 or h < 40 or not self.data:
            return
        pad_l, pad_r, pad_t, pad_b = 36, 10, 12, 26
        pw, ph = w - pad_l - pad_r, h - pad_t - pad_b
        top = max(self.data + [1])
        for i in range(4):
            y = pad_t + ph * i / 3
            self.create_line(pad_l, y, w - pad_r, y, fill=c["border"])
            self.create_text(pad_l - 8, y, anchor="e", fill=c["faint"],
                             font=self.theme.f_tiny(), text=str(int(round(top * (1 - i / 3)))))
        n = len(self.data)
        bw = pw / n
        for i, v in enumerate(self.data):
            x0 = pad_l + i * bw
            bh = ph * (v / top) if top else 0
            fill = c["accent"] if v else c["border"]
            if i == 0:
                fill = c["accent_hi"] if v else c["border"]
            if bh < 2 and v:
                bh = 2
            if bh:
                round_rect(self, x0 + bw * 0.16, pad_t + ph - bh,
                           x0 + bw * 0.84, pad_t + ph, min(4, bw * 0.34), fill=fill,
                           outline="")
        self.create_line(pad_l, pad_t + ph, w - pad_r, pad_t + ph, fill=c["border_hi"])
        for i in range(0, n, 5 if n > 14 else 1):
            label = "today" if i == 0 else f"+{i}d"
            x = pad_l + i * bw + bw / 2
            self.create_text(x, h - 12, text=label, fill=c["faint"],
                             font=self.theme.f_tiny())
        self.create_text(pad_l + n * bw / 2, pad_t - 2, text="cards due per day",
                         fill=c["faint"], font=self.theme.f_tiny(), anchor="n")


class Heatmap(tk.Canvas):
    def __init__(self, master, theme, height=190):
        self.theme = theme
        super().__init__(master, bg=theme.c["surface"], highlightthickness=0,
                         bd=0, height=height)
        self.grid = []
        self.start = None
        self.bind("<Configure>", lambda e: self.draw())

    def set_data(self, grid, start):
        self.grid, self.start = grid, start
        self.draw()

    def draw(self):
        self.delete("all")
        c = self.theme.c
        if not self.grid:
            return
        weeks = len(self.grid)
        cell, gap, left, top = 13, 3, 26, 20
        for w in range(weeks):
            for d in range(7):
                v = self.grid[w][d]
                x = left + w * (cell + gap)
                y = top + d * (cell + gap)
                if v is None:
                    colour = c["surface"]
                elif v == 0:
                    colour = c["border"]
                else:
                    lvl = min(1.0, 0.25 + v / 18.0)
                    colour = _mix(c["accent_soft"], c["accent"], lvl)
                round_rect(self, x, y, x + cell, y + cell, 3, fill=colour, outline="")
        for d, name in ((0, "Mon"), (2, "Wed"), (4, "Fri"), (6, "Sun")):
            y = top + d * (cell + gap) + cell / 2
            self.create_text(left - 8, y, text=name, anchor="e", fill=c["faint"],
                             font=self.theme.f_tiny())
        last_month = None
        for w in range(weeks):
            day = self.start.toordinal() + w * 7
            month = datetime.fromordinal(day).strftime("%b")
            if month != last_month:
                x = left + w * (cell + gap)
                self.create_text(x, top - 10, text=month, anchor="w", fill=c["faint"],
                                 font=self.theme.f_tiny())
                last_month = month


class KpiTile(Panel):
    def __init__(self, master, theme, label, value, hint="", accent=None):
        c = theme.c
        super().__init__(master, theme, pad=14, radius=14)
        self.body.grid_columnconfigure(0, weight=1)
        tk.Label(self.body, text=label.upper(), bg=c["surface"], fg=c["faint"],
                 font=theme.f_tiny(), anchor="w").pack(anchor="w")
        tk.Label(self.body, text=value, bg=c["surface"],
                 fg=accent or c["text"], font=theme.font(20, "bold"),
                 anchor="w").pack(anchor="w", pady=(2, 0))
        if hint:
            tk.Label(self.body, text=hint, bg=c["surface"], fg=c["faint"],
                     font=theme.f_tiny(), anchor="w").pack(anchor="w")


class StatsScreen(Screen):
    title = "Stats"
    subtitle = "The only number that really matters is your retention on delayed tests."

    def __init__(self, master, app):
        super().__init__(master, app)
        c = self.theme.c
        self.scroll = ScrollFrame(self.body, c["bg"])
        self.scroll.pack(fill="both", expand=True)
        self.holder = self.scroll.inner

    def refresh(self):
        for w in self.holder.winfo_children():
            w.destroy()
        c = self.theme.c
        counts = self.db.counts()
        reviews, seconds = self.db.reviews_today()
        ret = self.db.retention(30)
        ret_mature = self.db.retention(30, mature_only=True)
        states = self.db.state_counts()
        total = self.db.total_cards()
        mature = self.db.mature_cards()
        streak = self.db.streak_days()

        tiles = tk.Frame(self.holder, bg=c["bg"])
        tiles.pack(fill="x")
        specs = [
            ("Due now", str(counts["due"] + counts["learning"]), "cards waiting", c["accent"]),
            ("Reviews today", str(reviews), "answers given", None),
            ("Time today", f"{int(seconds // 60)}m", f"{int(seconds % 60)}s", None),
            ("Retention 30d", f"{ret * 100:.0f}%" if ret is not None else "—",
             f"mature: {ret_mature * 100:.0f}%" if ret_mature is not None else "no data yet",
             c["green"] if (ret or 0) >= 0.85 else c["amber"]),
            ("Cards", str(total), f"{mature} mature", None),
            ("Streak", f"{streak}d", "days in a row", None),
        ]
        for i, (label, value, hint, accent) in enumerate(specs):
            col, row = i % 3, i // 3
            tiles.grid_columnconfigure(col, weight=1, uniform="kpi")
            tile = KpiTile(tiles, self.theme, label, value, hint, accent)
            tile.grid(row=row, column=col, sticky="ew",
                      padx=(0 if col == 0 else 8, 0), pady=(0 if row == 0 else 8, 0))

        charts = tk.Frame(self.holder, bg=c["bg"])
        charts.pack(fill="x", pady=(16, 0))
        charts.grid_columnconfigure(0, weight=3)
        charts.grid_columnconfigure(1, weight=2)

        p1 = Panel(charts, self.theme, pad=16, radius=16, height=250)
        p1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(p1.body, text="Next 30 days", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(11, "bold")).pack(anchor="w")
        self.bars = BarChart(p1.body, self.theme, height=186)
        self.bars.pack(fill="both", expand=True, pady=(6, 0))

        p2 = Panel(charts, self.theme, pad=16, radius=16, height=250)
        p2.grid(row=0, column=1, sticky="nsew")
        tk.Label(p2.body, text="Reviews per day", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(11, "bold")).pack(anchor="w")
        self.heat = Heatmap(p2.body, self.theme, height=186)
        self.heat.pack(fill="both", expand=True, pady=(6, 0))

        bottom = tk.Frame(self.holder, bg=c["bg"])
        bottom.pack(fill="x", pady=(16, 8))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        p3 = Panel(bottom, self.theme, pad=16, radius=16, fill=c["surface"])
        p3.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(p3.body, text="Card states", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(11, "bold")).pack(anchor="w", pady=(0, 10))
        order = [("new", "New", "accent"), ("learning", "Learning", "amber"),
                 ("relearning", "Relearning", "amber"), ("review", "Review", "green")]
        mx = max(list(states.values()) + [1])
        for key, label, colour in order:
            n = states.get(key, 0)
            row = tk.Frame(p3.body, bg=c["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, width=12, anchor="w", bg=c["surface"],
                     fg=c["muted"], font=self.theme.f_small()).pack(side="left")
            track = tk.Frame(row, bg=c["surface_alt"], height=10)
            track.pack(side="left", fill="x", expand=True, padx=(0, 10))
            track.pack_propagate(False)
            fill = tk.Frame(track, bg=c[colour], height=10,
                            width=max(2, int(220 * n / mx)))
            fill.pack(side="left", fill="y")
            tk.Label(row, text=str(n), width=5, anchor="e", bg=c["surface"],
                     fg=c["text"], font=self.theme.f_small_b()).pack(side="right")

        p4 = Panel(bottom, self.theme, pad=16, radius=16, fill=c["surface"])
        p4.grid(row=0, column=1, sticky="nsew")
        tk.Label(p4.body, text="Decks", bg=c["surface"], fg=c["text"],
                 font=self.theme.font(11, "bold")).pack(anchor="w", pady=(0, 10))
        for d in self.db.decks():
            n = self.db.total_cards(d["id"])
            due = self.db.counts(d["id"])["due"]
            row = tk.Frame(p4.body, bg=c["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{n} cards · {due} due", anchor="e", bg=c["surface"],
                     fg=c["muted"], font=self.theme.f_small()).pack(side="right")
            name = d["name"] if len(d["name"]) <= 26 else d["name"][:25] + "…"
            tk.Label(row, text=name, anchor="w", bg=c["surface"], fg=c["text"],
                     font=self.theme.f_small_b()).pack(side="left", fill="x", expand=True)

        self.bars.set_data(self.db.forecast(30))
        grid, start = self.db.heatmap()
        self.heat.set_data(grid, start)
