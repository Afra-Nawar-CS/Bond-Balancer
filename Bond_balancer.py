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
            parts.append(f"{(str(c) if c != 1 else '')}{pretty_formula(s)}".strip())
        return " + ".join(parts)

    steps.append("Balanced equation: " + fmt_list(rcoeffs, reactants) + " → " + fmt_list(pcoeffs, products))
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
    ("What is the ionic equation for the reaction: AgNO₃(aq) + NaCl(aq) → AgCl(s) + NaNO₃(aq)?",
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
        lb_style.configure("Leaderboard.Treeview", font=self.header_font, rowheight=28,
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

    def reset_leaderboard(self):
        """Archive the current leaderboard's best scores into the permanent
        Top Scores hall of fame, then clear all names from the active
        leaderboard so it can start fresh."""
        lb = load_leaderboard()
        if not lb:
            messagebox.showinfo("Leaderboard Empty", "There are no scores on the leaderboard to reset.")
            return
        play_sound("reset_open")
        res = messagebox.askyesno(
            "Reset Leaderboard?",
            "This will save the best scorers into the Top Scores hall of fame, "
            "then remove all names from the current leaderboard. Continue?"
        )
        if not res:
            play_sound("confirm_no")
            return
        play_sound("confirm_yes")
        archive_top_scores_and_clear()
        self.refresh_leaderboard_display()
        messagebox.showinfo("Leaderboard Reset",
                            "🧹 Leaderboard cleared! Top scorers have been saved to the Top Scores hall of fame.")

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
        ttk.Button(footer, text="🏆 Refresh Leaderboard",
                   command=self.refresh_leaderboard_display).pack()

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
    def open_gas_window(self):
        # 🌊 Create top-level window
        play_sound("gas_open")  # sound when window opens
        w = tk.Toplevel(self.root)
        w.title("Interactive Gas Reactions — Mix & Learn")
        w.geometry("940x640")

        # Main frame
        self.gas_frame = tk.Frame(w, padx=12, pady=12, bg="#7df3e1")
        self.gas_frame.pack(fill="both", expand=True)

        tk.Label(self.gas_frame, text="Pick two reactants, set amounts, then Run Reaction",
                 font=self.header_font, bg="#7df3e1").pack(pady=(4, 8))

        # Gas species and emojis
        self.gas_species = ["H2", "O2", "Cl2", "K", "N2", "CH4"]
        self.gas_sel = {}
        self.gas_labels = {}

        emoji_map = {
            "H2": "💧",
            "O2": "🌬️",
            "Cl2": "🧪",
            "K": "⚙️",
            "N2": "💨",
            "CH4": "🔥"
        }

        species_frame = tk.Frame(self.gas_frame, bg="#7df3e1")
        species_frame.pack(pady=(8, 6))

        for i, g in enumerate(self.gas_species):
            sub = tk.Frame(species_frame, bg="#7df3e1", padx=6, pady=6)
            sub.grid(row=0, column=i, padx=12)

            self.gas_sel[g] = tk.BooleanVar(value=False)
            lbl = tk.Label(sub, text=f"{emoji_map[g]}\n{g}", font=("Segoe UI Emoji", 14),
                           bg="#eafbe7", width=6, relief="ridge", bd=2)
            lbl.pack()
            self.gas_labels[g] = lbl

            def toggle(var=self.gas_sel[g], label=lbl):
                var.set(not var.get())
                label.config(bg="#b6d7a8" if var.get() else "#eafbe7")
                # soft ping sound when selecting gases
                self.root.after(10, lambda: winsound.Beep(550, 40))

            lbl.bind("<Button-1>", lambda e, f=toggle: f())

        # Amount sliders
        amt_frame = tk.Frame(self.gas_frame, bg="#7df3e1")
        amt_frame.pack(pady=(8, 12))
        tk.Label(amt_frame, text="Reactant 1 amount (mol):", bg="#7df3e1").grid(row=0, column=0, padx=6)
        tk.Label(amt_frame, text="Reactant 2 amount (mol):", bg="#7df3e1").grid(row=0, column=2, padx=6)
        self.amt1 = tk.DoubleVar(value=1)
        self.amt2 = tk.DoubleVar(value=1)

        # function to play sound on slider move
        def slider_click(_):
            winsound.Beep(750, 30)

        scale1 = ttk.Scale(amt_frame, from_=0.5, to=5, orient="horizontal", variable=self.amt1, length=160)
        scale2 = ttk.Scale(amt_frame, from_=0.5, to=5, orient="horizontal", variable=self.amt2, length=160)
        scale1.grid(row=0, column=1)
        scale2.grid(row=0, column=3)
        scale1.bind("<ButtonRelease-1>", slider_click)
        scale2.bind("<ButtonRelease-1>", slider_click)

        tk.Label(amt_frame, textvariable=self.amt1, bg="#7df3e1").grid(row=1, column=1)
        tk.Label(amt_frame, textvariable=self.amt2, bg="#7df3e1").grid(row=1, column=3)

        # Buttons: Run Reaction + Reset Selection
        btn_frame = tk.Frame(self.gas_frame, bg="#7df3e1")
        btn_frame.pack(pady=(10, 6))

        tk.Button(btn_frame, text="Run Reaction ⚡", font=self.btn_font, bg="#93c47d",
                  fg="white", command=self.run_gas_reaction).grid(row=0, column=0, padx=8)

        tk.Button(btn_frame, text="Reset Selection 🔄", font=self.btn_font, bg="#ffd966",
                  command=lambda: self.reset_gas_selection()).grid(row=0, column=1, padx=8)

        # Output area
        self.gas_output = tk.Text(self.gas_frame, width=90, height=14, font=self.mono, bg="#dafff9",
                                  fg="#222222", wrap="word")
        self.gas_output.pack(pady=(6, 10), fill="both", expand=True)
        self.gas_output.insert(tk.END, "Results of your reaction will appear here.\n")
        self.gas_output.config(state="disabled")

        ttk.Button(w, text="Close", command=lambda: (play_sound("window_close"), w.destroy())).pack(pady=(0, 10))

    def reset_gas_selection(self):
        """Reset all gas selections and label colors."""
        for g in self.gas_species:
            self.gas_sel[g].set(False)
            self.gas_labels[g].config(bg="#eafbe7")
        winsound.Beep(500, 60)
        self.gas_output.config(state="normal")
        self.gas_output.insert(tk.END, "🧹 All reactants deselected.\n\n")
        self.gas_output.config(state="disabled")

    def run_gas_reaction(self):
        selected = [g for g, v in self.gas_sel.items() if v.get()]
        if len(selected) != 2:
            messagebox.showwarning("Need 2 reactants", "Please select exactly two gases/reactants.")
            self.root.after(10, lambda: winsound.Beep(400, 200))  # error sound
            return

        amt1 = self.amt1.get()
        amt2 = self.amt2.get()
        a, b = selected

        reaction, product_emoji = self.predict_reaction(a, b)

        # Flash selected labels
        def flash_labels(labels, count=6):
            if count == 0:
                for lbl in labels:
                    lbl.config(bg="#eafbe7")
                self.root.after(100, lambda: winsound.Beep(500, 70))
                return
            color = "#ffd966" if count % 2 == 0 else "#b6d7a8"
            for lbl in labels:
                lbl.config(bg=color)
            self.root.after(150, lambda: flash_labels(labels, count - 1))

        flash_labels([self.gas_labels[a], self.gas_labels[b]])

        # Build result text
        result_text = f"🧪 Experiment Result:\nReacting {amt1} mol of {a} with {amt2} mol of {b}...\n\n"
        if reaction:
            result_text += f"🔹 Predicted Reaction:\n    {reaction}\n\n"
            result_text += f"🔸 Stoichiometric ratio ~ {amt1}:{amt2}\n"
            result_text += f"✨ Product likely: {product_emoji}\n✅ Balanced automatically."
            play_sound("reaction")
        else:
            result_text += f"⚠️ Reaction cannot occur between {a} and {b}.\n"
            play_sound("wrong")  # or use winsound.Beep(350, 250)

        # Append to output and trim if needed
        self.gas_output.config(state="normal")
        MAX_OUTPUT_LINES = 300
        current_lines = int(self.gas_output.index('end-1c').split('.')[0])
        if current_lines > MAX_OUTPUT_LINES:
            self.gas_output.delete("1.0", "end")
            self.gas_output.insert(tk.END, "🧪 Starting a new log — old results cleared.\n\n")

        self.gas_output.insert(tk.END, result_text + "\n\n" + "-" * 80 + "\n\n")
        self.gas_output.see(tk.END)
        self.gas_output.config(state="disabled")

        # Animate product emoji
        if reaction:
            def animate_product(i=0):
                if i >= 6:
                    return
                color = "#ffd966" if i % 2 == 0 else "#ffffff"
                self.gas_output.tag_config("flash", background=color)
                self.gas_output.tag_add("flash", "end-2l", "end-1l")
                self.root.after(300, lambda: animate_product(i + 1))

            animate_product()

    def predict_reaction(self, a, b):
        # Define element types
        metal = {"K", "Na", "Ca", "Mg", "Fe", "Zn"}
        nonmetal = {"H2", "O2", "Cl2", "N2", "C", "CO", "CH4"}

        # Known direct reactions (ionic, combustion, covalent)
        combos = {
            ("H2", "O2"): ("2H2 + O2 → 2H2O", "💧 Water formed! (covalent)"),
            ("H2", "Cl2"): ("H2 + Cl2 → 2HCl", "🌫️ Hydrogen Chloride gas (covalent)"),
            ("CH4", "O2"): ("CH4 + 2O2 → CO2 + 2H2O", "🔥 Combustion releasing CO₂ and H₂O"),
            ("N2", "H2"): ("N2 + 3H2 → 2NH3", "💨 Ammonia gas (covalent)"),
            ("C", "O2"): ("C + O2 → CO2", "🌫️ Carbon dioxide forms (covalent)"),
            ("CO", "O2"): ("2CO + O2 → 2CO2", "💨 Carbon monoxide oxidized to CO₂"),
            ("K", "Cl2"): ("2K + Cl2 → 2KCl", "🧂 Potassium chloride (ionic)"),
            ("K", "O2"): ("4K + O2 → 2K2O", "⚙️ Potassium oxide (ionic)"),
        }

        # Check for known combo (order-independent)
        for (x, y), (eq, emoji) in combos.items():
            if {a, b} == {x, y}:
                return eq, emoji

        # --- NEW LOGIC: Predict based on element types ---
        # Metal + Nonmetal → Ionic
        if (a in metal and b in nonmetal) or (b in metal and a in nonmetal):
            return f"{a} + {b} → {a}{b}", "🧂 Ionic compound likely formed."

        # Nonmetal + Nonmetal → Covalent
        if (a in nonmetal and b in nonmetal):
            return f"{a} + {b} → Covalent molecule", "🔗 Covalent bond likely formed."

        # Same element → no new compound
        if a == b:
            return None, f"⚠️ {a} with {b}: No reaction (same element)."

        # Unknown → return descriptive error line
        return None, f"❌ No known reaction between {a} and {b}. Possibly inert under normal conditions."

    # -------------------------
    # AtoMole Arena — atomic structure + moles/stoichiometry, combined
    # (name blends "Atom" + "Mole"; violet colour theme; atomole_* sounds)
    # -------------------------
    def open_atomole_window(self):
        play_sound("atomole_open")
        w = tk.Toplevel(self.root)
        w.title("AtoMole Arena — Atomic Structure & Mole Calculations")
        # Sized extra generously so every card, label, and result line in
        # both tabs (including the Mole Calculator's three stacked cards)
        # is fully visible without needing to maximize the window.
        w.geometry("1360x980")
        w.minsize(1250, 900)
        w.configure(bg="#ede0ff")

        header = tk.Frame(w, bg="#5b21b6")
        header.pack(fill="x")
        tk.Label(header, text="⚛️ AtoMole Arena — where atoms meet moles⚙️",
                 font=self.header_font, bg="#5b21b6", fg="#ffffff", pady=10).pack()

        notebook = ttk.Notebook(w)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_atoms = tk.Frame(notebook, bg="#ede0ff")
        tab_moles = tk.Frame(notebook, bg="#f3ecff")
        notebook.add(tab_atoms, text="⚛️ Atomic Structure")
        notebook.add(tab_moles, text="⚙️ Mole Calculator")

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
        canvas.pack(pady=(14, 6))

        info_label = tk.Label(right_frame, text="", font=("Segoe UI", 12), bg="#ffffff",
                               justify="left", anchor="w")
        info_label.pack(fill="x", padx=16, pady=(4, 12))

        def draw_atom(sym):
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
                for e_idx in range(n_electrons):
                    angle = 2 * math.pi * e_idx / n_electrons - math.pi / 2
                    ex = cx + radius * math.cos(angle)
                    ey = cy + radius * math.sin(angle)
                    canvas.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                                        fill=shell_colors[i % len(shell_colors)], outline="#333333")

            protons = z
            neutrons = a - z
            electrons = sum(shells)
            config_str = ",".join(str(s) for s in shells)
            info_text = (
                f"Element: {name} ({sym})\n"
                f"Atomic number (protons): {protons}\n"
                f"Mass number: {a}\n"
                f"Neutrons: {neutrons}\n"
                f"Electrons: {electrons}\n"
                f"Electron configuration: {config_str}\n"
                f"Occupied shells (period): {len(shells)}\n"
                f"Outer shell (valence) electrons: {shells[-1]}"
            )
            info_label.config(text=info_text)

        def on_select(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            play_sound("atomole_select")
            sym = symbols[sel[0]]
            draw_atom(sym)

        listbox.bind("<<ListboxSelect>>", on_select)
        draw_atom(symbols[0])

        # ============ Tab 2: Mole / stoichiometry calculator ============
        mfrm = tk.Frame(tab_moles, bg="#f3ecff", padx=18, pady=16)
        mfrm.pack(fill="both", expand=True)

        tk.Label(mfrm, text="⚙️ Mole Calculator", font=("Georgia", 18, "bold"),
                 bg="#f3ecff", fg="#5b21b6").pack(pady=(0, 2))
        tk.Label(mfrm, text="Pick a calculation, enter what you know, and let AtoMole do the rest ✨",
                 font=("Segoe UI", 11, "italic"), bg="#f3ecff", fg="#6b5b8a").pack(pady=(0, 14))

        # --- Card 1: choose calculation type ---
        calc_card = tk.LabelFrame(mfrm, text="  ①  Choose a Calculation  ", font=self.header_font,
                                  bg="#ffffff", fg="#5b21b6", bd=2, relief="ridge", labelanchor="n",
                                  padx=14, pady=12)
        calc_card.pack(fill="x", pady=(0, 14))

        calc_types = [
            "Mass & Mr → Moles",
            "Moles & Mr → Mass",
            "Moles & Volume(dm³) → Concentration (mol/dm³)",
            "Concentration & Volume(dm³) → Moles",
            "Moles → Volume of gas at r.t.p. (dm³)",
        ]
        calc_var = tk.StringVar(value=calc_types[0])
        combo_style = ttk.Style()
        combo_style.configure("AtoMole.TCombobox", font=("Segoe UI", 12))
        combo = ttk.Combobox(calc_card, textvariable=calc_var, values=calc_types, state="readonly",
                              width=48, font=("Segoe UI", 12), style="AtoMole.TCombobox")
        combo.pack(fill="x", ipady=4)

        # --- Card 2: enter known values ---
        values_card = tk.LabelFrame(mfrm, text="  ②  Enter Known Values  ", font=self.header_font,
                                    bg="#ffffff", fg="#5b21b6", bd=2, relief="ridge", labelanchor="n",
                                    padx=14, pady=14)
        values_card.pack(fill="x", pady=(0, 14))
        values_card.grid_columnconfigure(1, weight=1)

        entry_font = ("Segoe UI", 13)
        label_a_widget = tk.Label(values_card, text="⚖️ Mass", font=("Segoe UI", 12, "bold"),
                                   bg="#ffffff", fg="#3B0A63", width=16, anchor="w")
        label_a_widget.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="w")
        val_a = tk.StringVar()
        entry_a = tk.Entry(values_card, textvariable=val_a, width=16, font=entry_font,
                            relief="solid", bd=1, highlightthickness=1,
                            highlightcolor="#8e44ec", highlightbackground="#d8c8f0")
        entry_a.grid(row=0, column=1, padx=6, pady=8, sticky="w")
        unit_a = tk.Label(values_card, text="g", font=("Segoe UI", 11, "italic"), bg="#ffffff", fg="#8e44ec")
        unit_a.grid(row=0, column=2, padx=6, sticky="w")

        label_b_widget = tk.Label(values_card, text="🔬 Mr (Molar Mass)", font=("Segoe UI", 12, "bold"),
                                   bg="#ffffff", fg="#3B0A63", width=16, anchor="w")
        label_b_widget.grid(row=1, column=0, padx=(0, 10), pady=8, sticky="w")
        val_b = tk.StringVar()
        entry_b = tk.Entry(values_card, textvariable=val_b, width=16, font=entry_font,
                            relief="solid", bd=1, highlightthickness=1,
                            highlightcolor="#8e44ec", highlightbackground="#d8c8f0")
        entry_b.grid(row=1, column=1, padx=6, pady=8, sticky="w")
        unit_b = tk.Label(values_card, text="g/mol", font=("Segoe UI", 11, "italic"), bg="#ffffff", fg="#8e44ec")
        unit_b.grid(row=1, column=2, padx=6, sticky="w")

        # label text, unit, and whether the field is needed for each calc type
        field_labels = {
            "Mass & Mr → Moles": ("⚖️ Mass", "g", "🔬 Mr (Molar Mass)", "g/mol", True),
            "Moles & Mr → Mass": ("⚙️ Moles", "mol", "🔬 Mr (Molar Mass)", "g/mol", True),
            "Moles & Volume(dm³) → Concentration (mol/dm³)": ("⚙️ Moles", "mol", "🧫 Volume", "dm³", True),
            "Concentration & Volume(dm³) → Moles": ("🌊 Concentration", "mol/dm³", "🧫 Volume", "dm³", True),
            "Moles → Volume of gas at r.t.p. (dm³)": ("⚙️ Moles", "mol", "— not needed", "", False),
        }

        def update_labels(event=None):
            a_lbl, a_unit, b_lbl, b_unit, b_needed = field_labels[calc_var.get()]
            label_a_widget.config(text=a_lbl)
            unit_a.config(text=a_unit)
            label_b_widget.config(text=b_lbl)
            unit_b.config(text=b_unit)
            if b_needed:
                entry_b.config(state="normal", bg="#ffffff")
            else:
                val_b.set("")
                entry_b.config(state="disabled", bg="#f0eaf9")

        combo.bind("<<ComboboxSelected>>", update_labels)
        update_labels()

        # --- Action buttons ---
        btn_frame = tk.Frame(mfrm, bg="#f3ecff")
        btn_frame.pack(pady=(0, 14))
        tk.Button(btn_frame, text="Calculate ✨", font=self.btn_font, bg="#8e44ec", fg="white",
                  activebackground="#7a2fd1", activeforeground="white", relief="flat",
                  padx=18, pady=8, command=lambda: calculate()).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Clear 🗑️ ", font=self.btn_font, bg="#e5d6ff", fg="#5b21b6",
                  activebackground="#d8c0ff", activeforeground="#5b21b6", relief="flat",
                  padx=18, pady=8, command=lambda: clear_fields()).grid(row=0, column=1, padx=8)

        # --- Card 3: result ---
        result_card = tk.LabelFrame(mfrm, text="  ③  Result  ", font=self.header_font,
                                    bg="#ffffff", fg="#5b21b6", bd=2, relief="ridge", labelanchor="n",
                                    padx=10, pady=10)
        result_card.pack(fill="both", expand=True)

        steps_text = tk.Text(result_card, font=("Segoe UI", 12), wrap="word", bg="#ffffff",
                              fg="#3B0A63", height=10, relief="flat", padx=10, pady=8)
        steps_text.pack(fill="both", expand=True)
        steps_text.tag_config("type", font=("Segoe UI", 13, "bold"), foreground="#5b21b6",
                               spacing3=6)
        steps_text.tag_config("formula", font=("Courier New", 12, "italic"), foreground="#6b5b8a",
                               spacing3=6)
        steps_text.tag_config("calc", font=("Courier New", 12), foreground="#333333", spacing3=6)
        steps_text.tag_config("answer", font=("Courier New", 14, "bold"), foreground="#0b6e4f",
                               background="#e2ffe0", spacing1=4, spacing3=4)
        steps_text.tag_config("error", font=("Segoe UI", 12, "bold"), foreground="#b00020")
        steps_text.insert(tk.END, "👋 Pick a calculation above, fill in the values, then hit Calculate ✨")
        steps_text.config(state="disabled")

        def clear_fields():
            val_a.set("")
            val_b.set("")
            steps_text.config(state="normal")
            steps_text.delete("1.0", tk.END)
            steps_text.insert(tk.END, "👋 Pick a calculation above, fill in the values, then hit Calculate ✨")
            steps_text.config(state="disabled")
            play_sound("atomole_clear")  # was play_sound("click")


        def on_calc_change(event=None):
            play_sound("atomole_calc_change")
            update_labels()

        combo.bind("<<ComboboxSelected>>", on_calc_change)
        update_labels()

        def calculate():
            play_sound("atomole_calculate")
            ctype = calc_var.get()
            try:
                a_str = val_a.get().strip()
                b_str = val_b.get().strip()
                a_num = float(a_str) if a_str else None
                b_num = float(b_str) if b_str else None

                lines = [(f"📌 {ctype}", "type")]

                if ctype == "Mass & Mr → Moles":
                    if a_num is None or b_num is None or b_num == 0:
                        raise ValueError("Please enter both mass and Mr (Mr must not be 0).")
                    moles = a_num / b_num
                    lines.append(("Formula:  moles = mass ÷ Mr", "formula"))
                    lines.append((f"Substitute:  moles = {a_num} g ÷ {b_num} g/mol", "calc"))
                    lines.append((f"✅ moles = {moles:.4g} mol", "answer"))

                elif ctype == "Moles & Mr → Mass":
                    if a_num is None or b_num is None:
                        raise ValueError("Please enter both moles and Mr.")
                    mass = a_num * b_num
                    lines.append(("Formula:  mass = moles × Mr", "formula"))
                    lines.append((f"Substitute:  mass = {a_num} mol × {b_num} g/mol", "calc"))
                    lines.append((f"✅ mass = {mass:.4g} g", "answer"))

                elif ctype == "Moles & Volume(dm³) → Concentration (mol/dm³)":
                    if a_num is None or b_num is None or b_num == 0:
                        raise ValueError("Please enter moles and volume (volume must not be 0).")
                    conc = a_num / b_num
                    lines.append(("Formula:  concentration = moles ÷ volume (dm³)", "formula"))
                    lines.append((f"Substitute:  concentration = {a_num} mol ÷ {b_num} dm³", "calc"))
                    lines.append((f"✅ concentration = {conc:.4g} mol/dm³", "answer"))

                elif ctype == "Concentration & Volume(dm³) → Moles":
                    if a_num is None or b_num is None:
                        raise ValueError("Please enter concentration and volume.")
                    moles = a_num * b_num
                    lines.append(("Formula:  moles = concentration × volume (dm³)", "formula"))
                    lines.append((f"Substitute:  moles = {a_num} mol/dm³ × {b_num} dm³", "calc"))
                    lines.append((f"✅ moles = {moles:.4g} mol", "answer"))

                elif ctype == "Moles → Volume of gas at r.t.p. (dm³)":
                    if a_num is None:
                        raise ValueError("Please enter moles in the first field.")
                    vol = a_num * 24
                    lines.append(("Formula:  volume (dm³) = moles × 24 dm³/mol  (r.t.p. molar volume)", "formula"))
                    lines.append((f"Substitute:  volume = {a_num} mol × 24 dm³/mol", "calc"))
                    lines.append((f"✅ volume = {vol:.4g} dm³", "answer"))

                steps_text.config(state="normal")
                steps_text.delete("1.0", tk.END)
                for text, tag in lines:
                    steps_text.insert(tk.END, text + "\n\n", tag)
                steps_text.config(state="disabled")
                play_sound("success")

            except ValueError as e:
                steps_text.config(state="normal")
                steps_text.delete("1.0", tk.END)
                steps_text.insert(tk.END, f"⚠️  {e}", "error")
                steps_text.config(state="disabled")
                play_sound("wrong")

        ttk.Button(w, text="Close", command=lambda: (play_sound("window_close"), w.destroy())).pack(pady=(0, 10))

    # -------------------------
    # Carbon Craft — organic chemistry explorer
    # (green colour theme; organic_* sounds)
    # -------------------------
    def open_organic_window(self):
        play_sound("organic_open")
        w = tk.Toplevel(self.root)
        w.title("Carbon Craft — Organic Chemistry Explorer")
        w.geometry("1000x660")
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

        info_text = tk.Text(right_frame, font=("Courier New", 11), wrap="word",
                             bg="#f0fff7", fg="#0b3d2e", height=11)
        info_text.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        info_text.config(state="disabled")

        atom_colors = {"C": "#333333", "H": "#93c47d", "O": "#e06666"}

        def draw_structure(data):
            canvas.delete("all")
            atoms = data["atoms"]
            bonds = data["bonds"]
            # draw bonds first (so atoms sit on top)
            for i, j, order in bonds:
                x1, y1 = atoms[i][1], atoms[i][2]
                x2, y2 = atoms[j][1], atoms[j][2]
                if order == 1:
                    canvas.create_line(x1, y1, x2, y2, width=3, fill="#0b6e4f")
                else:
                    # double bond: two parallel offset lines
                    dx, dy = x2 - x1, y2 - y1
                    length = math.hypot(dx, dy) or 1
                    ox, oy = -dy / length * 5, dx / length * 5
                    canvas.create_line(x1 + ox, y1 + oy, x2 + ox, y2 + oy, width=3, fill="#0b6e4f")
                    canvas.create_line(x1 - ox, y1 - oy, x2 - ox, y2 - oy, width=3, fill="#0b6e4f")
            # draw atoms
            for sym, x, y in atoms:
                r = 16 if sym == "C" else 12
                canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=atom_colors.get(sym, "#cccccc"), outline="#222222", width=1.5)
                canvas.create_text(x, y, text=sym, font=("Helvetica", 10, "bold"),
                                    fill="white" if sym != "H" else "#222222")

        def show_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            play_sound("organic_select")
            key = series_keys[sel[0]]
            data = ORGANIC_DATA[key]
            draw_structure(data)

            info_text.config(state="normal")
            info_text.delete("1.0", tk.END)
            lines = [
                f"✨ Homologous series: {key}",
                f"General formula: {data['general_formula']}",
                f"Functional group: {data['functional_group']}",
                "",
                f"Example: {data['example_name']} ({data['example_formula']})",
                "",
                f"Key reaction/test: {data['reaction']}",
                "",
                f"Common uses: {data['uses']}",
            ]
            for s in lines:
                info_text.insert(tk.END, s + "\n")
            info_text.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", show_selected)
        show_selected()

        ttk.Button(w, text="Close", command=lambda: (play_sound("window_close"), w.destroy())).pack(pady=(0, 10))

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
        w.title("Volt Vault — Electrolysis, Selective Discharge, Extraction & Electroplating")
        w.geometry("1040x700")
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

        canvas = tk.Canvas(right_frame, width=460, height=220, bg="#ffffff", highlightthickness=0)
        canvas.pack(pady=(10, 4))

        result_text = tk.Text(right_frame, font=("Courier New", 11), wrap="word",
                               bg="#fff9ea", fg="#4a3200", height=13)
        result_text.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        result_text.config(state="disabled")

        def draw_cell():
            canvas.delete("all")
            canvas.create_rectangle(60, 40, 400, 190, outline="#ffb300", width=3, fill="#12163a")
            canvas.create_rectangle(120, 20, 140, 210, fill="#555555", outline="#1b1f3b")
            canvas.create_rectangle(320, 20, 340, 210, fill="#555555", outline="#1b1f3b")
            canvas.create_text(130, 12, text="Cathode (−)", font=("Helvetica", 10, "bold"))
            canvas.create_text(330, 12, text="Anode (+)", font=("Helvetica", 10, "bold"))

            # Vivid neon ions — cations (bright neon green) drift toward the
            # cathode on the left, anions (bright neon magenta) drift toward
            # the anode on the right. A soft glow halo behind each ion makes
            # them pop against the dark electrolyte background.
            cation_fill = "#39FF14"      # neon green
            cation_glow = "#B9FFB0"
            cation_outline = "#0E5C0E"
            anion_fill = "#FF2EF2"       # neon magenta
            anion_glow = "#FFC2FB"
            anion_outline = "#7A0E63"

            for i in range(4):
                cy = 65 + i * 30
                cx = 165 + (i % 2) * 12
                canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12, fill=cation_glow, outline="")
                canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=cation_fill, outline=cation_outline, width=2)
                canvas.create_text(cx, cy, text="+", font=("Helvetica", 9, "bold"), fill="#0E5C0E")

                ax = 295 - (i % 2) * 12
                ay = 65 + i * 30
                canvas.create_oval(ax - 12, ay - 12, ax + 12, ay + 12, fill=anion_glow, outline="")
                canvas.create_oval(ax - 8, ay - 8, ax + 8, ay + 8, fill=anion_fill, outline=anion_outline, width=2)
                canvas.create_text(ax, ay, text="−", font=("Helvetica", 9, "bold"), fill="#7A0E63")

            canvas.create_text(230, 220, text="Ions migrate through the electrolyte to opposite electrodes",
                                font=("Segoe UI", 9, "italic"))

        def show_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            play_sound("electro_select")
            key = electrolyte_keys[sel[0]]
            electrodes, c_prod, c_eq, a_prod, a_eq, note = ELECTROLYSIS_DATA[key]
            draw_cell()

            result_text.config(state="normal")
            result_text.delete("1.0", tk.END)
            lines = [
                f"✨ Electrolyte: {key}",
                f"Electrodes used: {electrodes}",
                "",
                f"🔹 At the CATHODE (−): {c_prod}",
                f"    Half-equation: {c_eq}",
                "",
                f"🔸 At the ANODE (+): {a_prod}",
                f"    Half-equation: {a_eq}",
                "",
                f"Note: {note}",
            ]
            for s in lines:
                result_text.insert(tk.END, s + "\n")
            result_text.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", show_selected)
        show_selected()

        # ============ Tab 2: Selective discharge rules ============
        rules_frame = tk.Frame(tab_rules, bg="#fff6e0", padx=16, pady=16)
        rules_frame.pack(fill="both", expand=True)

        # --- Visual: at-a-glance diagram of which ion "wins" at each electrode ---
        rules_canvas = tk.Canvas(rules_frame, width=900, height=190, bg="#fffdf5", highlightthickness=0)
        rules_canvas.pack(pady=(0, 12))

        def draw_reactivity_diagram():
            c = rules_canvas
            c.delete("all")
            # ---- Cathode ladder (left) ----
            c.create_text(165, 14, text="⚡ CATHODE (−): which cation wins?",
                           font=("Segoe UI", 11, "bold"), fill="#1b1f3b")
            c.create_rectangle(20, 28, 310, 92, fill="#ffe0e0", outline="#cc4444", width=2)
            c.create_text(165, 40, text="NOT discharged (too reactive) — H⁺ wins instead",
                           font=("Segoe UI", 8, "bold"), fill="#8a1f1f")
            c.create_text(165, 64, text="K⁺   Na⁺   Ca²⁺   Mg²⁺   Al³⁺", font=("Consolas", 11, "bold"), fill="#8a1f1f")
            c.create_rectangle(20, 98, 310, 162, fill="#e2ffe0", outline="#2e8b2e", width=2)
            c.create_text(165, 110, text="DISCHARGED in preference to H⁺",
                           font=("Segoe UI", 8, "bold"), fill="#1f5c1f")
            c.create_text(165, 134, text="Zn²⁺   Fe²⁺   Pb²⁺   Cu²⁺   Ag⁺", font=("Consolas", 11, "bold"), fill="#1f5c1f")
            c.create_text(165, 178, text="↓ less reactive metals are discharged more easily ↓",
                           font=("Segoe UI", 8, "italic"), fill="#555555")

            # ---- Anode ladder (right) ----
            c.create_text(625, 14, text="⚡ ANODE (+): which anion wins?",
                           font=("Segoe UI", 11, "bold"), fill="#1b1f3b")
            c.create_rectangle(460, 28, 790, 66, fill="#fff0c0", outline="#cc8800", width=2)
            c.create_text(625, 47, text="1️⃣    Halide (Cl⁻, Br⁻, I⁻) — discharged first, if concentrated",
                           font=("Segoe UI", 9, "bold"), fill="#7a5200")
            c.create_rectangle(460, 71, 790, 109, fill="#fff8dc", outline="#cc8800", width=2)
            c.create_text(625, 90, text="2️⃣     OH⁻ (from water) — discharged next, gives O₂",
                           font=("Segoe UI", 9, "bold"), fill="#7a5200")
            c.create_rectangle(460, 114, 790, 152, fill="#f0f0f0", outline="#888888", width=2)
            c.create_text(625, 133, text="3️⃣    SO₄²⁻ / NO₃⁻ — NEVER discharged (spectator ions)",
                           font=("Segoe UI", 9, "bold"), fill="#555555")
            c.create_text(625, 172, text="↓ priority order for discharge at the anode ↓",
                           font=("Segoe UI", 8, "italic"), fill="#555555")

        draw_reactivity_diagram()

        rules_text = tk.Text(rules_frame, font=("Segoe UI", 12), wrap="word",
                              bg="#fffdf5", fg="#3a2900")
        rules_text.pack(fill="both", expand=True)
        rules_content = (
            "⚡ CATHODE (−): who wins?\n"
            "❌ K⁺ Na⁺ Ca²⁺ Mg²⁺ Al³⁺ → too reactive, NEVER discharged. H⁺ wins instead → H₂ gas.\n"
            "✔️ Zn²⁺ Fe²⁺ Pb²⁺ Cu²⁺ Ag⁺ → less reactive, THESE get discharged → metal deposits.\n"
            "💡 Rule of thumb: the weaker metal ion always loses to the stronger one... wait, wins! "
            "Less reactive = easier to discharge.\n\n"

            "⚡ ANODE (+): who wins?\n"
            "① Halide ion (Cl⁻, Br⁻, I⁻) — discharged first, IF concentrated enough.\n"
            "② OH⁻ (from water) — discharged if no halide, or halide is too dilute.\n"
            "③ SO₄²⁻ / NO₃⁻ — NEVER discharged. They just sit there watching.\n\n"

            "🔎 Molten vs aqueous — don't mix these up!\n"
            "• Molten compound = no water = no H⁺/OH⁻ around → the only ions present ARE discharged,\n"
            "  no matter how reactive the metal is.\n"
            "• Aqueous solution = water's ions (H⁺, OH⁻) are always competing too.\n\n"

            "🔌 Active electrodes (e.g. copper anode)?\n"
            "The electrode itself dissolves instead of any ion reacting. No ion race happens.\n\n"

            "📈 Want more product?\n"
            "Turn up the current, or run it for longer. Simple as that.\n"
        )
        rules_text.insert(tk.END, rules_content)
        rules_text.config(state="disabled")

        # ============ Tab 3: Extraction & electroplating ============
        apps_frame = tk.Frame(tab_apps, bg="#fff6e0", padx=16, pady=16)
        apps_frame.pack(fill="both", expand=True)

        # --- Visual: simplified electroplating setup with vivid neon ions ---
        apps_canvas = tk.Canvas(apps_frame, width=900, height=190, bg="#12163a", highlightthickness=0)
        apps_canvas.pack(pady=(0, 12))

        def draw_electroplating_diagram():
            c = apps_canvas
            c.delete("all")
            c.create_text(450, 16, text="🎨 Electroplating an object with metal", font=("Segoe UI", 11, "bold"),
                           fill="#ffd966")
            # electrolyte tank
            c.create_rectangle(150, 35, 750, 165, outline="#ffb300", width=3, fill="#12163a")
            # electrodes: object = cathode (grey), plating metal = anode (gold)
            c.create_rectangle(225, 20, 245, 180, fill="#c0c0c0", outline="#ffffff", width=1)
            c.create_rectangle(655, 20, 675, 180, fill="#d4af37", outline="#ffffff", width=1)
            c.create_text(235, 12, text="Object (Cathode −)", font=("Helvetica", 9, "bold"), fill="#ffffff")
            c.create_text(665, 12, text="Plating metal (Anode +)", font=("Helvetica", 9, "bold"), fill="#ffffff")

            # vivid neon metal-ion cations migrating anode -> cathode
            metal_fill = "#39FF14"
            metal_glow = "#B9FFB0"
            for i in range(5):
                y = 55 + i * 22
                x = 630 - i * 18
                c.create_oval(x - 11, y - 11, x + 11, y + 11, fill=metal_glow, outline="")
                c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=metal_fill, outline="#0E5C0E", width=2)
                c.create_text(x, y, text="+", font=("Helvetica", 8, "bold"), fill="#0E5C0E")

            c.create_text(450, 172, text="Metal ions leave the anode and deposit as a thin, even coating on the object",
                          font=("Segoe UI", 9, "italic"), fill="#ffd966")

        draw_electroplating_diagram()

        apps_text = tk.Text(apps_frame, font=("Segoe UI", 12), wrap="word",
                             bg="#fffdf5", fg="#3a2900")
        apps_text.pack(fill="both", expand=True)
        apps_content = (
            "🏭 EXTRACTING ALUMINIUM\n"
            "Al is too reactive for the 'heat it with carbon' trick → electrolysis instead.\n"
            "• Al₂O₃ dissolved in molten cryolite — this just lowers the melting point (saves energy).\n"
            "• Cathode: Al³⁺ + 3e⁻ → Al  (liquid metal collects at the bottom)\n"
            "• Anode: 2O²⁻ − 4e⁻ → O₂  (burns the carbon anode away — needs replacing often!)\n\n"

            "🏭 PURIFYING COPPER\n"
            "• Dirty copper = anode. Clean copper sheet = cathode. CuSO₄ solution = electrolyte.\n"
            "• Anode dissolves: Cu − 2e⁻ → Cu²⁺\n"
            "• Cathode grows pure: Cu²⁺ + 2e⁻ → Cu\n"
            "• Gold & silver impurities don't dissolve — they drop as 'anode sludge' (literally free money).\n\n"

            "🎨 ELECTROPLATING\n"
            "• Object to plate = cathode. Plating metal = anode. Solution has the plating metal's ions.\n"
            "• Anode dissolves → same metal deposits evenly on the object.\n"
            "• Why bother? Stops rust, looks nicer, or coats something cheap in something fancy.\n"
        )
        apps_text.insert(tk.END, apps_content)
        apps_text.config(state="disabled")

        ttk.Button(w, text="Close", command=lambda: (play_sound("window_close"), w.destroy())).pack(pady=(0, 10))

    # -------------------------
    # Top Scores window — permanent Hall of Fame (names + scores only),
    # populated whenever the leaderboard is reset. All content here is
    # centered, giving equal empty space above and below it.
    # -------------------------
    def show_top_scores(self):
        play_sound("top_scores_open")
        top = load_top_scores()
        win = tk.Toplevel(self.root)
        win.title("🏅 Top Scores — Hall of Fame")
        win.geometry("640x540")
        win.configure(bg="#fff3d6")

        # Packing this outer frame with expand=True (no fill) centers it
        # vertically AND horizontally in the window, giving equal space
        # above and below the content.
        outer = tk.Frame(win, bg="#fff3d6")
        outer.pack(expand=True)

        tk.Label(outer, text="🏅 All-Time Top 10 Lab Legends 🏅",
                 font=self.header_font, bg="#fff3d6", fg="#7A2E00").pack(pady=(0, 6))
        tk.Label(outer, text="Saved automatically whenever the leaderboard is reset.",
                 font=("Segoe UI", 10, "italic"), bg="#fff3d6", fg="#7A2E00").pack(pady=(0, 16))

        ts_style = ttk.Style()
        ts_style.configure("TopScores.Treeview", font=self.header_font, rowheight=36)
        ts_style.configure("TopScores.Treeview.Heading", font=self.btn_font)

        columns = ("rank", "name", "score", "bonus")
        tree = ttk.Treeview(outer, columns=columns, show="headings", height=10, style="TopScores.Treeview")
        tree.heading("rank", text="#")
        tree.heading("name", text="Name")
        tree.heading("score", text="Score /10")
        tree.heading("bonus", text="Bonus")
        tree.column("rank", width=50, anchor="center")
        tree.column("name", width=220, anchor="w")
        tree.column("score", width=130, anchor="center")
        tree.column("bonus", width=130, anchor="center")
        tree.pack()

        if not top:
            tk.Label(outer, text="No top scores yet — reset the leaderboard after a great\nquiz session to add players here!",
                     font=("Segoe UI", 11), bg="#fff3d6", fg="#7A2E00", justify="center").pack(pady=(18, 0))
        else:
            for i, e in enumerate(top, start=1):
                tree.insert("", tk.END, values=(i, e.get("name", "Anon"),
                                                 f"{e.get('score', 0)}/10", f"+{e.get('bonus', 0)}"))

        tk.Button(outer, text="Close", font=self.btn_font, bg="#f6b26b",
                  command=win.destroy).pack(pady=(20, 0))

# ----------------------------
# Program entry point
# ----------------------------

def main():
    root = tk.Tk()
    app = BondBalancerApp(root)
    root.mainloop()

if __name__ == "__main__":
  main()