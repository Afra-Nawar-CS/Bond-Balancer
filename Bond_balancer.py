"""
Bond Balancer — Full Polished App
Features:
 - MCQ Quiz (30-question pool, 10 questions per play; 20s/question)
 - Bonus +2 if answered within first 15s (special sound)
 - "Reveal Answer" ignores that question's scoring
 - Color-changing progress bar (green -> yellow -> orange -> red)
 - Step-by-step equation solver (20 options) with stars and spaced letters
 - Interactive gas reaction simulator with stoichiometric result
 - Leaderboard persisted to leaderboard.json (displayed below main menu)
 - Sounds via pygame (optional; app works without it)
 - Centered layout, playful fonts and emoji, robust error handling

"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import random
import math
import json
import os
import time
from datetime import datetime
from fractions import Fraction
import re
import sys
import sys
import threading

try:
    import winsound
    WINSOUND_AVAILABLE = True
except Exception:
    WINSOUND_AVAILABLE = False

def _run_beep_sequence(seq):
    if not WINSOUND_AVAILABLE:
        return
    try:
        for freq, dur in seq:
            winsound.Beep(int(freq), int(dur))
    except Exception:
        return

def play_sound(event):
    SOUNDS_ENABLED = True
    try:
        if event == "click":
            seq = [(900, 80)]
        elif event == "start":
            seq = [(1000, 120), (1300, 100)]
        elif event == "correct":
            seq = [(1100, 100), (1500, 120)]
        elif event == "bonus":
            seq = [(1400, 120), (1800, 150), (2100, 180)]
        elif event == "wrong":
            seq = [(400, 250)]
        elif event == "time_up":
            seq = [(600, 150), (400, 200)]
        elif event == "end":
            seq = [(900, 120), (1200, 180), (800, 160)]
        elif event == "success":
            seq = [(1000, 150), (1400, 200)]
        elif event == "reaction":
            seq = [(700, 100), (950, 120), (1200, 100)]
        elif event == "pop":
            seq = [(1500, 80), (900, 60)]
        elif event == "solver_select":
            seq = [(740, 55), (988, 70)]
        elif event == "solver_random":
            seq = [(600, 40), (800, 40), (1000, 40), (1200, 80)]
        elif event == "atomole_calc_change":
            seq = [(880, 50), (660, 50)]
        elif event == "atomole_calculate":
            seq = [(1200, 60), (1500, 60), (1800, 100)]
        elif event == "atomole_clear":
            seq = [(500, 60), (400, 60)]
        elif event == "electro_rules_view":
            seq = [(1500, 40), (1200, 40), (900, 80)]
        elif event == "electro_apps_view":
            seq = [(900, 40), (1200, 40), (1500, 80)]
        elif event == "top_scores_open":
            seq = [(1047, 70), (1319, 70), (1568, 110)]
        elif event == "reset_open":
            seq = [(300, 90), (260, 90), (220, 140)]
        elif event == "confirm_yes":
            seq = [(880, 70), (1175, 100)]
        elif event == "confirm_no":
            seq = [(500, 70), (350, 100)]
        elif event == "window_close":
            seq = [(500, 70), (350, 90)]
        # --- Distinct vivid sounds for the three original menu tools ---
        # (contrasting with each other AND with the newer tool sounds below)
        elif event == "quiz_open":
            # bold ascending "challenge" fanfare — amber Bond Battle theme
            seq = [(784, 90), (988, 90), (1175, 150)]
        elif event == "solver_open":
            # calm, methodical rising tone — blue EquiLab theme
            seq = [(587, 110), (698, 110), (880, 170)]
        elif event == "gas_open":
            # bubbly, fizzy alternating tone — teal Fizz Factory theme
            seq = [(660, 60), (990, 60), (660, 60), (1320, 150)]
        # --- Distinct vivid sounds for the three new tool windows ---
        elif event == "atomole_open":
            # bright ascending "orbiting" arpeggio — purple/violet AtoMole theme
            seq = [(523, 90), (659, 90), (784, 90), (988, 130)]
        elif event == "atomole_select":
            seq = [(1046, 55), (784, 55)]
        elif event == "mole_tab":
            # rapid "calculator keypad" blips ending on a bright ping
            seq = [(1318, 45), (1568, 45), (1318, 45), (1760, 45), (1568, 45), (2093, 140)]
        elif event == "pop":
            seq = [(1500, 80), (900, 60)]
        elif event == "h2_pop":
            seq = [(3000, 15), (1500, 20), (200, 90)]
        elif event == "organic_open":
            # warm, earthy rolling tones — green Carbon Craft theme
            seq = [(330, 110), (392, 110), (440, 110), (523, 160)]
        elif event == "organic_select":
            seq = [(392, 60), (523, 80)]
        elif event == "electro_open":
            # zappy alternating high/low spark — amber Volt Vault theme
            seq = [(2100, 35), (150, 35), (2100, 35), (150, 35), (2500, 110)]
        elif event == "electro_select":
            seq = [(1800, 45), (2400, 90)]
        else:
            return
        threading.Thread(target=_run_beep_sequence, args=(seq,), daemon=True).start()
    except Exception as e:
        print("play_sound error:", e, file=sys.stderr)

def play_bonus_chime():
    SOUNDS_ENABLED = True
    if not WINSOUND_AVAILABLE:
        return
    seq = [(660, 100), (880, 100), (990, 100), (880, 100), (660, 150)]
    threading.Thread(target=_run_beep_sequence, args=(seq,), daemon=True).start()

def play_bonus_chime():
    # A fun, playful chime with quick rise and fall
    sequence = [
        (660, 100),  # low note
        (880, 100),  # higher
        (990, 100),  # highest
        (880, 100),  # back down
        (660, 150)   # finish
    ]
    for freq, dur in sequence:
      winsound.Beep(freq, dur)


# ----------------------------
# Persistence: Leaderboard file + permanent Top Scores archive
# ----------------------------
LB_FILE = "leaderboard.json"
TOP_SCORES_FILE = "top_scores.json"

def load_leaderboard():
    if os.path.exists(LB_FILE):
        try:
            with open(LB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # normalize structure
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []

def save_leaderboard(data):
    try:
        with open(LB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def add_score_to_leaderboard(name, score, bonus=0):
    """score: quiz score out of 10 (int); bonus: total speed-bonus points earned (int)."""
    lb = load_leaderboard()
    entry = {
        "name": name,
        "score": int(score),
        "bonus": int(bonus),
        "time": datetime.now().isoformat()
    }
    lb.append(entry)
    # sort: score desc, then bonus desc (tie-breaker), then timestamp asc
    def score_key(e):
        return (-e.get("score", 0), -e.get("bonus", 0), e.get("time", ""))
    lb.sort(key=score_key)
    save_leaderboard(lb)

def load_top_scores():
    if os.path.exists(TOP_SCORES_FILE):
        try:
            with open(TOP_SCORES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []

def save_top_scores(data):
    try:
        with open(TOP_SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def archive_top_scores_and_clear():
    """Merge the current leaderboard's entries into the permanent Top Scores
    Hall of Fame (keeping only the best 10 overall, by score then bonus),
    then wipe the active leaderboard clean so new names can be added."""
    current = load_leaderboard()
    archive = load_top_scores()
    combined = archive + [
        {"name": e.get("name", "Anon"), "score": e.get("score", 0), "bonus": e.get("bonus", 0)}
        for e in current
    ]
    def score_key(e):
        return (-e.get("score", 0), -e.get("bonus", 0))
    combined.sort(key=score_key)
    top10 = combined[:10]
    save_top_scores(top10)
    save_leaderboard([])
    return top10

def clear_top_scores():
    """Permanently erase the all-time Top Scores hall of fame."""
    save_top_scores([])

# ----------------------------
# Chemistry formula parser & balancer
# (Rational nullspace method)
# ----------------------------

token_re = re.compile(r'([A-Z][a-z]?|\(|\)|\d+)')

def parse_formula(formula: str) -> dict:
    """
    Parse a chemical formula into element counts.
    e.g., "Ca(OH)2" -> {"Ca":1,"O":2,"H":2}
    """
    tokens = token_re.findall(formula)
    stack = [dict()]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == '(':
            stack.append(dict()); i += 1
        elif tok == ')':
            i += 1
            mul = 1
            if i < len(tokens) and tokens[i].isdigit():
                mul = int(tokens[i]); i += 1
            top = stack.pop()
            for el, cnt in top.items():
                stack[-1][el] = stack[-1].get(el, 0) + cnt * mul
        elif re.match(r'[A-Z][a-z]?$', tok):
            el = tok; i += 1
            mul = 1
            if i < len(tokens) and tokens[i].isdigit():
                mul = int(tokens[i]); i += 1
            stack[-1][el] = stack[-1].get(el, 0) + mul
        else:
            i += 1
    return stack[-1]

from fractions import Fraction

def build_element_matrix(reactants, products):
    species = reactants + products
    elements = sorted({el for s in species for el in parse_formula(s)})
    mat = []
    for el in elements:
        row = []
        for r in reactants:
            row.append(Fraction(parse_formula(r).get(el, 0)))
        for p in products:
            row.append(Fraction(-parse_formula(p).get(el, 0)))
        mat.append(row)
    return mat, elements

def rational_nullspace(matrix):
    """
    Compute an integer vector in the nullspace of rational matrix.
    Returns smallest integer vector or None.
    """
    A = [row[:] for row in matrix]
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    row = 0
    pivot_cols = []
    for col in range(n):
        if row >= m:
            break
        sel = None
        for r in range(row, m):
            if A[r][col] != 0:
                sel = r; break
        if sel is None:
            continue
        A[row], A[sel] = A[sel], A[row]
        piv = A[row][col]
        A[row] = [val / piv for val in A[row]]
        for r in range(m):
            if r != row and A[r][col] != 0:
                factor = A[r][col]
                A[r] = [A[r][c] - factor * A[row][c] for c in range(n)]
        pivot_cols.append(col)
        row += 1
    free_cols = [c for c in range(n) if c not in pivot_cols]
    if not free_cols:
        return None
    sol = [Fraction(0) for _ in range(n)]
    for c in free_cols:
        sol[c] = Fraction(1)
    pivot_row_of = {}
    r = 0
    for pc in pivot_cols:
        pivot_row_of[pc] = r; r += 1
    for pc in pivot_cols:
        prow = pivot_row_of[pc]
        val = Fraction(0)
        for c in free_cols:
            val += A[prow][c] * sol[c]
        sol[pc] = -val
    dens = [x.denominator for x in sol]
    lcm = 1
    for d in dens:
        lcm = lcm * d // math.gcd(lcm, d)
    ints = [int(x * lcm) for x in sol]
    g = 0
    for v in ints:
        g = math.gcd(g, abs(v))
    if g == 0:
        return None
    ints = [v // g for v in ints]
    if all(v <= 0 for v in ints):
        ints = [-v for v in ints]
    return ints

def balance_equation(reactants, products):
    mat, elements = build_element_matrix(reactants, products)
    steps = []
    steps.append("Elements involved: " + ", ".join(elements))
    steps.append("Constructed element matrix (rows = elements; cols = species [reactants then products]):")
    for el, row in zip(elements, mat):
        steps.append(f"  {el}: " + ", ".join(str(int(x)) if x == int(x) else str(x) for x in row))
    vec = rational_nullspace(mat)
    if vec is None:
        return None, ["Failed: no non-trivial nullspace (cannot balance)"]
    rcoeffs = vec[:len(reactants)]
    pcoeffs = vec[len(reactants):]
    steps.append("Solution vector (smallest integer coefficients): " + ", ".join(str(v) for v in vec))
    def fmt_list(coefs, species):
        parts = []
        for c, s in zip(coefs, species):
            parts.append(f"{(str(c) if c != 1 else '')}{s}".strip())
        return " + ".join(parts)
    steps.append("Balanced equation: " + fmt_list(rcoeffs, reactants) + " -> " + fmt_list(pcoeffs, products))
    return (rcoeffs, pcoeffs), steps

QUIZ_UI = {
    "bg": "#fff1b8", "card": "#ffffff", "border": "#ff9f1c",
    "ink": "#1d1030", "muted": "#7a5c00", "chip": "#ffca3a",
    "option": "#fffaf0", "option_hover": "#ffe066", "option_sel": "#8ac926",
    "primary": "#06d6a0", "accent": "#ff006e", "blue": "#3a86ff",
    "good": "#06d6a0", "good_bg": "#8ac926",
    "bad": "#ef233c", "bad_bg": "#ff8fa3", "warn": "#fb5607",
    "dot_idle": "#e8d48a",
}

SOLVER_UI = {
    "bg": "#cdeefd", "panel": "#ffe0f7", "card": "#ffffff", "border": "#7b2cbf",
    "ink": "#160b38", "muted": "#5a3d7a", "accent": "#3a86ff",
    "good": "#06d6a0", "row_a": "#f3d9ff", "row_b": "#ffffff", "latest": "#ffd60a",
}

_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def pretty_formula(text):
    """H2O -> H₂O  (display only; digits right after a letter or bracket)."""
    return re.sub(r"(?<=[A-Za-z\)\]])\d+", lambda m: m.group(0).translate(_SUB), text)


def _shade(color, factor=0.9):
    rgb = [int(int(color[i:i + 2], 16) * factor) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(rgb)


def add_hover(widget, base, hover):
    """Hover highlight that remembers the button's 'real' colour in widget._base."""
    widget._base = base
    widget.config(bg=base)

    def enter(_):
        if str(widget.cget("state")) == "normal":
            widget.config(bg=hover)

    def leave(_):
        widget.config(bg=widget._base)

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


def paint(widget, bg, border=None):
    widget._base = bg
    widget.config(bg=bg)
    if border:
        widget.config(highlightbackground=border)


def make_button(parent, text, command, bg, fg="white",
                font=("Segoe UI", 11, "bold"), **kw):
    b = tk.Button(parent, text=text, command=command, fg=fg, font=font,
                  activebackground=_shade(bg, 0.88), activeforeground=fg,
                  relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
                  takefocus=0, **kw)
    add_hover(b, bg, _shade(bg, 0.92))
    return b
def make_rich_text(parent, bg, fg, **kw):
    """Read-only Text box with ready-made styles for clean, readable content."""
    t = tk.Text(parent, font=("Segoe UI", 12), wrap="word", bg=bg, fg=fg,
                relief="flat", padx=22, pady=16, cursor="arrow", **kw)
    t.tag_config("title", font=("Georgia", 17, "bold"), foreground=fg, spacing3=4)
    t.tag_config("sub", font=("Segoe UI", 12, "italic"), foreground=fg, spacing3=14)
    t.tag_config("body", font=("Segoe UI", 12), foreground=fg,
                 spacing1=5, spacing3=2, lmargin1=14, lmargin2=34)
    t.tag_config("para", font=("Segoe UI", 12), foreground=fg,
                 spacing1=5, spacing3=2, lmargin1=14, lmargin2=14)
    return t


def add_chip(t, text, bg, fg="#ffffff"):
    """A coloured heading label, e.g. CATHODE (−)."""
    tag = "chip_" + bg
    t.tag_config(tag, font=("Segoe UI", 11, "bold"), foreground=fg, background=bg)
    t.insert(tk.END, f" {text} ", tag)
    t.insert(tk.END, "\n")


def add_line(t, text):
    """A bullet point."""
    t.insert(tk.END, "•  " + text + "\n", "body")


def add_eq(t, text, bg, fg):
    """An equation on a tinted background."""
    tag = "eq_" + bg
    t.tag_config(tag, font=("Segoe UI", 14, "bold"), foreground=fg, background=bg,
                 lmargin1=14, lmargin2=14)
    t.insert(tk.END, f"  {text}  ", tag)
    t.insert(tk.END, "\n")


def insert_formula(t, text, tag):
    """Insert a general formula such as CnH2n+2 with real subscripts."""
    sub = tag + "_sub"
    t.tag_config(sub, offset=-5, font=("Segoe UI", 12, "bold"))
    for i, part in enumerate(re.split(r"((?<=[A-Z])[0-9n+]+)", text)):
        t.insert(tk.END, part, (tag, sub) if i % 2 else tag)

# ----------------------------
# Pools: quiz questions, solver options, gas reaction rules
# ----------------------------

# 30 MCQ questions given by user earlier — we'll reuse (with keys A-D)
MCQ_POOL = [
    ("Which equation represents a neutralization reaction ❓",
    ["HCl + NaOH → NaCl + H₂O", "Zn + HCl → ZnCl₂ + H₂", "2Na + Cl₂ → 2NaCl", "CuCO₃ → CuO + CO₂"], "A"),
    ("What type of reaction is: 2H₂O₂ → 2H₂O + O₂",
     ["Displacement", "Decomposition", "Neutralization", "Precipitation"], "B"),
    ("Which equation is not balanced?",
     ["2Mg + O₂ → 2MgO", "2H₂ + O₂ → 2H₂O", "Na + Cl₂ → NaCl", "CaCO₃ → CaO + CO₂"], "C"),
    ("Which of the following is a displacement reaction?",
     ["Cu + 2AgNO₃ → Cu(NO₃)₂ + 2Ag", "2Na + Cl₂ → 2NaCl", "CaCO₃ → CaO + CO₂", "H₂ + Cl₂ → 2HCl"], "A"),
    ("Which of the following is a combination reaction?",
     ["C + O₂ → CO₂", "CaCO₃ → CaO + CO₂", "Zn + CuSO₄ → ZnSO₄ + Cu", "HCl + NaOH → NaCl + H₂O"], "A"),
    ("Which salt is formed when nitric acid reacts with magnesium oxide?",
     ["Magnesium nitrate", "Magnesium chloride", "Magnesium sulfate", "Magnesium carbonate"], "A"),
    ("Which equation represents the reaction of an acid with a metal?",
     ["2HCl + Zn → ZnCl₂ + H₂", "H₂SO₄ + NaOH → Na₂SO₄ + H₂O", "Na₂CO₃ + 2HCl → 2NaCl + CO₂ + H₂O", "CaO + H₂O → Ca(OH)₂"], "A"),
    ("Which equation shows an acid–carbonate reaction?",
     ["H₂SO₄ + Mg → MgSO₄ + H₂", "2HCl + CaCO₃ → CaCl₂ + CO₂ + H₂O", "NaOH + HCl → NaCl + H₂O", "2H₂O₂ → 2H₂O + O₂"], "B"),
    ("Which of the following produces carbon dioxide gas?",
     ["Hydrochloric acid + sodium hydroxide", "Hydrochloric acid + sodium carbonate", "Sodium + water", "Zinc + dilute sulfuric acid"], "B"),
    ("When excess ammonia is added to copper(II) sulfate solution, the final complex ion formed gives the solution a:",
     ["Green color", "Deep blue color", "Brown color", "Colorless appearance"], "B"),
    ("Which statement about oxidation is correct?",
     ["Gain of electrons", "Gain of hydrogen", "Loss of oxygen", "Loss of electrons"], "D"),
    ("In the reaction: Zn + CuSO₄ → ZnSO₄ + Cu, which substance is oxidized?",
     ["Zinc", "Copper", "Sulfate", "None"], "A"),
    ("Which reaction shows reduction of copper(II) oxide?",
     ["CuO + H₂ → Cu + H₂O", "Cu + O₂ → CuO", "CuCO₃ → CuO + CO₂", "Cu + 2AgNO₃ → Cu(NO₃)₂ + 2Ag"], "A"),
    ("Which of these is an oxidizing agent?",
     ["Hydrogen", "Oxygen", "Carbon monoxide", "Hydrogen sulfide"], "B"),
    ("The reaction between magnesium and oxygen can be described as:",
     ["Oxidation of magnesium", "Reduction of magnesium", "Neutralization", "Decomposition"], "A"),
    ("Which of the following pairs will form a precipitate?",
     ["NaCl + HCl", "Na₂SO₄ + BaCl₂", "H₂SO₄ + NaOH", "KNO₃ + HCl"], "B"),
    ("In the reaction: AgNO₃ + NaCl → AgCl + NaNO₃, the precipitate formed is:",
     ["NaNO₃", "NaCl", "AgCl", "AgNO₃"], "C"),
    ("The ionic equation for the above reaction is:",
     ["Ag⁺ + NO₃⁻ → AgNO₃", "Na⁺ + Cl⁻ → NaCl", "Ag⁺ + Cl⁻ → AgCl", "Na⁺ + NO₃⁻ → NaNO₃"], "C"),
    ("Which salt is insoluble in water?",
     ["NaCl", "KNO₃", "CaCO₃", "(NH₄)₂SO₄"], "C"),
    ("Which of the following methods can be used to prepare barium sulfate?",
     ["Precipitation", "Neutralization", "Filtration", "Evaporation"], "A"),
    ("Combustion of methane is represented by:",
     ["CH₄ + 2O₂ → CO₂ + 2H₂O", "CH₄ + O₂ → CO + H₂O", "2CH₄ → C₂H₄ + 2H₂", "CH₄ + H₂ → C + 2H₂O"], "A"),
    ("Which reaction is endothermic?",
     ["Combustion of hydrogen", "Photosynthesis", "Neutralization", "Respiration"], "B"),
    ("When calcium reacts with water, one product is:",
     ["Hydrogen gas", "Oxygen gas", "Carbon dioxide", "Ammonia"], "A"),
    ("Which reaction represents thermal decomposition?",
     ["2K + Cl₂ → 2KCl", "CuCO₃ → CuO + CO₂", "H₂ + Cl₂ → 2HCl", "NaOH + HCl → NaCl + H₂O"], "B"),
    ("The equation for complete combustion of ethane is:",
     ["2C₂H₆ + 7O₂ → 4CO₂ + 6H₂O", "C₂H₆ + 2O₂ → 2CO + 3H₂O", "C₂H₆ + O₂ → C + H₂O", "2C₂H₆ + 5O₂ → 4CO + 6H₂O"], "A"),
    ("Which statement about the law of conservation of mass is correct?",
     ["Atoms are created in reactions.", "Mass of reactants equals mass of products.", "Atoms are destroyed in reactions.", "Products always have more mass."], "B"),
    ("How many moles of H₂ are needed to react with 1 mole of O₂ to form water?",
     ["1", "2", "3", "4"], "B"),
    ("Which of the following correctly represents the neutralization reaction?",
     ["Acid + Base → Salt + Water", "Acid + Metal → Salt + Water", "Acid + Carbonate → Salt + Water", "Acid + Oxide → Hydrogen + Salt"], "A"),
    ("Which equation shows reversible reaction?",
     ["N₂ + 3H₂ ⇌ 2NH₃", "2H₂ + O₂ → 2H₂O", "CaCO₃ → CaO + CO₂", "Zn + HCl → ZnCl₂ + H₂"], "A"),
]

MCQ_POOL += [
    ("Which row correctly shows the colour change when excess ammonia is added to a pale blue copper(II) hydroxide precipitate?",
     ["Pale blue precipitate → dissolves to deep blue solution", "Pale blue precipitate → white precipitate", "Pale blue precipitate → green precipitate", "No visible change occurs"], "A"),
    ("Dilute hydrochloric acid is added to solid sodium carbonate. Which observation confirms a carbonate is present?",
     ["A yellow precipitate forms", "Effervescence occurs, producing a gas that turns limewater milky", "The solution turns blue litmus red only", "A smell of ammonia is produced"], "B"),
    ("In the Haber process, which condition is used to increase the yield of ammonia without drastically slowing the rate?",
     ["Very low pressure and very low temperature", "High pressure (~200 atm) and a compromise temperature (~450°C) with an iron catalyst", "High temperature only, no catalyst", "Low pressure with a platinum catalyst"], "B"),
    ("A student adds excess dilute sulfuric acid to a mixture of copper(II) oxide and copper metal, then filters. What remains on the filter paper?",
     ["Copper metal only", "Copper(II) sulfate crystals", "Copper(II) oxide only", "A mixture of both solids, unreacted"], "A"),
    ("0.1 mol of magnesium reacts completely with excess hydrochloric acid. Which volume of H₂ gas is produced at r.t.p. (molar gas volume = 24 dm³/mol)?",
     ["1.2 dm³", "2.4 dm³", "0.24 dm³", "24 dm³"], "A"),
    ("Which statement best explains why the rate of reaction between marble chips and hydrochloric acid increases when the chips are crushed into powder?",
     ["The acid becomes more concentrated", "The surface area of the solid increases, increasing collision frequency", "The temperature of the system increases automatically", "Powdered marble has a lower activation energy"], "B"),
]

# Solver options pool (20)
SOLVER_OPTIONS = [
    (["H2","O2"],["H2O"]),
    (["N2","H2"],["NH3"]),
    (["C","O2"],["CO2"]),
    (["Fe","O2"],["Fe2O3"]),
    (["Al","O2"],["Al2O3"]),
    (["Na","Cl2"],["NaCl"]),
    (["K","Cl2"],["KCl"]),
    (["C2H6","O2"],["CO2","H2O"]),
    (["C3H8","O2"],["CO2","H2O"]),
    (["KClO3"],["KCl","O2"]),
    (["H2O2"],["H2O","O2"]),
    (["FeS2","O2"],["Fe2O3","SO2"]),
    (["Pb(NO3)2"],["PbO","NO2","O2"]),
    (["C6H12O6","O2"],["CO2","H2O"]),
    (["NH4NO3"],["N2O","H2O"]),
    (["Zn","HCl"],["ZnCl2","H2"]),
    (["Cu","AgNO3"],["Cu(NO3)2","Ag"]),
    (["CH4","O2"],["CO2","H2O"]),
    (["Na","O2"],["Na2O"]),
    (["P4","O2"],["P2O5"]),
    (["Mg","O2"],["MgO"]),
    (["Ca","O2"],["CaO"]),
    (["Ca","H2O"],["Ca(OH)2","H2"]),
    (["Na","H2O"],["NaOH","H2"]),
    (["Fe","O2"],["Fe3O4"]),
    (["Fe2O3","CO"],["Fe","CO2"]),
    (["CuO","H2"],["Cu","H2O"]),
    (["Zn","H2SO4"],["ZnSO4","H2"]),
    (["Mg","HCl"],["MgCl2","H2"]),
    (["Al","HCl"],["AlCl3","H2"]),
    (["CaCO3"],["CaO","CO2"]),
    (["NaHCO3"],["Na2CO3","H2O","CO2"]),
    (["HCl","NaOH"],["NaCl","H2O"]),
    (["H2SO4","NaOH"],["Na2SO4","H2O"]),
    (["HNO3","KOH"],["KNO3","H2O"]),
    (["HCl","CaCO3"],["CaCl2","H2O","CO2"]),
    (["BaCl2","Na2SO4"],["BaSO4","NaCl"]),
    (["AgNO3","NaCl"],["AgCl","NaNO3"]),
    (["Pb(NO3)2","KI"],["PbI2","KNO3"]),
    (["CuSO4","Fe"],["FeSO4","Cu"]),
    (["AgNO3","Cu"],["Cu(NO3)2","Ag"]),
    (["C4H10","O2"],["CO2","H2O"]),
    (["C2H5OH","O2"],["CO2","H2O"]),
    (["CH3COOH","NaOH"],["CH3COONa","H2O"]),
    (["NH3","HCl"],["NH4Cl"]),
    (["N2","O2"],["NO"]),
    (["NO","O2"],["NO2"]),
    (["SO2","O2"],["SO3"]),
    (["Fe","Cl2"],["FeCl3"]),
    (["Ca(OH)2","CO2"],["CaCO3","H2O"]),
]

# ----------------------------
# NEW: Atomic Structure & Periodic Table MCQ pool
# ----------------------------
ATOMIC_MCQ_POOL = [
    ("The atomic number of an element tells you the number of:",
     ["Neutrons only", "Protons in the nucleus", "Protons + neutrons", "Electron shells"], "B"),
    ("Isotopes of an element have the same number of protons but different numbers of:",
     ["Electrons", "Neutrons", "Protons", "Shells"], "B"),
    ("What is the electronic configuration of a sodium atom (atomic number 11)?",
     ["2,8,1", "2,8,8", "2,9", "2,8,2"], "A"),
    ("The number of electrons in the outer shell of an atom mainly determines its:",
     ["Mass number", "Chemical properties", "Number of neutrons", "Isotope symbol"], "B"),
    ("Which subatomic particle has (almost) no mass?",
     ["Proton", "Neutron", "Electron", "Nucleus"], "C"),
    ("The period number of an element in the Periodic Table corresponds to the number of:",
     ["Protons", "Occupied electron shells", "Valence electrons", "Isotopes"], "B"),
    ("Elements in the same group of the Periodic Table have the same number of:",
     ["Neutrons", "Electron shells", "Outer shell (valence) electrons", "Protons"], "C"),
    ("Which particle carries a positive charge?",
     ["Electron", "Neutron", "Proton", "Photon"], "C"),
    ("Group 0 (Group 18) elements are unreactive because they have:",
     ["No electrons", "A full outer electron shell", "Only one shell", "No neutrons"], "B"),
    ("Across Period 3 (Na to Ar), atomic radius generally:",
     ["Increases", "Decreases", "Stays the same", "Increases then decreases sharply"], "B"),
    ("The mass number of an atom is equal to:",
     ["Protons only", "Protons + electrons", "Protons + neutrons", "Neutrons only"], "C"),
    ("Group I elements (alkali metals) are generally:",
     ["Hard and unreactive", "Soft and very reactive", "Gases at room temperature", "Non-metals"], "B"),
]

# ----------------------------
# NEW: Moles & Stoichiometry MCQ pool
# ----------------------------
MOLE_MCQ_POOL = [
    ("The number of particles in one mole of a substance is known as:",
     ["Molar volume", "Avogadro constant (6.02×10²³)", "Relative atomic mass", "Empirical mass"], "B"),
    ("Number of moles is calculated using the formula:",
     ["moles = mass × Mr", "moles = mass ÷ Mr", "moles = Mr ÷ mass", "moles = mass + Mr"], "B"),
    ("How many moles of CO₂ (Mr = 44) are in 22 g of CO₂?",
     ["0.5 mol", "1 mol", "2 mol", "44 mol"], "A"),
    ("At room temperature and pressure (r.t.p.), one mole of any gas occupies:",
     ["1 dm³", "22.4 dm³", "24 dm³", "100 dm³"], "C"),
    ("Concentration in mol/dm³ is calculated as:",
     ["moles ÷ volume (dm³)", "moles × volume (dm³)", "volume ÷ moles", "mass ÷ volume"], "A"),
    ("The limiting reactant in a reaction is the one that:",
     ["Is in excess", "Is used up first, stopping the reaction", "Has the largest Mr", "Is always a gas"], "B"),
    ("The empirical formula of a compound shows:",
     ["The exact number of atoms in one molecule", "The simplest whole-number ratio of atoms", "Only the metal atoms present", "The molar volume"], "B"),
    ("Percentage yield is calculated as:",
     ["(actual yield ÷ theoretical yield) × 100", "(theoretical yield ÷ actual yield) × 100", "actual yield − theoretical yield", "actual yield × theoretical yield"], "A"),
    ("The relative molecular mass (Mr) of water, H₂O, is:",
     ["16", "17", "18", "20"], "C"),
    ("How many moles of NaOH are in 250 cm³ of a 2.0 mol/dm³ solution?",
     ["0.25 mol", "0.5 mol", "2.0 mol", "8.0 mol"], "B"),
    ("Which quantity must you know, besides mass, to calculate moles of a substance?",
     ["Its colour", "Its relative formula mass (Mr)", "Its state of matter", "Its density only"], "B"),
    ("In the reaction N₂ + 3H₂ → 2NH₃, how many moles of H₂ are needed for 2 moles of N₂?",
     ["2 mol", "3 mol", "6 mol", "4 mol"], "C"),
]

# ----------------------------
# NEW: Electrolysis MCQ pool
# ----------------------------
ELECTROLYSIS_MCQ_POOL = [
    ("Electrolysis is best described as:",
     ["Heating a compound to break it down", "The decomposition of an ionic compound using electricity", "Mixing two solutions to form a precipitate", "A reaction between an acid and a metal"], "B"),
    ("During electrolysis, reduction (gain of electrons) occurs at the:",
     ["Anode (positive electrode)", "Cathode (negative electrode)", "Electrolyte", "Power source"], "B"),
    ("During electrolysis, oxidation (loss of electrons) occurs at the:",
     ["Cathode", "Anode", "Electrolyte surface", "Salt bridge"], "B"),
    ("When molten sodium chloride is electrolysed, the product at the cathode is:",
     ["Chlorine gas", "Sodium metal", "Hydrogen gas", "Oxygen gas"], "B"),
    ("When molten sodium chloride is electrolysed, the product at the anode is:",
     ["Sodium metal", "Chlorine gas", "Hydrogen gas", "Sodium oxide"], "B"),
    ("Electrolysis of dilute sulfuric acid using inert electrodes produces at the cathode:",
     ["Oxygen gas", "Hydrogen gas", "Sulfur", "Water only"], "B"),
    ("An electrolyte is a substance that:",
     ["Never conducts electricity", "Conducts electricity when molten or dissolved in water, and is decomposed in the process", "Only conducts electricity as a solid", "Is always a metal"], "B"),
    ("A common pair of inert (unreactive) electrode materials used in electrolysis is:",
     ["Copper and zinc", "Platinum and graphite (carbon)", "Sodium and potassium", "Iron and magnesium"], "B"),
    ("In the electrolytic purification/refining of copper, pure copper is deposited at the:",
     ["Impure copper anode", "Cathode", "Electrolyte solution", "Power supply"], "B"),
    ("Electroplating is used to:",
     ["Remove electrons from a metal permanently", "Coat one metal with a thin layer of another metal using electrolysis", "Melt a metal without electricity", "Increase the mass number of an atom"], "B"),
    ("Electrolysis of concentrated aqueous sodium chloride (brine) produces chlorine gas at the:",
     ["Cathode", "Anode", "Electrolyte bulk", "Both electrodes equally"], "B"),
    ("The half-equation for the formation of hydrogen gas at the cathode is:",
     ["2H⁺ + 2e⁻ → H₂", "2H⁺ − 2e⁻ → H₂", "H₂ → 2H⁺ + 2e⁻", "2OH⁻ → H₂O + O₂ + 2e⁻"], "A"),
]

# ----------------------------
# NEW: Organic Chemistry MCQ pool
# ----------------------------
ORGANIC_MCQ_POOL = [
    ("Organic chemistry is mainly the study of compounds containing:",
     ["Metal ions", "Carbon (covalently bonded)", "Only oxygen and hydrogen", "Noble gases"], "B"),
    ("A homologous series is a family of compounds that:",
     ["Have completely different chemical properties", "Have the same general formula and similar chemical properties", "Contain no carbon atoms", "Are all gases"], "B"),
    ("The general formula of the alkanes is:",
     ["CnH2n", "CnH2n+2", "CnH2n-2", "CnHn"], "B"),
    ("Alkanes are described as saturated hydrocarbons because they contain:",
     ["Only single C–C bonds", "At least one C=C double bond", "A benzene ring", "An –OH group"], "A"),
    ("The functional group present in all alkenes is:",
     ["–OH", "C=C double bond", "–COOH", "–NH2"], "B"),
    ("Which test distinguishes an alkene from an alkane?",
     ["Adding bromine water — alkene decolourises it, alkane does not", "Burning in air", "Adding water", "Measuring boiling point"], "A"),
    ("The functional group of an alcohol (e.g. ethanol) is:",
     ["–COOH", "–OH", "C=C", "–CHO"], "B"),
    ("Ethanoic acid (CH₃COOH) belongs to the homologous series of:",
     ["Alcohols", "Alkenes", "Carboxylic acids", "Alkanes"], "C"),
    ("Complete combustion of a hydrocarbon fuel in excess oxygen produces:",
     ["Carbon monoxide and water", "Carbon dioxide and water", "Carbon and hydrogen only", "Only carbon dioxide"], "B"),
    ("Addition polymerisation of many ethene monomers produces:",
     ["Poly(ethene)", "Ethanol", "Ethanoic acid", "Carbon dioxide"], "A"),
    ("Fermentation of glucose by yeast produces ethanol and:",
     ["Oxygen gas", "Carbon dioxide gas", "Hydrogen gas", "Nitrogen gas"], "B"),
    ("Which of these is an example of a saturated compound?",
     ["Ethene, C₂H₄", "Ethane, C₂H₆", "Propene, C₃H₆", "Ethyne, C₂H₂"], "B"),
]

# Registry used by the quiz window's chapter/topic selector
QUIZ_TOPIC_POOLS = {
    "Mixed (All Chapters)": MCQ_POOL + ATOMIC_MCQ_POOL + MOLE_MCQ_POOL + ELECTROLYSIS_MCQ_POOL + ORGANIC_MCQ_POOL,
    "Chemical Bonds & Reactions": MCQ_POOL,
    "Atomic Structure & Periodic Table": ATOMIC_MCQ_POOL,
    "Moles & Stoichiometry": MOLE_MCQ_POOL,
    "Electrolysis": ELECTROLYSIS_MCQ_POOL,
    "Organic Chemistry": ORGANIC_MCQ_POOL,
}
QUIZ_TOPIC_NAMES = list(QUIZ_TOPIC_POOLS.keys())

# ----------------------------
# NEW: Atomic structure data for "Atom Arena"
# element -> (name, atomic number Z, mass number A, electron shells list)
# ----------------------------
ELEMENT_DATA = {
    "H":  ("Hydrogen", 1, 1, [1]),
    "He": ("Helium", 2, 4, [2]),
    "Li": ("Lithium", 3, 7, [2, 1]),
    "Be": ("Beryllium", 4, 9, [2, 2]),
    "B":  ("Boron", 5, 11, [2, 3]),
    "C":  ("Carbon", 6, 12, [2, 4]),
    "N":  ("Nitrogen", 7, 14, [2, 5]),
    "O":  ("Oxygen", 8, 16, [2, 6]),
    "F":  ("Fluorine", 9, 19, [2, 7]),
    "Ne": ("Neon", 10, 20, [2, 8]),
    "Na": ("Sodium", 11, 23, [2, 8, 1]),
    "Mg": ("Magnesium", 12, 24, [2, 8, 2]),
    "Al": ("Aluminium", 13, 27, [2, 8, 3]),
    "Si": ("Silicon", 14, 28, [2, 8, 4]),
    "P":  ("Phosphorus", 15, 31, [2, 8, 5]),
    "S":  ("Sulfur", 16, 32, [2, 8, 6]),
    "Cl": ("Chlorine", 17, 35, [2, 8, 7]),
    "Ar": ("Argon", 18, 40, [2, 8, 8]),
    "K":  ("Potassium", 19, 39, [2, 8, 8, 1]),
    "Ca": ("Calcium", 20, 40, [2, 8, 8, 2]),
}

# ----------------------------
# NEW: Electrolysis data for "Volt Vault" — expanded to cover the full
# O-Level Chemistry 5070 electrolysis syllabus (molten binary compounds,
# aqueous electrolytes with inert/active electrodes, extraction of aluminium,
# purification of copper, and electroplating are all included below).
# key -> (electrolyte description, electrode type, cathode product, cathode half-eq,
#          anode product, anode half-eq, note)
# ----------------------------
ELECTROLYSIS_DATA = {
    "Molten lead(II) bromide, PbBr₂(l)": (
        "Inert (carbon/graphite) electrodes",
        "Lead metal, Pb (grey liquid bead)", "Pb²⁺ + 2e⁻ → Pb",
        "Bromine vapour, Br₂ (orange fumes)", "2Br⁻ − 2e⁻ → Br₂",
        "Classic 5070 example of a simple molten binary ionic compound: only Pb²⁺ and Br⁻ ions are present, so the products are obvious."
    ),
    "Molten sodium chloride, NaCl(l)": (
        "Inert electrodes",
        "Sodium metal, Na", "Na⁺ + e⁻ → Na",
        "Chlorine gas, Cl₂", "2Cl⁻ − 2e⁻ → Cl₂",
        "Shows how reactive metals (too reactive to extract by heating with carbon) are obtained industrially by molten electrolysis."
    ),
    "Molten aluminium oxide, Al₂O₃(l) — extraction of aluminium": (
        "Carbon (graphite) electrodes, dissolved in molten cryolite",
        "Aluminium metal, Al", "Al³⁺ + 3e⁻ → Al",
        "Oxygen gas, O₂ (burns away the carbon anode)", "2O²⁻ − 4e⁻ → O₂",
        "Cryolite lowers the melting point of Al₂O₃ (saving energy). The carbon anodes slowly burn away in the O₂ produced and must be replaced."
    ),
    "Dilute sulfuric acid, H₂SO₄(aq) — inert electrodes": (
        "Inert (platinum) electrodes",
        "Hydrogen gas, H₂", "2H⁺ + 2e⁻ → H₂",
        "Oxygen gas, O₂", "4OH⁻ − 4e⁻ → 2H₂O + O₂",
        "H⁺ is discharged instead of any metal ion (H is 'below' reactive metals); OH⁻ (from water) is discharged instead of SO₄²⁻, which is never discharged."
    ),
    "Very dilute sodium chloride, NaCl(aq)": (
        "Inert electrodes",
        "Hydrogen gas, H₂", "2H⁺ + 2e⁻ → H₂",
        "Oxygen gas, O₂ (not chlorine, as Cl⁻ is too dilute)", "4OH⁻ − 4e⁻ → 2H₂O + O₂",
        "When halide ion concentration is very low, OH⁻ is discharged in preference to Cl⁻ — concentration matters as well as reactivity."
    ),
    "Concentrated aqueous NaCl — brine (aq)": (
        "Inert electrodes",
        "Hydrogen gas, H₂", "2H⁺ + 2e⁻ → H₂",
        "Chlorine gas, Cl₂", "2Cl⁻ − 2e⁻ → Cl₂",
        "High Cl⁻ concentration means Cl₂ is discharged instead of O₂ at the anode — an important industrial process (chlor-alkali)."
    ),
    "Copper(II) sulfate, CuSO₄(aq) — inert electrodes": (
        "Inert (platinum/graphite) electrodes",
        "Copper metal, Cu (pink-brown deposit)", "Cu²⁺ + 2e⁻ → Cu",
        "Oxygen gas, O₂", "4OH⁻ − 4e⁻ → 2H₂O + O₂",
        "Cu²⁺ is discharged in preference to H⁺ since copper is less reactive than hydrogen. Blue colour of the solution fades as Cu²⁺ is used up."
    ),
    "Copper(II) sulfate, CuSO₄(aq) — copper electrodes (purification of copper)": (
        "Active copper electrodes: impure Cu anode, pure Cu cathode",
        "Pure copper metal deposited, Cu", "Cu²⁺ + 2e⁻ → Cu",
        "Impure copper anode dissolves, Cu²⁺", "Cu − 2e⁻ → Cu²⁺",
        "Industrial electrorefining: the impure anode loses mass as it dissolves, the cathode gains mass as pure Cu deposits, and impurities fall as 'anode sludge'."
    ),
    "Silver nitrate/plating bath, AgNO₃(aq) — electroplating an object with silver": (
        "Active electrodes: pure silver anode, the object to be plated is the cathode",
        "Silver deposited onto the object, Ag", "Ag⁺ + e⁻ → Ag",
        "Silver anode dissolves, Ag⁺", "Ag − e⁻ → Ag⁺",
        "Electroplating coats a cheaper/less attractive metal object with a thin, even layer of a more attractive or corrosion-resistant metal (e.g. silver-plated cutlery, chromium-plated car parts)."
    ),
}

# ----------------------------
# NEW: Organic chemistry data for "Carbon Craft"
# key -> (general formula, functional group, example name, example formula,
#          skeletal atoms for the canvas drawing, key reaction/test, uses)
# skeletal atoms format: list of (symbol, x, y) plus bonds list of (i, j, order)
# ----------------------------
ORGANIC_DATA = {
    "Alkanes (e.g. ethane)": {
        "general_formula": "CnH2n+2",
        "functional_group": "None — only single C–C and C–H bonds (saturated)",
        "example_name": "Ethane",
        "example_formula": "C2H6",
        "atoms": [("C", 150, 150), ("C", 250, 150), ("H", 150, 90), ("H", 110, 180), ("H", 190, 180),
                  ("H", 250, 90), ("H", 290, 180), ("H", 210, 180)],
        "bonds": [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 5, 1), (1, 6, 1), (1, 7, 1)],
        "reaction": "Undergo complete combustion (CO2 + H2O) and substitution reactions with halogens in UV light. Do NOT react with bromine water.",
        "uses": "Fuels — e.g. methane (natural gas), propane and butane (LPG), octane (petrol)."
    },
    "Alkenes (e.g. ethene)": {
        "general_formula": "CnH2n",
        "functional_group": "C=C double bond (unsaturated)",
        "example_name": "Ethene",
        "example_formula": "C2H4",
        "atoms": [("C", 150, 150), ("C", 250, 150), ("H", 150, 90), ("H", 110, 190),
                  ("H", 250, 90), ("H", 290, 190)],
        "bonds": [(0, 1, 2), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1)],
        "reaction": "Decolourises bromine water (orange -> colourless) via an addition reaction — this is the standard test for unsaturation.",
        "uses": "Starting material (monomer) for addition polymers such as poly(ethene); ripening agent for fruit."
    },
    "Alcohols (e.g. ethanol)": {
        "general_formula": "CnH2n+1OH",
        "functional_group": "–OH (hydroxyl group)",
        "example_name": "Ethanol",
        "example_formula": "C2H5OH",
        "atoms": [("C", 130, 150), ("C", 220, 150), ("O", 300, 150), ("H", 340, 150),
                  ("H", 130, 90), ("H", 90, 190), ("H", 220, 90), ("H", 220, 210)],
        "bonds": [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 4, 1), (0, 5, 1), (1, 6, 1), (1, 7, 1)],
        "reaction": "Produced by fermentation of glucose using yeast (anaerobic); burns completely to CO2 and H2O; oxidised to a carboxylic acid.",
        "uses": "Alcoholic drinks, solvent, and as a biofuel."
    },
    "Carboxylic acids (e.g. ethanoic acid)": {
        "general_formula": "CnH2n+1COOH",
        "functional_group": "–COOH (carboxyl group)",
        "example_name": "Ethanoic acid",
        "example_formula": "CH3COOH",
        "atoms": [("C", 130, 150), ("C", 220, 150), ("O", 260, 90), ("O", 260, 210), ("H", 320, 210),
                  ("H", 130, 90), ("H", 90, 190), ("H", 170, 190)],
        "bonds": [(0, 1, 1), (1, 2, 2), (1, 3, 1), (3, 4, 1), (0, 5, 1), (0, 6, 1), (0, 7, 1)],
        "reaction": "Reacts with carbonates to give CO2, with metals to give H2, and with alcohols (+ acid catalyst) to form an ester.",
        "uses": "Vinegar (dilute ethanoic acid), preservatives, making esters for flavourings/perfumes."
    },
}


# ----------------------------
# Fizz Factory (virtual reaction lab) data
# ----------------------------
# species -> (colour on screen, "solid" or "aq")
GAS_STYLE = {
    "HCl":   ("#ffd9a0", "aq"),
    "H2SO4": ("#ffb5a7", "aq"),
    "NaOH":  ("#b8c0ff", "aq"),
    "Zn":    ("#a9b2bf", "solid"),
    "Mg":    ("#d5d9df", "solid"),
    "CuO":   ("#9a8f86", "solid"),
    "CaCO3": ("#f3efe0", "solid"),
    "AgNO3": ("#d0f4de", "aq"),
    "NaCl":  ("#bde0fe", "aq"),
    "BaCl2": ("#e0c3fc", "aq"),
    "CuSO4": ("#74c0fc", "aq"),
}

# species -> (category, label shown on the chip)
GAS_INFO = {
    "HCl": ("acid", "acid"), "H2SO4": ("acid", "acid"),
    "NaOH": ("alkali", "alkali"),
    "Zn": ("metal", "metal"), "Mg": ("metal", "metal"),
    "CuO": ("oxide", "metal oxide"), "CaCO3": ("carbonate", "carbonate"),
    "AgNO3": ("salt", "salt (aq)"), "NaCl": ("salt", "salt (aq)"),
    "BaCl2": ("salt", "salt (aq)"), "CuSO4": ("salt", "salt (aq)"),
}
SALT_METAL = {"NaCl": "sodium", "BaCl2": "barium", "AgNO3": "silver", "CuSO4": "copper"}

RX_TYPES = {
    "neut": {
        "title": "Acid + alkali → salt + water  (neutralisation)",
        "tag": "Ionic + covalent",
        "text": "The salt is IONIC: metal ions and acid-radical ions held by electrostatic attraction, "
                "dissolved as free ions. The water is COVALENT: H⁺ from the acid and OH⁻ from the "
                "alkali join by sharing electrons (H–O–H)."},
    "acid_metal": {
        "title": "Acid + metal → salt + hydrogen",
        "tag": "Ionic + covalent",
        "text": "The salt is IONIC: each metal atom loses electrons to form a positive ion (oxidation). "
                "The hydrogen gas is COVALENT: H⁺ ions gain those electrons (reduction) and pairs of "
                "H atoms share electrons (H–H)."},
    "acid_base": {
        "title": "Acid + base (metal oxide) → salt + water",
        "tag": "Ionic + covalent",
        "text": "The base CuO is IONIC (Cu²⁺ and O²⁻). The oxide ion takes H⁺ from the acid to make "
                "COVALENT water, and the Cu²⁺ ions pair with the acid's negative ions to form an "
                "IONIC salt in solution."},
    "acid_carb": {
        "title": "Acid + carbonate → salt + water + carbon dioxide",
        "tag": "Ionic + covalent",
        "text": "Carbonates act as bases. CaCO₃ and the salt formed are IONIC. The carbonate ion reacts "
                "with H⁺ to make COVALENT water and COVALENT carbon dioxide (O=C=O) gas."},
    "precip": {
        "title": "Precipitation  (ionic double decomposition)",
        "tag": "Ionic",
        "text": "Everything here is IONIC. The two solutions swap partners, and the ions of the insoluble "
                "product clump together by electrostatic attraction and fall out as a solid precipitate. "
                "The other ions do not change; they are spectator ions."},
    "displace": {
        "title": "Metal displacement  (redox)",
        "tag": "Ionic",
        "text": "All IONIC. The more reactive metal loses electrons (oxidation) and goes into solution as "
                "ions. The less reactive metal's ions gain those electrons (reduction) and are deposited "
                "as solid metal (metallic bonding)."},
    "amph": {
        "title": "Amphoteric metal + hot concentrated alkali → zincate + hydrogen",
        "tag": "Ionic + covalent",
        "text": "Zinc is amphoteric, so it reacts with strong alkalis as well as acids. The sodium "
                "zincate is IONIC (Na⁺ and ZnO₂²⁻ ions). The hydrogen gas is COVALENT (H–H). "
                "Magnesium is purely basic, so it does not react with alkalis."},
    "dry_displace": {
        "title": "Solid-state displacement  (redox, needs heating)",
        "tag": "Ionic + metallic",
        "text": "The more reactive metal takes the oxygen from copper(II) oxide. The metal loses "
                "electrons (oxidation) and forms an IONIC oxide. The Cu²⁺ in CuO gains electrons "
                "(reduction) and becomes copper atoms held by METALLIC bonding. Once started, "
                "the reaction is strongly exothermic (thermite-like)."},
}

GAS_REACTIONS = {}

def _rx(a, b, eq, t, see, net="", cond="", liq="#eaf8ff", frm=None, ppt=None, gas=False, dep=None):
    GAS_REACTIONS[frozenset((a, b))] = {
        "eq": eq, "t": t, "see": see, "net": net, "cond": cond,
        "liq": liq, "frm": frm, "ppt": ppt, "gas": gas, "dep": dep}

_BLUE, _GREEN = "#8ecbff", "#7fd8c4"

# ---- acid + alkali (neutralisation) ----
_rx("HCl", "NaOH", "HCl(aq) + NaOH(aq) → NaCl(aq) + H2O(l)", "neut",
    "No visible change: the solution stays colourless but warms up (exothermic). An indicator would change colour at pH 7.",
    "H⁺ + OH⁻ → H₂O",
    "Find the end-point with a burette and indicator, then evaporate the solution to get sodium chloride crystals.")
_rx("H2SO4", "NaOH", "H2SO4(aq) + 2NaOH(aq) → Na2SO4(aq) + 2H2O(l)", "neut",
    "No visible change: the solution stays colourless but warms up. Sulfuric acid is dibasic, so it needs 2 mol of NaOH.",
    "H⁺ + OH⁻ → H₂O",
    "Titrate to the end-point, then crystallise the sodium sulfate.")

# ---- acid + metal ----
_rx("HCl", "Zn", "2HCl(aq) + Zn(s) → ZnCl2(aq) + H2(g)", "acid_metal",
    "Steady fizzing as hydrogen bubbles form on the zinc, which slowly shrinks into a colourless solution. A lighted splint gives a squeaky pop.",
    "Zn + 2H⁺ → Zn²⁺ + H₂",
    "Moderate at room temperature. Filter off excess zinc, then crystallise the zinc chloride.", gas=True)
_rx("HCl", "Mg", "2HCl(aq) + Mg(s) → MgCl2(aq) + H2(g)", "acid_metal",
    "Vigorous fizzing, the magnesium vanishes quickly and the flask gets warm. A lighted splint gives a squeaky pop.",
    "Mg + 2H⁺ → Mg²⁺ + H₂",
    "Very fast and exothermic, so use small pieces of ribbon.", gas=True)
_rx("H2SO4", "Zn", "H2SO4(aq) + Zn(s) → ZnSO4(aq) + H2(g)", "acid_metal",
    "Steady fizzing as hydrogen forms, and the zinc dissolves to leave a colourless zinc sulfate solution.",
    "Zn + 2H⁺ → Zn²⁺ + H₂",
    "Use dilute acid. Filter off excess zinc, then crystallise.", gas=True)
_rx("H2SO4", "Mg", "H2SO4(aq) + Mg(s) → MgSO4(aq) + H2(g)", "acid_metal",
    "Vigorous fizzing, the magnesium disappears quickly, and the solution warms up.",
    "Mg + 2H⁺ → Mg²⁺ + H₂",
    "Use dilute acid and small pieces of magnesium.", gas=True)

# ---- acid + base (metal oxide) ----
_rx("HCl", "CuO", "2HCl(aq) + CuO(s) → CuCl2(aq) + H2O(l)", "acid_base",
    "The black powder slowly dissolves and the solution turns blue-green (copper(II) chloride). No gas is given off.",
    "CuO + 2H⁺ → Cu²⁺ + H₂O",
    "Warm the acid gently and add CuO until some is left over (excess), then filter.", liq=_GREEN)
_rx("H2SO4", "CuO", "H2SO4(aq) + CuO(s) → CuSO4(aq) + H2O(l)", "acid_base",
    "The black powder dissolves on gentle warming and the solution turns blue (copper(II) sulfate). No gas is given off.",
    "CuO + 2H⁺ → Cu²⁺ + H₂O",
    "Warm the acid, add CuO until it stops dissolving, filter, then crystallise the blue copper sulfate.", liq=_BLUE)

# ---- acid + carbonate ----
_rx("HCl", "CaCO3", "2HCl(aq) + CaCO3(s) → CaCl2(aq) + H2O(l) + CO2(g)", "acid_carb",
    "Vigorous fizzing as carbon dioxide is released. The marble shrinks, leaving a colourless calcium chloride solution.",
    "CaCO₃ + 2H⁺ → Ca²⁺ + H₂O + CO₂",
    "Bubble the gas through limewater: it turns milky, which confirms CO₂.", gas=True)

# ---- precipitation ----
_rx("AgNO3", "NaCl", "AgNO3(aq) + NaCl(aq) → AgCl(s) + NaNO3(aq)", "precip",
    "A white, curdy precipitate of silver chloride forms at once and slowly settles. The solution above it is colourless sodium nitrate.",
    "Ag⁺ + Cl⁻ → AgCl",
    "This is the standard test for chloride ions (acidify with dilute nitric acid first).", ppt="#fdfdfd")
_rx("AgNO3", "HCl", "AgNO3(aq) + HCl(aq) → AgCl(s) + HNO3(aq)", "precip",
    "A white precipitate of silver chloride forms. The acid supplies the chloride ions, and nitric acid stays in solution.",
    "Ag⁺ + Cl⁻ → AgCl",
    "Filter off the precipitate to separate it from the acid.", ppt="#fdfdfd")
_rx("AgNO3", "BaCl2", "2AgNO3(aq) + BaCl2(aq) → 2AgCl(s) + Ba(NO3)2(aq)", "precip",
    "A thick white precipitate of silver chloride forms. Barium nitrate stays dissolved.",
    "Ag⁺ + Cl⁻ → AgCl",
    "Two chloride ions are released per BaCl₂, so 2 mol of AgNO₃ are needed.", ppt="#fdfdfd")
_rx("BaCl2", "H2SO4", "BaCl2(aq) + H2SO4(aq) → BaSO4(s) + 2HCl(aq)", "precip",
    "A dense white precipitate of barium sulfate appears. The hydrochloric acid formed stays in solution.",
    "Ba²⁺ + SO₄²⁻ → BaSO₄",
    "This is the standard test for sulfate ions (acidify with dilute HCl first).", ppt="#fdfdfd")
_rx("BaCl2", "CuSO4", "BaCl2(aq) + CuSO4(aq) → BaSO4(s) + CuCl2(aq)", "precip",
    "A white precipitate of barium sulfate forms in a solution that turns from blue to blue-green (copper(II) chloride).",
    "Ba²⁺ + SO₄²⁻ → BaSO₄",
    "Filter off the white solid; the filtrate is blue-green copper(II) chloride.", liq=_GREEN, frm=_BLUE, ppt="#fdfdfd")
_rx("CuSO4", "NaOH", "CuSO4(aq) + 2NaOH(aq) → Cu(OH)2(s) + Na2SO4(aq)", "precip",
    "A pale blue, jelly-like precipitate of copper(II) hydroxide forms and the blue colour of the solution fades.",
    "Cu²⁺ + 2OH⁻ → Cu(OH)₂",
    "Test for Cu²⁺ ions. The precipitate does not dissolve in excess NaOH.", frm=_BLUE, ppt="#5eb0ff")
_rx("AgNO3", "NaOH", "2AgNO3(aq) + 2NaOH(aq) → Ag2O(s) + 2NaNO3(aq) + H2O(l)", "precip",
    "A brown precipitate of silver(I) oxide forms (silver hydroxide is unstable and loses water).",
    "2Ag⁺ + 2OH⁻ → Ag₂O + H₂O",
    "The brown precipitate does not dissolve in excess NaOH.", ppt="#8b5a2b")

# ---- metal displacement ----
_rx("CuSO4", "Zn", "CuSO4(aq) + Zn(s) → ZnSO4(aq) + Cu(s)", "displace",
    "The blue colour fades as pink-brown copper coats the zinc and collects in the flask. A colourless zinc sulfate solution is left.",
    "Zn + Cu²⁺ → Zn²⁺ + Cu",
    "Zinc is above copper in the reactivity series, so it displaces it.", frm=_BLUE, dep="#c8693c")
_rx("CuSO4", "Mg", "CuSO4(aq) + Mg(s) → MgSO4(aq) + Cu(s)", "displace",
    "The blue colour fades as pink-brown copper is deposited, leaving colourless magnesium sulfate solution. The flask warms up.",
    "Mg + Cu²⁺ → Mg²⁺ + Cu",
    "Magnesium is much more reactive than copper, so the reaction is quick.", frm=_BLUE, dep="#c8693c")
_rx("AgNO3", "Zn", "2AgNO3(aq) + Zn(s) → Zn(NO3)2(aq) + 2Ag(s)", "displace",
    "Shiny grey crystals of silver grow on the zinc, leaving a colourless zinc nitrate solution.",
    "Zn + 2Ag⁺ → Zn²⁺ + 2Ag",
    "Zinc is above silver in the reactivity series, so it displaces it.", dep="#c0c7d1")
_rx("AgNO3", "Mg", "2AgNO3(aq) + Mg(s) → Mg(NO3)2(aq) + 2Ag(s)", "displace",
    "Shiny grey crystals of silver form on the magnesium, leaving a colourless magnesium nitrate solution.",
    "Mg + 2Ag⁺ → Mg²⁺ + 2Ag",
    "Magnesium is above silver in the reactivity series, so it displaces it.", dep="#c0c7d1")
# ---- H2SO4 + CaCO3: now gives CO2, so the limewater test works ----
_rx("H2SO4", "CaCO3", "H2SO4(aq) + CaCO3(s) → CaSO4(s) + H2O(l) + CO2(g)", "acid_carb",
    "Fizzing as carbon dioxide is released, but it slows as a white coating of calcium sulfate builds up on the marble and in the flask.",
    "CaCO₃ + 2H⁺ + SO₄²⁻ → CaSO₄ + H₂O + CO₂",
    "Bubble the gas through limewater: it turns milky, which confirms CO₂. Insoluble CaSO₄ coats the marble, so the reaction soon slows down.",
    ppt="#f5f1e3", gas=True)

# ---- AgNO3 + H2SO4 -> silver sulfate precipitate ----
_rx("AgNO3", "H2SO4", "2AgNO3(aq) + H2SO4(aq) → Ag2SO4(s) + 2HNO3(aq)", "precip",
    "A white precipitate of silver sulfate forms. It is only slightly soluble, so it shows clearly with fairly concentrated solutions. Nitric acid stays in solution.",
    "2Ag⁺ + SO₄²⁻ → Ag₂SO₄",
    "Use fairly concentrated solutions: Ag₂SO₄ dissolves a little (about 0.02 mol/dm³), so very dilute ones may stay clear.",
    ppt="#fdfdfd")

# ---- Zn + NaOH (amphoteric zinc) ----
_rx("Zn", "NaOH", "Zn(s) + 2NaOH(aq) → Na2ZnO2(aq) + H2(g)", "amph",
    "On warming with concentrated NaOH, the zinc slowly dissolves with steady fizzing of hydrogen, leaving a colourless sodium zincate solution. A lighted splint gives a squeaky pop.",
    "Zn + 2OH⁻ → ZnO₂²⁻ + H₂",
    "Needs hot, concentrated NaOH. Zinc is amphoteric, so it reacts with both acids and strong alkalis.",
    gas=True)

# ---- Zn / Mg + CuO (heated, thermite-like) ----
_rx("Zn", "CuO", "Zn(s) + CuO(s) → ZnO(s) + Cu(s)", "dry_displace",
    "When the dry powders are heated, the black mixture glows and sparks as a vigorous exothermic reaction starts. Zinc oxide (yellow when hot, white when cold) and pink-brown copper are left.",
    "Zn + CuO → ZnO + Cu",
    "Heat the dry powders strongly; the reaction then keeps itself going. Zinc is more reactive than copper, so it takes the oxygen.",
    liq="#d9b99b")
_rx("Mg", "CuO", "Mg(s) + CuO(s) → MgO(s) + Cu(s)", "dry_displace",
    "On heating, the mixture flashes brightly and gets extremely hot. White magnesium oxide and pink-brown copper are left.",
    "Mg + CuO → MgO + Cu",
    "Much more violent than zinc. Use tiny amounts and keep a safe distance.",
    liq="#d8b8a6")

for _pair in (("Zn", "CuO"), ("Mg", "CuO")):
    GAS_REACTIONS[frozenset(_pair)]["dry"] = True

NO_RX_SPECIAL = {
    frozenset(("H2SO4", "NaCl")):
        "Both are in aqueous solution, so they are just free ions (Na⁺, Cl⁻, H⁺, SO₄²⁻) and nothing new forms. "
        "A reaction only happens with concentrated H₂SO₄ and solid NaCl (usually heated), giving NaHSO₄ and HCl gas.",
    frozenset(("Mg", "NaOH")):
        "Magnesium and its oxide are purely basic, not amphoteric, so they do not react with aqueous alkali. "
        "Only zinc (an amphoteric metal) reacts with NaOH.",
}


RX_VISUALS = {
    frozenset(("HCl", "NaOH")):    ("#cfe8ff", "NaCl",     "#2f8fff", "Salt", "colourless solution"),
    frozenset(("H2SO4", "NaOH")):  ("#e3d8ff", "Na2SO4",   "#8b5cf6", "Salt", "colourless solution"),
    frozenset(("HCl", "Zn")):      ("#d2f5df", "ZnCl2",    "#10b981", "Salt", "colourless solution"),
    frozenset(("HCl", "Mg")):      ("#fff0b8", "MgCl2",    "#f5a800", "Salt", "colourless solution"),
    frozenset(("H2SO4", "Zn")):    ("#c9f3ee", "ZnSO4",    "#0d9488", "Salt", "colourless solution"),
    frozenset(("H2SO4", "Mg")):    ("#ffd9e8", "MgSO4",    "#ec4899", "Salt", "colourless solution"),
    frozenset(("HCl", "CuO")):     ("#7fd8c4", "CuCl2",    "#0f9f7a", "Salt", "blue-green solution"),
    frozenset(("H2SO4", "CuO")):   ("#6fb8ff", "CuSO4",    "#1d6fd6", "Salt", "blue solution"),
    frozenset(("HCl", "CaCO3")):   ("#fde7a6", "CaCl2",    "#d99a00", "Salt", "colourless solution"),
    frozenset(("AgNO3", "NaCl")):  ("#ffdcc2", "NaNO3",    "#f97316", "Salt", "colourless solution"),
    frozenset(("AgNO3", "HCl")):   ("#ecd5ff", "HNO3",     "#a855f7", "Acid", "colourless solution"),
    frozenset(("AgNO3", "BaCl2")): ("#d9f7b5", "Ba(NO3)2", "#65a30d", "Salt", "colourless solution"),
    frozenset(("BaCl2", "H2SO4")): ("#ffe0b0", "HCl",      "#ea580c", "Acid", "colourless solution"),
    frozenset(("BaCl2", "CuSO4")): ("#7fd8c4", "CuCl2",    "#0f9f7a", "Salt", "blue-green solution"),
    frozenset(("CuSO4", "NaOH")):  ("#d3dcff", "Na2SO4",   "#4f46e5", "Salt", "colourless solution"),
    frozenset(("AgNO3", "NaOH")):  ("#fff1b0", "NaNO3",    "#ca8a04", "Salt", "colourless solution"),
    frozenset(("CuSO4", "Zn")):    ("#dcf7c4", "ZnSO4",    "#4d9a0c", "Salt", "colourless solution"),
    frozenset(("CuSO4", "Mg")):    ("#ffd0e6", "MgSO4",    "#d6247e", "Salt", "colourless solution"),
    frozenset(("AgNO3", "Zn")):    ("#e6d2ff", "Zn(NO3)2", "#9333ea", "Salt", "colourless solution"),
    frozenset(("AgNO3", "Mg")):    ("#c9ebff", "Mg(NO3)2", "#0284c7", "Salt", "colourless solution"),
    frozenset(("AgNO3", "H2SO4")): ("#ffe3f1", "HNO3", "#db2777", "Acid", "colourless solution"),
    frozenset(("Zn", "NaOH")): ("#e0f2fe", "Na2ZnO2", "#0ea5e9", "Salt", "colourless solution"),
    frozenset(("H2SO4", "CaCO3")): ("#fff3c4", "CaSO4", "#ca8a04", "Salt", "slightly soluble, "
                                                                           "mostly solid"),
}

for _k, (_liq, _salt, _scol, _lab, _word) in RX_VISUALS.items():
    GAS_REACTIONS[_k].update(liq=_liq, salt=_salt, salt_col=_scol,
                             salt_label=_lab, salt_word=_word)

# which gas is given off (drives limewater test vs lighted-splint test)
for _k, _r in GAS_REACTIONS.items():
    _r["gas_type"] = (("co2" if "CaCO3" in _k else "h2") if _r["gas"] else None)

def gas_no_reaction_reason(a, b):
    """Plain-English reason why two chosen reactants do not react."""
    special = NO_RX_SPECIAL.get(frozenset((a, b)))
    if special:
        return special
    ca, cb = GAS_INFO[a][0], GAS_INFO[b][0]
    cats = {ca, cb}
    if ca == cb:
        return {"acid": "Two acids: neither can neutralise the other.",
                "metal": "Two metals: there are no ions to swap and nothing for either to reduce.",
                "salt": "Both are salt solutions and every possible product is soluble, so the ions "
                        "just stay mixed (spectator ions)."}.get(ca, "No reaction under normal conditions.")
    if cats == {"metal", "alkali"}:
        return "Alkalis do not attack these metals under normal lab conditions."
    if "metal" in cats and cats & {"oxide", "carbonate"}:
        return "A solid mixed with a solid does not react at room temperature (the oxide would need strong heating)."
    if "metal" in cats and "salt" in cats:
        metal, salt = (a, b) if ca == "metal" else (b, a)
        return f"{metal} is less reactive than {SALT_METAL[salt]}, so it cannot displace it from its salt."
    if "acid" in cats and "salt" in cats:
        return "No precipitate, gas or water can form, so the ions just stay dissolved together."
    if "alkali" in cats and cats & {"oxide", "carbonate"}:
        return "An alkali cannot neutralise a base or a carbonate: there is no acid present."
    if "alkali" in cats and "salt" in cats:
        return "Every possible product is soluble, so nothing new forms and the ions stay in solution."
    if cats & {"oxide", "carbonate"} and "salt" in cats:
        return "The solid is insoluble, so it releases no ions to react with the dissolved salt."
    if cats == {"oxide", "carbonate"}:
        return "Two insoluble solids do not react with each other."
    return "No reaction under normal conditions."


def _mix(c1, c2, k):
    """Blend colour c1 towards c2 by fraction k (0 = c1, 1 = c2)."""
    k = max(0.0, min(1.0, k))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _path_point(pts, u):
    """Point a fraction u (0 to 1) of the way along a polyline."""
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    d = u * (sum(seg) or 1)
    for i, s in enumerate(seg):
        if d <= s or i == len(seg) - 1:
            f = min(1.0, d / s) if s else 1.0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f,
                    pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
        d -= s

def fit_window(win, w, h, min_w=600, min_h=450):
    """Open at (w x h) but never bigger than the screen; centre it."""
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    w, h = min(w, sw - 40), min(h, sh - 100)
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 2 - 20)}")
    win.minsize(min(min_w, w), min(min_h, h))


def enable_fullscreen(win):
    """F11 toggles fullscreen, Esc leaves it. Returns the toggle function."""
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
    return toggle


def make_scrollable(parent, bg):
    """Returns (outer, inner). Pack `outer`; build your widgets inside `inner`."""
    outer = tk.Frame(parent, bg=bg)
    cv = tk.Canvas(outer, bg=bg, highlightthickness=0)
    vsb = ttk.Scrollbar(outer, orient="vertical", command=cv.yview)
    cv.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    cv.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(cv, bg=bg)
    wid = cv.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
    cv.bind("<Configure>", lambda e: cv.itemconfig(wid, width=e.width))

    def wheel(e):
        if str(e.widget).startswith(str(outer)) and not isinstance(e.widget, (tk.Text, tk.Listbox)):
            cv.yview_scroll(int(-e.delta / 120), "units")
    cv.bind_all("<MouseWheel>", wheel, add="+")
    return outer, inner

# ----------------------------
# Application GUI and logic
# (continuation from previous definitions)
# ----------------------------
class BondBalancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BondBalancer: Where Chemistry Comes Alive! ⚗️💫")
        # Recommended size for comfortable layout (a touch taller than
        # before to make room for the new title banner)
        self.root.geometry("1040x860")
        self.root.configure(bg="#88AAFF")
        self.toggle_fs = enable_fullscreen(self.root)
        # Fonts
        avail = list(font.families())
        self.title_face = "Comic Sans MS" if "Comic Sans MS" in avail else "Segoe UI"
        self.title_font = font.Font(family=self.title_face, size=28, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.btn_font = font.Font(family="Helvetica", size=13, weight="bold")
        self.mono = font.Font(family="Consolas", size=11)
        self.large_mono = font.Font(family="Consolas", size=14, weight="bold")
        # A distinct, bigger font for side-panel option lists (Volt Vault,
        # Carbon Craft, AtoMole atomic list, EquiLab) — bigger + more spaced.
        self.list_face = "Trebuchet MS" if "Trebuchet MS" in avail else ("Verdana" if "Verdana" in avail else "Segoe UI")
        self.list_font = font.Font(family=self.list_face, size=12, weight="bold")
        # A distinct, bigger font for notebook tab labels (used by AtoMole
        # Arena and Volt Vault) — applied globally via ttk.Style below.
        self.tab_face = "Georgia" if "Georgia" in avail else ("Trebuchet MS" if "Trebuchet MS" in avail else "Segoe UI")
        self.tab_font = font.Font(family=self.tab_face, size=13, weight="bold")
        _ttk_style = ttk.Style()
        try:
            _ttk_style.configure("TNotebook.Tab", font=self.tab_font, padding=[18, 10])
        except Exception:
            pass
        # Audio flag
        self.sounds_enabled =True
        # quiz state
        self.quiz_questions = []
        self.current_q = 0
        self.score = 0
        self.bonus_points = 0
        self.revealed_flags = []  # per question whether revealed (ignored)
        self.quiz_start_time = None
        self.time_total = 20.0  # seconds per question
        self.bonus_threshold = 5.0  # seconds for +2 bonus
        self.timer_job = None
        # Build main UI
        self.build_main_ui()
        # Load leaderboard initially
        self.refresh_leaderboard_display()

    # -------------------------
    # Main UI
    # -------------------------
    def build_main_ui(self):
        # ---------------------------------------------------------------
        # Full-width title banner — deep indigo (same colour as the title
        # text used to be), pinned to the very top so it reads as a proper
        # app header rather than plain labels floating on the background.
        # ---------------------------------------------------------------
        banner = tk.Frame(self.root, bg="#4422EE")
        banner.pack(fill="x", side="top")
        tk.Label(banner, text="🌈  Bond Balancer  🔬", font=self.title_font,
                 bg="#4422EE", fg="#ffffff").pack(pady=(16, 2))
        tk.Label(banner, text="✨ Your Digital Lab Partner — Where Atoms React, Bonds Evolve, and Curiosity Ignites! ✨",
                 font=self.header_font, bg="#4422EE", fg="#d9d2ff").pack(pady=(0, 14))

        # ---------------------------------------------------------------
        # Centered content column — packed with expand=True (no fill) so
        # everything below the banner sits vertically centered, giving
        # balanced space above and below the whole block of content.
        # ---------------------------------------------------------------

        content = tk.Frame(self.root, bg="#88AAFF")
        content.pack(fill="both", expand=True)

        tk.Label(content, text="🎮 Choose Your Lab Tool", font=("Georgia", 16, "bold"),
                 bg="#88AAFF", fg="#221177").pack(pady=(18, 8))

        # A soft white "card" groups the six tool buttons so the palette
        # colours (unchanged from the original menu) really pop against a
        # neutral background instead of blending into the blue page.
        tools_card = tk.Frame(content, bg="#ffffff", highlightthickness=2,
                               highlightbackground="#4422EE")
        tools_card.pack(pady=(0, 16), padx=24)

        # Row 1: reactions & bonds tools (original amber / blue / green)
        menu_frame = tk.Frame(tools_card, bg="#ffffff")
        menu_frame.pack(pady=(16, 8), padx=16)

        self.quiz_btn = tk.Button(
            menu_frame,
            text="Bond Battle ⚔",
            font=self.btn_font,
            width=20,
            height=2,
            bg="#fba0e3",
            fg="#e40078",
            relief="flat",
            activebackground="#f4c430",
            command=self.open_quiz_window
        )
        self.quiz_btn.grid(row=0, column=0, padx=12, pady=8)

        self.solver_btn = tk.Button(
            menu_frame,
            text="EquiLab✨",
            font=self.btn_font,
            width=24,
            height=2,
            bg="#1EF0FF",
            fg="#00606f",
            relief="flat",
            activebackground="#5590c8",
            command=self.open_solver_window
        )
        self.solver_btn.grid(row=0, column=1, padx=12, pady=8)

        self.gas_btn = tk.Button(
            menu_frame,
            text="Fizz Factory⚗",
            font=self.btn_font,
            width=20,
            height=2,
            bg="#50c878",
            fg="#005f5f",
            relief="flat",
            activebackground="#7fae69",
            command=self.open_gas_window
        )
        self.gas_btn.grid(row=0, column=2, padx=12, pady=8)

        # Row 2: atoms+moles, organic chemistry, electrolysis tools.
        # Each button keeps its distinct, vividly contrasting colour theme
        # that matches the window it opens: violet (AtoMole), green
        # (Carbon Craft), amber-on-navy (Volt Vault).
        menu_frame2 = tk.Frame(tools_card, bg="#ffffff")
        menu_frame2.pack(pady=(8, 16), padx=16)

        self.atomole_btn = tk.Button(
            menu_frame2,
            text="AtoMole Arena⚛️",
            font=self.btn_font,
            width=22,
            height=2,
            bg="#8e82fe",
            fg="#360f5a",
            relief="flat",
            activebackground="#7a2fd1",
            command=self.open_atomole_window
        )
        self.atomole_btn.grid(row=0, column=0, padx=12, pady=8)

        self.organic_btn = tk.Button(
            menu_frame2,
            text="Carbon Craft♻️",
            font=self.btn_font,
            width=22,
            height=2,
            bg="#e67451",
            fg="#830e0d",
            relief="flat",
            activebackground="#158563",
            command=self.open_organic_window
        )
        self.organic_btn.grid(row=0, column=1, padx=12, pady=8)

        self.volt_btn = tk.Button(
            menu_frame2,
            text="Volt Vault⚡",
            font=self.btn_font,
            width=22,
            height=2,
            bg="#ffb300",
            fg="#1b1f3b",
            relief="flat",
            activebackground="#e6a100",
            command=self.open_electrolysis_window
        )
        self.volt_btn.grid(row=0, column=2, padx=12, pady=8)

        # Small stickers row — playful emoji encouragement
        stickers_frame = tk.Frame(content, bg="#88AAFF")
        stickers_frame.pack(pady=(0, 10))
        tk.Label(stickers_frame, text="🧫 Ready?", font=("Segoe UI Emoji", 12, "bold"),
                  bg="#88AAFF", fg="#221177").grid(row=0, column=0, padx=30)
        tk.Label(stickers_frame, text="⚗️ Mix!", font=("Segoe UI Emoji", 12, "bold"),
                  bg="#88AAFF", fg="#221177").grid(row=0, column=1, padx=30)
        tk.Label(stickers_frame, text="📘 Learn!", font=("Segoe UI Emoji", 12, "bold"),
                  bg="#88AAFF", fg="#221177").grid(row=0, column=2, padx=30)

        # Sound toggle, with a matching speaker emoji
        sound_frame = tk.Frame(content, bg="#88AAFF")
        sound_frame.pack(pady=(0, 12))
        tk.Label(sound_frame, text="🔊", font=("Segoe UI Emoji", 12), bg="#88AAFF").grid(row=0, column=0, padx=(0, 4))
        self.sound_var = tk.BooleanVar(value=self.sounds_enabled)
        cb = ttk.Checkbutton(sound_frame, text="Enable sounds", variable=self.sound_var, command=self.toggle_sounds)
        cb.grid(row=0, column=1, padx=6)

        # Leaderboard frame displayed under menu (pink/maroon theme, same
        # palette as the original "Hall of Lab Legends" panel)
        lb_outer = tk.LabelFrame(
            content,
            text="🏆 Hall of Lab Legends! (Top 10) 🏆",
            font=self.header_font,
            padx=10,
            pady=10,
            bg="#f6cdd2",
            fg="#800000",  # maroon heading
            bd=2,
            relief="ridge"
        )

        lb_outer.pack(padx=24, pady=(4, 16), fill="both")

        # Bigger, columnar leaderboard display (Rank / Name / Score / Bonus / Date)
        lb_style = ttk.Style()
        lb_style.configure("Leaderboard.Treeview", font=self.header_font, rowheight=34,
                            background="#f6cdd2", fieldbackground="#f6cdd2", foreground="#800000")
        lb_style.configure("Leaderboard.Treeview.Heading", font=self.btn_font)

        lb_columns = ("rank", "name", "score", "bonus", "date")
        self.lb_tree = ttk.Treeview(lb_outer, columns=lb_columns, show="headings",
                                     height=5, style="Leaderboard.Treeview")
        self.lb_tree.heading("rank", text="#")
        self.lb_tree.heading("name", text="🙋 Name")
        self.lb_tree.heading("score", text="🎯 Score /10")
        self.lb_tree.heading("bonus", text="⚡ Bonus")
        self.lb_tree.heading("date", text="🗓️ Date")
        self.lb_tree.column("rank", width=40, anchor="center")
        self.lb_tree.column("name", width=240, anchor="w")
        self.lb_tree.column("score", width=110, anchor="center")
        self.lb_tree.column("bonus", width=110, anchor="center")
        self.lb_tree.column("date", width=180, anchor="center")
        self.lb_tree.pack(side="left", fill="both", expand=True, padx=(4, 0))
        lb_scroll = ttk.Scrollbar(lb_outer, orient="vertical", command=self.lb_tree.yview)
        lb_scroll.pack(side="right", fill="y")
        self.lb_tree.config(yscrollcommand=lb_scroll.set)

        # Footer buttons — recoloured using the same palette as the tools
        # above (amber, pink/maroon, blue) so the whole window reads as one
        # consistent colour scheme, each with a matching emoji.
        footer = tk.Frame(content, bg="#88AAFF")
        footer.pack(pady=(4, 20))
        tk.Button(footer, text="🏅 View Top Scores", font=self.btn_font, bg="#ffd966", fg="#CC7722",
                  relief="flat", activebackground="#f4c430", padx=14, pady=6,
                  command=self.show_top_scores).grid(row=0, column=0, padx=10)
        tk.Button(footer, text="🔄 Reset Leaderboard", font=self.btn_font, bg="#f6cdd2", fg="#800000",
                  relief="flat", activebackground="#eab5bc", padx=14, pady=6,
                  command=self.reset_leaderboard).grid(row=0, column=1, padx=10)
        tk.Button(footer, text="🚪 Quit", font=self.btn_font, bg="#6fa8dc", fg="#0A2472",
                  relief="flat", activebackground="#5590c8", padx=14, pady=6,
                  command=lambda: (play_sound("window_close"), self.root.quit())).grid(row=0, column=2, padx=10)
        tk.Button(footer, text="⛶ Fullscreen (F11)", font=self.btn_font, bg="#c3b1e1", fg="#2e1065",
                  relief="flat", padx=14, pady=6,
                  command=self.toggle_fs).grid(row=0, column=3, padx=10)

    def toggle_sounds(self):
        global SOUNDS_ENABLED
        SOUNDS_ENABLED = bool(self.sound_var.get())
        self.sounds_enabled = SOUNDS_ENABLED

    def refresh_leaderboard_display(self):
        lb = load_leaderboard()
        for row in self.lb_tree.get_children():
            self.lb_tree.delete(row)
        # Show top 10, each with its own Score /10 and Bonus columns
        for i, e in enumerate(lb[:10], start=1):
            name = e.get("name", "Anon")
            score = e.get("score", 0)
            bonus = e.get("bonus", 0)
            t = e.get("time", "")
            try:
                tstr = datetime.fromisoformat(t).strftime("%Y-%m-%d %H:%M")
            except Exception:
                tstr = str(t)
            self.lb_tree.insert("", tk.END, values=(i, name, f"{score}/10", f"+{bonus}", tstr))

    def reset_leaderboard(self, parent=None):
        """Archive the best scores to the Top Scores hall of fame, then clear the leaderboard."""
        parent = parent or self.root
        lb = load_leaderboard()
        if not lb:
            messagebox.showinfo("Leaderboard Empty",
                                "There are no scores on the leaderboard to reset.", parent=parent)
            return
        play_sound("reset_open")
        res = messagebox.askyesno(
            "Reset Leaderboard?",
            "This will save the best scorers into the Top Scores hall of fame, "
            "then remove all names from the current leaderboard. Continue?",
            parent=parent)
        if not res:
            play_sound("confirm_no")
            return
        play_sound("confirm_yes")
        archive_top_scores_and_clear()
        self.refresh_leaderboard_display()
        messagebox.showinfo("Leaderboard Reset",
                            "🧹 Leaderboard cleared! Top scorers have been saved to the Top Scores hall of fame.",
                            parent=parent)

     # -------------------------
    # QUIZ: window shell
    # -------------------------

    def open_quiz_window(self):
        play_sound("quiz_open")
        c = QUIZ_UI
        self.timer_job = None
        self._locked = False
        self._locked_at = 0.0
        self.player_name_var = tk.StringVar(value="Student")
        self.topic_var = tk.StringVar(value=QUIZ_TOPIC_NAMES[0])

        self.quiz_win = tk.Toplevel(self.root)
        enable_fullscreen(self.quiz_win)
        self.quiz_win.title("Quiz Time! — Can You Handle the Reactions?")
        self.quiz_win.geometry("940x780")
        self.quiz_win.minsize(820, 680)
        self.quiz_win.transient(self.root)
        self.quiz_win.configure(bg=c["bg"])
        self.quiz_win.protocol("WM_DELETE_WINDOW", self._close_quiz)

        self.quiz_body = tk.Frame(self.quiz_win, bg=c["bg"], padx=16, pady=12)
        self.quiz_body.pack(fill="both", expand=True)

        footer = tk.Frame(self.quiz_win, bg=c["bg"])
        footer.pack(fill="x", pady=(0, 8))
        make_button(footer, "🔄 Reset Hall of Lab Legends",
                    lambda: self.reset_leaderboard(parent=self.quiz_win),
                    c["accent"], font=("Helvetica", 11, "bold")).pack()

        self._build_quiz_setup()

    def _cancel_quiz_timer(self):
        if getattr(self, "timer_job", None):
            try:
                self.quiz_win.after_cancel(self.timer_job)
            except Exception:
                pass
        self.timer_job = None

    def _quiz_clear(self):
        self._cancel_quiz_timer()
        for w in self.quiz_body.winfo_children():
            w.destroy()

    def _close_quiz(self):
        play_sound("window_close")
        self._cancel_quiz_timer()
        try:
            self.quiz_win.destroy()
        except Exception:
            pass

        # -------------------------
        # QUIZ: setup screen
        # -------------------------

    def _build_quiz_setup(self):
        c = QUIZ_UI
        self._quiz_clear()
        self.quiz_win.unbind("<Key>")

        tk.Label(self.quiz_body, text="⚗️ Reaction Quiz",
                 font=("Helvetica", 26, "bold"), bg=c["bg"], fg=c["ink"]).pack(pady=(12, 2))
        tk.Label(self.quiz_body, text="10 questions · beat the clock · earn speed bonuses",
                 font=("Helvetica", 12), bg=c["bg"], fg=c["muted"]).pack(pady=(0, 16))

        card = tk.Frame(self.quiz_body, bg=c["card"], highlightthickness=1,
                        highlightbackground=c["border"], padx=32, pady=24)
        card.pack(pady=6)

        tk.Label(card, text="Your name", font=("Helvetica", 12, "bold"),
                 bg=c["card"], fg=c["ink"]).grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(card, textvariable=self.player_name_var, width=36,
                          font=("Helvetica", 12))
        entry.grid(row=1, column=0, sticky="ew", pady=(2, 14))

        tk.Label(card, text="Choose chapter", font=("Helvetica", 12, "bold"),
                 bg=c["card"], fg=c["ink"]).grid(row=2, column=0, sticky="w")
        ttk.Combobox(card, textvariable=self.topic_var, values=QUIZ_TOPIC_NAMES,
                     state="readonly", width=34, font=("Helvetica", 12)
                     ).grid(row=3, column=0, sticky="ew", pady=(2, 14))

        rules = (f"⏱ {int(self.time_total)} s per question\n"
                 f"⚡ Answer within {int(self.bonus_threshold)} s for a +2 bonus\n"
                 f"⌨ Keys: A–D (or 1–4) to choose, Enter to submit")
        tk.Label(card, text=rules, justify="left", font=("Helvetica", 11),
                 bg=c["card"], fg=c["muted"]).grid(row=4, column=0, sticky="w", pady=(0, 10))

        self.quiz_msg = tk.Label(card, text="", font=("Helvetica", 11, "bold"),
                                 bg=c["card"], fg=c["bad"])
        self.quiz_msg.grid(row=5, column=0, sticky="w")

        make_button(card, "▶  Start Quiz", self.confirm_quiz_start, c["primary"],
                    font=self.btn_font, width=24
                    ).grid(row=6, column=0, pady=(8, 0))

        entry.bind("<Return>", lambda e: self.confirm_quiz_start())
        entry.focus_set()
        entry.select_range(0, "end")

    def confirm_quiz_start(self):
        name = self.player_name_var.get().strip()
        if not name:
            play_sound("wrong")
            self.quiz_msg.config(text="👆 Please enter your name first.")
            return
        play_sound("start")
        self.start_quiz_session()

        # -------------------------
        # QUIZ: question screen
        # -------------------------

    def start_quiz_session(self):
        c = QUIZ_UI
        topic_name = self.topic_var.get() if getattr(self, "topic_var", None) else QUIZ_TOPIC_NAMES[0]
        pool = QUIZ_TOPIC_POOLS.get(topic_name, MCQ_POOL)
        if len(pool) < 10:
            messagebox.showerror("Error", "Not enough questions in the pool.")
            return

        self.quiz_questions = random.sample(pool, 10)
        self.current_q = 0
        self.score = 0
        self.bonus_points = 0
        self.results = [None] * len(self.quiz_questions)  # "good" / "bad" / "skip"
        self.quiz_question_start_time = time.time()
        self._locked = False

        self._quiz_clear()
        body = self.quiz_body

        # --- top bar: question counter + score chip
        top = tk.Frame(body, bg=c["bg"])
        top.pack(fill="x")
        self.q_counter = tk.Label(top, text="", font=self.header_font, bg=c["bg"], fg=c["ink"])
        self.q_counter.pack(side="left")
        self.score_label = tk.Label(top, text="⭐ Score: 0", font=self.header_font,
                                    bg=c["chip"], fg=c["ink"], padx=12, pady=4)
        self.score_label.pack(side="right")

        # --- progress dots
        dots = tk.Frame(body, bg=c["bg"])
        dots.pack(pady=(8, 4))
        self.dot_labels = []
        for _ in self.quiz_questions:
            d = tk.Label(dots, text="●", font=("Helvetica", 14), bg=c["bg"], fg=c["dot_idle"])
            d.pack(side="left", padx=3)
            self.dot_labels.append(d)

        # --- timer
        pb = tk.Frame(body, bg=c["bg"])
        pb.pack(fill="x", pady=(6, 6))
        tk.Label(pb, text="Time left:", bg=c["bg"], fg=c["ink"]).pack(side="left")
        self.time_label = tk.Label(pb, text="", bg=c["bg"], fg=c["ink"],
                                   font=self.header_font, width=5)
        self.time_label.pack(side="left", padx=(6, 10))
        self.pb_canvas = tk.Canvas(pb, height=22, bg="#f1f1f1", highlightthickness=1,
                                   highlightbackground="#cfcfcf")
        self.pb_canvas.pack(side="left", fill="x", expand=True)
        self.pb_bg = self.pb_canvas.create_rectangle(0, 0, 0, 22, fill="#eeeeee", outline="")
        self.pb_fill = self.pb_canvas.create_rectangle(0, 0, 0, 22, fill="#00b050", outline="")

        # --- question card (text re-wraps when the window is resized)
        qcard = tk.Frame(body, bg=c["card"], highlightthickness=1,
                         highlightbackground=c["border"], padx=18, pady=16)
        qcard.pack(fill="x", pady=(10, 8))
        self.q_label = tk.Label(qcard, text="", font=self.large_mono, bg=c["card"],
                                fg=c["ink"], wraplength=800, justify="left", anchor="w")
        self.q_label.pack(fill="x")
        qcard.bind("<Configure>",
                   lambda e: self.q_label.config(wraplength=max(200, e.width - 40)))

        # --- options
        opts = tk.Frame(body, bg=c["bg"])
        opts.pack(fill="x", pady=(4, 2))
        self.option_buttons = []
        self.option_selected = None
        self.option_selected_idx = None
        for i in range(4):
            btn = tk.Button(
                opts, text="", font=("Helvetica", 14), anchor="w", justify="left",
                relief="flat", bd=0, highlightthickness=2,
                highlightbackground=c["border"], highlightcolor=c["primary"],
                fg=c["ink"], disabledforeground=c["ink"], padx=16, pady=10,
                cursor="hand2", takefocus=0, wraplength=760,
                command=lambda idx=i: self.select_option(idx))
            btn.pack(fill="x", padx=30, pady=5)
            add_hover(btn, c["option"], c["option_hover"])
            self.option_buttons.append(btn)

        # --- feedback line (replaces the old popup boxes)
        self.feedback_label = tk.Label(body, text="", font=("Helvetica", 13, "bold"),
                                       bg=c["bg"], fg=c["ink"], wraplength=800)
        self.feedback_label.pack(pady=(8, 4))

        # --- buttons: either Submit/Reveal OR Next
        self.btn_row = tk.Frame(body, bg=c["bg"])
        self.btn_row.pack(pady=(4, 8))
        self.answer_btns = tk.Frame(self.btn_row, bg=c["bg"])
        make_button(self.answer_btns, "✔ Submit Answer", self.submit_answer, c["primary"],
                    font=self.btn_font, width=18).pack(side="left", padx=8)
        make_button(self.answer_btns, "💡 Reveal (no score)", self.reveal_answer, c["blue"],
                    font=self.btn_font, width=20).pack(side="left", padx=8)
        self.next_btn = make_button(self.btn_row, "Next ➜", self._next_question, c["accent"],
                                    font=self.btn_font, width=18)

        self.quiz_win.bind("<Key>", self._quiz_key)
        self.quiz_win.focus_set()
        self.show_question()

    def _refresh_dots(self):
        c = QUIZ_UI
        colors = {"good": c["good"], "bad": c["bad"], "skip": "#999999"}
        for i, d in enumerate(self.dot_labels):
            r = self.results[i]
            if r:
                d.config(fg=colors[r])
            elif i == self.current_q:
                d.config(fg=c["blue"])
            else:
                d.config(fg=c["dot_idle"])

        # --- keyboard shortcuts

    def _quiz_key(self, event):
        k = event.keysym.lower()
        if self._locked:
            if k in ("return", "space", "right", "n") and time.time() - self._locked_at > 0.4:
                self._next_question()
            return
        if k in ("a", "b", "c", "d"):
            self.select_option(ord(k) - 97)
        elif k in ("1", "2", "3", "4"):
            self.select_option(int(k) - 1)
        elif k == "return":
            self.submit_answer()

        # --- option selection with fade

    def select_option(self, idx):
        if self._locked:
            return
        c = QUIZ_UI
        play_sound("click")
        if self.option_selected_idx is not None and self.option_selected_idx != idx:
            prev = self.option_buttons[self.option_selected_idx]
            self._fade_to_color(prev, c["option"])
            prev.config(highlightbackground=c["border"])
        self.option_selected_idx = idx
        self.option_selected = chr(65 + idx)
        btn = self.option_buttons[idx]
        self._fade_to_color(btn, c["option_sel"])
        btn.config(highlightbackground=c["primary"])
        self.feedback_label.config(text="")

    def _fade_to_color(self, widget, target_color, steps=5, delay=30):
        """Gradually change a button's background to target_color."""
        widget._base = target_color  # so hover/leave returns to the new colour
        try:
            start = [v // 256 for v in widget.winfo_rgb(widget.cget("bg"))]
        except tk.TclError:
            return
        end = [int(target_color[i:i + 2], 16) for i in (1, 3, 5)]

        def step(n=0):
            try:
                if n >= steps:
                    widget.config(bg=target_color)
                    return
                col = [start[i] + (end[i] - start[i]) * n / steps for i in range(3)]
                widget.config(bg="#%02x%02x%02x" % tuple(int(v) for v in col))
                widget.after(delay, step, n + 1)
            except tk.TclError:
                pass  # widget was destroyed mid-fade

        step()

        # --- show a question

    def show_question(self):
        c = QUIZ_UI
        self._cancel_quiz_timer()
        if self.current_q >= len(self.quiz_questions):
            self.end_quiz()
            return

        q, choices, correct = self.quiz_questions[self.current_q]
        self._locked = False
        self.option_selected = None
        self.option_selected_idx = None

        self.q_counter.config(text=f"Question {self.current_q + 1} of {len(self.quiz_questions)}")
        self.q_label.config(text=q)
        self.feedback_label.config(text="")
        for i, btn in enumerate(self.option_buttons):
            btn.config(state="normal", text=f"{chr(65 + i)}.  {choices[i]}")
            paint(btn, c["option"], c["border"])

        self.next_btn.pack_forget()
        self.answer_btns.pack()
        self._refresh_dots()

        self.time_left = float(self.time_total)
        self.quiz_question_start_time = time.time()
        self._update_quiz_progress()

        # --- timer

    def _update_quiz_progress(self):
        elapsed = time.time() - self.quiz_question_start_time
        self.time_left = max(0.0, self.time_total - elapsed)
        self.time_label.config(text=f"{int(math.ceil(self.time_left))} s")

        frac = max(0.0, min(1.0, self.time_left / self.time_total))
        width = max(self.pb_canvas.winfo_width(), 1)
        self.pb_canvas.coords(self.pb_bg, (0, 0, width, 22))
        self.pb_canvas.coords(self.pb_fill, (0, 0, int(width * frac), 22))
        if frac > 0.6:
            color = "#00b050"
        elif frac > 0.3:
            color = "#ffd700"
        elif frac > 0.15:
            color = "#ff8c00"
        else:
            color = "#d9534f"
        self.pb_canvas.itemconfig(self.pb_fill, fill=color)

        if self.time_left <= 0:
            self._on_time_up()
        else:
            self.timer_job = self.quiz_win.after(100, self._update_quiz_progress)

        # --- shared helpers for the "answered" state

    def _lock_options(self):
        self._cancel_quiz_timer()
        self._locked = True
        for btn in self.option_buttons:
            btn.config(state="disabled")

    def _after_answer(self, text, color):
        self.feedback_label.config(text=text, fg=color)
        self.answer_btns.pack_forget()
        last = self.current_q == len(self.quiz_questions) - 1
        self.next_btn.config(text="Finish 🏁" if last else "Next ➜   (Enter)")
        self.next_btn.pack()
        self._locked_at = time.time()
        self._refresh_dots()

    def _next_question(self):
        self.current_q += 1
        self.show_question()

    def _on_time_up(self):
        c = QUIZ_UI
        play_sound("time_up")
        correct = self.quiz_questions[self.current_q][2]
        self._lock_options()
        paint(self.option_buttons[ord(correct) - 65], c["good_bg"], c["good"])
        self.results[self.current_q] = "bad"
        self._after_answer(f"⏰ Time's up! The answer was {correct}. Marked incorrect.", c["warn"])

        # --- submit

    def submit_answer(self):
        if self._locked:
            return
        c = QUIZ_UI
        if not self.option_selected:
            play_sound("wrong")
            self.feedback_label.config(text="👆 Pick an answer first (click it, or press A–D).",
                                       fg=c["warn"])
            return

        correct = self.quiz_questions[self.current_q][2]
        self._lock_options()
        sel_btn = self.option_buttons[self.option_selected_idx]
        correct_btn = self.option_buttons[ord(correct) - 65]

        if self.option_selected == correct:
            self.score += 1
            self.results[self.current_q] = "good"
            paint(sel_btn, c["good_bg"], c["good"])
            elapsed = time.time() - self.quiz_question_start_time
            if elapsed <= 5.0:
                self.bonus_points += 2
                play_sound("bonus")
                msg = "⚡ Correct — lightning fast!  +1 point and +2 bonus 🎉"
            else:
                play_sound("correct")
                msg = "✅ Correct!  +1 point."
            self._after_answer(msg, c["good"])
        else:
            play_sound("wrong")
            self.results[self.current_q] = "bad"
            paint(sel_btn, c["bad_bg"], c["bad"])
            paint(correct_btn, c["good_bg"], c["good"])
            self._after_answer(f"❌ Not quite. The correct answer is {correct}.", c["bad"])

        self.score_label.config(text=f"⭐ Score: {self.score}")

        # --- reveal (not scored)

    def reveal_answer(self):
        if self._locked:
            return
        c = QUIZ_UI
        correct = self.quiz_questions[self.current_q][2]
        play_sound("wrong")
        self._lock_options()
        paint(self.option_buttons[ord(correct) - 65], c["good_bg"], c["good"])
        self.results[self.current_q] = "skip"
        self._after_answer(f"💡 The answer is {correct}. This question isn't scored.", c["blue"])

        # -------------------------
        # QUIZ: results screen
        # -------------------------

    def end_quiz(self):
        c = QUIZ_UI
        self._cancel_quiz_timer()
        self.quiz_win.unbind("<Key>")

        total = len(self.quiz_questions)
        pct = self.score / total
        if pct == 1:
            emoji, line = "🏆", "Perfect! Flawless chemistry!"
        elif pct >= 0.7:
            emoji, line = "🎉", "Great work — you know your reactions!"
        elif pct >= 0.4:
            emoji, line = "💪", "Good effort. Review and try again!"
        else:
            emoji, line = "🌱", "Every chemist starts somewhere. Try again!"

        play_sound("end")
        name = self.player_name_var.get().strip() or "Student"
        add_score_to_leaderboard(name, self.score, bonus=self.bonus_points)
        self.refresh_leaderboard_display()

        self._quiz_clear()
        tk.Label(self.quiz_body, text=emoji, font=("Helvetica", 64), bg=c["bg"]).pack(pady=(30, 0))
        tk.Label(self.quiz_body, text="Quiz complete!", font=("Helvetica", 26, "bold"),
                 bg=c["bg"], fg=c["ink"]).pack()
        tk.Label(self.quiz_body, text=f"{name}, you scored {self.score}/{total}",
                 font=("Helvetica", 18), bg=c["bg"], fg=c["ink"]).pack(pady=(6, 0))
        if self.bonus_points > 0:
            tk.Label(self.quiz_body,
                     text=f"⚡ Speed bonus: +{self.bonus_points} (for answering quickly!)",
                     font=("Helvetica", 14), bg=c["bg"], fg=c["warn"]).pack(pady=(4, 0))
        tk.Label(self.quiz_body, text=line, font=("Helvetica", 14), bg=c["bg"],
                 fg=c["muted"]).pack(pady=(10, 20))

        row = tk.Frame(self.quiz_body, bg=c["bg"])
        row.pack()
        make_button(row, "🔁 Play again", self._build_quiz_setup, c["primary"],
                    font=self.btn_font, width=16).pack(side="left", padx=8)
        make_button(row, "Close", self._close_quiz, c["accent"],
                    font=self.btn_font, width=12).pack(side="left", padx=8)


    # -------------------------
    # Equation Solver popup
    # -------------------------
    def open_solver_window(self):
        play_sound("solver_open")
        c = SOLVER_UI

        w = tk.Toplevel(self.root)
        enable_fullscreen(w)
        w.title("Equation Solver — Step-by-step")
        w.geometry("1100x680")
        w.minsize(900, 560)
        w.configure(bg=c["bg"])

        state = {"steps": [], "shown": 0, "filtered": [], "size": 11}
        step_mode = tk.BooleanVar(value=True)
        search_var = tk.StringVar()

        outer = tk.Frame(w, bg=c["bg"], padx=14, pady=12)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="✨ Step-by-step Equation Solver ✨", font=self.header_font,
                 bg=c["bg"], fg=c["ink"]).pack(pady=(0, 2))
        tk.Label(outer, text="Pick a reaction, then press Next step (or the → key) to watch it get balanced.",
                 font=("Segoe UI", 11), bg=c["bg"], fg=c["muted"]).pack(pady=(0, 10))

        main = tk.Frame(outer, bg=c["bg"])
        main.pack(fill="both", expand=True)

        # ---------------- left: search + list ----------------
        left = tk.Frame(main, bg=c["bg"])
        left.pack(side="left", fill="y", padx=(0, 12))

        search_row = tk.Frame(left, bg=c["bg"])
        search_row.pack(fill="x", pady=(0, 4))
        tk.Label(search_row, text="🔍", bg=c["bg"]).pack(side="left")
        search_entry = ttk.Entry(search_row, textvariable=search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))

        count_label = tk.Label(left, text="", anchor="w", bg=c["bg"], fg=c["muted"],
                               font=("Segoe UI", 9))
        count_label.pack(fill="x", pady=(0, 4))

        list_frame = tk.Frame(left, bg=c["bg"])
        list_frame.pack(fill="both", expand=True)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        listbox = tk.Listbox(list_frame, font=self.list_font, width=34, activestyle="none",
                             selectbackground=c["accent"], selectforeground="white",
                             exportselection=False, relief="flat", highlightthickness=1,
                             highlightbackground=c["border"])
        listbox.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        vs.grid(row=0, column=1, sticky="ns")
        hs = ttk.Scrollbar(list_frame, orient="horizontal", command=listbox.xview)
        hs.grid(row=1, column=0, sticky="ew")
        listbox.config(yscrollcommand=vs.set, xscrollcommand=hs.set)

        # ---------------- right: equation + controls + steps ----------------
        right = tk.Frame(main, bg=c["panel"])
        right.pack(side="left", fill="both", expand=True)

        eq_card = tk.Frame(right, bg=c["card"], highlightthickness=1,
                           highlightbackground=c["border"], padx=14, pady=10)
        eq_card.pack(fill="x", padx=10, pady=(10, 6))
        eq_label = tk.Label(eq_card, text="", font=("Segoe UI", 16, "bold"), bg=c["card"],
                            fg=c["ink"], wraplength=560, justify="center")
        eq_label.pack(fill="x")
        eq_card.bind("<Configure>", lambda e: eq_label.config(wraplength=max(200, e.width - 30)))

        status_label = tk.Label(right, text="", font=("Segoe UI", 11, "bold"),
                                bg=c["panel"], fg=c["muted"])
        status_label.pack(pady=(2, 4))

        controls = tk.Frame(right, bg=c["panel"])
        controls.pack(fill="x", padx=10, pady=(0, 6))
        controls2 = tk.Frame(right, bg=c["panel"])
        controls2.pack(fill="x", padx=10, pady=(0, 6))

        text_frame = tk.Frame(right, bg=c["panel"])
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        steps_scroll = ttk.Scrollbar(text_frame, orient="vertical")
        steps_scroll.pack(side="right", fill="y")
        steps_text = tk.Text(text_frame, font=("Courier New", state["size"]), wrap="word",
                             bg=c["card"], fg=c["ink"], relief="flat", padx=10, pady=8,
                             yscrollcommand=steps_scroll.set, state="disabled")
        steps_text.pack(side="left", fill="both", expand=True)
        steps_scroll.config(command=steps_text.yview)

        # ---------------- logic ----------------
        def show_message(msg):
            steps_text.config(state="normal")
            steps_text.delete("1.0", tk.END)
            steps_text.insert(tk.END, msg)
            steps_text.config(state="disabled")

        def update_status(flash=None):
            n, shown = len(state["steps"]), state["shown"]
            if flash:
                status_label.config(text=flash, fg=c["good"])
            elif n == 0:
                status_label.config(text="Select a reaction on the left", fg=c["muted"])
            elif shown >= n:
                status_label.config(text=f"✅ Balanced!  ({n} of {n} steps)", fg=c["good"])
            else:
                status_label.config(text=f"Step {shown} of {n}", fg=c["ink"])
            n_ok = n > 0
            back_btn.config(state="normal" if n_ok and shown > 1 else "disabled")
            next_btn.config(state="normal" if n_ok and shown < n else "disabled")
            all_btn.config(state="normal" if n_ok and shown < n else "disabled")
            reset_btn.config(state="normal" if n_ok else "disabled")
            copy_btn.config(state="normal" if n_ok else "disabled")

        def render():
            steps, shown = state["steps"], state["shown"]
            steps_text.config(state="normal")
            steps_text.delete("1.0", tk.END)
            highlight_latest = step_mode.get() and 0 < shown < len(steps)
            for i, s in enumerate(steps[:shown]):
                prefix = "✨ " if i == 0 else "   "
                steps_text.insert(tk.END, f"{prefix}{s}\n")
                tag = f"line{i}"
                if highlight_latest and i == shown - 1:
                    bg = c["latest"]
                else:
                    bg = c["row_a"] if i % 2 == 0 else c["row_b"]
                steps_text.tag_add(tag, f"{i + 1}.0", f"{i + 1}.end")
                steps_text.tag_config(tag, background=bg)
            steps_text.see(tk.END)
            steps_text.config(state="disabled")
            update_status()

        def next_step():
            if state["shown"] < len(state["steps"]):
                state["shown"] += 1
                render()
                play_sound("success" if state["shown"] == len(state["steps"]) else "click")

        def prev_step():
            if state["shown"] > 1:
                state["shown"] -= 1
                play_sound("click")
                render()

        def show_all():
            if state["steps"]:
                state["shown"] = len(state["steps"])
                render()
                play_sound("success")

        def restart(quiet=False):
            if not state["steps"]:
                return
            state["shown"] = 1 if step_mode.get() else len(state["steps"])
            if not quiet:
                play_sound("click")
            render()

        def copy_steps():
            if not state["steps"]:
                return
            w.clipboard_clear()
            w.clipboard_append("\n".join(state["steps"]))
            play_sound("click")
            update_status(flash="📋 Copied to clipboard!")
            w.after(1400, update_status)

        def change_font(delta):
            state["size"] = max(8, min(22, state["size"] + delta))
            steps_text.config(font=("Courier New", state["size"]))

        def on_select(event=None, quiet=False):
            sel = listbox.curselection()
            if not sel or sel[0] >= len(state["filtered"]):
                return
            idx = state["filtered"][sel[0]]
            reactants, products = SOLVER_OPTIONS[idx]
            if not quiet:
                play_sound("select")

            eq_label.config(text=f"{pretty_formula(' + '.join(reactants))}   →   "
                                 f"{pretty_formula(' + '.join(products))}")
            res, steps = balance_equation(reactants, products)
            if res is None:
                state["steps"], state["shown"] = [], 0
                show_message("⚠️ Cannot balance this equation")
                update_status()
                play_sound("wrong")
                return

            state["steps"] = list(steps)
            state["shown"] = min(1, len(steps)) if step_mode.get() else len(steps)
            render()
            if not quiet and state["shown"] == len(steps) and steps:
                play_sound("success")
            if not quiet:
                play_sound("solver_select")

        def populate(*_):
            q = search_var.get().strip().lower()
            listbox.delete(0, tk.END)
            state["filtered"] = []
            for i, (r, p) in enumerate(SOLVER_OPTIONS):
                left_s, right_s = " + ".join(r), " + ".join(p)
                if q and q not in f"{left_s} {right_s}".lower():
                    continue
                state["filtered"].append(i)
                listbox.insert(tk.END, f"{i + 1:2d}. {pretty_formula(left_s)} → {pretty_formula(right_s)}")
            count_label.config(text=f"{len(state['filtered'])} of {len(SOLVER_OPTIONS)} reactions")
            if state["filtered"]:
                listbox.selection_set(0)
                on_select(quiet=True)
            else:
                state["steps"], state["shown"] = [], 0
                eq_label.config(text="")
                show_message("No reactions match your search.")
                update_status()

        def random_pick():
            if not state["filtered"]:
                return
            pos = random.randrange(len(state["filtered"]))
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(pos)
            listbox.see(pos)
            play_sound("solver_random")
            on_select(quiet=True)

        # ---------------- buttons ----------------
        back_btn = make_button(controls, "◀ Back", prev_step, "#9fc5e8", font=self.btn_font)
        back_btn.pack(side="left", padx=(0, 6))
        next_btn = make_button(controls, "Next step ▶", next_step, "#6aa84f", font=self.btn_font)
        next_btn.pack(side="left", padx=6)
        all_btn = make_button(controls, "⏩ Show all", show_all, c["accent"], font=self.btn_font)
        all_btn.pack(side="left", padx=6)
        reset_btn = make_button(controls, "↺ Restart", restart, "#b4a7d6", font=self.btn_font)
        reset_btn.pack(side="left", padx=6)

        tk.Checkbutton(controls2, text="One step at a time", variable=step_mode,
                       command=lambda: restart(quiet=True), bg=c["panel"], fg=c["ink"],
                       activebackground=c["panel"], selectcolor=c["card"],
                       font=("Segoe UI", 10)).pack(side="left")
        make_button(controls2, "Close", lambda: (play_sound("window_close"), w.destroy()),
                    "#f6b26b", font=self.btn_font).pack(side="right")
        make_button(controls2, "A+", lambda: change_font(1), "#999999",
                    font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 6))
        make_button(controls2, "A−", lambda: change_font(-1), "#999999",
                    font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 4))
        copy_btn = make_button(controls2, "📋 Copy", copy_steps, "#76a5af", font=self.btn_font)
        copy_btn.pack(side="right", padx=(0, 10))

        random_btn = make_button(left, "🎲 Random reaction", random_pick, "#b4a7d6",
                                 font=self.btn_font)
        random_btn.pack(fill="x", pady=(8, 0))

        # ---------------- bindings ----------------
        def guard(fn):
            def handler(event):
                if w.focus_get() is search_entry:
                    return  # let the search box keep its own arrow/space keys
                fn()

            return handler

        w.bind("<Right>", guard(next_step))
        w.bind("<space>", guard(next_step))
        w.bind("<Left>", guard(prev_step))
        listbox.bind("<<ListboxSelect>>", on_select)

        populate()
        search_var.trace_add("write", populate)
        listbox.focus_set()


    # ----------------------------
    # Gas Reaction Window
    # -------------------------
    # Fizz Factory — virtual gas lab with pictorial reactions
    # -------------------------
    def open_gas_window(self):
        old = getattr(self, "gas_win", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.lift()
                    return
            except tk.TclError:
                pass

        play_sound("gas_open")
        bg, ink = "#7df3e1", "#064e46"
        w = tk.Toplevel(self.root)
        enable_fullscreen(w)
        w.title("Fizz Factory — Virtual Reaction Lab")
        fit_window(w, 1000, 900, 960, 500)
        enable_fullscreen(w)
        w.configure(bg=bg)
        self.gas_win = w
        self.gas_order = []
        self.lab = {"running": True, "job": None, "mode": "idle", "t": 0.0, "t0": 0.0,
                    "tick": 0.0, "a": None, "b": None, "kind": "none", "rx": None,
                    "parts": [], "na": 0, "nb": 0}

        def close_gas():
            self.lab["running"] = False
            if self.lab["job"]:
                try:
                    self.lab_canvas.after_cancel(self.lab["job"])
                except Exception:
                    pass
            play_sound("window_close")
            w.destroy()

        bottom = tk.Frame(w, bg=bg)
        bottom.pack(side="bottom", fill="x")
        ttk.Button(bottom, text="Close", command=close_gas).pack(pady=(0, 10))
        outer, frame = make_scrollable(w, bg)
        outer.pack(fill="both", expand=True)
        frame.config(padx=12, pady=8)
        self.gas_frame = frame

        tk.Label(frame, text="Pick two reactants, set the amounts, then run the experiment",
                 font=self.header_font, bg=bg, fg=ink).pack(pady=(2, 8))

        # ---- reactant chips (two rows) ----
        self.gas_species = list(GAS_STYLE.keys())
        self.gas_sel = {}
        self.gas_labels = {}
        chips = tk.Frame(frame, bg=bg)
        chips.pack(pady=(0, 6))
        for i, g in enumerate(self.gas_species):
            self.gas_sel[g] = tk.BooleanVar(value=False)
            lbl = tk.Label(chips, text=f"{pretty_formula(g)}\n{GAS_INFO[g][1]}",
                           font=("Segoe UI", 12, "bold"), bg="#eafbe7", fg=ink,
                           width=12, pady=4, relief="ridge", bd=2, cursor="hand2")
            lbl.grid(row=i // 6, column=i % 6, padx=6, pady=4)
            lbl.bind("<Button-1>", lambda e, gas=g: self._toggle_gas(gas))
            self.gas_labels[g] = lbl

        # ---- amount sliders ----
        amt_frame = tk.Frame(frame, bg=bg)
        amt_frame.pack(pady=(4, 6))
        self.amt1 = tk.DoubleVar(value=1.0)
        self.amt2 = tk.DoubleVar(value=1.0)
        lab_font = ("Segoe UI", 11, "bold")
        self.amt1_label = tk.Label(amt_frame, text="Reactant 1 amount (mol):", bg=bg, fg=ink, font=lab_font)
        self.amt1_label.grid(row=0, column=0, padx=6)
        self.amt2_label = tk.Label(amt_frame, text="Reactant 2 amount (mol):", bg=bg, fg=ink, font=lab_font)
        self.amt2_label.grid(row=0, column=2, padx=6)
        scale1 = ttk.Scale(amt_frame, from_=0.5, to=5, orient="horizontal", variable=self.amt1, length=200,
                           command=lambda v: self._gas_amount_changed(self.amt1, v))
        scale2 = ttk.Scale(amt_frame, from_=0.5, to=5, orient="horizontal", variable=self.amt2, length=200,
                           command=lambda v: self._gas_amount_changed(self.amt2, v))
        scale1.grid(row=0, column=1)
        scale2.grid(row=0, column=3)
        tk.Label(amt_frame, textvariable=self.amt1, bg=bg, fg=ink, font=lab_font).grid(row=1, column=1)
        tk.Label(amt_frame, textvariable=self.amt2, bg=bg, fg=ink, font=lab_font).grid(row=1, column=3)

        # ---- the lab bench ----
        self.lab_canvas = tk.Canvas(frame, width=920, height=340, bg="#e8fbff",
                                    highlightthickness=2, highlightbackground=ink)
        self.lab_canvas.pack(pady=(4, 8))

        btns = tk.Frame(frame, bg=bg)
        btns.pack(pady=(0, 6))
        make_button(btns, "Run Reaction", self.run_gas_reaction, "#2e9e5b",
                    font=self.btn_font).grid(row=0, column=0, padx=8)
        make_button(btns, "Reset Selection", self.reset_gas_selection, "#e0a800",
                    font=self.btn_font).grid(row=0, column=1, padx=8)

        # ---- lab notebook (with scrollbar) ----
        out_frame = tk.Frame(frame, bg=bg)
        out_frame.pack(fill="both", expand=True, pady=(4, 4))
        out_scroll = ttk.Scrollbar(out_frame, orient="vertical")
        out_scroll.pack(side="right", fill="y")
        self.gas_output = make_rich_text(out_frame, bg="#f2fffc", fg=ink, height=10,
                                         yscrollcommand=out_scroll.set)
        self.gas_output.pack(side="left", fill="both", expand=True)
        out_scroll.config(command=self.gas_output.yview)
        self.gas_output.tag_config("strong", font=("Segoe UI", 12, "bold"), foreground=ink,
                                   lmargin1=14, lmargin2=14, spacing1=5, spacing3=4)
        self._gas_show_intro()

        self._gas_set_idle()
        w.protocol("WM_DELETE_WINDOW", close_gas)
        self._gas_loop()

    # ---- selecting reactants ----
    def _toggle_gas(self, g):
        var = self.gas_sel[g]
        if var.get():
            var.set(False)
            self.gas_order.remove(g)
        else:
            if len(self.gas_order) >= 2:
                play_sound("wrong")      # only two reactants allowed
                return
            var.set(True)
            self.gas_order.append(g)
        play_sound("pop")
        for gas, lbl in self.gas_labels.items():
            lbl.config(bg=GAS_STYLE[gas][0] if self.gas_sel[gas].get() else "#eafbe7")
        self._gas_set_idle()

    def _gas_amount_changed(self, var, v):
        var.set(round(float(v) * 2) / 2)       # snap to 0.5 mol steps
        lab = self.lab
        if lab["mode"] == "run":
            if lab["t"] > 10.5:                 # experiment finished, so go back to setup
                self._gas_set_idle()
        else:
            na = max(2, round(self.amt1.get() * 4))
            nb = max(2, round(self.amt2.get() * 4))
            if (na, nb) != (lab["na"], lab["nb"]):
                self._gas_set_idle()

    def _gas_make_particles(self, na, nb):
        parts = []
        for side, n in (("a", na), ("b", nb)):
            for i in range(n):
                parts.append({
                    "side": side, "i": i, "consumed": False,
                    "jx": random.uniform(-45, 45), "jy": random.uniform(15, 130),
                    "ph": random.uniform(0, 6.28),
                    "delay": random.uniform(0, 1.0),
                    "react_at": 3.0 + random.uniform(0, 1.0),
                    "tx": random.uniform(425, 495), "ty": random.uniform(235, 285),
                })
        return parts

    def _gas_set_idle(self):
        lab = self.lab
        lab["a"] = self.gas_order[0] if len(self.gas_order) > 0 else None
        lab["b"] = self.gas_order[1] if len(self.gas_order) > 1 else None
        lab["mode"], lab["t"], lab["kind"] = "idle", 0.0, "none"
        lab["na"] = max(2, round(self.amt1.get() * 4))
        lab["nb"] = max(2, round(self.amt2.get() * 4))
        lab["parts"] = self._gas_make_particles(lab["na"] if lab["a"] else 0,
                                                lab["nb"] if lab["b"] else 0)
        self.amt1_label.config(text=f"{pretty_formula(lab['a'])} amount (mol):" if lab["a"]
                               else "Reactant 1 amount (mol):")
        self.amt2_label.config(text=f"{pretty_formula(lab['b'])} amount (mol):" if lab["b"]
                               else "Reactant 2 amount (mol):")

    def _gas_show_intro(self):
        box = self.gas_output
        box.config(state="normal")
        box.delete("1.0", tk.END)
        box.insert(tk.END, "Lab notebook\n", "title")
        box.insert(tk.END, "Your results will appear here after you run a reaction.\n", "sub")
        box.config(state="disabled")

    def reset_gas_selection(self):
        for g in self.gas_species:
            self.gas_sel[g].set(False)
            self.gas_labels[g].config(bg="#eafbe7")
        self.gas_order = []
        self._gas_set_idle()
        self._gas_show_intro()
        play_sound("click")

    # ---- running an experiment ----
    def run_gas_reaction(self):
        if len(self.gas_order) != 2:
            play_sound("wrong")
            messagebox.showwarning("Need 2 reactants", "Please select exactly two reactants first.",
                                   parent=self.gas_win)
            return
        a, b = self.gas_order
        amt1, amt2 = self.amt1.get(), self.amt2.get()
        rx = GAS_REACTIONS.get(frozenset((a, b)))
        lab = self.lab

        box = self.gas_output
        box.config(state="normal")
        box.delete("1.0", tk.END)
        box.insert(tk.END, "Experiment Result\n", "title")
        box.insert(tk.END, f"{amt1:g} mol {pretty_formula(a)}  +  {amt2:g} mol {pretty_formula(b)}\n", "sub")

        ua = ub = 0
        if rx:
            def parse(side):
                out = []
                for term in side.split(" + "):
                    m = re.match(r"\s*(\d*)\s*(.+?)(?:\((aq|s|l|g)\))?\s*$", term)
                    out.append((int(m.group(1) or 1), m.group(2), m.group(3) or ""))
                return out

            def state_word(name, st):
                if st == "s":
                    if name in ("Cu", "Ag"):
                        return "solid metal"
                    if name in ("ZnO", "MgO"):
                        return "solid oxide"
                    return "precipitate"
                return {"aq": "in solution", "l": "liquid", "g": "gas"}.get(st, "")

            lhs, rhs = rx["eq"].split("→")
            reac, prod = parse(lhs), parse(rhs)
            coef = {name: cf for cf, name, _ in reac}
            ca, cb = coef[a], coef[b]
            extent = min(amt1 / ca, amt2 / cb)
            used_a, used_b = extent * ca, extent * cb
            left_a, left_b = max(0.0, amt1 - used_a), max(0.0, amt2 - used_b)
            left_a = 0.0 if left_a < 1e-9 else left_a
            left_b = 0.0 if left_b < 1e-9 else left_b

            na = max(2, round(amt1 * 4))
            nb = max(2, round(amt2 * 4))
            ua = max(1, min(na, round(used_a * 4)))
            ub = max(1, min(nb, round(used_b * 4)))
            if left_a > 0:
                ua = min(ua, na - 1)
            if left_b > 0:
                ub = min(ub, nb - 1)

            info = RX_TYPES[rx["t"]]

            add_chip(box, "REACTION", "#1d4ed8")
            add_eq(box, pretty_formula(rx["eq"]), "#dff5e6", "#0b4a24")

            add_chip(box, "REACTION TYPE", "#be123c")
            box.insert(tk.END, info["title"] + "\n\n", "strong")

            add_chip(box, "BONDING: " + info["tag"].upper(), "#0f766e")
            box.insert(tk.END, info["text"] + "\n\n", "para")

            if rx["net"]:
                add_chip(box, "NET IONIC EQUATION", "#0369a1")
                add_eq(box, rx["net"], "#e0f2fe", "#075985")
                box.insert(tk.END, "\n")

            add_chip(box, "STOICHIOMETRY", "#7c3aed")
            if left_a == 0 and left_b == 0:
                add_line(box, "Both reactants are used up exactly (a perfect ratio).")
            else:
                lim, other, left = (a, b, left_b) if left_a == 0 else (b, a, left_a)
                add_line(box, f"Limiting reactant: {pretty_formula(lim)} (completely used up)")
                add_line(box, f"Leftover: {left:.3g} mol {pretty_formula(other)} (excess, unreacted)")
            for cf, n, st in prod:
                sw = state_word(n, st)
                add_line(box, f"Formed: {cf * extent:.3g} mol {pretty_formula(n)}" + (f"  ({sw})" if sw else ""))
            box.insert(tk.END, "\n")

            if rx.get("salt"):
                add_chip(box, "SALT & SOLUTION COLOUR", "#0e7490")
                add_line(box, f"{rx.get('salt_label', 'Salt')} formed: "
                              f"{pretty_formula(rx['salt'])}(aq)  \u2014  {rx['salt_word']}")
                add_line(box, "The coloured dots in the flask are the dissolved salt ions. "
                              "Colourless solutions are tinted on screen so each reaction looks different.")
                box.insert(tk.END, "\n")
            elif rx.get("dry"):
                add_chip(box, "SOLID PRODUCTS", "#0e7490")
                add_line(box, "No solution forms: the metal oxide and the copper are both solids left in the flask.")
                add_line(box, "The mixture has to be heated to start the reaction.")
                box.insert(tk.END, "\n")

            if rx.get("gas_type") == "h2":
                add_chip(box, "GAS TEST: HYDROGEN", "#be123c")
                add_line(box, "A lighted splint held at the mouth of the tube gives a squeaky pop: H\u2082 is present.")
                add_line(box,
                         "2H\u2082 + O\u2082 \u2192 2H\u2082O  (the hydrogen burns rapidly with oxygen in the air)")
                box.insert(tk.END, "\n")
            elif rx.get("gas_type") == "co2":
                add_chip(box, "GAS TEST: CARBON DIOXIDE", "#475569")
                add_line(box, "Bubbled through limewater, the gas turns it milky: "
                              "CO\u2082 + Ca(OH)\u2082 \u2192 CaCO\u2083 + H\u2082O  (insoluble calcium carbonate).")
                box.insert(tk.END, "\n")

            add_chip(box, "WHAT YOU SEE", "#b45309")
            add_line(box, rx["see"])
            box.insert(tk.END, "\n")
            lab["popped"] = False
            lab["t0"], lab["t"], lab["mode"] = time.time(), 0.0, "run"
            add_chip(box, "LAB NOTE", "#475569")
            add_line(box, rx["cond"])
            play_sound("start")
            self.root.after(2700, lambda: play_sound("reaction"))
        else:
            add_chip(box, "NO REACTION", "#b91c1c")
            add_line(box, f"{pretty_formula(a)} and {pretty_formula(b)} do not react.")
            box.insert(tk.END, "\n")
            add_chip(box, "WHY NOT?", "#475569")
            add_line(box, gas_no_reaction_reason(a, b))
            play_sound("start")
            self.root.after(2700, lambda: play_sound("wrong"))
        box.config(state="disabled")

        lab = self.lab
        lab["a"], lab["b"] = a, b
        lab["kind"] = "rx" if rx else "none"
        lab["rx"] = rx
        lab["parts"] = self._gas_make_particles(max(2, round(amt1 * 4)), max(2, round(amt2 * 4)))
        for part in lab["parts"]:
            part["consumed"] = part["i"] < (ua if part["side"] == "a" else ub)
        lab["t0"], lab["t"], lab["mode"] = time.time(), 0.0, "run"

    # ------ animation -------------------------------
    def _gas_loop(self):
        lab = self.lab
        if not lab["running"]:
            return
        lab["tick"] += 0.04
        if lab["mode"] == "run":
            lab["t"] = time.time() - lab["t0"]
        try:
            self._gas_draw()
        except tk.TclError:
            return                      # window was closed
        except Exception as e:          # never let one bad frame kill the animation
            print("gas draw error:", e, file=sys.stderr)
        lab["job"] = self.lab_canvas.after(40, self._gas_loop)

    def _gas_draw_dry(self, c, rx, t, p, tick):
        def xl(y):
            return 440 - 0.5 * (y - 180)

        def xr(y):
            return 480 + 0.5 * (y - 180)

        lvl = max(0.0, min(1.0, (t - 1.0) / 2.2))
        if lvl <= 0:
            return
        top = 298 - 22 * lvl
        heat = max(0.0, min(1.0, (t - 2.7) / 1.0))
        glow = heat * (1 - max(0.0, (p - 0.75) / 0.25))
        col = _mix("#3b3632", rx["liq"], p)
        col = _mix(col, "#ff9d3c", 0.75 * glow)
        c.create_polygon(xl(top) + 3, top, xr(top) - 3, top, xr(300) - 3, 298, xl(300) + 3, 298,
                         fill=col, outline="")
        for i in range(int(24 * p)):                       # copper specks
            f1 = ((i * 37) % 100) / 100.0
            f2 = ((i * 61) % 100) / 100.0
            y = top + 4 + f2 * (294 - top - 4)
            x = xl(y) + 8 + f1 * (xr(y) - xl(y) - 16)
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#c8693c", outline="#8a4524")
        if heat > 0:                                       # flames at the base
            fade = 1 - 0.8 * max(0.0, (p - 0.8) / 0.2)
            for i in range(7):
                fx = 405 + i * 18
                h = (16 + 10 * math.sin(tick * 14 + i * 1.9)) * heat * fade
                c.create_polygon(fx - 8, 300, fx, 300 - h - 8, fx + 8, 300,
                                 fill="#ff8c00", outline="", smooth=True)
                c.create_polygon(fx - 4, 300, fx, 300 - h * 0.6, fx + 4, 300,
                                 fill="#ffe14d", outline="", smooth=True)
        if 0.05 < p < 0.9:                                 # sparks
            for i in range(9):
                ph = (tick * 1.6 + i / 9.0) % 1.0
                f1 = ((i * 53) % 100) / 100.0
                x = 440 + (f1 - 0.5) * 70 + 12 * math.sin(tick * 5 + i)
                y = top - ph * 40
                r = 2.4 * (1 - ph) + 0.5
                c.create_oval(x - r, y - r, x + r, y + r, fill="#fff3a0", outline="#ff7a00")

    # ------------------------------------------------------------------
    # Product solution: coloured liquid, dissolved salt ions, surface fizz
    # ------------------------------------------------------------------
    def _gas_draw_product(self, c, rx, t, p, tick):
        def xl(y):
            return 440 - 0.5 * (y - 180)

        def xr(y):
            return 480 + 0.5 * (y - 180)

        if rx.get("dry"):
            self._gas_draw_dry(c, rx, t, p, tick)
            return
        # liquid rises as the solutions run in, and changes to the product colour
        lvl = max(0.0, min(1.0, (t - 1.0) / 2.2))
        if lvl <= 0:
            return
        top = 300 - 52 * lvl
        col = _mix(rx.get("frm") or "#eaf8ff", rx["liq"], min(1.0, p * 1.4))
        c.create_polygon(xl(top) + 3, top, xr(top) - 3, top, xr(300) - 3, 298, xl(300) + 3, 298,
                            fill=col, outline="")
        c.create_line(xl(top) + 3, top, xr(top) - 3, top, fill="#ffffff", width=2)

        # precipitate: cloudy at first, then it settles to the bottom
        if rx["ppt"] and p > 0:
            settle = max(0.0, (p - 0.35) / 0.65)
            for i in range(int(52 * min(1.0, p * 2))):
                f1 = ((i * 37) % 100) / 100.0
                f2 = ((i * 61) % 100) / 100.0
                y0 = top + 6 + f2 * (288 - top - 6)
                y = y0 + (293 - (i % 4) * 3 - y0) * settle
                x = xl(y) + 9 + f1 * (xr(y) - xl(y) - 18)
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=rx["ppt"],
                                outline=_mix(rx["ppt"], "#000000", 0.3))
            if settle > 0:
                yb = 298 - 9 * settle
                c.create_polygon(xl(yb) + 3, yb, xr(yb) - 3, yb, xr(298) - 3, 298, xl(298) + 3, 298,
                                    fill=rx["ppt"], outline="")

        # dissolved SALT: coloured ions drifting through the solution
        if p > 0 and rx.get("salt_col"):
            scol = rx["salt_col"]
            edge = _mix(scol, "#000000", 0.4)
            for i in range(int(34 * min(1.0, p * 1.6))):
                f1 = ((i * 29) % 100) / 100.0
                f2 = ((i * 71) % 100) / 100.0
                y = top + 8 + f2 * (286 - top - 8) + 3 * math.cos(tick * 2.2 + i)
                x = xl(y) + 10 + f1 * (xr(y) - xl(y) - 20) + 3 * math.sin(tick * 1.8 + i * 1.7)
                c.create_oval(x - 4, y - 4, x + 4, y + 4, fill=scol, outline=edge, width=1)

        # gas bubbles rising through the liquid, dying away as the reaction ends
        if rx["gas"] and p > 0:
            act = min(1.0, p * 4) * (1 - max(0.0, (p - 0.85) / 0.15))
            for i in range(int(18 * act)):
                ph = (tick * 0.9 + i / 18.0) % 1.0
                y = 294 - ph * (294 - top)
                f1 = ((i * 53) % 100) / 100.0
                x = xl(y) + 10 + f1 * (xr(y) - xl(y) - 20)
                r = 2.5 + (i % 3) * 1.5
                c.create_oval(x - r, y - r, x + r, y + r, fill="#f8fdff", outline="#6b93b3", width=1)

            # FIZZ on top: a foam of bubbles at the surface + spray above it
            for i in range(int(20 * act)):
                f1 = ((i * 47) % 100) / 100.0
                r = 3.2 + (i % 3) + 1.2 * math.sin(tick * 6 + i * 1.3)
                x = xl(top) + 9 + f1 * (xr(top) - xl(top) - 18)
                y = top - r * 0.55
                c.create_oval(x - r, y - r, x + r, y + r, fill="#ffffff", outline="#8fb2c8", width=1)
                c.create_oval(x - r * 0.5, y - r * 0.6, x - r * 0.1, y - r * 0.2,
                                fill="#e6f6ff", outline="")
            for i in range(int(10 * act)):
                ph = (tick * 1.7 + i / 10.0) % 1.0
                f1 = ((i * 59) % 100) / 100.0
                x = xl(top) + 12 + f1 * (xr(top) - xl(top) - 24) + 4 * math.sin(tick * 5 + i)
                y = top - 4 - ph * 26
                r = 2.2 * (1 - ph) + 0.4
                c.create_oval(x - r, y - r, x + r, y + r, fill="#ffffff", outline="#9bbbd0")

        # metal deposit (displacement reactions)
        if rx["dep"] and p > 0:
            for i in range(int(26 * p)):
                f1 = ((i * 43) % 100) / 100.0
                y = 294 - (i % 3) * 5
                x = xl(y) + 9 + f1 * (xr(y) - xl(y) - 18)
                c.create_rectangle(x - 4, y - 2.5, x + 4, y + 2.5, fill=rx["dep"],
                                    outline=_mix(rx["dep"], "#000000", 0.35))

    # ------------------------------------------------------------------
    # Gas test station: limewater (CO2) or inverted tube + lighted splint (H2)
    # ------------------------------------------------------------------
    def _gas_draw_station(self, c, rx, t, p, tick):
        gt = rx.get("gas_type")
        if not gt:
            return
        lab = self.lab
        act = min(1.0, p * 4) * (1 - max(0.0, (p - 0.85) / 0.15))  # gas being produced
        cx = 590
        T_IN, T_POP = 6.9, 8.1

        def poly(pts):
            return [v for pt in pts for v in pt]

        if gt == "co2":
            path = [(460, 116), (460, 28), (cx, 28), (cx, 272)]
            # test tube of limewater
            c.create_rectangle(cx - 30, 190, cx + 30, 300, fill="#f4fdff", outline="#7aa7c0", width=3)
            milk = max(0.0, min(1.0, (t - 4.2) / 4.0))
            lime = _mix("#d8f1ff", "#fbfbf4", milk)
            c.create_rectangle(cx - 28, 222, cx + 28, 298, fill=lime, outline="")
            c.create_line(cx - 28, 222, cx + 28, 222, fill="#ffffff", width=2)
            for i in range(int(24 * milk)):  # chalky specks appear
                f1 = ((i * 41) % 100) / 100.0
                f2 = ((i * 67) % 100) / 100.0
                x = cx - 24 + f1 * 48
                y = 228 + f2 * 66
                c.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, fill="#ffffff", outline="#cfcfc4")
            c.create_text(cx, 322, text="Limewater", font=("Segoe UI", 12, "bold"), fill="#ffffff")
        else:
            path = [(460, 116), (460, 28), (556, 28), (556, 286), (cx, 286), (cx, 218)]
            # stand + clamp
            c.create_rectangle(612, 296, 676, 302, fill="#6b7280", outline="#374151")
            c.create_line(644, 298, 644, 196, width=5, fill="#8b95a1")
            c.create_line(644, 204, cx + 30, 204, width=5, fill="#8b95a1")
            # inverted test tube collecting hydrogen (gas is lighter than air)
            c.create_rectangle(cx - 30, 180, cx + 30, 262, fill="#f4fdff", outline="#7aa7c0", width=3)
            f = min(1.0, p * 1.15)
            if t > T_POP:
                f *= max(0.0, 1 - (t - T_POP) / 0.3)  # gas burns away at the pop
            if f > 0:
                c.create_rectangle(cx - 28, 182, cx + 28, 182 + 78 * f, fill="#dbeafe", outline="")
                for i in range(int(12 * f)):
                    f1 = ((i * 37) % 100) / 100.0
                    f2 = ((i * 53) % 100) / 100.0
                    x = cx - 22 + f1 * 44 + 2 * math.sin(tick * 3 + i)
                    y = 188 + f2 * max(4.0, 70 * f)
                    c.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, fill="#bfdbfe", outline="#60a5fa")
            c.create_text(cx, 322, text="Collecting H\u2082", font=("Segoe UI", 12, "bold"), fill="#ffffff")

        # delivery tube from the flask to the test tube
        line = poly(path)
        c.create_line(*line, width=8, fill="#8fa9b8", joinstyle="round", capstyle="round")
        c.create_line(*line, width=4, fill="#e8f4fb", joinstyle="round", capstyle="round")
        if act > 0:
            for i in range(10):  # gas puffs travelling along it
                x, y = _path_point(path, (tick * 0.5 + i / 10.0) % 1.0)
                c.create_oval(x - 2.6, y - 2.6, x + 2.6, y + 2.6, fill="#ffffff", outline="#6b93b3")
        if gt == "co2" and act > 0:  # bubbles through the limewater
            for i in range(int(6 * act)):
                ph = (tick * 1.3 + i / 6.0) % 1.0
                y = 272 - ph * 48
                x = cx + 7 * math.sin(tick * 4 + i * 2)
                r = 2.2 + (i % 2)
                c.create_oval(x - r, y - r, x + r, y + r, fill="#ffffff", outline="#6b93b3")

        # ---------- test result ----------
        if gt == "co2":
            if t > 7.0:
                c.create_text(cx, 172, text="Limewater turns milky: CO\u2082 \u2714",
                                font=("Segoe UI", 10, "bold"), fill="#7c2d12")
            return

        # hydrogen: lighted splint approaches the mouth of the tube -> squeaky pop
        if t >= T_IN:
            u = min(1.0, (t - T_IN) / (T_POP - T_IN))
            e = u * u * (3 - 2 * u)
            tx = 712 - (712 - (cx + 6)) * e
            ty = 276
            c.create_line(tx, ty, tx + 58, ty + 5, width=5, fill="#c08a4b", capstyle="round")
            c.create_line(tx, ty, tx + 58, ty + 5, width=1, fill="#7a4e1d")
            if t < T_POP:
                fl = 1 + 0.18 * math.sin(tick * 18)
                c.create_polygon(tx - 7, ty - 2, tx - 4, ty - 15 * fl, tx, ty - 25 * fl,
                                    tx + 4, ty - 14 * fl, tx + 7, ty - 2,
                                    fill="#ff8c00", outline="#e65100", smooth=True)
                c.create_polygon(tx - 3, ty - 2, tx - 1, ty - 10 * fl, tx, ty - 15 * fl,
                                     tx + 2, ty - 9 * fl, tx + 3, ty - 2,
                                     fill="#ffe14d", outline="", smooth=True)
            else:
                c.create_oval(tx - 3, ty - 3, tx + 3, ty + 3, fill="#7f1d1d", outline="")  # ember
                for i in range(4):  # smoke
                    ph = ((t - T_POP) * 0.8 + i / 4.0) % 1.0
                    c.create_oval(tx - 4 + 6 * math.sin(i * 2 + ph * 5), ty - 8 - ph * 30,
                                    tx + 4 + 6 * math.sin(i * 2 + ph * 5), ty - 0 - ph * 30,
                                    outline="#9ca3af")

        if t >= T_POP:
            if not lab.get("popped"):
                lab["popped"] = True
                play_sound("h2_pop")
            k = (t - T_POP) / 0.6
            if k < 1:
                r_out = 12 + 42 * k
                pts = []
                for j in range(16):
                    ang = math.pi * 2 * j / 16
                    rr = r_out if j % 2 == 0 else r_out * 0.45
                    pts.append((cx + rr * math.cos(ang), 250 + rr * math.sin(ang)))
                c.create_polygon(*poly(pts), fill="#fff3a0", outline="#ff7a00", width=2)
            if t < T_POP + 1.0:
                c.create_text(cx, 150, text="POP!", font=("Segoe UI", 20, "bold"), fill="#d90429")
            else:
                c.create_text(cx, 168, text="Squeaky pop: H\u2082 \u2714",
                                  font=("Segoe UI", 10, "bold"), fill="#be123c")

    def _gas_draw_particle(self, c, g, x, y, s=1.0):
        """Draw one reactant particle: solids as chunks, solutions as dots."""
        colour, state = GAS_STYLE[g]
        edge = _mix(colour, "#000000", 0.45)
        r = 7 * s
        if r <= 0.5:
            return
        if state == "solid":
            c.create_rectangle(x - r, y - r * 0.8, x + r, y + r * 0.8,
                               fill=colour, outline=edge, width=1)
        else:
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill=colour, outline=edge, width=2)
            c.create_oval(x - r * 0.5, y - r * 0.6, x - r * 0.1, y - r * 0.2,
                          fill="#ffffff", outline="")

    # ------------------------------------------------------------------
    # Main bench drawing (replaces the old _gas_draw)
    # ------------------------------------------------------------------
    def _gas_draw(self):
        c, lab = self.lab_canvas, self.lab
        t, tick = lab["t"], lab["tick"]
        a, b, kind = lab["a"], lab["b"], lab["kind"]
        rx = lab.get("rx") if kind != "none" else None
        running = lab["mode"] == "run"
        p = max(0.0, min(1.0, (t - 3.2) / 3.5)) if running else 0.0
        c.delete("all")

        # bench
        c.create_rectangle(0, 300, 920, 340, fill="#a0642d", outline="")
        c.create_rectangle(0, 300, 920, 305, fill="#c58a4b", outline="")

        # reaction flask
        c.create_polygon(440, 128, 480, 128, 480, 180, 540, 300, 380, 300, 440, 180,
                             fill="#f4fdff", outline="")
        if running and rx:
            self._gas_draw_product(c, rx, t, p, tick)
        c.create_line(440, 128, 440, 180, 380, 300, 540, 300, 480, 180, 480, 128,
                        fill="#7aa7c0", width=3, joinstyle="round")
        c.create_line(424, 222, 410, 262, fill="#ffffff", width=3)
        c.create_rectangle(432, 116, 488, 132, fill="#a16207", outline="#713f12")

        # reactant jars (solutions show a liquid level, solids sit at the bottom)
        for g, cx, amt in ((a, 120, self.amt1.get()), (b, 800, self.amt2.get())):
            if g:
                colour, state = GAS_STYLE[g]
                c.create_rectangle(cx - 60, 150, cx + 60, 300, fill="#f4fdff", outline="#7aa7c0", width=3)
                if state == "aq":
                    c.create_rectangle(cx - 58, 162, cx + 58, 298,
                                        fill=_mix(colour, "#ffffff", 0.55), outline="")
                c.create_rectangle(cx - 66, 142, cx + 66, 152, fill="#6b7280", outline="#374151")
                c.create_text(cx, 322, text=f"{pretty_formula(g)}   {amt:g} mol",
                                  font=("Segoe UI", 12, "bold"), fill="#ffffff")
            else:
                c.create_rectangle(cx - 60, 150, cx + 60, 300, outline="#9db4c0", width=2, dash=(5, 4))
                c.create_text(cx, 225, text="select a\nreactant", justify="center",
                                font=("Segoe UI", 11, "italic"), fill="#7a93a3")
        c.create_text(460, 322, text="Reaction flask", font=("Segoe UI", 12, "bold"), fill="#ffffff")

        # delivery tubes
        for g, cx, top, fx in ((a, 120, 62, 445), (b, 800, 82, 475)):
            if g:
                line = [cx, 150, cx, top, fx, top, fx, 178]
                c.create_line(*line, width=10, fill="#8fa9b8", joinstyle="round", capstyle="round")
                c.create_line(*line, width=6, fill=_mix(GAS_STYLE[g][0], "#ffffff", 0.7),
                              joinstyle="round", capstyle="round")

        # gas test apparatus (limewater / lighted splint)
        if running and rx and rx.get("gas_type"):
            self._gas_draw_station(c, rx, t, p, tick)

        # particles
        for part in lab["parts"]:
            g = a if part["side"] == "a" else b
            if not g:
                continue
            solid = GAS_STYLE[g][1] == "solid"
            cx = 120 if part["side"] == "a" else 800
            wob = 0 if solid else 5
            rx_ = cx + part["jx"] + wob * math.sin(tick * 3 + part["ph"])
            ry_ = 150 + (118 + part["jy"] % 17 if solid else part["jy"]) + wob * math.cos(tick * 2.6 + part["ph"])
            x, y, s = rx_, ry_, 1.0
            if running:
                u = (t - part["delay"]) / 1.6
                if u > 0:
                    u = min(1.0, u)
                    e = u * u * (3 - 2 * u)
                    if part["side"] == "a":
                        path = [(rx_, ry_), (120, 150), (120, 62), (445, 62), (445, 178), (part["tx"], part["ty"])]
                    else:
                        path = [(rx_, ry_), (800, 150), (800, 82), (475, 82), (475, 178), (part["tx"], part["ty"])]
                    x, y = _path_point(path, e)
                    settle = min(1.0, max(0.0, (t - part["delay"] - 1.6) / 0.4))
                    amp = (7 if kind == "none" else 5) * settle
                    x += amp * math.sin(tick * 4 + part["ph"])
                    y += amp * math.cos(tick * 3.3 + part["ph"])
                if part["consumed"] and t > part["react_at"]:
                    k = (t - part["react_at"]) / 0.35
                    if k >= 1:
                        continue
                    s = 1 - k
            self._gas_draw_particle(c, g, x, y, s)

        # ripple where the solutions meet
        if running and rx and not rx.get("dry") and 2.7 < t < 3.6:
            k = (t - 2.7) / 0.9
            r = 10 + 45 * k
            c.create_oval(460 - r, 262 - r * 0.3, 460 + r, 262 + r * 0.3, outline="#ffffff", width=3)
            c.create_oval(460 - r * 0.6, 262 - r * 0.18, 460 + r * 0.6, 262 + r * 0.18,
                            outline="#7aa7c0", width=2)

        # salt card (top right): name + colour of the salt that has formed
        if running and rx and rx.get("salt") and p > 0.25:
            scol = rx["salt_col"]
            c.create_rectangle(716, 6, 912, 50, fill=_mix(scol, "#ffffff", 0.82), outline=scol, width=2)
            c.create_oval(724, 16, 744, 36, fill=scol, outline=_mix(scol, "#000000", 0.4), width=2)
            c.create_text(752, 18, anchor="w", text=f"{rx.get('salt_label', 'Salt')}: {pretty_formula(rx['salt'])}(aq)",
                              font=("Segoe UI", 10, "bold"), fill=_mix(scol, "#000000", 0.55))
            c.create_text(752, 36, anchor="w", text=rx.get("salt_word", ""),
                              font=("Segoe UI", 9, "italic"), fill="#334155")

        # status line
        colour = "#064e46"
        if not a or not b:
            msg = "Select two reactants to set up the experiment"
        elif not running:
            msg = "Ready: press Run Reaction"
        elif t < 2.7:
            msg = "Reactants are flowing into the flask..."
        elif t < 3.6:
            msg = "Mixing..."
        elif p < 1:
            msg = (("Heating: the powders glow and react..." if rx.get("dry") else "Reaction in progress...")
                   if rx else "Mixing... no visible change")
        elif rx:
            gt = rx.get("gas_type")
            if gt == "h2" and t < 8.1:
                msg = "Testing the gas with a lighted splint..."
            elif gt == "h2":
                msg = "Squeaky pop: hydrogen gas confirmed"
            elif gt == "co2":
                msg = ("Limewater has turned milky: carbon dioxide confirmed"
                           if t > 7.5 else "Testing the gas with limewater...")
            else:
                if rx.get("dry"):
                    msg = "Reaction complete: metal oxide + copper formed"
                else:
                    bits = []
                    if rx["ppt"]:
                        bits.append("precipitate")
                    if rx["dep"]:
                        bits.append("metal deposit")
                    bits.append("salt solution")
                    msg = "Reaction complete: " + " + ".join(bits) + " formed"
        else:
            msg, colour = "No reaction: nothing changed", "#b91c1c"
        c.create_text(14, 14, anchor="w", text=msg, font=("Segoe UI", 12, "bold"), fill=colour)

    # -------------------------
    # AtoMole Arena — atomic structure + moles/stoichiometry, combined
    # (name blends "Atom" + "Mole"; violet colour theme; atomole_* sounds)
    # -------------------------
    def open_atomole_window(self):
        play_sound("atomole_open")
        w = tk.Toplevel(self.root)
        enable_fullscreen(w)
        w.title("AtoMole Arena — Atomic Structure & Mole Calculations")
        # Sized extra generously so every card, label, and result line in
        # both tabs (including the Mole Calculator's three stacked cards)
        # is fully visible without needing to maximize the window.
        fit_window(w, 1360, 980, 900, 500)
        enable_fullscreen(w)
        w.configure(bg="#ede0ff")

        header = tk.Frame(w, bg="#5b21b6")
        header.pack(fill="x")
        tk.Label(header, text="⚛️ AtoMole Arena — where atoms meet moles⚙️",
                 font=self.header_font, bg="#5b21b6", fg="#ffffff", pady=10).pack()
        close_btn = ttk.Button(w, text="Close")
        close_btn.pack(side="bottom", pady=(0, 10))
        notebook = ttk.Notebook(w)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_atoms = tk.Frame(notebook, bg="#ede0ff")
        tab_moles = tk.Frame(notebook, bg="#f3ecff")
        notebook.add(tab_atoms, text="⚛️ Atomic Structure")
        notebook.add(tab_moles, text="⚙️ Mole Calculator")

        def on_atomole_tab_change(event):
            try:
                tab_text = event.widget.tab(event.widget.select(), "text")
            except tk.TclError:
                return
            if "Mole Calculator" in tab_text:
                play_sound("mole_tab")

        notebook.bind("<<NotebookTabChanged>>", on_atomole_tab_change)

        # ============ Tab 1: Atomic structure explorer ============
        main_frame = tk.Frame(tab_atoms, bg="#ede0ff")
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        list_frame = tk.Frame(main_frame, bg="#ede0ff")
        list_frame.pack(side="left", fill="y", padx=(0, 12))
        listbox = tk.Listbox(list_frame, font=self.list_font, width=28, height=24,
                              selectbackground="#8e44ec", selectforeground="white",
                              activestyle="none", exportselection=False)
        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=listbox.xview)
        hscrollbar.grid(row=1, column=0, sticky="ew")
        listbox.config(yscrollcommand=scrollbar.set, xscrollcommand=hscrollbar.set)
        list_frame.grid_rowconfigure(0, weight=1)

        symbols = list(ELEMENT_DATA.keys())
        for sym in symbols:
            name, z, a, shells = ELEMENT_DATA[sym]
            listbox.insert(tk.END, f"{z:2d}. {sym:3s} — {name}")
        listbox.selection_set(0)

        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        right_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(right_frame, width=480, height=420, bg="#ffffff", highlightthickness=0)
        canvas.pack(side="left", anchor="n", padx=(14, 6), pady=14)

        # (replaces the old info_label)
        info_text = make_rich_text(right_frame, bg="#f6f0ff", fg="#3B0A63", width=30, height=11)
        info_text.pack(side="left", fill="both", expand=True, padx=(6, 12), pady=14)
        info_text.tag_config("cfg", font=("Segoe UI", 17, "bold"), foreground="#3B0A63",
                             background="#e5d6ff", lmargin1=14, lmargin2=14)
        info_text.config(state="disabled")

        atom_anim = {"angle": 0.0, "job": None, "sym": None, "running": True}

        def show_info(sym):
            name, z, a, shells = ELEMENT_DATA[sym]
            roman = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
            noble = sym in ("He", "Ne", "Ar")
            box = info_text
            box.config(state="normal")
            box.delete("1.0", tk.END)
            box.insert(tk.END, f"{name} ({sym})\n", "title")
            box.insert(tk.END, f"Atomic number {z}  ·  Mass number {a}\n", "sub")

            add_chip(box, "SUBATOMIC PARTICLES", "#5b21b6")
            add_line(box, f"Protons: {z}  (the atomic number)")
            add_line(box, f"Neutrons: {a - z}  (mass number − protons)")
            add_line(box, f"Electrons: {sum(shells)}  (equal to protons in a neutral atom)")
            box.insert(tk.END, "\n")

            add_chip(box, "ELECTRON CONFIGURATION", "#1d4ed8")
            box.insert(tk.END, "  " + ",".join(str(s) for s in shells) + "  \n\n", "cfg")

            add_chip(box, "SHELLS & VALENCE", "#b45309")
            add_line(box, f"Occupied shells: {len(shells)}  (this is the period number)")
            add_line(box, f"Outer shell (valence) electrons: {shells[-1]}")
            grp = "0 (noble gas)" if noble else roman[shells[-1]]
            add_line(box, f"Group: {grp}")
            if noble:
                add_line(box, "Full outer shell, so it is very unreactive.")
            box.config(state="disabled")

        def draw_atom(sym, angle=0.0):
            canvas.delete("all")
            name, z, a, shells = ELEMENT_DATA[sym]
            cx, cy = 240, 200
            canvas.create_oval(cx - 26, cy - 26, cx + 26, cy + 26, fill="#b085e0", outline="#3B0A63", width=2)
            canvas.create_text(cx, cy, text=sym, font=("Helvetica", 14, "bold"))
            shell_colors = ["#8e44ec", "#1fa878", "#ffb300", "#e06666"]
            for i, n_electrons in enumerate(shells):
                radius = 45 + i * 38
                canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                   outline=shell_colors[i % len(shell_colors)], width=2)
                shell_speed = (1 if i % 2 == 0 else -1) * (0.9 + i * 0.25)
                for e_idx in range(n_electrons):
                    a_rad = 2 * math.pi * e_idx / n_electrons + angle * shell_speed
                    ex, ey = cx + radius * math.cos(a_rad), cy + radius * math.sin(a_rad)
                    canvas.create_oval(ex - 9, ey - 9, ex + 9, ey + 9,
                                       outline=shell_colors[i % len(shell_colors)], width=1)
                    canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                                       fill=shell_colors[i % len(shell_colors)], outline="#333333")
            # NOTE: text is no longer rewritten every frame (that would flicker)

        # animate_atom stays exactly as it was
        def animate_atom():
            if not atom_anim["running"] or atom_anim["sym"] is None:
                return
            atom_anim["angle"] += 0.04
            try:
                draw_atom(atom_anim["sym"], atom_anim["angle"])
            except tk.TclError:
                return
            if atom_anim["running"]:
                atom_anim["job"] = canvas.after(40, animate_atom)

        def on_select(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            play_sound("atomole_select")
            atom_anim["sym"] = symbols[sel[0]]
            atom_anim["angle"] = 0.0
            show_info(symbols[sel[0]])

        listbox.bind("<<ListboxSelect>>", on_select)
        atom_anim["sym"] = symbols[0]
        show_info(symbols[0])
        animate_atom()

        # ============ Tab 2: Mole / stoichiometry calculator ============
        PU, PU_D, PU_L = "#5b21b6", "#3B0A63", "#f3ecff"
        AVOGADRO = 6.022e23
        AR = {"H": 1, "He": 4, "Li": 7, "Be": 9, "B": 11, "C": 12, "N": 14, "O": 16, "F": 19,
              "Ne": 20, "Na": 23, "Mg": 24, "Al": 27, "Si": 28, "P": 31, "S": 32, "Cl": 35.5,
              "Ar": 40, "K": 39, "Ca": 40, "Fe": 56, "Cu": 63.5, "Zn": 65, "Br": 80,
              "Ag": 108, "I": 127, "Ba": 137, "Pb": 207}

        calc_types = [
            "Mass & Mr → Moles",
            "Moles & Mr → Mass",
            "Moles & Volume(dm³) → Concentration (mol/dm³)",
            "Concentration & Volume(dm³) → Moles",
            "Moles → Volume of gas at r.t.p. (dm³)",
        ]
        # (top, bottom-left, bottom-right, quantity being solved: top/bl/br, formula)
        TRIANGLES = {
            calc_types[0]: ("mass", "moles", "Mr", "bl", "n = m ÷ Mr"),
            calc_types[1]: ("mass", "moles", "Mr", "top", "m = n × Mr"),
            calc_types[2]: ("moles", "conc.", "volume", "bl", "c = n ÷ V"),
            calc_types[3]: ("moles", "conc.", "volume", "top", "n = c × V"),
            calc_types[4]: ("volume", "moles", "24", "top", "V = n × 24"),
        }

        # ---------- little drawing helpers ----------
        def draw_flask(c, cx, base_y, s=1.0, liquid="#a78bfa"):
            c.create_polygon(cx - 7*s, base_y - 62*s, cx + 7*s, base_y - 62*s, cx + 7*s, base_y - 36*s,
                             cx + 26*s, base_y, cx - 26*s, base_y, cx - 7*s, base_y - 36*s,
                             fill="#f5f3ff", outline="#4c1d95", width=2)
            c.create_polygon(cx - 17*s, base_y - 14*s, cx + 17*s, base_y - 14*s, cx + 26*s, base_y,
                             cx - 26*s, base_y, fill=liquid, outline="")
            c.create_rectangle(cx - 9*s, base_y - 68*s, cx + 9*s, base_y - 62*s, fill="#4c1d95", outline="")

        # ---------- banner ----------
        banner = tk.Canvas(tab_moles, height=70, bg="#2e1065", highlightthickness=0)
        banner.pack(fill="x")

        def draw_banner(event=None):
            banner.delete("all")
            W = max(banner.winfo_width(), 900)
            for x, col in ((70, "#a78bfa"), (150, "#34d399"), (W - 150, "#fbbf24"), (W - 70, "#f472b6")):
                draw_flask(banner, x, 62, 0.75, col)
            banner.create_text(W / 2, 24, text="⚙  M O L E   C A L C U L A T O R  ⚙",
                               font=("Georgia", 20, "bold"), fill="#ffffff")
            banner.create_text(W / 2, 52,
                               text="1 mol = 6.022 × 10²³ particles   ·   24 dm³ of any gas at r.t.p.",
                               font=("Segoe UI", 11, "italic"), fill="#c4b5fd")
        banner.bind("<Configure>", draw_banner)

        mfrm = tk.Frame(tab_moles, bg=PU_L, padx=16, pady=12)
        mfrm.pack(fill="both", expand=True)

        # ---------- RIGHT column: images ----------
        right_col = tk.Frame(mfrm, bg=PU_L)
        right_col.pack(side="right", fill="y", padx=(14, 0))

        bench_card = tk.LabelFrame(right_col, text="  🔎 Lab Bench  ", font=self.header_font, bg="#ffffff",
                                   fg=PU, bd=2, relief="ridge", labelanchor="n", padx=8, pady=6)
        bench_card.pack(fill="x", pady=(0, 12))
        bench = tk.Canvas(bench_card, width=400, height=256, bg="#faf7ff", highlightthickness=0)
        bench.pack()

        tri_card = tk.LabelFrame(right_col, text="  🔺 Mole Triangle  ", font=self.header_font, bg="#ffffff",
                                 fg=PU, bd=2, relief="ridge", labelanchor="n", padx=8, pady=6)
        tri_card.pack(fill="x", pady=(0, 12))
        tri = tk.Canvas(tri_card, width=400, height=250, bg="#faf7ff", highlightthickness=0)
        tri.pack()


        def draw_scene():
            c, ct = bench, calc_var.get()
            c.delete("all")
            if ct in (calc_types[0], calc_types[1]):                 # ---- balance
                c.create_text(200, 14, text="Weighing a sample", font=("Georgia", 12, "bold"), fill=PU)
                c.create_rectangle(70, 205, 330, 220, fill="#4c1d95", outline="")
                c.create_rectangle(192, 68, 208, 205, fill="#7c3aed", outline="")
                c.create_polygon(200, 44, 188, 68, 212, 68, fill="#a78bfa", outline="")
                c.create_line(70, 68, 330, 68, width=6, fill=PU)
                for x in (70, 330):
                    c.create_line(x, 68, x - 38, 150, fill="#6b5b8a")
                    c.create_line(x, 68, x + 38, 150, fill="#6b5b8a")
                    c.create_line(x - 42, 150, x + 42, 150, width=5, fill="#4c1d95")
                draw_flask(c, 70, 148, 0.9, "#c4b5fd")
                for i, w_ in enumerate((34, 28, 22)):
                    c.create_rectangle(330 - w_/2, 148 - (i+1)*14, 330 + w_/2, 148 - i*14,
                                       fill="#fbbf24", outline="#92400e")
                c.create_text(70, 180, text="sample", font=("Segoe UI", 10, "bold"), fill=PU_D)
                c.create_text(330, 180, text="masses (g)", font=("Segoe UI", 10, "bold"), fill=PU_D)

            elif ct in (calc_types[2], calc_types[3]):               # ---- beaker
                c.create_text(200, 14, text="Solution in a beaker", font=("Georgia", 12, "bold"), fill=PU)
                c.create_polygon(120, 40, 280, 40, 275, 205, 125, 205, fill="#f5f3ff", outline="#4c1d95", width=3)
                c.create_polygon(124, 95, 276, 95, 275, 205, 125, 205, fill="#c4b5fd", outline="")
                for i in range(6):
                    y = 60 + i * 24
                    c.create_line(120, y, 140, y, fill="#4c1d95", width=2)
                rnd = random.Random(7)
                for _ in range(26):
                    x, y = rnd.randint(140, 262), rnd.randint(105, 195)
                    c.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#7c3aed", outline="#3B0A63")
                c.create_line(300, 95, 300, 205, arrow=tk.BOTH, fill="#b45309", width=2)
                c.create_text(335, 150, text="V\n(dm³)", font=("Segoe UI", 10, "bold"), fill="#b45309")
                c.create_text(70, 150, text="● solute\n   particles", font=("Segoe UI", 10, "bold"), fill="#7c3aed")

            else:                                                    # ---- gas syringe
                c.create_text(200, 14, text="Gas syringe at r.t.p.", font=("Georgia", 12, "bold"), fill=PU)
                c.create_rectangle(90, 80, 300, 140, fill="#f5f3ff", outline="#4c1d95", width=3)
                c.create_rectangle(90, 86, 250, 134, fill="#ccfbf1", outline="")
                c.create_rectangle(250, 80, 262, 140, fill="#4c1d95", outline="")
                c.create_line(262, 110, 340, 110, width=6, fill="#6b5b8a")
                c.create_rectangle(338, 90, 350, 130, fill="#6b5b8a", outline="")
                c.create_line(90, 110, 50, 110, width=8, fill="#6b5b8a")
                for i in range(11):
                    x = 100 + i * 15
                    c.create_line(x, 140, x, 148 if i % 5 else 156, fill="#4c1d95")
                rnd = random.Random(11)
                for _ in range(14):
                    x, y = rnd.randint(100, 238), rnd.randint(94, 126)
                    c.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#0d9488", outline="#134e4a")
                c.create_text(200, 180, text="1 mol of any gas = 24 dm³", font=("Segoe UI", 12, "bold"), fill="#0d9488")
            c.create_text(200, 242, text=TRIANGLES[ct][4],
                          font=("Courier New", 11, "bold"), fill="#6b5b8a")

        def draw_triangle():
            c = tri
            c.delete("all")
            top, bl, br, solve, formula = TRIANGLES[calc_var.get()]
            zones = {"top": [(190, 20), (255, 105), (125, 105)],
                     "bl": [(125, 105), (190, 105), (190, 195), (60, 195)],
                     "br": [(190, 105), (255, 105), (320, 195), (190, 195)]}
            centres = {"top": (190, 75, top), "bl": (125, 150, bl), "br": (255, 150, br)}
            for k, pts in zones.items():
                c.create_polygon(*[v for p in pts for v in p],
                                 fill="#fde047" if k == solve else "#ede9fe", outline=PU, width=3)
                x, y, label = centres[k]
                c.create_text(x, y, text=label, font=("Segoe UI", 13, "bold"),
                              fill="#92400e" if k == solve else PU_D)
            c.create_text(190, 218, text=formula, font=("Courier New", 15, "bold"), fill="#0b6e4f")
            c.create_text(190, 238, text="yellow = the quantity you are finding", font=("Segoe UI", 9, "italic"), fill="#6b5b8a")



        # ---------- LEFT column: calculator ----------
        left_col = tk.Frame(mfrm, bg=PU_L)
        left_col.pack(side="left", fill="both", expand=True)

        calc_card = tk.LabelFrame(left_col, text="  ①  Choose a Calculation  ", font=self.header_font,
                                  bg="#ffffff", fg=PU, bd=2, relief="ridge", labelanchor="n", padx=14, pady=10)
        calc_card.pack(fill="x", pady=(0, 12))
        calc_var = tk.StringVar(value=calc_types[0])
        ttk.Style().configure("AtoMole.TCombobox", font=("Segoe UI", 12))
        combo = ttk.Combobox(calc_card, textvariable=calc_var, values=calc_types, state="readonly",
                             font=("Segoe UI", 12), style="AtoMole.TCombobox")
        combo.pack(fill="x", ipady=4)

        values_row = tk.Frame(left_col, bg=PU_L)
        values_row.pack(fill="x", pady=(0, 6))

        values_card = tk.LabelFrame(values_row, text="  ②  Enter Known Values  ", font=self.header_font,
                                    bg="#ffffff", fg=PU, bd=2, relief="ridge", labelanchor="n", padx=14, pady=12)
        values_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        values_card.grid_columnconfigure(1, weight=1)
        entry_font = ("Segoe UI", 13)

        label_a_widget = tk.Label(values_card, text="⚖️ Mass", font=("Segoe UI", 12, "bold"),
                                  bg="#ffffff", fg=PU_D, width=18, anchor="w")
        label_a_widget.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="w")
        val_a = tk.StringVar()
        entry_a = tk.Entry(values_card, textvariable=val_a, width=16, font=entry_font, relief="solid", bd=1,
                           highlightthickness=1, highlightcolor="#8e44ec", highlightbackground="#d8c8f0")
        entry_a.grid(row=0, column=1, padx=6, pady=8, sticky="w")
        unit_a = tk.Label(values_card, text="g", font=("Segoe UI", 11, "italic"), bg="#ffffff", fg="#8e44ec")
        unit_a.grid(row=0, column=2, padx=6, sticky="w")

        label_b_widget = tk.Label(values_card, text="🔬 Mr (Molar Mass)", font=("Segoe UI", 12, "bold"),
                                  bg="#ffffff", fg=PU_D, width=18, anchor="w")
        label_b_widget.grid(row=1, column=0, padx=(0, 10), pady=8, sticky="w")
        val_b = tk.StringVar()
        entry_b = tk.Entry(values_card, textvariable=val_b, width=16, font=entry_font, relief="solid", bd=1,
                           highlightthickness=1, highlightcolor="#8e44ec", highlightbackground="#d8c8f0")
        entry_b.grid(row=1, column=1, padx=6, pady=8, sticky="w")
        unit_b = tk.Label(values_card, text="g/mol", font=("Segoe UI", 11, "italic"), bg="#ffffff", fg="#8e44ec")
        unit_b.grid(row=1, column=2, padx=6, sticky="w")

        mr_card = tk.LabelFrame(values_row, text="  🔬 Mr Helper  ", font=self.header_font, bg="#ffffff",
                                fg=PU, bd=2, relief="ridge", labelanchor="n", padx=10, pady=8)
        mr_card.pack(side="left", fill="y")
        mr_row = tk.Frame(mr_card, bg="#ffffff")
        mr_row.pack(fill="x")
        mr_formula = tk.StringVar()
        mr_entry = tk.Entry(mr_row, textvariable=mr_formula, font=("Segoe UI", 13), width=12,
                            relief="solid", bd=1, highlightthickness=1,
                            highlightcolor="#8e44ec", highlightbackground="#d8c8f0")
        mr_entry.pack(side="left", padx=(0, 8), ipady=3)
        mr_out = tk.Label(mr_card, text="Type a formula such as\nCa(OH)2 or CuSO4,\nthen press Get Mr.",
                          font=("Segoe UI", 10, "italic"), bg="#ffffff", fg="#6b5b8a",
                          wraplength=250, justify="left", anchor="w")
        mr_out.pack(fill="x", pady=(8, 0))

        def get_mr():
            try:
                counts = parse_formula(mr_formula.get().strip())
                if not counts:
                    raise ValueError
                parts, total = [], 0
                for el, n in counts.items():
                    if el not in AR:
                        mr_out.config(text=f"⚠️ No Ar stored for '{el}'.", fg="#b00020")
                        return
                    parts.append(f"{n}×{AR[el]:g}")
                    total += n * AR[el]
                mr_out.config(text=f"{pretty_formula(mr_formula.get())}:\nMr = {' + '.join(parts)} = {total:g}",
                              fg="#0b6e4f", font=("Segoe UI", 11, "bold"))
                if calc_var.get() in (calc_types[0], calc_types[1]):
                    val_b.set(f"{total:g}")
                play_sound("atomole_calc_change")
            except Exception:
                mr_out.config(text="⚠️ Couldn't read that formula.", fg="#b00020")

        tk.Button(mr_row, text="Get Mr", font=("Segoe UI", 11, "bold"), bg=PU, fg="white",
                  activebackground="#7a2fd1", activeforeground="white", relief="flat",
                  padx=12, pady=3, command=get_mr).pack(side="left")

        field_labels = {
            calc_types[0]: ("⚖️ Mass", "g", "🔬 Mr (Molar Mass)", "g/mol", True),
            calc_types[1]: ("⚙️ Moles", "mol", "🔬 Mr (Molar Mass)", "g/mol", True),
            calc_types[2]: ("⚙️ Moles", "mol", "🧫 Volume", "dm³", True),
            calc_types[3]: ("🌊 Concentration", "mol/dm³", "🧫 Volume", "dm³", True),
            calc_types[4]: ("⚙️ Moles", "mol", "— not needed", "", False),
        }

        def update_labels(event=None):
            a_lbl, a_unit, b_lbl, b_unit, b_needed = field_labels[calc_var.get()]
            label_a_widget.config(text=a_lbl); unit_a.config(text=a_unit)
            label_b_widget.config(text=b_lbl); unit_b.config(text=b_unit)
            if b_needed:
                entry_b.config(state="normal", bg="#ffffff")
            else:
                val_b.set("")
                entry_b.config(state="disabled", bg="#f0eaf9")
            draw_scene()
            draw_triangle()

        def on_calc_change(event=None):
            play_sound("atomole_calc_change")
            update_labels()

        combo.bind("<<ComboboxSelected>>", on_calc_change)

        btn_frame = tk.Frame(left_col, bg=PU_L)
        btn_frame.pack(pady=(0, 12))
        tk.Button(btn_frame, text="Calculate ✨", font=self.btn_font, bg="#8e44ec", fg="white",
                  activebackground="#7a2fd1", activeforeground="white", relief="flat",
                  padx=18, pady=8, command=lambda: calculate()).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Clear 🗑️", font=self.btn_font, bg="#e5d6ff", fg=PU,
                  activebackground="#d8c0ff", activeforeground=PU, relief="flat",
                  padx=18, pady=8, command=lambda: clear_fields()).grid(row=0, column=1, padx=8)

        result_card = tk.LabelFrame(left_col, text="  ③  Result  ", font=self.header_font, bg="#ffffff",
                                    fg=PU, bd=2, relief="ridge", labelanchor="n", padx=10, pady=10)
        result_card.pack(fill="both", expand=True)
        steps_text = tk.Text(result_card, font=("Segoe UI", 12), wrap="word", bg="#ffffff", fg=PU_D,
                             height=10, relief="flat", padx=10, pady=8)
        steps_text.pack(fill="both", expand=True)
        steps_text.tag_config("type", font=("Segoe UI", 13, "bold"), foreground="#ffffff",
                              background=PU, spacing3=8)
        steps_text.tag_config("formula", font=("Courier New", 12, "italic"), foreground="#6b5b8a", spacing3=6)
        steps_text.tag_config("calc", font=("Courier New", 12), foreground="#333333", spacing3=6)
        steps_text.tag_config("answer", font=("Courier New", 15, "bold"), foreground="#0b6e4f",
                              background="#e2ffe0", spacing1=4, spacing3=4)
        steps_text.tag_config("sci", font=("Courier New", 11, "bold"), foreground="#92400e",
                              background="#fef3c7", spacing3=4)
        steps_text.tag_config("error", font=("Segoe UI", 12, "bold"), foreground="#b00020")

        HINT = "👋 Pick a calculation above, fill in the values, then hit Calculate ✨"

        def set_result(lines):
            steps_text.config(state="normal")
            steps_text.delete("1.0", tk.END)
            for text, tag in lines:
                steps_text.insert(tk.END, text + "\n\n", tag)
            steps_text.config(state="disabled")

        set_result([(HINT, "calc")])

        def clear_fields():
            val_a.set(""); val_b.set("")
            set_result([(HINT, "calc")])
            play_sound("atomole_clear")

        def calculate():
            play_sound("atomole_calculate")
            ctype = calc_var.get()
            try:
                a_str, b_str = val_a.get().strip(), val_b.get().strip()
                a_num = float(a_str) if a_str else None
                b_num = float(b_str) if b_str else None
                if (a_num is not None and a_num < 0) or (b_num is not None and b_num < 0):
                    raise ValueError("Values cannot be negative.")
                lines = [(f" 📌 {ctype} ", "type")]
                n = None
                if ctype == calc_types[0]:
                    if a_num is None or b_num is None or b_num == 0:
                        raise ValueError("Please enter both mass and Mr (Mr must not be 0).")
                    n = a_num / b_num
                    lines += [("Formula:  moles = mass ÷ Mr", "formula"),
                              (f"Substitute:  moles = {a_num} g ÷ {b_num} g/mol", "calc"),
                              (f"✅ moles = {n:.4g} mol", "answer")]
                elif ctype == calc_types[1]:
                    if a_num is None or b_num is None:
                        raise ValueError("Please enter both moles and Mr.")
                    n = a_num
                    lines += [("Formula:  mass = moles × Mr", "formula"),
                              (f"Substitute:  mass = {a_num} mol × {b_num} g/mol", "calc"),
                              (f"✅ mass = {a_num * b_num:.4g} g", "answer")]
                elif ctype == calc_types[2]:
                    if a_num is None or b_num is None or b_num == 0:
                        raise ValueError("Please enter moles and volume (volume must not be 0).")
                    n = a_num
                    lines += [("Formula:  concentration = moles ÷ volume (dm³)", "formula"),
                              (f"Substitute:  c = {a_num} mol ÷ {b_num} dm³", "calc"),
                              (f"✅ concentration = {a_num / b_num:.4g} mol/dm³", "answer")]
                elif ctype == calc_types[3]:
                    if a_num is None or b_num is None:
                        raise ValueError("Please enter concentration and volume.")
                    n = a_num * b_num
                    lines += [("Formula:  moles = concentration × volume (dm³)", "formula"),
                              (f"Substitute:  moles = {a_num} mol/dm³ × {b_num} dm³", "calc"),
                              (f"✅ moles = {n:.4g} mol", "answer")]
                else:
                    if a_num is None:
                        raise ValueError("Please enter moles in the first field.")
                    n = a_num
                    lines += [("Formula:  volume (dm³) = moles × 24 dm³/mol  (r.t.p.)", "formula"),
                              (f"Substitute:  volume = {a_num} mol × 24 dm³/mol", "calc"),
                              (f"✅ volume = {a_num * 24:.4g} dm³", "answer")]
                if n is not None:
                    lines.append((f"⚛ particles  N = n × 6.022×10²³ = {n:.4g} × 6.022×10²³ = {n * AVOGADRO:.3e}", "sci"))
                set_result(lines)
                play_sound("success")
            except ValueError as e:
                set_result([(f"⚠️  {e}", "error")])
                play_sound("wrong")

        update_labels()
        w.after(150, draw_banner)

        def close_atomole():
            atom_anim["running"] = False
            if atom_anim["job"]:
                try:
                    canvas.after_cancel(atom_anim["job"])
                except Exception:
                    pass
            play_sound("window_close")
            w.destroy()

        w.protocol("WM_DELETE_WINDOW", close_atomole)
        close_btn.config(command=close_atomole)

    # -------------------------
    # Carbon Craft — organic chemistry explorer
    # (green colour theme; organic_* sounds)
    # -------------------------
    def open_organic_window(self):
        play_sound("organic_open")
        w = tk.Toplevel(self.root)
        enable_fullscreen(w)
        w.title("Carbon Craft — Organic Chemistry Explorer")
        w.geometry("1040x780")
        w.configure(bg="#e6fff0")

        header = tk.Frame(w, bg="#0b6e4f")
        header.pack(fill="x")
        tk.Label(header, text="♻️ Carbon Craft — homologous series, structures & reactions ♻️",
                 font=self.header_font, bg="#0b6e4f", fg="#ffffff", pady=10).pack()

        main_frame = tk.Frame(w, bg="#e6fff0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        list_frame = tk.Frame(main_frame, bg="#e6fff0")
        list_frame.pack(side="left", fill="y", padx=(0, 12))
        listbox = tk.Listbox(list_frame, font=self.list_font, width=28, height=14,
                              selectbackground="#1fa878", selectforeground="white",
                              exportselection=False)
        listbox.grid(row=0, column=0, sticky="nsew")
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=listbox.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        series_keys = list(ORGANIC_DATA.keys())
        for idx, k in enumerate(series_keys, start=1):
            listbox.insert(tk.END, f"{idx}. {k}")
        listbox.selection_set(0)

        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        right_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(right_frame, width=420, height=260, bg="#ffffff", highlightthickness=0)
        canvas.pack(pady=(10, 4))

        info_text = make_rich_text(right_frame, bg="#f0fff7", fg="#0b3d2e", height=11)
        info_text.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        info_text.tag_config("gf", font=("Segoe UI", 17, "bold"), foreground="#0b4a24",
                             background="#dff5e6", lmargin1=14, lmargin2=14)
        info_text.config(state="disabled")

        atom_colors = {"C": "#333333", "H": "#93c47d", "O": "#e06666"}

        organic_anim = {"t": 0.0, "job": None, "key": None, "running": True}

        def draw_structure(data, t=0.0):
            canvas.delete("all")
            atoms = data["atoms"]
            bonds = data["bonds"]
            pulse = 1 + 0.08 * math.sin(t)

            positions = []
            for i, (sym, x, y) in enumerate(atoms):
                jx = 3 * math.sin(t * 1.3 + i * 2.1)
                jy = 3 * math.cos(t * 1.1 + i * 1.7)
                positions.append((sym, x + jx, y + jy))

            for i, j, order in bonds:
                x1, y1 = positions[i][1], positions[i][2]
                x2, y2 = positions[j][1], positions[j][2]
                if order == 1:
                    canvas.create_line(x1, y1, x2, y2, width=3, fill="#0b6e4f")
                else:
                    dx, dy = x2 - x1, y2 - y1
                    length = math.hypot(dx, dy) or 1
                    ox, oy = -dy / length * 5, dx / length * 5
                    canvas.create_line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, width=3, fill="#0b6e4f")
                    canvas.create_line(x1 - ox, y1 - oy, x2 - ox, y2 - oy, width=3, fill="#0b6e4f")

            for sym, x, y in positions:
                r = (16 if sym == "C" else 12) * pulse
                canvas.create_oval(x - r, y - r, x + r, y + r,
                                   fill=atom_colors.get(sym, "#cccccc"), outline="#222222", width=1.5)
                canvas.create_text(x, y, text=sym, font=("Helvetica", 10, "bold"),
                                   fill="white" if sym != "H" else "#222222")

        def animate_organic():
            if not organic_anim["running"] or organic_anim["key"] is None:
                return
            organic_anim["t"] += 0.12
            try:
                draw_structure(ORGANIC_DATA[organic_anim["key"]], organic_anim["t"])
            except tk.TclError:
                return
            if organic_anim["running"]:
                organic_anim["job"] = canvas.after(50, animate_organic)

        def show_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            play_sound("organic_select")
            key = series_keys[sel[0]]
            organic_anim["key"] = key
            organic_anim["t"] = 0.0
            data = ORGANIC_DATA[key]

            box = info_text
            box.config(state="normal")
            box.delete("1.0", tk.END)

            box.insert(tk.END, key + "\n", "title")
            box.insert(tk.END, "Example: " + data["example_name"] + ",  "
                       + pretty_formula(data["example_formula"]) + "\n", "sub")

            add_chip(box, "GENERAL FORMULA", "#0b6e4f")
            box.insert(tk.END, "  ", "gf")
            insert_formula(box, data["general_formula"], "gf")
            box.insert(tk.END, "  ", "gf")
            box.insert(tk.END, "\n\n")

            add_chip(box, "FUNCTIONAL GROUP", "#1d4ed8")
            box.insert(tk.END, data["functional_group"] + "\n\n", "para")

            add_chip(box, "KEY REACTION / TEST", "#b45309")
            box.insert(tk.END, pretty_formula(data["reaction"]).replace("->", "→") + "\n\n", "para")

            add_chip(box, "COMMON USES", "#7c3aed")
            box.insert(tk.END, pretty_formula(data["uses"]) + "\n", "para")

            box.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", show_selected)
        series_keys0 = series_keys[0]
        show_selected()
        organic_anim["key"] = series_keys0
        organic_anim["t"] = 0.0
        animate_organic()

        def close_organic():
            organic_anim["running"] = False
            if organic_anim["job"]:
                try:
                    canvas.after_cancel(organic_anim["job"])
                except Exception:
                    pass
            play_sound("window_close")
            w.destroy()

        w.protocol("WM_DELETE_WINDOW", close_organic)
        ttk.Button(w, text="Close", command=close_organic).pack(pady=(0, 10))

    # -------------------------
    # Volt Vault — full electrolysis explorer, covering the O-Level
    # Chemistry 5070 electrolysis syllabus: molten binary compounds,
    # aqueous electrolytes (inert & active electrodes), selective discharge
    # rules, extraction of aluminium, purification of copper, and
    # electroplating.
    # (amber-on-navy colour theme; electro_* sounds)
    # -------------------------
    def open_electrolysis_window(self):
        play_sound("electro_open")
        w = tk.Toplevel(self.root)
        enable_fullscreen(w)
        w.title("Volt Vault — Electrolysis: Full 5070 Syllabus Explorer")
        w.geometry("1040x820")
        w.configure(bg="#1b1f3b")

        header = tk.Frame(w, bg="#1b1f3b")
        header.pack(fill="x")
        tk.Label(header, text="⚡ Volt Vault — Electrolysis, Selective Discharge, Extraction & Electroplating",
                 font=self.header_font, bg="#1b1f3b", fg="#ffb300", pady=10, wraplength=980).pack()

        notebook = ttk.Notebook(w)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_explorer = tk.Frame(notebook, bg="#fff6e0")
        tab_rules = tk.Frame(notebook, bg="#fff6e0")
        tab_apps = tk.Frame(notebook, bg="#fff6e0")
        notebook.add(tab_explorer, text="⚡ Electrolyte Explorer")
        notebook.add(tab_rules, text="📖 Selective Discharge Rules")
        notebook.add(tab_apps, text="🏭 Extraction & Electroplating")

        def on_volt_tab_change(event):
            tab_text = event.widget.tab(event.widget.select(), "text")
            if "Selective Discharge" in tab_text:
                play_sound("electro_rules_view")
            elif "Extraction" in tab_text:
                play_sound("electro_apps_view")

        notebook.bind("<<NotebookTabChanged>>", on_volt_tab_change)

        # ============ Tab 1: Electrolyte explorer ============
        main_frame = tk.Frame(tab_explorer, bg="#fff6e0")
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        list_frame = tk.Frame(main_frame, bg="#fff6e0")
        list_frame.pack(side="left", fill="y", padx=(0, 12))
        listbox = tk.Listbox(list_frame, font=self.list_font, width=40, height=13,
                              selectbackground="#ffb300", selectforeground="#1b1f3b",
                              exportselection=False)
        listbox.grid(row=0, column=0, sticky="nsew")
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=listbox.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        electrolyte_keys = list(ELECTROLYSIS_DATA.keys())
        for idx, k in enumerate(electrolyte_keys, start=1):
            listbox.insert(tk.END, f"{idx}. {k}")
        listbox.selection_set(0)

        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        right_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(right_frame, width=460, height=270, bg="#ffffff", highlightthickness=0)
        canvas.pack(pady=(10, 4))

        result_text = tk.Text(right_frame, font=("Segoe UI", 13), wrap="word",
                              bg="#fff9ea", fg="#3a2900", relief="flat", height=13,
                              padx=22, pady=16, cursor="arrow")
        result_text.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        # --- text styles ---
        result_text.tag_config("title", font=("Georgia", 16, "bold"), foreground="#1b1f3b", spacing3=4)
        result_text.tag_config("electrodes", font=("Segoe UI", 12, "italic"), foreground="#6b5200", spacing3=16)
        result_text.tag_config("cathode_chip", font=("Segoe UI", 11, "bold"), foreground="#ffffff",
                               background="#1f9d55")
        result_text.tag_config("anode_chip", font=("Segoe UI", 11, "bold"), foreground="#ffffff", background="#c2189b")
        result_text.tag_config("side", font=("Segoe UI", 11, "italic"), foreground="#7a5200")
        result_text.tag_config("product", font=("Segoe UI", 14, "bold"), foreground="#1b1f3b",
                               spacing1=8, spacing3=4, lmargin1=6, lmargin2=6)
        result_text.tag_config("eq_c", font=("Segoe UI", 15, "bold"), foreground="#0b4a24", background="#dff5e6")
        result_text.tag_config("eq_a", font=("Segoe UI", 15, "bold"), foreground="#6b0b58", background="#fbe0f6")
        result_text.tag_config("gap", spacing3=16)
        result_text.tag_config("note_chip", font=("Segoe UI", 11, "bold"), foreground="#1b1f3b", background="#ffb300")
        result_text.tag_config("note", font=("Segoe UI", 12), foreground="#4a3200",
                               spacing1=8, lmargin1=6, lmargin2=6)
        result_text.config(state="disabled")

        cell_anim = {"t": 0.0, "job": None, "running": True}

        def draw_cell(t=0.0):
            canvas.delete("all")
            # --- row 1: labels (nothing else shares this row) ---
            canvas.create_text(130, 14, text="Cathode (−)", font=("Segoe UI", 11, "bold"), fill="#1f9d55")
            canvas.create_text(330, 14, text="Anode (+)", font=("Segoe UI", 11, "bold"), fill="#c2189b")

            # --- row 2: battery and wires ---
            canvas.create_line(130, 40, 205, 40, fill="#333333", width=2)
            canvas.create_line(255, 40, 330, 40, fill="#333333", width=2)
            canvas.create_line(130, 40, 130, 62, fill="#333333", width=2)
            canvas.create_line(330, 40, 330, 62, fill="#333333", width=2)
            canvas.create_rectangle(205, 30, 255, 50, fill="#444444", outline="#222222")
            canvas.create_text(230, 40, text="DC", font=("Segoe UI", 9, "bold"), fill="#ffd700")

            # --- beaker ---
            canvas.create_rectangle(60, 85, 400, 225, outline="#ffb300", width=3, fill="#12163a")
            canvas.create_line(62, 92, 398, 92, fill="#2a2f5c", width=2)

            # --- electrodes ---
            canvas.create_rectangle(120, 62, 140, 240, fill="#888888", outline="#1b1f3b")
            canvas.create_rectangle(320, 62, 340, 240, fill="#888888", outline="#1b1f3b")

            cation_fill, cation_glow, cation_outline = "#39FF14", "#B9FFB0", "#0E5C0E"
            anion_fill, anion_glow, anion_outline = "#FF2EF2", "#FFC2FB", "#7A0E63"

            for i in range(4):
                by = 112 + i * 28
                phase = (t * 0.6 + i * 0.25) % 1.0
                cx_pos = 230 - phase * (230 - 165)
                canvas.create_oval(cx_pos - 12, by - 12, cx_pos + 12, by + 12, fill=cation_glow, outline="")
                canvas.create_oval(cx_pos - 8, by - 8, cx_pos + 8, by + 8, fill=cation_fill,
                                   outline=cation_outline, width=2)
                canvas.create_text(cx_pos, by, text="+", font=("Helvetica", 9, "bold"), fill="#0E5C0E")

                phase2 = (t * 0.6 + i * 0.25 + 0.1) % 1.0
                ax_pos = 230 + phase2 * (295 - 230)
                canvas.create_oval(ax_pos - 12, by - 12, ax_pos + 12, by + 12, fill=anion_glow, outline="")
                canvas.create_oval(ax_pos - 8, by - 8, ax_pos + 8, by + 8, fill=anion_fill,
                                   outline=anion_outline, width=2)
                canvas.create_text(ax_pos, by, text="−", font=("Helvetica", 9, "bold"), fill="#7A0E63")

            # --- bubbles rising beside each electrode ---
            for i in range(3):
                bub_y = 215 - ((t * 20 + i * 45) % 120)
                canvas.create_oval(143, bub_y - 4, 151, bub_y + 4, outline="#cfd8ff", width=1)
                canvas.create_oval(309, bub_y - 4, 317, bub_y + 4, outline="#ffe9b0", width=1)

            # --- caption (now inside the canvas) ---
            canvas.create_text(230, 258, text="Ions migrate through the electrolyte to opposite electrodes",
                               font=("Segoe UI", 9, "italic"), fill="#555555")

        def animate_cell():
            if not cell_anim["running"]:
                return
            cell_anim["t"] += 0.05
            try:
                draw_cell(cell_anim["t"])
            except tk.TclError:
                return
            if cell_anim["running"]:
                cell_anim["job"] = canvas.after(60, animate_cell)

        def show_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            play_sound("electro_select")
            key = electrolyte_keys[sel[0]]
            electrodes, c_prod, c_eq, a_prod, a_eq, note = ELECTROLYSIS_DATA[key]

            t = result_text
            t.config(state="normal")
            t.delete("1.0", tk.END)

            t.insert(tk.END, key + "\n", "title")
            t.insert(tk.END, "Electrodes: " + electrodes + "\n", "electrodes")

            t.insert(tk.END, " CATHODE (−) ", "cathode_chip")
            t.insert(tk.END, "   reduction\n", "side")
            t.insert(tk.END, c_prod + "\n", "product")
            t.insert(tk.END, "  " + c_eq + "  ", "eq_c")
            t.insert(tk.END, "\n\n", "gap")

            t.insert(tk.END, " ANODE (+) ", "anode_chip")
            t.insert(tk.END, "   oxidation\n", "side")
            t.insert(tk.END, a_prod + "\n", "product")
            t.insert(tk.END, "  " + a_eq + "  ", "eq_a")
            t.insert(tk.END, "\n\n", "gap")

            t.insert(tk.END, " NOTE ", "note_chip")
            t.insert(tk.END, "\n" + note + "\n", "note")

            t.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", show_selected)
        show_selected()
        animate_cell()


        # ============ Tab 2: Selective discharge rules ============
        rules_frame = tk.Frame(tab_rules, bg="#fff6e0", padx=16, pady=16)
        rules_frame.pack(fill="both", expand=True)

        # --- Visual: at-a-glance diagram of which ion "wins" at each electrode ---
        rules_canvas = tk.Canvas(rules_frame, width=940, height=230, bg="#fffdf5", highlightthickness=0)
        rules_canvas.pack(pady=(0, 12))

        def draw_reactivity_diagram():
            c = rules_canvas
            c.delete("all")
            ink = "#1b1f3b"

            # ---- Cathode (left) ----
            c.create_text(230, 16, text="CATHODE (−): which cation wins?",
                          font=("Georgia", 13, "bold"), fill=ink)
            c.create_rectangle(20, 34, 440, 104, fill="#ffe0e0", outline="#cc4444", width=2)
            c.create_text(230, 53, text="Too reactive: NOT discharged (H⁺ wins instead)",
                          font=("Segoe UI", 10, "bold"), fill="#8a1f1f")
            c.create_text(230, 81, text="K⁺     Na⁺     Ca²⁺     Mg²⁺     Al³⁺",
                          font=("Segoe UI", 14, "bold"), fill="#8a1f1f")
            c.create_rectangle(20, 114, 440, 184, fill="#e2ffe0", outline="#2e8b2e", width=2)
            c.create_text(230, 133, text="Less reactive: DISCHARGED in preference to H⁺",
                          font=("Segoe UI", 10, "bold"), fill="#1f5c1f")
            c.create_text(230, 161, text="Zn²⁺     Fe²⁺     Pb²⁺     Cu²⁺     Ag⁺",
                          font=("Segoe UI", 14, "bold"), fill="#1f5c1f")
            c.create_text(230, 207, text="↓  the less reactive the metal, the more easily it is discharged  ↓",
                          font=("Segoe UI", 9, "italic"), fill="#555555")

            # ---- Anode (right) ----
            c.create_text(710, 16, text="ANODE (+): which anion wins?",
                          font=("Georgia", 13, "bold"), fill=ink)
            rows = [
                ("#fff0c0", "#cc8800", "#7a5200", "1.  Halide (Cl⁻, Br⁻, I⁻): first, if concentrated"),
                ("#fff8dc", "#cc8800", "#7a5200", "2.  OH⁻ (from water): next, gives O₂"),
                ("#f0f0f0", "#888888", "#555555", "3.  SO₄²⁻ / NO₃⁻: never discharged"),
            ]
            for i, (fill, line, txt, label) in enumerate(rows):
                y = 34 + i * 52
                c.create_rectangle(500, y, 920, y + 44, fill=fill, outline=line, width=2)
                c.create_text(710, y + 22, text=label, font=("Segoe UI", 10, "bold"), fill=txt)
            c.create_text(710, 207, text="↓  priority order for discharge at the anode  ↓",
                          font=("Segoe UI", 9, "italic"), fill="#555555")

        draw_reactivity_diagram()

        rules_text = make_rich_text(rules_frame, bg="#fffdf5", fg="#3a2900")
        rules_text.pack(fill="both", expand=True)
        box = rules_text

        box.insert(tk.END, "Selective Discharge Rules\n", "title")
        box.insert(tk.END, "Which ion is discharged when several ions compete?\n", "sub")

        add_chip(box, "CATHODE (−)  ·  positive ions", "#1f9d55")
        add_line(box,
                 "Too reactive, never discharged: K⁺  Na⁺  Ca²⁺  Mg²⁺  Al³⁺. H⁺ is discharged instead, giving H₂ gas.")
        add_line(box, "Less reactive, discharged: Zn²⁺  Fe²⁺  Pb²⁺  Cu²⁺  Ag⁺. The metal is deposited.")
        add_line(box, "Rule of thumb: the less reactive the metal, the more easily its ion is discharged.")
        box.insert(tk.END, "\n")

        add_chip(box, "ANODE (+)  ·  negative ions", "#c2189b")
        add_line(box, "1st: a halide ion (Cl⁻, Br⁻, I⁻), if the solution is concentrated enough.")
        add_line(box, "2nd: OH⁻ from water, if there is no halide or it is too dilute. This gives O₂.")
        add_line(box, "Never: SO₄²⁻ and NO₃⁻ stay in solution as spectator ions.")
        box.insert(tk.END, "\n")

        add_chip(box, "MOLTEN  vs  AQUEOUS", "#1d4ed8")
        add_line(box,
                 "Molten: no water, so no H⁺ or OH⁻. The only ions present are discharged, however reactive the metal is.")
        add_line(box, "Aqueous: water's H⁺ and OH⁻ are always competing as well.")
        box.insert(tk.END, "\n")

        add_chip(box, "ACTIVE ELECTRODES", "#7a5200")
        add_line(box, "An active anode (e.g. copper) dissolves itself, so no anion is discharged.")
        box.insert(tk.END, "\n")

        add_chip(box, "WANT MORE PRODUCT?", "#ffb300", fg="#1b1f3b")
        add_line(box, "Increase the current, or run the electrolysis for longer.")
        box.config(state="disabled")


        # ============ Tab 3: Extraction & electroplating ============
        apps_frame = tk.Frame(tab_apps, bg="#fff6e0", padx=16, pady=16)
        apps_frame.pack(fill="both", expand=True)

        # --- Visual: simplified electroplating setup with vivid neon ions ---
        apps_canvas = tk.Canvas(apps_frame, width=900, height=190, bg="#12163a", highlightthickness=0)
        apps_canvas.pack(pady=(0, 12))

        plating_anim = {"t": 0.0, "job": None, "running": True}

        def draw_electroplating_diagram(t=0.0):
            c = apps_canvas
            c.delete("all")
            c.create_text(450, 16, text="🎨 Electroplating an object with metal", font=("Segoe UI", 11, "bold"),
                          fill="#ffd966")
            c.create_rectangle(150, 35, 750, 165, outline="#ffb300", width=3, fill="#12163a")
            c.create_rectangle(225, 20, 245, 180, fill="#c0c0c0", outline="#ffffff", width=1)
            c.create_rectangle(655, 20, 675, 180, fill="#d4af37", outline="#ffffff", width=1)
            c.create_text(235, 12, text="Object (Cathode −)", font=("Helvetica", 9, "bold"), fill="#ffffff")
            c.create_text(665, 12, text="Plating metal (Anode +)", font=("Helvetica", 9, "bold"), fill="#ffffff")

            # growing metal layer on the object — cycles to show repeated deposition
            cycle = (t * 6) % 100
            layer_w = 4 + (cycle / 100) * 10
            c.create_rectangle(245, 20, 245 + layer_w, 180, fill="#39FF14", outline="")

            metal_fill, metal_glow = "#39FF14", "#B9FFB0"
            for i in range(5):
                y = 55 + i * 22
                phase = (t * 0.5 + i * 0.2) % 1.0
                x = 630 - phase * (630 - 255)
                c.create_oval(x - 11, y - 11, x + 11, y + 11, fill=metal_glow, outline="")
                c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=metal_fill, outline="#0E5C0E", width=2)
                c.create_text(x, y, text="+", font=("Helvetica", 8, "bold"), fill="#0E5C0E")

            c.create_text(450, 172, text="Metal ions leave the anode and deposit as a thin, even coating on the object",
                          font=("Segoe UI", 9, "italic"), fill="#ffd966")

        def animate_plating():
            if not plating_anim["running"]:
                return
            plating_anim["t"] += 0.08
            try:
                draw_electroplating_diagram(plating_anim["t"])
            except tk.TclError:
                return
            if plating_anim["running"]:
                plating_anim["job"] = apps_canvas.after(60, animate_plating)

        animate_plating()

        apps_text = make_rich_text(apps_frame, bg="#fffdf5", fg="#3a2900")
        apps_text.pack(fill="both", expand=True, pady=(8, 0))
        box = apps_text

        box.insert(tk.END, "Industrial Uses of Electrolysis\n", "title")
        box.insert(tk.END, "Three important 5070 applications\n", "sub")

        add_chip(box, "EXTRACTING ALUMINIUM", "#475569")
        add_line(box, "Al is too reactive to extract by heating with carbon, so electrolysis is used instead.")
        add_line(box, "Al₂O₃ is dissolved in molten cryolite, which lowers the melting point and saves energy.")
        box.insert(tk.END, "Cathode (−):  ", "para")
        add_eq(box, "Al³⁺ + 3e⁻ → Al", "#dff5e6", "#0b4a24")
        box.insert(tk.END, "Anode (+):  ", "para")
        add_eq(box, "2O²⁻ − 4e⁻ → O₂", "#fbe0f6", "#6b0b58")
        add_line(box,
                 "Liquid aluminium collects at the bottom. The oxygen burns away the carbon anodes, so they need replacing often.")
        box.insert(tk.END, "\n")

        add_chip(box, "PURIFYING COPPER", "#b45309")
        add_line(box,
                 "Impure copper is the anode, a pure copper sheet is the cathode, and CuSO₄(aq) is the electrolyte.")
        box.insert(tk.END, "Anode (+):  ", "para")
        add_eq(box, "Cu − 2e⁻ → Cu²⁺", "#fbe0f6", "#6b0b58")
        box.insert(tk.END, "Cathode (−):  ", "para")
        add_eq(box, "Cu²⁺ + 2e⁻ → Cu", "#dff5e6", "#0b4a24")
        add_line(box,
                 "Unreactive impurities such as gold and silver do not dissolve. They fall away as anode sludge, a valuable by-product.")
        box.insert(tk.END, "\n")

        add_chip(box, "ELECTROPLATING", "#7c3aed")
        add_line(box,
                 "The object to be plated is the cathode, the plating metal is the anode, and the solution contains ions of the plating metal.")
        add_line(box, "The anode dissolves and the same metal is deposited evenly on the object.")
        add_line(box, "Why bother? It stops rust, improves appearance, or coats a cheap metal in a more valuable one.")
        box.config(state="disabled")

        def close_volt():
            cell_anim["running"] = False
            plating_anim["running"] = False
            for job_dict, widget in ((cell_anim, canvas), (plating_anim, apps_canvas)):
                if job_dict["job"]:
                    try:
                        widget.after_cancel(job_dict["job"])
                    except Exception:
                        pass
            play_sound("window_close")
            w.destroy()

        w.protocol("WM_DELETE_WINDOW", close_volt)
        ttk.Button(w, text="Close", command=close_volt).pack(pady=(0, 10))

    # -------------------------
    # Top Scores window — permanent Hall of Fame (names + scores only),
    # populated whenever the leaderboard is reset. All content here is
    # centered, giving equal empty space above and below it.
    # -------------------------
    def show_top_scores(self):
        play_sound("top_scores_open")
        win = tk.Toplevel(self.root)
        enable_fullscreen(win)
        win.title("🏅 Top Scores — Hall of Fame")
        win.geometry("640x600")
        win.configure(bg="#fff3d6")
        win.transient(self.root)

        outer = tk.Frame(win, bg="#fff3d6")
        outer.pack(expand=True)

        tk.Label(outer, text="🏅 All-Time Top 10 Lab Legends 🏅",
                 font=self.header_font, bg="#fff3d6", fg="#7A2E00").pack(pady=(0, 6))
        tk.Label(outer, text="Saved automatically whenever the leaderboard is reset.",
                 font=("Segoe UI", 10, "italic"), bg="#fff3d6", fg="#7A2E00").pack(pady=(0, 16))

        ts_style = ttk.Style()
        ts_style.configure("TopScores.Treeview", font=self.header_font, rowheight=28)
        ts_style.configure("TopScores.Treeview.Heading", font=self.btn_font)

        columns = ("rank", "name", "score", "bonus")
        tree = ttk.Treeview(outer, columns=columns, show="headings", height=10,
                            style="TopScores.Treeview")
        tree.heading("rank", text="#")
        tree.heading("name", text="Name")
        tree.heading("score", text="Score /10")
        tree.heading("bonus", text="Bonus")
        tree.column("rank", width=50, anchor="center")
        tree.column("name", width=220, anchor="w")
        tree.column("score", width=130, anchor="center")
        tree.column("bonus", width=130, anchor="center")
        tree.pack()

        empty_label = tk.Label(
            outer,
            text="No top scores yet — reset the leaderboard after a great\n"
                 "quiz session to add players here!",
            font=("Segoe UI", 11), bg="#fff3d6", fg="#7A2E00", justify="center")

        def fill_tree():
            for row in tree.get_children():
                tree.delete(row)
            top = load_top_scores()
            for i, e in enumerate(top, start=1):
                tree.insert("", tk.END, values=(i, e.get("name", "Anon"),
                                                f"{e.get('score', 0)}/10",
                                                f"+{e.get('bonus', 0)}"))
            if top:
                empty_label.pack_forget()
                erase_btn.config(state="normal")
            else:
                empty_label.pack(pady=(18, 0))
                erase_btn.config(state="disabled")

        def erase_all():
            if not load_top_scores():
                return
            play_sound("reset_open")
            if not messagebox.askyesno(
                    "Erase All-Time Legends?",
                    "This will permanently delete EVERY name in the all-time "
                    "Top Scores hall of fame. This cannot be undone.\n\nContinue?",
                    icon="warning", parent=win):
                play_sound("confirm_no")
                return
            play_sound("confirm_yes")
            clear_top_scores()
            fill_tree()
            messagebox.showinfo("Hall of Fame Cleared",
                                "🗑️ All-time Top Scores have been erased.", parent=win)

        btn_row = tk.Frame(outer, bg="#fff3d6")
        btn_row.pack(pady=(20, 0))
        erase_btn = tk.Button(btn_row, text="🗑️ Erase All-Time Legends", font=self.btn_font,
                              bg="#ef233c", fg="black", disabledforeground="black",
                              activebackground="#c1121f", activeforeground="black",
                              relief="flat", padx=14, pady=6,
                              cursor="hand2", command=erase_all)
        erase_btn.grid(row=0, column=0, padx=8)
        tk.Button(btn_row, text="Close", font=self.btn_font, bg="#f6b26b", relief="flat",
                  padx=14, pady=6, command=win.destroy).grid(row=0, column=1, padx=8)

        fill_tree()



# ----------------------------
# Program entry point
# ----------------------------

def main():
    root = tk.Tk()
    app = BondBalancerApp(root)
    root.mainloop()

if __name__ == "__main__":
  main()