# 🧪 Bond Balancer

### *Where Chemistry Comes Alive*

> **🏆 Winner — Best Chemistry Project, School Science Fair**
> Built independently by a Grade 9 student of HURDCO International School, as an exploration of computational chemistry and interactive education.

---

## What Is Bond Balancer?

An app made by 16-year-old Afra Nawar for struggling students to enjoy relearning chemistry through the interface of a simple game.

Bond Balancer is a fully interactive desktop chemistry learning application built in Python. It combines real mathematical equation-balancing (using rational nullspace computation) with a gamified quiz system and a six-tool virtual laboratory aligned with the Cambridge O-Level Chemistry (5070) syllabus, making chemistry accessible, visual, and competitive for students at any level!

---

## 🚀 Quick Start (for complete beginners)

You do **not** need to know how to code. You only need to install Python once, then double-click or type one command.

### Step 1: Install Python (one time only)

1. Go to **https://www.python.org/downloads/** and click the big yellow **Download Python** button.
2. Open the file you downloaded.
3. **Windows: tick the box that says "Add python.exe to PATH" at the bottom of the first screen**, then click **Install Now**. (This is the step people forget, and it causes the most problems.)
4. **macOS:** use the installer from python.org. It already includes the window toolkit (Tkinter) that this app needs.
5. **Linux:** open a terminal and run `sudo apt install python3 python3-tk` (Ubuntu/Debian). On other distributions, install the package that provides Tkinter for Python 3.

### Step 2: Download Bond Balancer

1. Open **https://github.com/Afra-Nawar-CS/Bond-Balancer**
2. Click the green **Code** button, then **Download ZIP**.
3. Find the ZIP file (usually in your **Downloads** folder), right-click it and choose **Extract All** (Windows) or double-click it (macOS).

You should now have a folder called `Bond-Balancer-main` that contains a file named `Bond_balancer.py`.

### Step 3: Open a terminal inside that folder

- **Windows:** open the `Bond-Balancer-main` folder in File Explorer, click the address bar at the top, type `cmd`, and press **Enter**. A black window opens, already in the right folder.
- **macOS:** open **Terminal**, type `cd ` (with a space after it), drag the `Bond-Balancer-main` folder into the Terminal window, and press **Enter**.
- **Linux:** right-click inside the folder and choose **Open in Terminal**.

### Step 4: Run it

| System | Type this and press Enter |
| --- | --- |
| Windows | `py Bond_balancer.py` |
| macOS / Linux | `python3 Bond_balancer.py` |

The Bond Balancer window opens. 🎉 (The capital **B** in `Bond_balancer.py` matters on macOS and Linux.)

> **Already know Git?** `git clone https://github.com/Afra-Nawar-CS/Bond-Balancer.git`, then `cd Bond-Balancer`, then run the command above.

### Something went wrong?

| What you see | What to do |
| --- | --- |
| `'py' is not recognized` or `'python' is not recognized` | Python is not on your PATH. Run the Python installer again, choose **Modify**, and tick **Add python.exe to PATH** (or just reinstall and tick it). Then close and reopen the black window. |
| `No module named 'tkinter'` (or `_tkinter`) | Tkinter is missing. Linux: `sudo apt install python3-tk`. macOS with Homebrew Python: `brew install python-tk`. Otherwise reinstall Python from python.org. |
| `can't open file ... Bond_balancer.py` | The terminal is not in the right folder. Repeat Step 3, and check that the folder really contains `Bond_balancer.py`. |
| The window is cut off at the bottom of a small screen | Press **F11** inside any window for full screen (press **Esc** to leave it), or use a larger screen. |
| No sound on macOS or Linux | Expected. The sound effects use Windows' `winsound`, so the app runs silently on other systems. Everything else works. |
| Scores seem to vanish | The leaderboard is saved in `leaderboard.json` next to the program. If the folder is read-only (for example inside a ZIP), copy the folder to your Desktop and run it from there. |

---

## Features

### ⚔️ Bond Battle — Chapter-Based MCQ Quiz

- **84 questions across five chapters**, plus a **Mixed (All Chapters)** mode: Chemical Bonds & Reactions (36), Atomic Structure & Periodic Table (12), Moles & Stoichiometry (12), Electrolysis (12), and Organic Chemistry (12)
- Pick your chapter on the setup screen, enter your name, and press **Start Quiz**
- **10 randomly selected questions per game**, so every round is different
- **20-second countdown** per question with a progress bar that changes colour as time runs out (green → yellow → orange → red)
- **+1 point for every correct answer.** Answer correctly within the first **5 seconds** and you also earn a **+2 speed bonus**. The bonus is shown separately and is used as the **tie-breaker** on the leaderboard, so it does not change your score out of 10
- **Time's up?** The correct answer is highlighted and the question is marked incorrect
- **💡 Reveal (no score)** shows the answer without counting the question as right or wrong (your result is still out of 10)
- **Instant feedback** under each question: ✅ correct, ⚡ lightning fast, ❌ not quite, or ⏰ time's up, with sound effects (Windows)
- **Progress dots** along the top turn green (right), red (wrong), or grey (revealed) as you go
- **Keyboard controls:** `A`–`D` (or `1`–`4`) to choose, `Enter` to submit, then `Enter`, `Space`, `→` or `N` for the next question. `F11` toggles full screen
- **Results screen** with your score out of 10, any speed bonus, and an encouraging message based on how you did, plus **Play again** and **Close** buttons
- Your result is saved to the persistent leaderboard automatically

### ✨ EquiLab — Step-by-Step Equation Solver

- Balances 50 chemical equations using a rational nullspace algorithm (the same mathematical method used in professional chemistry software)
- Shows full working: element matrix construction, solution vector, and final balanced equation, with proper subscripts (H₂O, Pb(NO₃)₂)
- "One step at a time" mode with Back / Next / Show all / Restart controls and arrow-key navigation
- Search box to filter reactions, plus a Random reaction button
- Copy-to-clipboard for the full working, and A+ / A− font size controls
- Alternating colour-coded steps with the latest step highlighted
- Audio and visual feedback on selection and solution

### ⚗️ Fizz Factory — Virtual Reaction Lab

Run real school-lab reactions on screen, watch what happens, and read the science behind it in your lab notebook.

**Set up an experiment**

- Choose **any two** of **11 reactants**: hydrochloric acid (HCl), sulfuric acid (H₂SO₄), sodium hydroxide (NaOH), zinc (Zn), magnesium (Mg), copper(II) oxide (CuO), calcium carbonate (CaCO₃), silver nitrate (AgNO₃), sodium chloride (NaCl), barium chloride (BaCl₂), and copper(II) sulfate (CuSO₄). Each tile shows its type (acid, alkali, metal, metal oxide, carbonate, salt)
- Set the amount of each reactant from **0.5 to 5 mol** with the sliders
- Press **Run Reaction** to watch the reactants pour into the flask, mix, and react. **Reset Selection** starts again

**Reaction types covered**

- Neutralisation (acid + alkali), acid + metal, acid + metal oxide, acid + carbonate
- Precipitation (ionic double decomposition) and metal displacement
- Heated metal + copper(II) oxide reactions, drawn with a glowing powder, flames and sparks
- Pairs that do **not** react, with a plain-English explanation of why not

**What you see in the flask**

- 🎨 **A different solution colour for every reaction**, so each product looks unique (colourless solutions are tinted on screen)
- 🧂 **The salt that forms is shown** as coloured dots drifting in the solution, plus a **salt card** in the corner giving its name, formula and colour
- ⚪ White, brown or blue **precipitates** cloud the liquid and then settle at the bottom
- 🟤 **Metal deposits**, such as pink-brown copper or shiny silver, appear in displacement reactions
- 🫧 **Fizzing on top:** hydrogen and carbon dioxide reactions bubble up through the liquid and form a **foam of bubbles with spray above the surface**

**Gas tests, shown on screen**

- **Carbon dioxide (acid + carbonate):** the gas travels along a delivery tube into a test tube of **limewater, which turns milky**, confirming CO₂
- **Hydrogen (acid + metal):** the gas is collected in an inverted test tube, a **lighted splint** moves up to its mouth, and you get a **squeaky POP** with a flash and a sound effect (sound on Windows), confirming H₂

**Your lab notebook** fills in after every run with:

- the balanced equation with state symbols and the reaction type
- whether the bonding is **ionic or covalent**, and why
- the **net ionic equation**
- **stoichiometry:** the limiting reactant, how much is left over, and how many moles of each product formed
- **what you see**, the **salt and solution colour**, the **gas test** and its equation, and a practical **lab note**

### ⚛️ AtoMole Arena — Atomic Structure & Mole Calculator

- Atomic Structure tab: explore the first 20 elements (H to Ca) with a drawn atom model showing the nucleus and colour-coded electron shells
- Shows protons, neutrons, electrons, mass number, electron configuration, period, and valence electrons for each element
- Mole Calculator tab: five calculation types — mass & Mr → moles, moles & Mr → mass, moles & volume → concentration, concentration & volume → moles, and moles → gas volume at r.t.p.
- Every answer is shown with the formula, the substitution, and the final result, so students see the method as well as the number

### ♻️ Carbon Craft — Organic Chemistry Explorer

- Covers four homologous series: alkanes, alkenes, alcohols, and carboxylic acids
- Draws the structure of an example from each series (ethane, ethene, ethanol, ethanoic acid), with single and double bonds
- Shows the general formula, functional group, key reactions or tests, and common uses

### ⚡ Volt Vault — Electrolysis Explorer

- Electrolyte Explorer: 9 cases covering molten compounds, aqueous solutions, inert and active electrodes, with half-equations for the cathode and anode and an animated-style ion diagram
- Selective Discharge Rules: a visual guide to which ion wins at each electrode, plus molten vs aqueous and active electrode rules
- Extraction & Electroplating: extraction of aluminium, purification of copper, and electroplating, each with a labelled diagram or half-equations

### 🏆 Persistent Leaderboard & Hall of Fame

- All quiz scores saved to `leaderboard.json` with timestamps
- Top 10 displayed on the main menu at all times, with rank, name, score out of 10, speed bonus, and date
- Sorted by score descending, then speed bonus, then timestamp as the final tiebreaker
- Reset Leaderboard archives the best players into a permanent Top Scores Hall of Fame (`top_scores.json`) before clearing the board for new players
- View Top Scores opens the all-time top 10 in its own window

---

## The Science Behind It

### Equation Balancing: Rational Nullspace Method

Most equation balancers use trial and error. However, Bond Balancer is unique, because it uses **linear algebra** and stoichiometric prediction logic.

Each chemical equation is converted into an **element matrix** where:

- Rows represent elements involved
- Columns represent chemical species (reactants as positive, products as negative)

The **nullspace** of this matrix gives the coefficients that balance the equation. The algorithm uses **Gaussian elimination over rational numbers** (via Python's `fractions.Fraction`) to find the smallest integer solution vector — guaranteeing exact, reduced coefficients with no floating-point errors.

```
Example: H₂ + O₂ → H₂O

Element matrix:
  H:  2  0  -2
  O:  0  2  -1

Nullspace → [2, 1, 2]
Balanced:  2H₂ + O₂ → 2H₂O ✓
```

---

## Tech Stack

| Component         | Technology                                                      |
| ----------------- | --------------------------------------------------------------- |
| Language          | Python 3.x                                                      |
| GUI Framework     | Tkinter + TTK (Notebook tabs, Treeview tables, Canvas drawings) |
| Animation         | Tkinter Canvas redrawn about 25 times a second from a timeline  |
| Mathematical Core | `fractions.Fraction`, `math.gcd`                                |
| Audio             | `winsound` (Windows only), threaded beep sequences              |
| Persistence       | JSON (`leaderboard.json`, `top_scores.json`)                    |
| Concurrency       | `threading` (non-blocking audio)                                |
| Chemistry Parser  | Custom recursive tokenizer with regex                           |

**Requirements:** Python 3.8 or newer (the latest from python.org is best). No extra libraries are needed: everything is in Python's standard library. Sound effects need Windows; on macOS and Linux the app works but is silent.


---

## Visual Display

<img width="1915" height="1012" alt="image" src="https://github.com/user-attachments/assets/9f75bbc4-52ca-40d9-9590-b3e8e292c99e" />
<img width="1917" height="1005" alt="Screenshot 2026-10-08 011745" src="https://github.com/user-attachments/assets/959e7f99-4abd-41d8-8f16-3a5e278e9ce8" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231131" src="https://github.com/user-attachments/assets/f689ec52-ae3c-42e3-a1b4-2d84d6568073" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231433" src="https://github.com/user-attachments/assets/ac4c3761-7155-43e1-9542-684bf17643d6" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231453" src="https://github.com/user-attachments/assets/888e364d-1467-40b7-8537-bda01daa3f39" />
<img width="1917" height="1010" alt="Screenshot 2026-10-05 231504" src="https://github.com/user-attachments/assets/5df649b7-e506-4625-ac11-1054ad73ce0d" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231522" src="https://github.com/user-attachments/assets/2a81abad-0a7a-4b3d-b601-eecf3f935175" />
<img width="1917" height="1017" alt="Screenshot 2026-10-05 231535" src="https://github.com/user-attachments/assets/1c76a622-87c7-4680-9ac6-c53cb78d10b2" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231602" src="https://github.com/user-attachments/assets/11407b39-6cc0-4aae-8b0a-8f1a87fe463f" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231722" src="https://github.com/user-attachments/assets/820987d9-96b9-4e3f-9071-3423090da0de" />
<img width="1912" height="1015" alt="Screenshot 2026-10-05 231749" src="https://github.com/user-attachments/assets/87533c72-c0b6-4e68-a0da-6d12b1e9713c" />
<img width="1917" height="1015" alt="Screenshot 2026-10-05 231858" src="https://github.com/user-attachments/assets/16d0389c-1a97-44cf-8efd-1561ab345d7c" />
<img width="1917" height="1012" alt="Screenshot 2026-10-05 231911" src="https://github.com/user-attachments/assets/1d18d95f-50cf-4e03-9062-ef1b615a4ddc" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231921" src="https://github.com/user-attachments/assets/d14416f8-520b-4b13-956f-aaff1c7a8503" />
<img width="1917" height="1018" alt="Screenshot 2026-10-08 011906" src="https://github.com/user-attachments/assets/5014d55c-4165-4548-ba6f-5e2fae9e8d97" />
<img width="1917" height="1015" alt="Screenshot 2026-10-08 011926" src="https://github.com/user-attachments/assets/726d4def-9bc1-4784-b534-3c01a61bf946" />
<img width="1917" height="1011" alt="Screenshot 2026-10-08 011951" src="https://github.com/user-attachments/assets/d1ca3fdf-3d12-4479-b585-1e4d5c6f2735" />
<img width="1917" height="1015" alt="Screenshot 2026-10-08 012235" src="https://github.com/user-attachments/assets/8e9451dc-65f1-498e-b661-a3af9170c41c" />
<img width="1917" height="1015" alt="Screenshot 2026-10-08 012306" src="https://github.com/user-attachments/assets/b2da6748-9443-4c56-addd-3402f2db02f7" />
<img width="1892" height="1013" alt="Screenshot 2026-10-08 012332" src="https://github.com/user-attachments/assets/380de7b4-20fa-47db-b37e-2c62336fb1a4" />
<img width="1917" height="1020" alt="Screenshot 2026-10-08 012346" src="https://github.com/user-attachments/assets/3d2a303f-c853-4b26-bb09-3f0f6cbd7a71" />
<img width="1917" height="1012" alt="Screenshot 2026-10-08 012400" src="https://github.com/user-attachments/assets/6d6f0375-c1b0-45a9-8476-feb2268150e4" />
<img width="1917" height="1015" alt="Screenshot 2026-10-08 012409" src="https://github.com/user-attachments/assets/b21bf92f-7309-47ae-81b0-6fcb6318c668" />



---

## Project Structure

```
Bond-Balancer/
│
├── Bond_balancer.py      # Main application (all features)
├── leaderboard.json      # Auto-generated on first quiz result
├── top_scores.json       # Auto-generated when the leaderboard is first reset
├── PUBLISHING.md         # How to build an .exe and publish
├── build_windows.bat     # One-click Windows build script
├── icon.ico / icon.png   # App icon
└── README.md             # This file
```

---

## Why I Built This

Chemistry can feel intimidating, especially because of equation balancing, where students fail to remember how to use logical processes when they see complex compounds. I wanted to build something that showed the *mathematical structure* underneath chemical equations, while making practice genuinely engaging through competition and experimentation.

The gas reactor grew from my curiosity: what if students could experiment without a physical lab?
On the other hand, the leaderboard was made after I remembered how hard students work when they are motivated to win a competition, because that same energy belongs in our chemistry education as well!

Since then, Bond Balancer has grown to cover more of the O-Level syllabus: atomic structure, mole calculations, organic chemistry, and electrolysis.
Now, each topic has its own tool, so a student can revise a whole topic in one app.

---


**Skills demonstrated:**

- Algorithm design, stoichiometric prediction logic and linear algebra implementation
- GUI application development
- Object-oriented programming
- Data persistence and file I/O
- Multi-threading for responsive UI and threaded audio systems
- Chemistry domain knowledge (stoichiometry, reaction types, element classification, electrolysis, organic chemistry

 
---
 
## Project Structure
 
```
bond-balancer/
│
├── bond_balancer.py      # Main application (all features)
├── leaderboard.json      # Auto-generated on first run
├── top_scores.json       # Auto-generated when the leaderboard is first reset
└── README.md             # This file
```
 
---
 
## Why I Built This
 
Chemistry can feel intimidating, especially because of equation balancing, where students fail to remember how to use logical processes when they see complex compounds. I wanted to build something that showed the *mathematical structure* underneath chemical equations, while making practice genuinely engaging through competition and experimentation.
 
The gas reactor grew from my curiosity: what if students could experiment without a physical lab? 
On the other hand, The leaderboard was made after I remembered how hard students work when they are motivated to win a competition, because that same energy belongs in chemistry education as well!

Since then, Bond Balancer has grown to cover more of the O-Level syllabus: atomic structure, mole calculations, organic chemistry, and electrolysis now each have their own tool, so a student can revise a whole topic in one app.
 
---
 
## Future Development

**Done so far**
- [x] Expand equation database beyond 20 (now 50 reactions)
- [x] Add organic chemistry (homologous series explorer)
- [x] Redesigned main menu and interface with colour-themed tools
- [x] Pictorial, animated virtual lab for Fizz Factory
- [x] Animated atoms, organic structures, and electrolysis cells
- [x] Cleaner, colour-coded notes panels in Carbon Craft and Volt Vault

**Three new menu tools**
- [ ] 🧫 **Experiment Station** — virtual practicals: titration, salt preparation, gas tests, and qualitative analysis (identifying cations and anions), so students can rehearse the practical paper without a physical lab
- [ ] 📖 **Theory Library** — illustrated revision notes and flashcards for every 5070 topic (bonding, the periodic table, acids, bases and salts, rates, energetics), linked to the matching quiz chapter
- [ ] 📝 **Exam Zone** — exam-style structured questions with mark schemes and self-marking, to move from multiple choice to full written answers

**New topics and content**
- [ ] Add acids, bases and salts, rates of reaction, and energetics chapters to the quiz and tools
- [ ] Add organic chemistry reaction mechanisms
- [ ] Interactive periodic table with trends (reactivity, atomic radius, electronegativity)
- [ ] Expand the quiz bank beyond 84 questions, with difficulty levels (easy, medium, hard)
- [ ] More gases, metals, and reaction types in Fizz Factory, including reactions that need heat or a catalyst
- [ ] Extend EquiLab to ionic equations and state symbols

**Learning features**
- [ ] Personal progress tracker showing strengths and weak topics for each student
- [ ] "Review mistakes" mode that replays the questions a student got wrong
- [ ] Daily challenge question
- [ ] Achievement badges and streaks to keep revision fun
- [ ] Introduce 3D molecular visualisation

**Platform and sharing**
- [ ] Cross-platform audio (replace `winsound`)
- [ ] Packaged `.exe` installer so students can run it without installing Python
- [ ] Web version for browser access
- [ ] Teacher dashboard for classroom leaderboard management
- [ ] Light and dark themes, plus a larger-text accessibility mode
---
 
## Academic Context
 
This project was developed as an independent science fair entry exploring the intersection of **computer science and chemistry education**. The rational nullspace balancing algorithm was researched and implemented from first principles — no chemistry libraries were used.
 
**Skills demonstrated:**
- Algorithm design, stoichiometric prediction logic and linear algebra implementation
- GUI application development
- Object-oriented programming
- Data persistence and file I/O
- Multi-threading for responsive UI and threaded audio systems
- Chemistry domain knowledge (stoichiometry, reaction types, element classification, electrolysis, organic chemistry)
---
 
## Author
 
**Afra Nawar**  
Grade 10A Student | Cambridge O-Level Candidate 2027  
Interests: Computational Chemistry, Computer Science, Environmental Technology, Chemistry 
 
*Open to feedback, collaboration, and questions about the algorithm.*
 
---
 
## License
 
MIT License; free to use, modify, and distribute with attribution.
