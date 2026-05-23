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
# Persistence: Leaderboard file
# ----------------------------
LB_FILE = "leaderboard.json"

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

def add_score_to_leaderboard(name, score, bonus_shown=False):
    """score: numeric; bonus_shown: if true and score==10 show as '10+2' on display."""
    lb = load_leaderboard()
    entry = {
        "name": name,
        "score": score,
        "bonus_shown": bool(bonus_shown),
        "time": datetime.now().isoformat()
    }
    lb.append(entry)
    # sort: numeric score desc; tie-breaker timestamp asc
    def score_key(e):
        return (-e["score"], e.get("time", ""))
    lb.sort(key=score_key)
    save_leaderboard(lb)

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
    ("Which reaction demonstrates the formation of a complex ion?",
     ["Cu²⁺ + 4NH₃ → [Cu(NH₃)₄]²⁺", "NaOH + HCl → NaCl + H₂O", "Zn + H₂SO₄ → ZnSO₄ + H₂", "CuO + H₂ → Cu + H₂O"], "A")
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
]

# ----------------------------
# Application GUI and logic
# (continuation from previous definitions)
# ----------------------------
class BondBalancerApp:
    def __init__(self, root):
        #self.show_full_leaderboard = None
        self.root = root
        self.root.title("BondBalancer: Where Chemistry Comes Alive! ⚗️💫")
        # Recommended size for comfortable layout
        self.root.geometry("1000x760")
        self.root.configure(bg="#88AAFF")
        # Fonts
        avail = list(font.families())
        self.title_face = "Comic Sans MS" if "Comic Sans MS" in avail else "Segoe UI"
        self.title_font = font.Font(family=self.title_face, size=28, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.btn_font = font.Font(family="Helvetica", size=13, weight="bold")
        self.mono = font.Font(family="Consolas", size=11)
        self.large_mono = font.Font(family="Consolas", size=14, weight="bold")
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
        self.bonus_threshold = 15.0  # seconds for +2 bonus
        self.timer_job = None
        # Build main UI
        self.build_main_ui()
        # Load leaderboard initially
        self.refresh_leaderboard_display()

    # -------------------------
    # Main UI
    # -------------------------
    def build_main_ui(self):
        # Top heading
        header_frame = tk.Frame(self.root, bg="#88AAFF")
        header_frame.pack(pady=12)
        tk.Label(header_frame, text="🧪", font=("Segoe UI Emoji", 34), bg="#88AAFF").pack(side="left")
        tk.Label(header_frame, text="Bond Balancer", font=self.title_font, fg="#4422EE", bg="#88AAFF").pack(side="left",
                                                                                                            padx=8)
        tk.Label(header_frame, text="🔬", font=("Segoe UI Emoji", 34), bg="#88AAFF").pack(side="left")

        # Subheading
        sub = tk.Label(
            self.root,
            text="Your Digital Lab Partner — Where Atoms React, Bonds Evolve, and Curiosity Ignites!",
            font=self.header_font,
            bg="#88AAFF",
            fg="#221177"
        )
        sub.pack(pady=(0, 12))

        # Menu buttons (centered)
        menu_frame = tk.Frame(self.root, bg="#88AAFF")
        menu_frame.pack(pady=6)

        self.quiz_btn = tk.Button(
            menu_frame,
            text="Bond Battle ⚔",
            font=self.btn_font,
            width=20,
            height=2,
            bg="#ffd966",
            fg="#CC7722",
            command=self.open_quiz_window
        )
        self.quiz_btn.grid(row=0, column=0, padx=12, pady=8)

        self.solver_btn = tk.Button(
            menu_frame,
            text="EquiLab✨",
            font=self.btn_font,
            width=24,
            height=2,
            bg="#6fa8dc",
            fg="#0A2472",
            command=self.open_solver_window
        )
        self.solver_btn.grid(row=0, column=1, padx=12, pady=8)

        self.gas_btn = tk.Button(
            menu_frame,
            text="Fizz Factory⚗",
            font=self.btn_font,
            width=20,
            height=2,
            bg="#93c47d",
            fg="#06402B",
            command=self.open_gas_window
        )
        self.gas_btn.grid(row=0, column=2, padx=12, pady=8)

        # Small stickers row
        stickers_frame = tk.Frame(self.root, bg="#88AAFF")
        stickers_frame.pack(pady=(4, 12))
        tk.Label(stickers_frame, text="🧫 Ready?", font=("Segoe UI Emoji", 12), bg="#88AAFF", fg="#221177").grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=30)
        tk.Label(stickers_frame, text="⚗️ Mix!", font=("Segoe UI Emoji", 12), bg="#88AAFF", fg="#221177").grid(row=0,
                                                                                                               column=1,
                                                                                                               padx=30)
        tk.Label(stickers_frame, text="📘 Learn!", font=("Segoe UI Emoji", 12), bg="#88AAFF", fg="#221177").grid(row=0,
                                                                                                                column=2,
                                                                                                                padx=30)

        # Sound toggle
        sound_frame = tk.Frame(self.root, bg="#88AAFF")
        sound_frame.pack(pady=(0, 8))
        self.sound_var = tk.BooleanVar(value=self.sounds_enabled)
        cb = ttk.Checkbutton(sound_frame, text="Enable sounds", variable=self.sound_var, command=self.toggle_sounds)
        cb.grid(row=0, column=0, padx=6)

        # Leaderboard frame displayed under menu
        lb_outer = tk.LabelFrame(
            self.root,
            text="🏆 Hall of Lab Legends! (Top 10)🏆",
            font=self.header_font,
            padx=8,
            pady=8,
            bg="#f6cdd2",
            fg="#800000"  # maroon heading
        )

        lb_outer.pack(padx=12, pady=12, fill="both")

        self.lb_listbox = tk.Listbox(
            lb_outer,
            height=8,
            font=self.mono,
            width=90,
            bg="#f6cdd2",
            fg="#FF0000"
        )
        self.lb_listbox.pack(side="left", fill="both", expand=True, padx=(4, 0))
        lb_scroll = ttk.Scrollbar(lb_outer, orient="vertical", command=self.lb_listbox.yview)
        lb_scroll.pack(side="right", fill="y")
        self.lb_listbox.config(yscrollcommand=lb_scroll.set)

        # Footer buttons
        footer = tk.Frame(self.root, bg="#88AAFF")
        footer.pack(pady=(8, 16))
        ttk.Button(footer, text="View full Leaderboard", command=self.show_full_leaderboard).grid(row=0, column=0,
                                                                                                  padx=10)
        ttk.Button(footer, text="Quit", command=self.root.quit).grid(row=0, column=1, padx=10)

    def toggle_sounds(self):
        global SOUNDS_ENABLED
        SOUNDS_ENABLED = bool(self.sound_var.get())
        self.sounds_enabled = SOUNDS_ENABLED

    def refresh_leaderboard_display(self):
        lb = load_leaderboard()
        self.lb_listbox.delete(0, tk.END)
        # Show top 10 with nice formatting
        for i, e in enumerate(lb[:10], start=1):
            name = e.get("name", "Anon")
            score = e.get("score", 0)
            bonus_shown = e.get("bonus_shown", False)
            t = e.get("time", "")
            try:
                tstr = datetime.fromisoformat(t).strftime("%Y-%m-%d %H:%M")
            except Exception:
                tstr = str(t)
            if bonus_shown and score == 10:
                disp = f"{score} + 2"
            else:
                disp = str(score)
            line = f"{i:2d}. {name:15s}  Score: {disp:>5s}   {tstr}"
            self.lb_listbox.insert(tk.END, line)
    # -------------------------
# QUIZ: windows and logic
    # -------------------------
    def open_quiz_window(self):
        play_sound("click")
        self.quiz_win = tk.Toplevel(self.root)
        self.quiz_win.title("Quiz Time! — Can You Handle the Reactions?")
        self.quiz_win.geometry("920x700")
        self.quiz_win.transient(self.root)
        self.quiz_win.configure(bg="#fff9c4")

        frame = tk.Frame(self.quiz_win, bg="#fff9c4", padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="⚗️ Ready, set, react! Solve 10 questions, beat the clock, prove your chemical genius! 🔥",
                 font=self.header_font, bg="#fff9c4").pack(pady=(4, 10))

        name_frame = tk.Frame(frame, bg="#fff9c4")
        name_frame.pack(pady=(4, 8))
        tk.Label(name_frame, text="Your name:", bg="#fff9c4").pack(side="left")
        self.player_name_var = tk.StringVar(value="Student")
        ttk.Entry(name_frame, textvariable=self.player_name_var, width=30).pack(side="left", padx=8)

        start_btn = tk.Button(frame, text="Are you ready to start?",
                              font=self.btn_font, bg="#ffd966", width=28, height=2,
                              command=self.confirm_quiz_start)
        start_btn.pack(pady=(8, 12))

        self.quiz_content_frame = tk.Frame(frame, bg="#fff9c4")
        self.quiz_content_frame.pack(fill="both", expand=True)

        ttk.Button(frame, text="Refresh Leaderboard", command=self.refresh_leaderboard_display).pack(pady=(6,0))

    # --- Confirm Quiz Start ---
    def confirm_quiz_start(self):
        name = self.player_name_var.get().strip()
        if not name:
            messagebox.showwarning("Name required", "Please enter your name before starting the quiz.")
            return
        res = messagebox.askyesno("Ready?", "Are you ready to start the quiz now?")
        if not res:
            play_sound("click")
            return
        play_sound("start")
        self.start_quiz_session()

    # --- Start Quiz Session ---
    def start_quiz_session(self):
        if len(MCQ_POOL) < 10:
            messagebox.showerror("Error", "Not enough questions in the pool.")
            return
        self.quiz_questions = random.sample(MCQ_POOL, 10)
        self.current_q = 0
        self.score = 0
        self.bonus_points = 0
        self.revealed_flags = [False] * len(self.quiz_questions)
        self.quiz_question_start_time = None

        for w in self.quiz_content_frame.winfo_children():
            w.destroy()

        # Question header
        info_frame = tk.Frame(self.quiz_content_frame, bg="#fff9c4")
        info_frame.pack(pady=(4,6))
        self.q_label = tk.Label(info_frame, text="", font=self.large_mono, bg="#fff9c4")
        self.q_label.pack()

        # Timer/progress bar
        pb_frame = tk.Frame(self.quiz_content_frame, bg="#fff9c4")
        pb_frame.pack(pady=(8,6))
        tk.Label(pb_frame, text="Time left:", bg="#fff9c4").grid(row=0, column=0, sticky="w")
        self.time_label = tk.Label(pb_frame, text="20 s", bg="#fff9c4", fg="#333333", font=self.header_font)
        self.time_label.grid(row=0, column=1, padx=(6,12))
        self.pb_canvas = tk.Canvas(pb_frame, width=640, height=22, bg="#f1f1f1", highlightthickness=1, highlightbackground="#cfcfcf")
        self.pb_canvas.grid(row=0, column=2)
        self.pb_canvas.create_rectangle(0,0,640,22, fill="#eeeeee", outline="")
        self.pb_fill = self.pb_canvas.create_rectangle(0,0,640,22, fill="#00b050", outline="")

        # Options as boxes
        self.options_frame = tk.Frame(self.quiz_content_frame, bg="#fff9c4")
        self.options_frame.pack(pady=(12,6), fill="x")
        self.option_buttons = []
        self.option_selected = None
        self.option_selected_idx = None
        for i in range(4):
            btn = tk.Button(
                self.options_frame,
                text="",
                font=("Helvetica", 14),
                bg="#fff9c4",
                anchor="w",
                justify="left",
                relief="raised",
                bd=2,
                command=lambda idx=i: self.select_option(idx)
            )
            btn.pack(fill="x", padx=40, pady=6)
            self.option_buttons.append(btn)

        # Submit/Reveal buttons
        btns = tk.Frame(self.quiz_content_frame, bg="#fff9c4")
        btns.pack(pady=(10,12))
        self.submit_btn = tk.Button(
            btns, text="Submit Answer", font=self.btn_font, bg="#93c47d", fg="white",
            command=self.submit_answer, width=18
        )
        self.submit_btn.grid(row=0, column=0, padx=8)
        self.reveal_btn = tk.Button(
            btns, text="Reveal Answer (ignore)", font=self.btn_font, bg="#6fa8dc", fg="white",
            command=self.reveal_answer, width=22
        )
        self.reveal_btn.grid(row=0, column=1, padx=8)

        # Score label
        self.score_label = tk.Label(self.quiz_content_frame, text=f"Score: {self.score}", font=self.header_font, bg="#fff9c4")
        self.score_label.pack(pady=(8,4))

        self.show_question()

    # --- Option Selection with fade effect ---
    def select_option(self, idx):
        play_sound("click")

        # fade previous selection back
        if self.option_selected_idx is not None:
            prev_idx = self.option_selected_idx
            self._fade_to_color(self.option_buttons[prev_idx], "#fff9c4", steps=5)

        # mark new selection
        self.option_selected_idx = idx
        self.option_selected = chr(65 + idx)
        self.option_buttons[idx].config(bg="#93c47d")

    def _fade_to_color(self, widget, target_color, steps=5, delay=30):
        """Gradually change button bg to target_color"""

        # convert color strings like "#fff9c4" to (R,G,B)
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return "#%02x%02x%02x" % tuple(int(v) for v in rgb)

        # start color in 8-bit RGB
        start_rgb = widget.winfo_rgb(widget.cget("bg"))
        start_rgb = [val // 256 for val in start_rgb]  # convert 16-bit to 8-bit

        end_rgb = hex_to_rgb(target_color)
        step_rgb = [(e - s) / steps for s, e in zip(start_rgb, end_rgb)]
        count = 0

        def step():
            nonlocal count
            if count >= steps:
                widget.config(bg=target_color)
                return
            new_rgb = [start_rgb[i] + step_rgb[i] * count for i in range(3)]
            widget.config(bg=rgb_to_hex(new_rgb))
            count += 1
            widget.after(delay, step)

        step()

    # --- Show Question ---
    def show_question(self):
        if self.timer_job:
            try:
                self.quiz_win.after_cancel(self.timer_job)
            except:
                pass
            self.timer_job = None
        if self.current_q >= len(self.quiz_questions):
            self.end_quiz()
            return

        q, choices, correct = self.quiz_questions[self.current_q]
        self.q_label.config(text=f"Q{self.current_q+1}: {q}")

        self.option_selected = None
        self.option_selected_idx = None
        for i, opt_text in enumerate(choices):
            self.option_buttons[i].config(text=f"{chr(65+i)}.  {opt_text}", bg="#fff9c4")

        # Timer setup
        self.time_left = float(self.time_total)
        self.quiz_question_start_time = time.time()
        self._update_quiz_progress()

    # --- Timer Update ---
    def _update_quiz_progress(self):
        now = time.time()
        elapsed = now - self.quiz_question_start_time
        self.time_left = max(0.0, self.time_total - elapsed)
        self.time_label.config(text=f"{int(math.ceil(self.time_left))} s")
        frac = max(0.0, min(1.0, self.time_left/self.time_total))
        fill_w = int(640*frac)
        self.pb_canvas.coords(self.pb_fill, (0,0,fill_w,22))
        if frac > 0.6:
            color="#00b050"
        elif frac > 0.3:
            color="#ffd700"
        elif frac > 0.15:
            color="#ff8c00"
        else:
            color="#d9534f"
        self.pb_canvas.itemconfig(self.pb_fill, fill=color)

        if self.time_left <= 0:
            play_sound("time_up")
            messagebox.showinfo("Time's up", "⏰ Time is up for this question. It will be marked incorrect.")
            self.current_q += 1
            self.show_question()
            return
        else:
            self.timer_job = self.quiz_win.after(100, self._update_quiz_progress)

    # --- Submit Answer ---
    def submit_answer(self):
        if not self.option_selected:
            messagebox.showwarning("Choose an answer", "Please select an option before submitting.")
            return

        if self.revealed_flags[self.current_q]:
            messagebox.showinfo("Ignored", "This question was revealed earlier and is ignored for scoring.")
            self.current_q += 1
            self.show_question()
            return

        correct = self.quiz_questions[self.current_q][2]
        if self.option_selected == correct:
            self.score += 1
            elapsed = time.time() - self.quiz_question_start_time
            if elapsed <= self.bonus_threshold:
                self.bonus_points += 2
                play_sound("bonus")
                messagebox.showinfo("Bonus!", "Correct — and fast! +1 score and +2 bonus 🎉")
            else:
                play_sound("correct")
                messagebox.showinfo("Correct", "Correct! +1 point.")
        else:
            play_sound("wrong")
            messagebox.showinfo("Incorrect", f"Incorrect. The correct answer was {correct}.")

        self.score_label.config(text=f"Score: {self.score}")
        self.current_q += 1
        self.show_question()

    # --- Reveal Answer ---
    def reveal_answer(self):
        self.revealed_flags[self.current_q] = True
        correct = self.quiz_questions[self.current_q][2]
        play_sound("wrong")
        messagebox.showinfo("Reveal", f"The correct answer is {correct}. This question will be ignored for scoring.")
        self.current_q += 1
        self.show_question()

    # --- End Quiz ---
    def end_quiz(self):
        if self.timer_job:
            try:
                self.quiz_win.after_cancel(self.timer_job)
            except:
                pass
            self.timer_job = None

        final_score = self.score
        bonus_shown = False
        if self.score < len(self.quiz_questions):
            final_score += self.bonus_points
        else:
            bonus_shown = (self.bonus_points > 0)

        if bonus_shown:
            msg = f"Quiz complete! Score: {self.score}/{len(self.quiz_questions)}  (+{self.bonus_points} bonus shown)\nDisplayed as: {self.score}+{self.bonus_points}"
        else:
            msg = f"Quiz complete! Final Score: {final_score}/{len(self.quiz_questions)}"

        play_sound("end")
        messagebox.showinfo("Quiz Finished", msg)

        name = self.player_name_var.get().strip() or "Student"
        store_score = self.score if not bonus_shown else self.score
        add_score_to_leaderboard(name, store_score, bonus_shown=bonus_shown)
        self.refresh_leaderboard_display()

        try:
            self.quiz_win.destroy()
        except:
            pass

    # -------------------------
    # Equation Solver popup
    # -------------------------
    def open_solver_window(self):
        play_sound("click")

        # Create the solver window
        w = tk.Toplevel(self.root)
        w.title("Equation Solver — Step-by-step")
        w.geometry("1000x620")
        w.configure(bg="#e3f2fd")

        frm = tk.Frame(w, padx=12, pady=12, bg="#e3f2fd")
        frm.pack(fill="both", expand=True)

        # Title and instructions
        tk.Label(frm, text="✨ Step-by-step Equation Solver ✨", font=self.header_font, bg="#e3f2fd").pack(pady=(4, 12))
        tk.Label(frm, text="Select an equation from the list to see step-by-step solution.",
                 font=("Segoe UI", 11), bg="#e3f2fd").pack(pady=(0, 8))

        main_frame = tk.Frame(frm, bg="#e3f2fd")
        main_frame.pack(fill="both", expand=True)

        # === Left panel: equation list ===
        list_frame = tk.Frame(main_frame, bg="#e3f2fd")
        list_frame.pack(side="left", fill="y", padx=(0, 12))

        listbox = tk.Listbox(list_frame, font=self.mono, width=40, height=25,
                             selectbackground="#6fa8dc", selectforeground="white")
        listbox.pack(side="left", fill="y")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        # Populate equation list
        for idx, (r, p) in enumerate(SOLVER_OPTIONS, start=1):
            left = " + ".join(r)
            right = " + ".join(p)
            line = f"{idx:2d}. {left} → {right}"
            listbox.insert(tk.END, line)

        listbox.selection_set(0)

        # === Right panel: step-by-step solution ===
        steps_frame = tk.Frame(main_frame, bg="#f3e5f5")  # light violet
        steps_frame.pack(side="left", fill="both", expand=True)

        # Close button
        btn_frame = tk.Frame(steps_frame, bg="#f3e5f5")
        btn_frame.pack(pady=(0, 4))
        tk.Button(btn_frame, text="Close", font=self.btn_font, bg="#f6b26b",
                  command=lambda: (play_sound("click"), w.destroy())).pack(side="left", padx=6)

        # Steps label
        steps_label = tk.Label(steps_frame, text="Steps will appear here",
                               font=("Segoe UI", 12, "bold"), bg="#f3e5f5")
        steps_label.pack(pady=(4, 4))

        # Steps text box
        steps_text = tk.Text(steps_frame, font=("Courier New", 11), wrap="word",
                             bg="#f3e5f5", fg="#003366")
        steps_text.pack(fill="both", expand=True)
        steps_scroll = ttk.Scrollbar(steps_frame, orient="vertical", command=steps_text.yview)
        steps_scroll.pack(side="right", fill="y")
        steps_text.config(yscrollcommand=steps_scroll.set)
        steps_text.config(state="disabled")

        # === Update steps function with alternating colors and sounds ===
        def update_steps(event=None):
            sel = listbox.curselection()
            if not sel:
                return

            play_sound("select")  # <-- Changed sound for selecting a reaction

            index = sel[0]
            reactants, products = SOLVER_OPTIONS[index]
            res, steps = balance_equation(reactants, products)

            steps_text.config(state="normal")
            steps_text.delete("1.0", tk.END)

            if res is None:
                steps_text.insert(tk.END, "⚠️ Cannot balance this equation")
                steps_text.config(state="disabled")
                play_sound("wrong")
                return

            # Insert steps with alternating colors
            for i, s in enumerate(steps):
                prefix = "✨ " if i == 0 else "  "
                steps_text.insert(tk.END, f"{prefix}{s}\n")
                tag_name = f"line{i}"
                bg_color = "#f2d5f6" if i % 2 == 0 else "#ffffff"
                steps_text.tag_add(tag_name, f"{i + 1}.0", f"{i + 1}.end")
                steps_text.tag_config(tag_name, background=bg_color)

            steps_text.config(state="disabled")
            play_sound("success")  # satisfying success tone when solved

        # Bind selection and show initial steps
        listbox.bind("<<ListboxSelect>>", update_steps)
        update_steps()

    # ----------------------------
    # Gas Reaction Window
    def open_gas_window(self):
        # 🌊 Create top-level window
        play_sound("click")  # sound when window opens
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

        ttk.Button(self.gas_frame, text="Close", command=w.destroy).pack(pady=(8, 8))

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
    # Leaderboard window
    # -------------------------
    def show_full_leaderboard(self):
        lb = load_leaderboard()
        win = tk.Toplevel(self.root)
        win.title("Full Leaderboard — Bond Balancer")
        win.geometry("640x480")
        f = tk.Frame(win, padx=10, pady=10)
        f.pack(fill="both", expand=True)
        lbx = tk.Listbox(f, font=self.mono, width=80, height=20)
        lbx.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(f, orient="vertical", command=lbx.yview)
        scroll.pack(side="right", fill="y")
        lbx.config(yscrollcommand=scroll.set)

        for i, e in enumerate(lb, start=1):
            name = e.get("name", "Anon")
            score = e.get("score", 0)
            bonus_shown = e.get("bonus_shown", False)
            t = e.get("time", "")
            try:
                tstr = datetime.fromisoformat(t).strftime("%Y-%m-%d %H:%M")
            except Exception:
                tstr = str(t)
            if bonus_shown and score == 10:
                disp = f"{score}+2"
            else:
                disp = str(score)
            line = f"{i:2d}. {name:15s}  Score: {disp:>5s}   {tstr}"
            lbx.insert(tk.END, line)

        tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

# ----------------------------
# Program entry point
# ----------------------------

def main():
    root = tk.Tk()
    app = BondBalancerApp(root)
    root.mainloop()

if __name__ == "__main__":
  main()