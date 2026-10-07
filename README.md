# 🧪 Bond Balancer
### *Where Chemistry Comes Alive*
 
> **🏆 Winner — Best Chemistry Project, School Science Fair**  
> Built independently by a Grade 9 student of HURDCO International School, as an exploration of computational chemistry and interactive education.
 
---
 
## What Is Bond Balancer?
An app made by 16-year-old Afra Nawar for struggling students to enjoy relearning chemistry through 
the interface of a simple game.  
Bond Balancer is a fully interactive desktop chemistry learning application built in Python. It combines real mathematical equation-balancing (using rational nullspace computation) with a gamified quiz system and a **six-tool virtual laboratory** aligned with the Cambridge O-Level Chemistry (5070) syllabus; making chemistry accessible, visual, and competitive for students at any level.
 
---
 
## Features
 
### ⚔️ Bond Battle — Chapter-Based MCQ Quiz
- **84-question bank** across five chapters, plus a "Mixed (All Chapters)" mode: Chemical Bonds & Reactions, Atomic Structure & Periodic Table, Moles & Stoichiometry, Electrolysis, and Organic Chemistry
- 10 randomly selected questions per session, with a chapter selector on the setup screen
- 20-second countdown timer per question with a **colour-changing progress bar** (green → yellow → orange → red)
- **Bonus +2 points** awarded for correct answers within the first 5 seconds
- "Reveal Answer" option that gracefully removes the question from scoring
- Keyboard shortcuts: **A–D** (or **1–4**) to choose, **Enter** to submit
- Progress dots show right, wrong, and skipped questions at a glance
- Real-time score tracking with audio feedback for correct, incorrect, bonus, and timeout events
- Player name entry with results saved to a **persistent leaderboard**
### ✨ EquiLab — Step-by-Step Equation Solver
- Balances **50 chemical equations** using a **rational nullspace algorithm** (the same mathematical method used in professional chemistry software)
- Shows full working: element matrix construction, solution vector, and final balanced equation, with proper subscripts (H₂O, Pb(NO₃)₂)
- "One step at a time" mode with **Back / Next / Show all / Restart** controls and arrow-key navigation
- Search box to filter reactions, plus a **Random reaction** button
- Copy-to-clipboard for the full working, and **A+ / A−** font size controls
- Alternating colour-coded steps with the latest step highlighted
- Audio and visual feedback on selection and solution
### ⚗️ Fizz Factory — Virtual Gas Lab
- A **pictorial lab bench**: pick two reactants from H₂, O₂, Cl₂, K, N₂, and CH₄ and watch them fill labelled gas jars
- Set molar amounts with sliders (0.5–5 mol); the number of molecules in each jar changes with the amount
- Press **Run Reaction** and the molecules travel through delivery tubes into a reaction flask, a spark fires, and the reacted molecules disappear
- Each reaction looks different: water droplets and a pool (H₂ + O₂), a flickering flame with CO₂ and water (CH₄ + O₂), white fumes (H₂ + Cl₂), ammonia molecules (N₂ + H₂), and a lilac flame leaving white crystals (K + Cl₂ or O₂)
- Pairs that do not react show the molecules mixing with no change, so students see what *doesn't* happen too
- A colour-coded lab notebook shows the balanced equation, the **limiting reactant**, the leftover amount of the excess reactant, the product formed, what you would see, and the conditions needed in a real lab
- Sound effects for starting, reacting, and failed reactions
### ⚛️ AtoMole Arena — Atomic Structure & Mole Calculator
- **Atomic Structure tab:** explore the first 20 elements (H to Ca) with an **animated atom model**: electrons orbit the nucleus on colour-coded shells, spinning in alternating directions
- Shows protons, neutrons, electrons, mass number, electron configuration, period, and valence electrons for each element
- **Mole Calculator tab:** five calculation types — mass & Mr → moles, moles & Mr → mass, moles & volume → concentration, concentration & volume → moles, and moles → gas volume at r.t.p.
- Every answer is shown with the formula, the substitution, and the final result, so students see the method as well as the number
### ♻️ Carbon Craft — Organic Chemistry Explorer
- Covers four homologous series: **alkanes, alkenes, alcohols, and carboxylic acids**
- Draws an **animated structure** of an example from each series (ethane, ethene, ethanol, ethanoic acid), with single and double bonds and gently vibrating atoms
- A redesigned, colour-coded notes panel with clear headings for the general formula (with proper subscripts), functional group, key reaction or test, and common uses
### ⚡ Volt Vault — Electrolysis Explorer
- **Electrolyte Explorer:** 9 cases covering molten compounds, aqueous solutions, and inert and active electrodes. An **animated cell** shows ions migrating to opposite electrodes, with gas bubbles rising at each one
- Results are laid out with colour-coded **CATHODE (−)** and **ANODE (+)** tags, the products, the half-equations on tinted backgrounds, and an explanatory note
- **Selective Discharge Rules:** a redesigned diagram showing which cation and anion wins at each electrode, with clear notes on molten vs aqueous solutions and active electrodes
- **Extraction & Electroplating:** extraction of aluminium, purification of copper, and electroplating, each with half-equations, plus an animated plating diagram where the metal layer grows on the object
### 🏆 Persistent Leaderboard & Hall of Fame
- All quiz scores saved to `leaderboard.json` with timestamps
- Top 10 displayed on the main menu at all times, with rank, name, score out of 10, speed bonus, and date
- Sorted by score descending, then speed bonus, then timestamp as the final tiebreaker
- **Reset Leaderboard** archives the best players into a permanent Top Scores Hall of Fame (`top_scores.json`) before clearing the board for new players
- **View Top Scores** opens the all-time top 10 in its own window
---
 
## The Science Behind It
 
### Equation Balancing — Rational Nullspace Method
 
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
 
| Component | Technology |
|---|---|
| Language | Python 3.x |
| GUI Framework | Tkinter + TTK (Notebook tabs, Treeview tables, Canvas drawings) |
| Mathematical Core | `fractions.Fraction`, `math.gcd` |
| Audio | `winsound` (Windows), threaded beep sequences |
| Persistence | JSON (`leaderboard.json`, `top_scores.json`) |
| Concurrency | `threading` (non-blocking audio) |
| Chemistry Parser | Custom recursive tokenizer with regex |
 
---
 
## How to Run
 
### Requirements
- Python 3.7 or higher
- Windows OS (for `winsound` audio, which the app uses throughout)
- No external libraries required (all standard library)
### Steps
```bash
# Clone the repository
git clone https://github.com/Afra-Nawar-CS/bond-balancer.git
 
# Navigate into the folder
cd bond-balancer
 
# Run the app
python bond_balancer.py
```
 
The leaderboard is automatically created as `leaderboard.json` in the same directory on first run, which is a persistent JSON leaderboard. The Hall of Fame file, `top_scores.json`, is created the first time the leaderboard is reset.
 
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
Interests: Computational Chemistry, Computer Science, Environmental Technology  
 
*Open to feedback, collaboration, and questions about the algorithm.*
 
---
 
## License
 
MIT License; free to use, modify, and distribute with attribution.
