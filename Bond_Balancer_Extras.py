"""
bb_extras.py  -  extra screens for Bond Balancer

Keep this file in the SAME folder as bond_balancer.py.  It provides:
  * draw_gas_station()   - the gas-test apparatus in Fizz Factory (hydrogen splint test
                           now happens on a test tube kept well away from the flask)
  * open_analysis_lab()  - ion tests, flame tests and gas tests for your products
  * build_quiz_setup() / build_question_screen() - the restyled quiz screens
"""
import math
import random
import re
import time
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------- sound hook
_sound = lambda event: None


def set_sound(fn):
    """bond_balancer.py hands over its play_sound() function here."""
    global _sound
    _sound = fn


# ---------------------------------------------------------------- small helpers
_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def pretty_formula(text):
    return re.sub(r"(?<=[A-Za-z\)\]])\d+", lambda m: m.group(0).translate(_SUB), text)


def _mix(c1, c2, k):
    k = max(0.0, min(1.0, k))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _ease(u):
    u = _clamp(u)
    return u * u * (3 - 2 * u)


def _path_point(pts, u):
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    d = u * (sum(seg) or 1)
    for i, s in enumerate(seg):
        if d <= s or i == len(seg) - 1:
            f = min(1.0, d / s) if s else 1.0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f,
                    pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
        d -= s


def _shade(color, factor=0.9):
    rgb = [int(int(color[i:i + 2], 16) * factor) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(rgb)


def _fg_for(bg):
    r, g, b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#1d1030" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def add_hover(widget, base, hover):
    widget._base = base
    widget.config(bg=base)
    widget.bind("<Enter>", lambda e: widget.config(bg=hover) if str(widget.cget("state")) == "normal" else None)
    widget.bind("<Leave>", lambda e: widget.config(bg=widget._base))


def make_button(parent, text, command, bg, fg="white", font=("Segoe UI", 11, "bold"), **kw):
    b = tk.Button(parent, text=text, command=command, fg=fg, font=font,
                  activebackground=_shade(bg, 0.88), activeforeground=fg,
                  disabledforeground=_mix(bg, "#ffffff", 0.62),
                  relief="flat", bd=0, padx=14, pady=6, cursor="hand2", takefocus=0, **kw)
    add_hover(b, bg, _shade(bg, 0.92))
    return b


def fit_window(win, w, h, min_w=600, min_h=450):
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    w, h = min(w, sw - 40), min(h, sh - 100)
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 2 - 20)}")
    win.minsize(min(min_w, w), min(min_h, h))


def enable_fullscreen(win):
    win._fs = False

    def toggle(event=None):
        win._fs = not win._fs
        win.attributes("-fullscreen", win._fs)
        return "break"

    def leave(event=None):
        win._fs = False
        win.attributes("-fullscreen", False)
        return "break"

    win.bind("<F11>", toggle)
    win.bind("<Escape>", leave)


def _rich(parent, bg, fg, **kw):
    t = tk.Text(parent, font=("Segoe UI", 12), wrap="word", bg=bg, fg=fg, relief="flat",
                padx=18, pady=10, cursor="arrow", **kw)
    t.tag_config("title", font=("Georgia", 15, "bold"), foreground=fg, spacing3=2)
    t.tag_config("sub", font=("Segoe UI", 11, "italic"), foreground=fg, spacing3=6)
    t.tag_config("body", font=("Segoe UI", 12), foreground=fg, spacing1=3, spacing3=2, lmargin1=12, lmargin2=30)
    return t


def _chip(t, text, bg, fg="#ffffff"):
    tag = "chip_" + bg
    t.tag_config(tag, font=("Segoe UI", 10, "bold"), foreground=fg, background=bg)
    t.insert(tk.END, f" {text} ", tag)
    t.insert(tk.END, "\n")


def _bullet(t, text):
    t.insert(tk.END, "•  " + text + "\n", "body")


def _eq(t, text, bg="#dff5e6", fg="#0b4a24"):
    tag = "eq_" + bg
    t.tag_config(tag, font=("Segoe UI", 13, "bold"), foreground=fg, background=bg, lmargin1=12, lmargin2=12)
    t.insert(tk.END, f"  {text}  ", tag)
    t.insert(tk.END, "\n")


def _tube(c, x, top, bottom, r=30, liquid=None, level=None, outline="#6b93b3", width=3):
    """Round-bottomed test tube. Liquid is drawn from `level` down."""
    yb = bottom - r
    if liquid and level is not None:
        lv = min(level, yb)
        c.create_rectangle(x - r + 2, lv, x + r - 2, yb, fill=liquid, outline="")
        c.create_arc(x - r + 2, bottom - 2 * r + 2, x + r - 2, bottom - 2, start=180, extent=180,
                     style=tk.CHORD, fill=liquid, outline="")
        c.create_line(x - r + 2, lv, x + r - 2, lv, fill="#ffffff", width=2)
    c.create_line(x - r, top, x - r, yb, fill=outline, width=width)
    c.create_line(x + r, top, x + r, yb, fill=outline, width=width)
    c.create_arc(x - r, bottom - 2 * r, x + r, bottom, start=180, extent=180, style=tk.ARC,
                 outline=outline, width=width)
    c.create_line(x - r + 8, top + 14, x - r + 8, yb - 10, fill="#ffffff", width=3)
    c.create_line(x - r - 4, top, x - r, top, fill=outline, width=width)
    c.create_line(x + r, top, x + r + 4, top, fill=outline, width=width)


def _flame(c, x, y, h, wd, tick, outer, inner, flick=1.0):
    """A candle/splint style flame whose base is at (x, y)."""
    fl = 1 + 0.12 * math.sin(tick * 17) * flick
    hh = h * fl
    c.create_polygon(x - wd, y, x - wd * 1.05, y - hh * 0.35, x - wd * 0.4, y - hh * 0.75, x, y - hh,
                     x + wd * 0.4, y - hh * 0.75, x + wd * 1.05, y - hh * 0.35, x + wd, y,
                     fill=outer, outline="", smooth=True)
    c.create_polygon(x - wd * 0.5, y, x - wd * 0.5, y - hh * 0.3, x, y - hh * 0.62,
                     x + wd * 0.5, y - hh * 0.3, x + wd * 0.5, y, fill=inner, outline="", smooth=True)


def _burst(c, x, y, k, col="#fff176", edge="#ff7a00"):
    r_out = 12 + 42 * k
    pts = []
    for j in range(16):
        ang = math.pi * 2 * j / 16
        rr = r_out if j % 2 == 0 else r_out * 0.45
        pts += [x + rr * math.cos(ang), y + rr * math.sin(ang)]
    c.create_polygon(pts, fill=col, outline=edge, width=2)


# =================================================================================
#  1.  FIZZ FACTORY  -  gas test station
# =================================================================================
def draw_gas_station(app, c, rx, t, p, tick):
    """Limewater for CO2; for H2 the gas is collected, carried away from the flask,
    and tested with a lighted splint lowered from ABOVE the test tube."""
    gt = rx.get("gas_type")
    if not gt:
        return
    lab = app.lab
    act = _clamp(p * 4) * (1 - max(0.0, (p - 0.85) / 0.15))
    cx = 590                        # where the gas is collected
    tcx = 665                       # hydrogen test stand: far from the flask
    T_MOVE0, T_MOVE1, T_IN, T_POP = 6.1, 6.9, 6.9, 8.1

    def poly(pts):
        return [v for pt in pts for v in pt]

    def gas_tube(x, top, mouth_up, fill):
        c.create_rectangle(x - 30, top, x + 30, top + 82, fill="#f4fdff", outline="")
        if fill > 0:
            h = 78 * fill
            y0 = top + 82 - h - 2 if mouth_up else top + 2
            c.create_rectangle(x - 28, y0, x + 28, y0 + h, fill="#dbeafe", outline="")
            for i in range(int(12 * fill)):
                f1 = ((i * 37) % 100) / 100.0
                f2 = ((i * 53) % 100) / 100.0
                bx = x - 22 + f1 * 44 + 2 * math.sin(tick * 3 + i)
                by = y0 + 4 + f2 * max(4.0, h - 8)
                c.create_oval(bx - 2.5, by - 2.5, bx + 2.5, by + 2.5, fill="#bfdbfe", outline="#60a5fa")
        if mouth_up:
            c.create_line(x - 30, top, x - 30, top + 82, x + 30, top + 82, x + 30, top,
                          fill="#7aa7c0", width=3, joinstyle="round")
        else:
            c.create_line(x - 30, top + 82, x - 30, top, x + 30, top, x + 30, top + 82,
                          fill="#7aa7c0", width=3, joinstyle="round")

    # ---------------------------------------------------------------- carbon dioxide
    if gt == "co2":
        path = [(460, 116), (460, 28), (cx, 28), (cx, 272)]
        c.create_rectangle(cx - 30, 190, cx + 30, 300, fill="#f4fdff", outline="#7aa7c0", width=3)
        milk = _clamp((t - 4.2) / 4.0)
        lime = _mix("#d8f1ff", "#fbfbf4", milk)
        c.create_rectangle(cx - 28, 222, cx + 28, 298, fill=lime, outline="")
        c.create_line(cx - 28, 222, cx + 28, 222, fill="#ffffff", width=2)
        for i in range(int(24 * milk)):
            f1 = ((i * 41) % 100) / 100.0
            f2 = ((i * 67) % 100) / 100.0
            x, y = cx - 24 + f1 * 48, 228 + f2 * 66
            c.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, fill="#ffffff", outline="#cfcfc4")
        c.create_text(cx, 322, text="Limewater", font=("Segoe UI", 12, "bold"), fill="#ffffff")
        line = poly(path)
        c.create_line(*line, width=8, fill="#8fa9b8", joinstyle="round", capstyle="round")
        c.create_line(*line, width=4, fill="#e8f4fb", joinstyle="round", capstyle="round")
        if act > 0:
            for i in range(10):
                x, y = _path_point(path, (tick * 0.5 + i / 10.0) % 1.0)
                c.create_oval(x - 2.6, y - 2.6, x + 2.6, y + 2.6, fill="#ffffff", outline="#6b93b3")
            for i in range(int(6 * act)):
                ph = (tick * 1.3 + i / 6.0) % 1.0
                y = 272 - ph * 48
                x = cx + 7 * math.sin(tick * 4 + i * 2)
                r = 2.2 + (i % 2)
                c.create_oval(x - r, y - r, x + r, y + r, fill="#ffffff", outline="#6b93b3")
        if t > 7.0:
            c.create_text(cx, 172, text="Limewater turns milky: CO\u2082 \u2714",
                          font=("Segoe UI", 10, "bold"), fill="#7c2d12")
        return

    # ---------------------------------------------------------------- hydrogen
    moved = t >= T_MOVE0
    f = _clamp(p * 1.3)
    path = [(460, 116), (460, 28), (556, 28), (556, 286), (cx, 286)]
    if not moved:
        path.append((cx, 218))

    # stand for the test tube (right-hand side, away from the flask and its tubing)
    c.create_rectangle(632, 296, 698, 302, fill="#6b7280", outline="#374151")
    c.create_line(712, 298, 712, 196, width=5, fill="#8b95a1")
    c.create_line(712, 214, tcx + 30, 214, width=5, fill="#8b95a1")

    line = poly(path)
    c.create_line(*line, width=8, fill="#8fa9b8", joinstyle="round", capstyle="round")
    c.create_line(*line, width=4, fill="#e8f4fb", joinstyle="round", capstyle="round")
    if act > 0:
        for i in range(10):
            x, y = _path_point(path, (tick * 0.5 + i / 10.0) % 1.0)
            c.create_oval(x - 2.6, y - 2.6, x + 2.6, y + 2.6, fill="#ffffff", outline="#6b93b3")

    if t < T_MOVE0:                                   # collecting (mouth down, over the tube end)
        gas_tube(cx, 180, False, f)
        c.create_text(cx, 322, text="Collecting H\u2082", font=("Segoe UI", 12, "bold"), fill="#ffffff")
    else:
        u = _clamp((t - T_MOVE0) / (T_MOVE1 - T_MOVE0))
        x = cx + (tcx - cx) * _ease(u)
        top = 180 - 38 * math.sin(math.pi * u)         # lifted off, carried away, set in the clamp
        gas_tube(x, top, u > 0.5, f if t < T_POP else f * max(0.0, 1 - (t - T_POP) / 0.3))
        c.create_text(tcx, 322, text="Test tube of H\u2082", font=("Segoe UI", 12, "bold"), fill="#ffffff")
        if u < 1:
            c.create_text(560, 150, text="carried well away\nfrom the flask",
                          font=("Segoe UI", 9, "italic"), fill="#7a4e1d", justify="center")

    # lighted splint is lowered from ABOVE the tube mouth
    if t >= T_IN:
        u = _clamp((t - T_IN) / (T_POP - T_IN))
        e = _ease(u)
        tx = tcx + 44 - 40 * e
        ty = 56 + 114 * e                              # tip ends just above the open mouth (y = 180)
        c.create_line(tx, ty, tx + 46, ty - 62, width=5, fill="#c08a4b", capstyle="round")
        c.create_line(tx, ty, tx + 46, ty - 62, width=1, fill="#7a4e1d")
        if t < T_POP:
            _flame(c, tx, ty - 2, 26, 7, tick, "#ff8c00", "#ffe14d")
        else:
            c.create_oval(tx - 3, ty - 3, tx + 3, ty + 3, fill="#7f1d1d", outline="")
            for i in range(4):
                ph = ((t - T_POP) * 0.8 + i / 4.0) % 1.0
                c.create_oval(tx - 4 + 6 * math.sin(i * 2 + ph * 5), ty - 8 - ph * 30,
                              tx + 4 + 6 * math.sin(i * 2 + ph * 5), ty - ph * 30, outline="#9ca3af")
    if t >= T_POP:
        if not lab.get("popped"):
            lab["popped"] = True
            _sound("h2_pop")
        k = (t - T_POP) / 0.6
        if k < 1:
            _burst(c, tcx, 178, k)
        if t < T_POP + 1.0:
            c.create_text(tcx, 110, text="POP!", font=("Segoe UI", 20, "bold"), fill="#d90429")
        else:
            c.create_text(tcx - 40, 232, text="Squeaky pop:\nH\u2082 \u2714", anchor="e", justify="right",
                          font=("Segoe UI", 10, "bold"), fill="#be123c")


# =================================================================================
#  2.  ANALYSIS LAB  -  ion tests, flame tests, gas tests
# =================================================================================
# product solution -> (cation key, anion key)
SALT_IONS = {
    "NaCl": ("Na", "Cl"), "Na2SO4": ("Na", "SO4"), "ZnCl2": ("Zn", "Cl"), "MgCl2": ("Mg", "Cl"),
    "ZnSO4": ("Zn", "SO4"), "MgSO4": ("Mg", "SO4"), "CuCl2": ("Cu", "Cl"), "CuSO4": ("Cu", "SO4"),
    "CaCl2": ("Ca", "Cl"), "NaNO3": ("Na", "NO3"), "HNO3": ("H", "NO3"), "Ba(NO3)2": ("Ba", "NO3"),
    "HCl": ("H", "Cl"), "Zn(NO3)2": ("Zn", "NO3"), "Mg(NO3)2": ("Mg", "NO3"),
    "Na2ZnO2": ("Na", "ZnO2"), "CaSO4": ("Ca", "SO4"),
}
ANION_NAME = {"Cl": "Cl\u207b", "SO4": "SO\u2084\u00b2\u207b", "NO3": "NO\u2083\u207b", "ZnO2": "ZnO\u2082\u00b2\u207b"}
COLOURLESS = "#c4e9ff"      # drawn as a clear pale aqua so the liquid is easy to see


def _R(ppt=None, name="", obs="No precipitate forms.", excess=None, after=None, after_obs="",
       eq="", eq2="", says=""):
    return dict(ppt=ppt, name=name, obs=obs, excess=excess, after=after, after_obs=after_obs,
                eq=eq, eq2=eq2, says=says)


_NONE_NAOH = "No precipitate forms."
CATION = {
    "Cu": dict(ion="Cu\u00b2\u207a", sol="#6cc0ff",
               naoh=_R("#5fb4ff", "Cu(OH)\u2082", "Light blue precipitate forms.", "insoluble", None,
                       "The precipitate does NOT dissolve in excess NaOH.",
                       "Cu\u00b2\u207a + 2OH\u207b \u2192 Cu(OH)\u2082", "",
                       "Light blue precipitate, insoluble in excess: Cu\u00b2\u207a is present."),
               nh3=_R("#5fb4ff", "Cu(OH)\u2082", "Light blue precipitate forms.", "soluble", "#2456d6",
                      "The precipitate DISSOLVES in excess NH\u2083 to give a deep blue solution.",
                      "Cu\u00b2\u207a + 2OH\u207b \u2192 Cu(OH)\u2082",
                      "Cu(OH)\u2082 + 4NH\u2083 \u2192 [Cu(NH\u2083)\u2084]\u00b2\u207a + 2OH\u207b",
                      "Light blue precipitate, deep blue solution in excess: Cu\u00b2\u207a is present.")),
    "Zn": dict(ion="Zn\u00b2\u207a", sol=COLOURLESS,
               naoh=_R("#ffffff", "Zn(OH)\u2082", "White precipitate forms.", "soluble", COLOURLESS,
                       "The precipitate DISSOLVES in excess NaOH to give a colourless solution.",
                       "Zn\u00b2\u207a + 2OH\u207b \u2192 Zn(OH)\u2082",
                       "Zn(OH)\u2082 + 2OH\u207b \u2192 ZnO\u2082\u00b2\u207b + 2H\u2082O",
                       "White precipitate, soluble in excess NaOH: Zn\u00b2\u207a (or Al\u00b3\u207a)."),
               nh3=_R("#ffffff", "Zn(OH)\u2082", "White precipitate forms.", "soluble", COLOURLESS,
                      "The precipitate DISSOLVES in excess NH\u2083 to give a colourless solution.",
                      "Zn\u00b2\u207a + 2OH\u207b \u2192 Zn(OH)\u2082",
                      "Zn(OH)\u2082 + 4NH\u2083 \u2192 [Zn(NH\u2083)\u2084]\u00b2\u207a + 2OH\u207b",
                      "White precipitate, soluble in excess NH\u2083: Zn\u00b2\u207a is present (Al\u00b3\u207a would NOT dissolve).")),
    "Mg": dict(ion="Mg\u00b2\u207a", sol=COLOURLESS,
               naoh=_R("#ffffff", "Mg(OH)\u2082", "White precipitate forms.", "insoluble", None,
                       "The precipitate does NOT dissolve in excess NaOH.",
                       "Mg\u00b2\u207a + 2OH\u207b \u2192 Mg(OH)\u2082", "",
                       "White precipitate, insoluble in excess: Mg\u00b2\u207a or Ca\u00b2\u207a (NH\u2083 and a flame test tell them apart)."),
               nh3=_R("#ffffff", "Mg(OH)\u2082", "White precipitate forms.", "insoluble", None,
                      "The precipitate does NOT dissolve in excess NH\u2083.",
                      "Mg\u00b2\u207a + 2OH\u207b \u2192 Mg(OH)\u2082", "",
                      "White precipitate with NH\u2083 as well: Mg\u00b2\u207a is present (Ca\u00b2\u207a gives no precipitate).")),
    "Ca": dict(ion="Ca\u00b2\u207a", sol=COLOURLESS,
               naoh=_R("#ffffff", "Ca(OH)\u2082", "White precipitate forms (only slight if the solution is dilute).",
                       "insoluble", None, "The precipitate does NOT dissolve in excess NaOH.",
                       "Ca\u00b2\u207a + 2OH\u207b \u2192 Ca(OH)\u2082", "",
                       "White precipitate, insoluble in excess: Mg\u00b2\u207a or Ca\u00b2\u207a."),
               nh3=_R(None, "", "No precipitate (at most a very slight one).", None, None, "", "", "",
                      "No precipitate with NH\u2083 but a precipitate with NaOH: Ca\u00b2\u207a is present.")),
    "Na": dict(ion="Na\u207a", sol=COLOURLESS,
               naoh=_R(None, "", "No precipitate. (NaOH already contains Na\u207a, so it cannot identify sodium.)",
                       says="No precipitate: use a flame test to identify Na\u207a."),
               nh3=_R(None, "", "No precipitate forms.", says="No precipitate: use a flame test to identify Na\u207a.")),
    "Ba": dict(ion="Ba\u00b2\u207a", sol=COLOURLESS,
               naoh=_R(None, "", "No precipitate (or only a very faint one).", says="No precipitate: use a flame test (apple green)."),
               nh3=_R(None, "", "No precipitate forms.", says="No precipitate: use a flame test (apple green).")),
    "H": dict(ion="H\u207a", sol=COLOURLESS,
              naoh=_R(None, "", "No precipitate: the acid is simply neutralised.", eq="H\u207a + OH\u207b \u2192 H\u2082O",
                      says="No metal ion here: the solution is an acid."),
              nh3=_R(None, "", "No precipitate: the acid is simply neutralised.", eq="H\u207a + OH\u207b \u2192 H\u2082O",
                     says="No metal ion here: the solution is an acid.")),
}

ANION_TESTS = {
    "cl": dict(anion="Cl", first="HNO\u2083(aq)", second="AgNO\u2083(aq)", title="Chloride test",
               pos=_R("#ffffff", "AgCl", "White precipitate forms (silver chloride).", "soluble", COLOURLESS,
                      "The precipitate DISSOLVES in dilute ammonia.", "Ag\u207a + Cl\u207b \u2192 AgCl",
                      "AgCl + 2NH\u2083 \u2192 [Ag(NH\u2083)\u2082]\u207a + Cl\u207b",
                      "Chloride ions, Cl\u207b, are present."),
               neg=_R(None, "", "No precipitate forms.", says="No chloride ions present."),
               exc=("Add dilute NH\u2083", "NH\u2083(aq)")),
    "so4": dict(anion="SO4", first="HNO\u2083(aq)", second="Ba(NO\u2083)\u2082(aq)", title="Sulfate test",
                pos=_R("#ffffff", "BaSO\u2084", "White precipitate forms (barium sulfate).", "insoluble", None,
                       "The precipitate does NOT dissolve in excess acid.", "Ba\u00b2\u207a + SO\u2084\u00b2\u207b \u2192 BaSO\u2084", "",
                       "Sulfate ions, SO\u2084\u00b2\u207b, are present."),
                neg=_R(None, "", "No precipitate forms.", says="No sulfate ions present."),
                exc=("Add excess HNO\u2083", "HNO\u2083(aq)")),
}
NO3_EQ = "3NO\u2083\u207b + 8Al + 5OH\u207b + 18H\u2082O \u2192 3NH\u2083 + 8[Al(OH)\u2084]\u207b"

FLAME = {
    "Li\u207a": ("Crimson red", "#e11d48", "lithium"),
    "Na\u207a": ("Golden yellow", "#ffc400", "sodium"),
    "K\u207a": ("Lilac (pale purple)", "#c9a6ff", "potassium"),
    "Ca\u00b2\u207a": ("Brick red (orange-red)", "#ff5a1f", "calcium"),
    "Ba\u00b2\u207a": ("Apple green", "#9bd13d", "barium"),
    "Cu\u00b2\u207a": ("Blue-green", "#2ee6b0", "copper"),
}
CAT_FLAME = {"Na": "Na\u207a", "Ca": "Ca\u00b2\u207a", "Ba": "Ba\u00b2\u207a", "Cu": "Cu\u00b2\u207a"}

# key, name, test, positive result, equation, tint of the gas in the tube
GAS_TESTS = [
    ("h2", "Hydrogen, H\u2082", "Lighted splint at the mouth of the test tube",
     "The gas burns with a squeaky pop.", "2H\u2082 + O\u2082 \u2192 2H\u2082O", "#e3f0ff"),
    ("o2", "Oxygen, O\u2082", "Glowing splint inserted into the gas",
     "The glowing splint relights.", "", "#e8f4ff"),
    ("co2", "Carbon dioxide, CO\u2082", "Bubble the gas through limewater",
     "Limewater turns milky (cloudy white).", "CO\u2082 + Ca(OH)\u2082 \u2192 CaCO\u2083 + H\u2082O", "#eeeeee"),
    ("nh3", "Ammonia, NH\u2083", "Damp red litmus paper at the mouth of the tube",
     "Red litmus turns blue (ammonia is alkaline). It also has a pungent smell.",
     "NH\u2083 + H\u2082O \u21cc NH\u2084\u207a + OH\u207b", "#f2f0ff"),
    ("cl2", "Chlorine, Cl\u2082", "Damp blue litmus paper at the mouth of the tube",
     "Blue litmus turns red, then is bleached white. The gas is pale green.", "", "#d6f08a"),
    ("so2", "Sulfur dioxide, SO\u2082", "Filter paper dipped in acidified potassium dichromate(VI)",
     "The orange paper turns green. (Acidified KMnO\u2084 goes from purple to colourless.)", "", "#f4f4ea"),
    ("h2o", "Water", "Add water to anhydrous copper(II) sulfate",
     "White powder turns blue. (Cobalt chloride paper goes from blue to pink.)",
     "CuSO\u2084 + 5H\u2082O \u2192 CuSO\u2084\u00b75H\u2082O", "#ffffff"),
]
PRODUCT_GAS = {"h2": "h2", "co2": "co2"}


def open_analysis_lab(parent, rx, a, b):
    BG, INK = "#e6f7ff", "#0b3c5d"
    win = tk.Toplevel(parent)
    win.title("Analysis Lab \u2014 test your products")
    win.configure(bg=BG)
    fit_window(win, 1000, 900, 900, 600)
    enable_fullscreen(win)
    S = {"running": True, "job": None, "tick": 0.0}

    salt = rx.get("salt")
    ions = SALT_IONS.get(salt) if salt else None
    cat, an = ions if ions else (None, None)
    sample_col = CATION[cat]["sol"] if cat else COLOURLESS

    head = tk.Frame(win, bg="#0b5563")
    head.pack(fill="x")
    tk.Label(head, text="\U0001F52C  Analysis Lab \u2014 test your products", font=("Georgia", 19, "bold"),
             bg="#0b5563", fg="#ffffff", pady=8).pack()
    if ions:
        sub = (f"Sample: {pretty_formula(salt)}(aq)   \u00b7   made from {pretty_formula(a)} + {pretty_formula(b)}"
               f"   \u00b7   {rx.get('salt_word', '')}")
    else:
        sub = (f"{pretty_formula(a)} + {pretty_formula(b)} made solid products only, so there is no solution to "
               f"test. The gas tests are still available.")
    tk.Label(head, text=sub, font=("Segoe UI", 11), bg="#0b5563", fg="#bff3ff", pady=(0)).pack(pady=(0, 8))

    bottom = tk.Frame(win, bg=BG)
    bottom.pack(side="bottom", fill="x")
    close_btn = ttk.Button(bottom, text="Close")
    close_btn.pack(pady=(2, 8))

    nb = ttk.Notebook(win)
    nb.pack(fill="both", expand=True, padx=10, pady=(8, 2))

    def make_log(parent_frame):
        fr = tk.Frame(parent_frame, bg=BG)
        fr.pack(fill="both", expand=True, padx=14, pady=(4, 6))
        sb = ttk.Scrollbar(fr, orient="vertical")
        sb.pack(side="right", fill="y")
        t = _rich(fr, "#ffffff", INK, height=6, yscrollcommand=sb.set)
        t.pack(side="left", fill="both", expand=True)
        sb.config(command=t.yview)
        t.insert("1.0", "Results will appear here.\n", "sub")
        t.config(state="disabled")
        t._fresh = True
        return t

    def add_log(t, title, colour, lines=(), eqs=(), says=None, clear=False):
        t.config(state="normal")
        if clear or getattr(t, "_fresh", False):
            t.delete("1.0", tk.END)
            t._fresh = False
        _chip(t, title, colour)
        for ln in lines:
            _bullet(t, ln)
        for e in eqs:
            if e:
                _eq(t, e)
        if says:
            t.insert(tk.END, "\u2714 " + says + "\n\n", "body")
        else:
            t.insert(tk.END, "\n")
        t.config(state="disabled")
        t.see(tk.END)

    # ================================================================= TAB 1: ion tests
    tab1 = tk.Frame(nb, bg=BG)
    nb.add(tab1, text="\u2697 Ion tests")
    cv1 = tk.Canvas(tab1, width=900, height=290, bg="#f7fcff", highlightthickness=1,
                    highlightbackground="#9fc9dd")
    cv1.pack(pady=(8, 4))
    log1 = make_log(tab1)
    T1 = dict(liquid=sample_col, amt=0.0, ppt=None, ctx=None, act=None, buttons=[])
    REAG = {"naoh": "NaOH(aq)", "nh3": "NH\u2083(aq)"}
    EXC = {"naoh": ("Add excess NaOH", "NaOH(aq)"), "nh3": ("Add excess NH\u2083", "NH\u2083(aq)"),
           "cl": ANION_TESTS["cl"]["exc"], "so4": ANION_TESTS["so4"]["exc"]}

    def reset_sample():
        T1.update(liquid=sample_col, amt=0.0, ppt=None, ctx=None, act=None)
        set_excess()

    def set_excess():
        ctx = T1["ctx"]
        if ctx and ctx["d"]["excess"]:
            btn_exc.config(state="normal", text=EXC[ctx["kind"]][0])
        else:
            btn_exc.config(state="disabled", text="Add excess")

    def lock(on):
        for bt in T1["buttons"]:
            bt.config(state="disabled" if on else "normal")
        if not on:
            set_excess()

    def start1(kind):
        if T1["act"] or not ions:
            return
        d, ctx = None, None
        if kind in ("naoh", "nh3"):
            reset_sample()
            d = CATION[cat][kind]
            dur = 3.2
        elif kind == "excess":
            ctx = T1["ctx"]
            if not ctx:
                return
            d, kind_ctx = ctx["d"], ctx["kind"]
            dur = 3.6
        elif kind in ("cl", "so4"):
            reset_sample()
            tst = ANION_TESTS[kind]
            d = tst["pos"] if an == tst["anion"] else tst["neg"]
            dur = 3.6
        else:                                              # nitrate test
            reset_sample()
            d = dict(pos=(an == "NO3"))
            dur = 5.2
        _sound("click")
        T1["act"] = dict(kind=kind, t0=time.time(), dur=dur, d=d, ctx=ctx, liquid0=T1["liquid"])
        lock(True)

    def finish1():
        act = T1["act"]
        k, d = act["kind"], act["d"]
        T1["act"] = None
        if k in ("naoh", "nh3"):
            t_name = f"CATION TEST: {REAG[k]} dropwise"
            if d["ppt"]:
                T1.update(ppt=d["ppt"], amt=1.0, ctx=dict(kind=k, d=d))
            add_log(log1, t_name, "#1d4ed8", [d["obs"]], [d["eq"]], d["says"])
        elif k == "excess":
            kc, dd = act["ctx"]["kind"], act["ctx"]["d"]
            if dd["excess"] == "soluble":
                T1.update(amt=0.0, liquid=dd["after"] or COLOURLESS)
            T1["ctx"] = None
            add_log(log1, f"EXCESS: {EXC[kc][1]}", "#7c3aed", [dd["after_obs"]], [dd["eq2"]])
        elif k in ("cl", "so4"):
            tst = ANION_TESTS[k]
            if d["ppt"]:
                T1.update(ppt=d["ppt"], amt=1.0, ctx=dict(kind=k, d=d))
            add_log(log1, f"ANION TEST: {tst['title']} (add {tst['first']}, then {tst['second']})", "#be123c",
                    [d["obs"]], [d["eq"]], d["says"])
        else:
            if d["pos"]:
                add_log(log1, "ANION TEST: Nitrate test (NaOH(aq) + aluminium foil, warm)", "#be123c",
                        ["Bubbles of a pungent gas form on warming.",
                         "The gas turns damp RED litmus paper BLUE: it is ammonia."],
                        [NO3_EQ], "Nitrate ions, NO\u2083\u207b, are present.")
            else:
                add_log(log1, "ANION TEST: Nitrate test (NaOH(aq) + aluminium foil, warm)", "#be123c",
                        ["No ammonia given off; damp red litmus stays red."], [], "No nitrate ions present.")
        lock(False)

    ctrl = tk.Frame(tab1, bg=BG)
    ctrl.pack(pady=(0, 2))

    def lab_btn(txt, kind, col, row, colno, span=1):
        bt = make_button(ctrl, txt, lambda: start1(kind), col, font=("Segoe UI", 10, "bold"))
        bt.grid(row=row, column=colno, columnspan=span, padx=4, pady=3, sticky="ew")
        T1["buttons"].append(bt)
        return bt

    tk.Label(ctrl, text="Cation tests", font=("Segoe UI", 10, "bold"), bg=BG, fg=INK).grid(row=0, column=0, padx=6)
    lab_btn("NaOH(aq) dropwise", "naoh", "#1d4ed8", 0, 1)
    lab_btn("NH\u2083(aq) dropwise", "nh3", "#0e7490", 0, 2)
    btn_exc = lab_btn("Add excess", "excess", "#7c3aed", 0, 3)
    tk.Label(ctrl, text="Anion tests", font=("Segoe UI", 10, "bold"), bg=BG, fg=INK).grid(row=1, column=0, padx=6)
    lab_btn("Cl\u207b: HNO\u2083 + AgNO\u2083", "cl", "#be123c", 1, 1)
    lab_btn("SO\u2084\u00b2\u207b: HNO\u2083 + Ba(NO\u2083)\u2082", "so4", "#c2410c", 1, 2)
    lab_btn("NO\u2083\u207b: NaOH + Al, warm", "no3", "#a16207", 1, 3)
    make_button(ctrl, "\u21ba New sample", lambda: (reset_sample(), lock(False)) if not T1["act"] else None,
                "#475569", font=("Segoe UI", 10, "bold")).grid(row=0, column=4, rowspan=2, padx=8, sticky="ns")
    if not ions:
        for bt in T1["buttons"]:
            bt.config(state="disabled")
    btn_exc.config(state="disabled")

    BOTTLES = [("NaOH", "#bfdbfe"), ("NH\u2083", "#c7d2fe"), ("AgNO\u2083", "#e5e7eb"),
               ("Ba(NO\u2083)\u2082", "#e9d5ff"), ("HNO\u2083", "#fde68a")]

    def draw1(tick):
        c = cv1
        c.delete("all")
        c.create_rectangle(0, 262, 900, 290, fill="#a0642d", outline="")
        c.create_rectangle(0, 262, 900, 267, fill="#c58a4b", outline="")
        tx, LV = 300, 172
        act = T1["act"]
        t = (time.time() - act["t0"]) if act else 0.0
        liquid, amt, ppt = T1["liquid"], T1["amt"], T1["ppt"]
        label, drop_times, drop_col = None, [], "#dbeafe"
        heat, foil, litmus, bubbles = False, None, None, 0.0
        if not ions:
            c.create_text(450, 120, text="No solution to test: the products of this reaction are solids.",
                          font=("Georgia", 15, "italic"), fill=INK)
        if act:
            k, d = act["kind"], act["d"]
            if k in ("naoh", "nh3"):
                label = REAG[k]
                drop_times = [0.25 + i * 0.32 for i in range(7)]
                if d["ppt"]:
                    ppt, amt = d["ppt"], _clamp((t - 1.0) / 1.8)
            elif k == "excess":
                kc, dd = act["ctx"]["kind"], act["ctx"]["d"]
                label = EXC[kc][1]
                drop_times = [0.2 + i * 0.2 for i in range(13)]
                if dd["excess"] == "soluble":
                    q = _clamp((t - 0.8) / 2.2)
                    amt = 1 - q
                    liquid = _mix(act["liquid0"], dd["after"] or COLOURLESS, q)
            elif k in ("cl", "so4"):
                tst = ANION_TESTS[k]
                if t < 1.1:
                    label, drop_times = tst["first"], [0.15, 0.55]
                else:
                    label, drop_times = tst["second"], [1.2 + i * 0.3 for i in range(6)]
                    if d["ppt"]:
                        ppt, amt = d["ppt"], _clamp((t - 1.9) / 1.4)
            else:                                           # nitrate
                if t < 1.2:
                    label, drop_times = "NaOH(aq)", [0.15 + i * 0.28 for i in range(4)]
                if t >= 1.2:
                    foil = _clamp((t - 1.2) / 0.6)
                if t >= 2.0:
                    heat = True
                    bubbles = _clamp((t - 2.0) / 0.6)
                litmus = _mix("#d6334a", "#3a5bd9", _clamp((t - 3.2) / 1.4)) if d["pos"] else "#d6334a"
            if t >= act["dur"]:
                finish1()
        # reagent bottle + dropper
        if label:
            c.create_polygon(tx - 55, 18, tx + 55, 18, tx + 50, 62, tx - 50, 62, fill="#eaf4ff",
                             outline="#4b7a9b", width=2)
            c.create_rectangle(tx - 11, 62, tx + 11, 82, fill="#d1d5db", outline="#4b7a9b")
            c.create_polygon(tx - 6, 82, tx + 6, 82, tx, 104, fill="#d1d5db", outline="#4b7a9b")
            c.create_rectangle(tx - 44, 30, tx + 44, 52, fill="#ffffff", outline="#9ca3af")
            c.create_text(tx, 41, text=label, font=("Segoe UI", 10, "bold"), fill=INK)
        for st in drop_times:
            ph = (t - st) / 0.34
            if 0 <= ph < 1:
                y = 106 + ph * (LV - 106)
                c.create_oval(tx - 3, y - 4, tx + 3, y + 5, fill=drop_col, outline="#4b7a9b")
        # aluminium foil strip (nitrate test)
        if foil is not None:
            fy = 40 + _ease(foil) * 130
            c.create_polygon(tx - 8, fy, tx + 8, fy, tx + 10, fy + 28, tx - 10, fy + 28,
                             fill="#c7ccd1", outline="#7b848c")
        # the test tube and what is in it
        _tube(c, tx, 112, 250, 30, liquid=liquid, level=LV)
        if ppt and amt > 0:
            n = int(60 * amt)
            for i in range(n):
                f1 = ((i * 37) % 100) / 100.0
                f2 = ((i * 61) % 100) / 100.0
                settle = _clamp((amt - 0.5) * 2) if act is None else 0.0
                y0 = LV + 6 + f2 * (214 - LV - 6)
                y = y0 + (216 - (i % 4) * 3 - y0) * settle
                x = tx - 24 + f1 * 48 + 2 * math.sin(tick * 2 + i)
                c.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, fill=ppt, outline=_mix(ppt, "#000000", 0.35))
            bh = 12 * amt
            c.create_rectangle(tx - 26, 220 - bh, tx + 26, 222, fill=ppt, outline="")
        # heating, bubbles and litmus paper
        if heat:
            _flame(c, tx, 262, 34, 11, tick, "#4aa3ff", "#cfeaff")
            for i in range(int(8 * bubbles)):
                ph = (tick * 1.2 + i / 8.0) % 1.0
                bx = tx - 18 + ((i * 53) % 100) / 100.0 * 36
                by = 215 - ph * 70
                c.create_oval(bx - 2.5, by - 2.5, bx + 2.5, by + 2.5, fill="#ffffff", outline="#6b93b3")
        if litmus:
            c.create_polygon(tx + 4, 70, tx + 18, 70, tx + 22, 130, tx + 8, 130, fill=litmus, outline="#555555")
            c.create_text(tx + 60, 80, text="damp red litmus", font=("Segoe UI", 9, "italic"), fill=INK, anchor="w")
        # sample card and reagent shelf
        c.create_rectangle(560, 18, 880, 100, fill="#ffffff", outline="#9fc9dd", width=2)
        c.create_text(720, 36, text="SAMPLE", font=("Segoe UI", 9, "bold"), fill="#0e7490")
        c.create_text(720, 62, text=(pretty_formula(salt) + "(aq)") if salt else "(solids only)",
                      font=("Georgia", 20, "bold"), fill=INK)
        c.create_text(720, 86, text=rx.get("salt_word", "") if ions else "", font=("Segoe UI", 10, "italic"), fill="#555")
        for i, (nm, col) in enumerate(BOTTLES):
            bx = 585 + i * 58
            c.create_polygon(bx - 18, 214, bx + 18, 214, bx + 20, 262, bx - 20, 262, fill=col, outline="#4b7a9b", width=2)
            c.create_rectangle(bx - 7, 200, bx + 7, 214, fill="#d1d5db", outline="#4b7a9b")
            c.create_text(bx, 240, text=nm, font=("Segoe UI", 8, "bold"), fill=INK)
        c.create_text(450, 280, text=("Testing..." if act else "Each test uses a fresh portion of the sample."),
                      font=("Segoe UI", 10, "italic"), fill="#ffffff")

    # ================================================================= TAB 2: flame tests
    tab2 = tk.Frame(nb, bg=BG)
    nb.add(tab2, text="\U0001F525 Flame tests")
    cv2 = tk.Canvas(tab2, width=900, height=290, bg="#1a1d33", highlightthickness=1, highlightbackground="#9fc9dd")
    cv2.pack(pady=(8, 4))
    F = dict(act=None, buttons=[], last=("#4aa3ff", 0.0))
    log2 = make_log(tab2)

    def start2(ion_label, name, colour, salt_name):
        if F["act"]:
            return
        _sound("click")
        F["act"] = dict(t0=time.time(), dur=6.0, ion=ion_label, name=name, col=colour, salt=salt_name)
        for bt in F["buttons"]:
            bt.config(state="disabled")

    def finish2():
        a2 = F["act"]
        F["act"] = None
        for bt in F["buttons"]:
            bt.config(state="normal")
        if a2["col"]:
            add_log(log2, f"FLAME TEST: {a2['ion']} ({a2['salt']})", "#c2410c",
                    [f"The flame turns {a2['name'].lower()}."], [],
                    f"{a2['ion']} gives a {a2['name'].lower()} flame.")
        else:
            add_log(log2, f"FLAME TEST: {a2['ion']} ({a2['salt']})", "#c2410c",
                    ["No characteristic flame colour: the flame stays blue."], [],
                    "A flame test cannot identify this ion; use the precipitate tests instead.")
        _sound("success")

    row2 = tk.Frame(tab2, bg=BG)
    row2.pack(pady=(0, 2))
    items = list(FLAME.items())
    for i, (ion_label, (name, col, metal)) in enumerate(items):
        bt = make_button(row2, f"{ion_label}  {metal}", lambda il=ion_label, n=name, c_=col, m=metal:
                         start2(il, n, c_, m + " chloride"), col, fg=_fg_for(col), font=("Segoe UI", 10, "bold"))
        bt.grid(row=0, column=i, padx=4, pady=3)
        F["buttons"].append(bt)
    if ions:
        fl = CAT_FLAME.get(cat)
        nm, col = (FLAME[fl][0], FLAME[fl][1]) if fl else ("", None)
        txt = f"\u2605 Your product ({CATION[cat]['ion']})"
        bt = make_button(row2, txt, lambda: start2(CATION[cat]["ion"], nm, col, pretty_formula(salt)),
                         "#0b5563", font=("Segoe UI", 10, "bold"))
        bt.grid(row=0, column=len(items), padx=(14, 4), pady=3)
        F["buttons"].append(bt)

    def draw2(tick):
        c = cv2
        c.delete("all")
        c.create_rectangle(0, 250, 900, 290, fill="#6b4423", outline="")
        c.create_rectangle(0, 250, 900, 255, fill="#8a5a2d", outline="")
        a2 = F["act"]
        t = (time.time() - a2["t0"]) if a2 else 0.0
        target = a2["col"] if a2 and a2["col"] else None
        k_on = _clamp((t - 2.2) / 0.6) * (1 - _clamp((t - 4.8) / 0.8)) if a2 else 0.0
        fcol = _mix("#4aa3ff", target, k_on) if target else "#4aa3ff"
        # bunsen burner
        bx = 560
        c.create_rectangle(bx - 14, 150, bx + 14, 240, fill="#9aa3ad", outline="#4b5563", width=2)
        c.create_polygon(bx - 46, 252, bx + 46, 252, bx + 30, 238, bx - 30, 238, fill="#4b5563", outline="")
        c.create_rectangle(bx - 16, 196, bx + 16, 212, fill="#6b7280", outline="#374151")
        # flame (glow, outer, inner)
        h = 92 + 6 * math.sin(tick * 15)
        if target and k_on > 0:
            glow = _mix("#1a1d33", fcol, 0.35 * k_on)
            c.create_oval(bx - 70, 150 - h - 14, bx + 70, 160, fill=glow, outline="")
        c.create_polygon(bx - 20, 150, bx - 24, 150 - h * 0.45, bx - 8, 150 - h * 0.85, bx, 150 - h,
                         bx + 8, 150 - h * 0.85, bx + 24, 150 - h * 0.45, bx + 20, 150,
                         fill=fcol, outline="", smooth=True)
        c.create_polygon(bx - 9, 150, bx - 9, 150 - h * 0.28, bx, 150 - h * 0.55, bx + 9, 150 - h * 0.28, bx + 9, 150,
                         fill=_mix("#9bd3ff", "#ffffff", 0.5 * k_on), outline="", smooth=True)
        # watch glass with salt
        wx = 190
        c.create_arc(wx - 60, 214, wx + 60, 266, start=180, extent=180, style=tk.CHORD, fill="#dff1ff",
                     outline="#8fb4cc", width=2)
        pc = "#ffffff"
        if a2 and a2["col"]:
            pc = _mix("#ffffff", a2["col"], 0.35)
        c.create_polygon(wx - 26, 246, wx - 8, 232, wx + 10, 230, wx + 28, 246, fill=pc, outline="#cbd5e1", smooth=True)
        c.create_text(wx, 276, text="salt on a watch glass", font=("Segoe UI", 9, "italic"), fill="#ffffff")
        # wire
        rest = (360, 120)
        if a2:
            if t < 1.0:
                p_ = _ease(t / 1.0)
                pos = (rest[0] + (wx + 5 - rest[0]) * p_, rest[1] + (232 - rest[1]) * p_)
            elif t < 2.2:
                p_ = _ease((t - 1.0) / 1.2)
                pos = (wx + 5 + (bx - wx - 5) * p_, 232 + (112 - 232) * p_)
            elif t < 4.8:
                pos = (bx, 112)
            else:
                p_ = _ease((t - 4.8) / 1.2)
                pos = (bx + (rest[0] - bx) * p_, 112 + (rest[1] - 112) * p_)
        else:
            pos = rest
        c.create_line(pos[0] - 120, pos[1] - 110, pos[0], pos[1], width=3, fill="#aab1b8")
        c.create_line(pos[0] - 130, pos[1] - 123, pos[0] - 100, pos[1] - 90, width=9, fill="#8b5a2b", capstyle="round")
        c.create_oval(pos[0] - 6, pos[1] - 6, pos[0] + 6, pos[1] + 6, outline="#cbd5e1", width=3)
        # colour key
        c.create_text(740, 18, text="Flame colours", font=("Segoe UI", 11, "bold"), fill="#ffffff")
        for i, (il, (nm, col, metal)) in enumerate(FLAME.items()):
            y = 44 + i * 30
            c.create_oval(668, y - 8, 684, y + 8, fill=col, outline="#ffffff")
            c.create_text(694, y, text=f"{il}  {nm}", font=("Segoe UI", 9, "bold"), fill="#ffffff", anchor="w")
        if a2 and t >= a2["dur"]:
            finish2()
        if a2:
            c.create_text(450, 20, text=f"Testing {a2['ion']} ...", font=("Georgia", 14, "bold"), fill="#ffffff")
        else:
            c.create_text(450, 20, text="Pick an ion to see its flame colour", font=("Georgia", 14, "italic"), fill="#cbd5e1")

    # ================================================================= TAB 3: gas tests
    tab3 = tk.Frame(nb, bg=BG)
    nb.add(tab3, text="\U0001F4A8 Gas tests")
    cv3 = tk.Canvas(tab3, width=900, height=290, bg="#f7fcff", highlightthickness=1, highlightbackground="#9fc9dd")
    cv3.pack(pady=(8, 4))
    G = dict(act=None, buttons=[])
    log3 = make_log(tab3)
    DUR3 = 4.6
    mine = PRODUCT_GAS.get(rx.get("gas_type") or "", None)

    def start3(entry):
        if G["act"]:
            return
        _sound("click")
        G["act"] = dict(t0=time.time(), e=entry, popped=False)
        for bt in G["buttons"]:
            bt.config(state="disabled")

    def finish3():
        e = G["act"]["e"]
        G["act"] = None
        for bt in G["buttons"]:
            bt.config(state="normal")
        add_log(log3, f"GAS TEST: {e[1]}", "#0f766e", [f"Test: {e[2]}.", f"Positive result: {e[3]}"], [e[4]],
                None)
        _sound("success")

    row3 = tk.Frame(tab3, bg=BG)
    row3.pack(pady=(0, 2))
    for i, e in enumerate(GAS_TESTS):
        star = "\u2605 " if e[0] == mine else ""
        bt = make_button(row3, star + e[1].split(",")[0], lambda en=e: start3(en),
                         "#0f766e" if e[0] != mine else "#be123c", font=("Segoe UI", 10, "bold"))
        bt.grid(row=0, column=i, padx=4, pady=3)
        G["buttons"].append(bt)

    def draw3(tick):
        c = cv3
        c.delete("all")
        c.create_rectangle(0, 262, 900, 290, fill="#a0642d", outline="")
        c.create_rectangle(0, 262, 900, 267, fill="#c58a4b", outline="")
        a3 = G["act"]
        if not a3:
            c.create_text(450, 130, text="Choose a gas to see how it is tested", font=("Georgia", 16, "italic"), fill=INK)
            c.create_text(450, 160, text=("\u2605 = the gas your reaction made" if mine else ""),
                          font=("Segoe UI", 10, "italic"), fill="#be123c")
            return
        e = a3["e"]
        key = e[0]
        t = time.time() - a3["t0"]
        u = _clamp(t / DUR3)
        tx, top, bot = 450, 104, 252
        c.create_text(450, 16, text=f"{e[1]}:  {e[2]}", font=("Segoe UI", 11, "bold"), fill=INK)
        if key == "h2o":
            c.create_arc(tx - 90, 180, tx + 90, 250, start=180, extent=180, style=tk.CHORD, fill="#dff1ff",
                         outline="#8fb4cc", width=2)
            pc = _mix("#ffffff", "#2f7be8", _ease((u - 0.45) / 0.45))
            c.create_polygon(tx - 55, 218, tx - 25, 196, tx + 25, 196, tx + 55, 218, fill=pc,
                             outline="#9aa7b4", smooth=True)
            for i in range(3):
                ph = (t - (0.3 + i * 0.35)) / 0.4
                if 0 <= ph < 1:
                    y = 80 + ph * 112
                    c.create_oval(tx - 4, y - 5, tx + 4, y + 6, fill="#7cc4ff", outline="#2f7be8")
            c.create_text(tx + 100, 222, text="anhydrous\ncopper(II) sulfate", anchor="w", justify="left", font=("Segoe UI", 10, "italic"), fill=INK)
        else:
            tint = e[5]
            lime = None
            if key == "co2":
                lime = _mix("#d8f1ff", "#fbfbf4", _ease((u - 0.2) / 0.7))
                _tube(c, tx, top, bot, 30, liquid=lime, level=170)
                path = [(250, 250), (250, 70), (tx, 70), (tx, 215)]
                ln = [v for pt in path for v in pt]
                c.create_line(*ln, width=8, fill="#8fa9b8", joinstyle="round", capstyle="round")
                c.create_line(*ln, width=4, fill="#e8f4fb", joinstyle="round", capstyle="round")
                for i in range(7):
                    ph = (tick * 1.4 + i / 7.0) % 1.0
                    y = 215 - ph * 45
                    x = tx + 8 * math.sin(tick * 4 + i * 2)
                    c.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#ffffff", outline="#6b93b3")
                for i in range(int(40 * _ease((u - 0.2) / 0.7))):
                    f1 = ((i * 41) % 100) / 100.0
                    f2 = ((i * 67) % 100) / 100.0
                    x, y = tx - 24 + f1 * 48, 176 + f2 * 66
                    c.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, fill="#ffffff", outline="#cfcfc4")
                c.create_text(tx + 44, 232, text="limewater", anchor="w", font=("Segoe UI", 10, "italic"), fill=INK)
            else:
                c.create_rectangle(tx - 28, top + 2, tx + 28, bot - 30, fill=tint, outline="")
                c.create_arc(tx - 28, bot - 58, tx + 28, bot - 2, start=180, extent=180, style=tk.CHORD,
                             fill=tint, outline="")
                for i in range(7):
                    ph = (tick * 0.5 + i / 7.0) % 1.0
                    wx_ = tx - 18 + ((i * 53) % 100) / 100.0 * 36 + 4 * math.sin(tick * 3 + i)
                    wy = bot - 40 - ph * 120
                    if wy > top - 16:
                        c.create_oval(wx_ - 3, wy - 3, wx_ + 3, wy + 3, outline=_mix(tint, "#9ca3af", 0.5))
                strip = None
                if key in ("nh3", "cl2", "so2"):
                    if key == "nh3":
                        strip = _mix("#d6334a", "#3a5bd9", _ease((u - 0.35) / 0.4))
                    elif key == "cl2":
                        if u < 0.45:
                            strip = _mix("#4a6fe3", "#d6334a", _ease((u - 0.15) / 0.25))
                        else:
                            strip = _mix("#d6334a", "#f6f6f6", _ease((u - 0.5) / 0.35))
                    else:
                        strip = _mix("#f59e0b", "#4d9a3a", _ease((u - 0.3) / 0.5))
                    sy = 40 + 40 * _ease(u / 0.2)
                    c.create_polygon(tx - 9, sy, tx + 9, sy, tx + 9, sy + 78, tx - 9, sy + 78,
                                     fill=strip, outline="#555555")
                _tube(c, tx, top, bot, 30)
                if key in ("h2", "o2"):
                    ue = _ease(u / 0.55) if u < 0.55 else 1.0
                    glow = key == "o2"
                    deep = 70 if glow else 0
                    ty = 34 + (62 + deep) * ue
                    tpx = tx + 44 - 40 * ue
                    c.create_line(tpx, ty, tpx + 46, ty - 62, width=5, fill="#c08a4b", capstyle="round")
                    c.create_line(tpx, ty, tpx + 46, ty - 62, width=1, fill="#7a4e1d")
                    if key == "h2":
                        if u < 0.7:
                            _flame(c, tpx, ty - 2, 26, 7, tick, "#ff8c00", "#ffe14d")
                        else:
                            if not a3["popped"]:
                                a3["popped"] = True
                                _sound("h2_pop")
                            k = (u - 0.7) / 0.18
                            if k < 1:
                                _burst(c, tx, top + 2, k)
                            if u < 0.95:
                                c.create_text(tx, 70, text="POP!", font=("Segoe UI", 20, "bold"), fill="#d90429")
                    else:
                        if u < 0.5:
                            c.create_oval(tpx - 4, ty - 4, tpx + 4, ty + 4, fill="#ff9d3c", outline="#b45309")
                        else:
                            k = _ease((u - 0.5) / 0.15)
                            _flame(c, tpx, ty - 2, 14 + 30 * k, 6 + 8 * k, tick, "#ff8c00", "#fff3a0")
        if u > 0.92:
            c.create_text(450, 276, text="Result: " + e[3], font=("Segoe UI", 10, "bold"), fill="#ffffff")
        if t >= DUR3 + 0.4:
            finish3()

    draws = [draw1, draw2, draw3]

    def loop():
        if not S["running"]:
            return
        S["tick"] += 0.04
        try:
            draws[nb.index(nb.select())](S["tick"])
        except tk.TclError:
            return
        except Exception as ex:                        # one bad frame must not stop the lab
            print("analysis draw error:", ex)
        S["job"] = win.after(40, loop)

    def close():
        S["running"] = False
        if S["job"]:
            try:
                win.after_cancel(S["job"])
            except Exception:
                pass
        _sound("window_close")
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close)
    close_btn.config(command=close)
    set_excess()
    loop()
    return win


# =================================================================================
#  3.  QUIZ  -  restyled opening screen and question screen
# =================================================================================
QUIZ_UI = {
    "bg": "#fff6dc", "card": "#ffffff", "border": "#ffb703",
    "ink": "#1d1030", "muted": "#7a5c00", "chip": "#ffca3a",
    "option": "#fffaf0", "option_hover": "#ffe9a8", "option_sel": "#9be564",
    "primary": "#06d6a0", "accent": "#ff006e", "blue": "#3a86ff",
    "good": "#06d6a0", "good_bg": "#8ac926",
    "bad": "#ef233c", "bad_bg": "#ff8fa3", "warn": "#fb5607",
    "dot_idle": "#e8d48a",
    "hero": "#4422EE", "hero2": "#6d4bff", "shadow": "#e3bf5e", "trough": "#f1e3b0",
}
OPTION_STRIPS = ["#ff006e", "#3a86ff", "#06d6a0", "#fb5607"]
CHAPTER_STYLE = {
    "Mixed (All Chapters)": ("\U0001F308", "Mixed"),
    "Chemical Bonds & Reactions": ("\u2697\ufe0f", "Bonds & Reactions"),
    "Atomic Structure & Periodic Table": ("\u269b\ufe0f", "Atoms & Periodic Table"),
    "Moles & Stoichiometry": ("\u2696\ufe0f", "Moles"),
    "Electrolysis": ("\u26a1", "Electrolysis"),
    "Organic Chemistry": ("\u267b\ufe0f", "Organic"),
}


def _flask(c, cx, base_y, s, liquid):
    c.create_polygon(cx - 7 * s, base_y - 62 * s, cx + 7 * s, base_y - 62 * s, cx + 7 * s, base_y - 36 * s,
                     cx + 26 * s, base_y, cx - 26 * s, base_y, cx - 7 * s, base_y - 36 * s,
                     fill="#f5f3ff", outline="#2a1a7a", width=2)
    c.create_polygon(cx - 17 * s, base_y - 14 * s, cx + 17 * s, base_y - 14 * s, cx + 26 * s, base_y,
                     cx - 26 * s, base_y, fill=liquid, outline="")
    c.create_rectangle(cx - 9 * s, base_y - 68 * s, cx + 9 * s, base_y - 62 * s, fill="#2a1a7a", outline="")


try:
    from bb_questions import HARD_QUESTIONS
except Exception:                      # question bank missing: no question is "extreme"
    HARD_QUESTIONS = set()
HARD_TIME = 40.0                       # seconds for an extremely difficult question


def prepare_question(app, q):
    """Called for every question: shows the EXTREME badge and returns the time allowed (seconds)."""
    hard = q in HARD_QUESTIONS
    badge = getattr(app, "hard_badge", None)
    if badge is not None:
        try:
            if hard:
                badge.config(text=f"\U0001F525 EXTREME  \u00b7  {int(HARD_TIME)} s")
                badge.pack(side="left", padx=16)
            else:
                badge.pack_forget()
        except tk.TclError:
            pass
    return HARD_TIME if hard else app.time_total


def build_quiz_setup(app, pools):
    """Opening screen: animated banner, name box, chapter cards, rule tiles, big start button."""
    c = QUIZ_UI
    app._quiz_clear()
    app.quiz_win.unbind("<Key>")
    app.quiz_win.configure(bg=c["bg"])
    body = app.quiz_body
    body.configure(bg=c["bg"], padx=0, pady=0)

    # ---------------- animated banner
    hero = tk.Canvas(body, height=150, bg=c["hero"], highlightthickness=0)
    hero.pack(fill="x")
    rnd = random.Random(5)
    bubbles = [dict(x=rnd.random(), y=rnd.random() * 170, v=rnd.uniform(8, 22), r=rnd.randint(4, 11))
               for _ in range(16)]
    anim = {"tick": 0.0}

    def draw_hero():
        try:
            if not hero.winfo_exists():
                return
            anim["tick"] += 0.05
            tk_ = anim["tick"]
            hero.delete("all")
            W = max(hero.winfo_width(), 900)
            hero.create_polygon(0, 112, W * 0.28, 90, W * 0.6, 122, W, 96, W, 150, 0, 150,
                                fill=c["hero2"], outline="", smooth=True)
            for b in bubbles:
                y = (b["y"] - tk_ * b["v"]) % 170 - 10
                x = b["x"] * W + 8 * math.sin(tk_ * 1.3 + b["y"])
                hero.create_oval(x - b["r"], y - b["r"], x + b["r"], y + b["r"], outline="#a99bff", width=2)
            for x, s, liq in ((80, 1.0, "#ffca3a"), (170, 0.75, "#06d6a0"),
                              (W - 170, 0.75, "#ff006e"), (W - 80, 1.0, "#3a86ff")):
                _flask(hero, x, 138 + 3 * math.sin(tk_ + x), s, liq)
            hero.create_text(W / 2, 54, text="R E A C T I O N    Q U I Z", font=("Georgia", 32, "bold"), fill="#ffffff")
            hero.create_text(W / 2, 100, text="10 questions   \u00b7   beat the clock   \u00b7   earn speed bonuses",
                             font=("Segoe UI", 13), fill="#d9d2ff")
            hero.after(50, draw_hero)
        except tk.TclError:
            pass

    draw_hero()

    # ---------------- card with a soft shadow
    wrap = tk.Frame(body, bg=c["bg"])
    wrap.pack(pady=(16, 4))
    shadow = tk.Frame(wrap, bg=c["shadow"])
    shadow.pack()
    card = tk.Frame(shadow, bg=c["card"], highlightthickness=2, highlightbackground=c["border"], padx=30, pady=18)
    card.pack(padx=(0, 6), pady=(0, 6))

    tk.Label(card, text="YOUR NAME", font=("Segoe UI", 9, "bold"), bg=c["card"], fg=c["accent"]).pack(anchor="w")
    entry = tk.Entry(card, textvariable=app.player_name_var, font=("Segoe UI", 15), relief="flat",
                     bg="#fff8e1", fg=c["ink"], width=36, highlightthickness=2,
                     highlightbackground="#ffd166", highlightcolor=c["accent"], insertbackground=c["ink"])
    entry.pack(fill="x", ipady=7, pady=(3, 14))

    tk.Label(card, text="CHOOSE A CHAPTER", font=("Segoe UI", 9, "bold"), bg=c["card"], fg=c["accent"]).pack(anchor="w")
    grid = tk.Frame(card, bg=c["card"])
    grid.pack(pady=(4, 12))
    chips = {}

    def refresh_chips():
        for name, lbl in chips.items():
            on = app.topic_var.get() == name
            lbl.config(bg=c["chip"] if on else "#fffaf0",
                       highlightbackground=c["accent"] if on else "#eadca6")

    def pick(name):
        app.topic_var.set(name)
        refresh_chips()

    for i, name in enumerate(pools):
        icon, short = CHAPTER_STYLE.get(name, ("\U0001F4D8", name))
        lbl = tk.Label(grid, text=f"{icon}  {short}\n{len(pools[name])} questions", font=("Segoe UI", 11, "bold"),
                       fg=c["ink"], justify="center", width=22, pady=9, cursor="hand2", highlightthickness=3)
        lbl.grid(row=i // 3, column=i % 3, padx=5, pady=5)
        lbl.bind("<Button-1>", lambda e, n=name: pick(n))
        chips[name] = lbl
    refresh_chips()

    tiles = tk.Frame(card, bg=c["card"])
    tiles.pack(pady=(2, 8))
    for txt in (f"\u23f1  {int(app.time_total)} s per question ({int(HARD_TIME)} s if extreme)",
                f"\u26a1  +2 bonus within {int(app.bonus_threshold)} s",
                "\u2328  A\u2013D or 1\u20134, Enter"):
        tk.Label(tiles, text=txt, font=("Segoe UI", 10, "bold"), bg="#efeaff", fg=c["hero"],
                 padx=14, pady=6).pack(side="left", padx=5)

    app.quiz_msg = tk.Label(card, text="", font=("Segoe UI", 11, "bold"), bg=c["card"], fg=c["bad"])
    app.quiz_msg.pack()
    make_button(card, "\u25b6   START QUIZ", app.confirm_quiz_start, c["primary"],
                font=("Segoe UI", 16, "bold"), width=24).pack(pady=(4, 0), ipady=4)

    make_button(wrap, "\U0001F504  Reset Hall of Lab Legends",
                lambda: app.reset_leaderboard(parent=app.quiz_win), "#111111",
                font=("Segoe UI", 11, "bold")).pack(pady=(14, 6))

    entry.bind("<Return>", lambda e: app.confirm_quiz_start())
    entry.focus_set()
    entry.select_range(0, "end")


def build_question_screen(app):
    """Question screen: coloured header, progress dots, timer bar, question card, lettered answers."""
    c = QUIZ_UI
    body = app.quiz_body
    body.configure(bg=c["bg"], padx=0, pady=0)
    app.quiz_win.configure(bg=c["bg"])

    head = tk.Frame(body, bg=c["hero"], padx=24, pady=12)
    head.pack(fill="x")
    app.q_counter = tk.Label(head, text="", font=("Georgia", 18, "bold"), bg=c["hero"], fg="#ffffff")
    app.q_counter.pack(side="left")
    app.score_label = tk.Label(head, text="\u2b50 Score: 0", font=("Segoe UI", 14, "bold"),
                               bg=c["chip"], fg=c["ink"], padx=14, pady=4)
    app.score_label.pack(side="right")
    app.hard_badge = tk.Label(head, text="", font=("Segoe UI", 11, "bold"), bg="#ff6b35", fg="#ffffff",
                              padx=10, pady=3)

    main = tk.Frame(body, bg=c["bg"], padx=28, pady=6)
    main.pack(fill="both", expand=True)

    dots = tk.Frame(main, bg=c["bg"])
    dots.pack(pady=(4, 4))
    app.dot_labels = []
    for _ in app.quiz_questions:
        d = tk.Label(dots, text="\u25cf", font=("Segoe UI", 17), bg=c["bg"], fg=c["dot_idle"])
        d.pack(side="left", padx=3)
        app.dot_labels.append(d)

    pb = tk.Frame(main, bg=c["bg"])
    pb.pack(fill="x", pady=(0, 8))
    tk.Label(pb, text="\u23f1", font=("Segoe UI Emoji", 15), bg=c["bg"], fg=c["ink"]).pack(side="left")
    app.time_label = tk.Label(pb, text="", font=("Segoe UI", 16, "bold"), bg=c["bg"], fg=c["ink"], width=5)
    app.time_label.pack(side="left", padx=(4, 10))
    app.pb_canvas = tk.Canvas(pb, height=22, bg=c["trough"], highlightthickness=0)
    app.pb_canvas.pack(side="left", fill="x", expand=True)
    app.pb_bg = app.pb_canvas.create_rectangle(0, 0, 0, 22, fill=c["trough"], outline="")
    app.pb_fill = app.pb_canvas.create_rectangle(0, 0, 0, 22, fill="#00b050", outline="")

    qshadow = tk.Frame(main, bg=c["shadow"])
    qshadow.pack(fill="x", pady=(2, 10))
    qcard = tk.Frame(qshadow, bg=c["card"])
    qcard.pack(fill="x", padx=(0, 6), pady=(0, 6))
    tk.Frame(qcard, bg=c["accent"], width=9).pack(side="left", fill="y")
    inner = tk.Frame(qcard, bg=c["card"], padx=18, pady=12)
    inner.pack(side="left", fill="x", expand=True)
    app.q_label = tk.Label(inner, text="", font=("Segoe UI", 18, "bold"), bg=c["card"], fg=c["ink"],
                           wraplength=760, justify="center", anchor="center")
    app.q_label.pack(fill="x")
    inner.bind("<Configure>", lambda e: app.q_label.config(wraplength=max(200, e.width - 40)))

    opts = tk.Frame(main, bg=c["bg"])
    opts.pack(fill="x")
    app.option_buttons = []
    app.option_selected = None
    app.option_selected_idx = None
    for i in range(4):
        row = tk.Frame(opts, bg=c["bg"])
        row.pack(fill="x", pady=5)
        tk.Frame(row, bg=OPTION_STRIPS[i], width=10).pack(side="left", fill="y")
        btn = tk.Button(row, text="", font=("Segoe UI", 15), anchor="w", justify="left", relief="flat", bd=0,
                        highlightthickness=2, highlightbackground=c["border"], highlightcolor=c["primary"],
                        fg=c["ink"], disabledforeground=c["ink"], padx=18, pady=13, cursor="hand2",
                        takefocus=0, wraplength=760, command=lambda idx=i: app.select_option(idx))
        btn.pack(side="left", fill="x", expand=True)
        add_hover(btn, c["option"], c["option_hover"])
        app.option_buttons.append(btn)

    app.feedback_label = tk.Label(main, text="", font=("Segoe UI", 14, "bold"), bg=c["bg"], fg=c["ink"],
                                  wraplength=800)
    app.feedback_label.pack(pady=(20, 10))

    app.btn_row = tk.Frame(main, bg=c["bg"])
    app.btn_row.pack(pady=(4, 6))
    app.answer_btns = tk.Frame(app.btn_row, bg=c["bg"])
    make_button(app.answer_btns, "\u2714 Submit Answer", app.submit_answer, c["primary"],
                font=("Segoe UI", 13, "bold"), width=18).pack(side="left", padx=8)
    make_button(app.answer_btns, "\U0001F4A1 Reveal (no score)", app.reveal_answer, c["blue"],
                font=("Segoe UI", 13, "bold"), width=20).pack(side="left", padx=8)
    app.next_btn = make_button(app.btn_row, "Next \u279c", app._next_question, c["accent"],
                               font=("Segoe UI", 13, "bold"), width=18)

    app.quiz_win.bind("<Key>", app._quiz_key)
    app.quiz_win.focus_set()
    app.show_question()
