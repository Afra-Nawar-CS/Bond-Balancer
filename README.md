# 🧪 Bond Balancer
### *Where Chemistry Comes Alive*
 
> **🏆 Winner — Best Chemistry Project, School Science Fair**  
> Built independently by a Grade 9 student of HURDCO International School, as an exploration of computational chemistry and interactive education.
 
---
 
## What Is Bond Balancer?
An app made by 16-year-old Afra Nawar for struggling students to enjoy relearning chemistry through 
the interface of a simple game.  
Bond Balancer is a fully interactive desktop chemistry learning application built in Python. It combines real mathematical equation-balancing (using rational nullspace computation) with a gamified quiz system and a six-tool virtual laboratory aligned with the Cambridge O-Level Chemistry (5070) syllabus, making chemistry accessible, visual, and competitive for students at any level!

---
 
## Features

### ⚔️ Bond Battle — Chapter-Based MCQ Quiz
- 84-question bank across five chapters, plus a "Mixed (All Chapters)" mode: Chemical Bonds & Reactions, Atomic Structure & Periodic Table, Moles & Stoichiometry, Electrolysis, and Organic Chemistry
- 10 randomly selected questions per session, with a chapter selector on the setup screen
- 20-second countdown timer per question with a colour-changing progress bar (green → yellow → orange → red)
- Bonus +2 points awarded for correct answers within the first 5 seconds
- "Reveal Answer" option that gracefully removes the question from scoring
- Keyboard shortcuts: A–D (or 1–4) to choose, Enter to submit
- Progress dots show right, wrong, and skipped questions at a glance
- Real-time score tracking with audio feedback for correct, incorrect, bonus, and timeout events
- Player name entry with results saved to a persistent leaderboard

### ✨ EquiLab — Step-by-Step Equation Solver
- Balances 50 chemical equations using a rational nullspace algorithm (the same mathematical method used in professional chemistry software)
- Shows full working: element matrix construction, solution vector, and final balanced equation, with proper subscripts (H₂O, Pb(NO₃)₂)
- "One step at a time" mode with Back / Next / Show all / Restart controls and arrow-key navigation
- Search box to filter reactions, plus a Random reaction button
- Copy-to-clipboard for the full working, and A+ / A− font size controls
- Alternating colour-coded steps with the latest step highlighted
- Audio and visual feedback on selection and solution

### ⚗️ Fizz Factory — Interactive Gas Reactor
- Select two reactants from 6 gas/element species (H₂, O₂, Cl₂, K, N₂, CH₄)
- Set molar amounts using interactive sliders (0.5–5 mol)
- Predicts reaction type (ionic, covalent, combustion) using element classification logic
- Animated label flashing on reaction run
- Scrollable output log with stoichiometric ratio display
  
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
- All quiz scores saved to leaderboard.json with timestamps
- Top 10 displayed on the main menu at all times, with rank, name, score out of 10, speed bonus, and date
- Sorted by score descending, then speed bonus, then timestamp as the final tiebreaker
- Reset Leaderboard archives the best players into a permanent Top Scores Hall of Fame (top_scores.json) before clearing the board for new players
- View Top Scores opens the all-time top 10 in its own window

---
 
## The Science Behind It
 
### Equation Balancing : Rational Nullspace Method
 
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
<img width="1917" height="1010" alt="Screenshot 2026-10-03 135736" src="https://github.com/user-attachments/assets/726b41d5-d93a-4e35-8f0c-2f22ee6ab6b6" />
<img width="1917" height="1015" alt="Screenshot 2026-10-03 140346" src="https://github.com/user-attachments/assets/02031c5e-922f-46d5-856c-459005aec963" />
<img width="1901" height="1008" alt="Screenshot 2026-10-03 140635" src="https://github.com/user-attachments/assets/a4ee8461-9296-42e9-af8e-e076d6a7428e" />
<img width="1350" height="882" alt="Screenshot 2026-10-04 104433" src="https://github.com/user-attachments/assets/43d71489-10a2-413d-9275-1615de1d7738" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231030" src="https://github.com/user-attachments/assets/2b203fb2-76f5-4400-8df0-f59a2c689856" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231030" src="https://github.com/user-attachments/assets/d82b75d7-8c92-4aad-ab79-ad15fa223c78" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231131" src="https://github.com/user-attachments/assets/a4ffb595-76e1-4cfc-93ef-fb62add2d016" />
<img width="1917" height="1015" alt="Screenshot 2026-10-05 231239" src="https://github.com/user-attachments/assets/6432fdf3-9ca9-49ca-94fb-4f2fbdf4098f" />
<img width="1917" height="1013" alt="Screenshot 2026-10-05 231256" src="https://github.com/user-attachments/assets/10525e1e-c1e6-45b8-b0ed-8c669acb4e8b" />
<img width="1917" height="1013" alt="Screenshot 2026-10-05 231322" src="https://github.com/user-attachments/assets/8508f087-babc-4d6a-b607-d9f27c04b9ac" />
<img width="1916" height="1012" alt="Screenshot 2026-10-05 231335" src="https://github.com/user-attachments/assets/86768675-f997-48da-8468-310108e250fa" />
<img width="1915" height="1012" alt="Screenshot 2026-10-05 231355" src="https://github.com/user-attachments/assets/3812be7f-bccd-40c2-b18e-a22e8c0ed4f7" />
<img width="1917" height="1015" alt="Screenshot 2026-10-05 231404" src="https://github.com/user-attachments/assets/b50b61e3-714e-46b5-890d-aaa458d2fc1b" />
<img width="1917" height="1015" alt="Screenshot 2026-10-05 231411" src="https://github.com/user-attachments/assets/e347a54c-3640-4ff8-95c4-cd6d926c0feb" />
<img width="1917" height="1007" alt="Screenshot 2026-10-05 231420" src="https://github.com/user-attachments/assets/ce194466-0502-4820-840a-2314120b5d3c" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231433" src="https://github.com/user-attachments/assets/db018b22-b2ab-4528-b54f-09800618ce46" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231453" src="https://github.com/user-attachments/assets/79b6ed1c-f71f-4c77-93a1-a322799c8bd4" />
<img width="1917" height="1010" alt="Screenshot 2026-10-05 231504" src="https://github.com/user-attachments/assets/fdc2559a-162b-455d-ab57-28a5261c63e5" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231522" src="https://github.com/user-attachments/assets/a6865b2f-2b90-4c60-a657-914dd8085a3c" />
<img width="1917" height="1017" alt="Screenshot 2026-10-05 231535" src="https://github.com/user-attachments/assets/7f8843b2-6065-4d63-9389-b4dc24b504d5" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231602" src="https://github.com/user-attachments/assets/0fb129a9-059e-4a7c-a6e6-1975f230bf7d" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231722" src="https://github.com/user-attachments/assets/b53b7c8a-c819-43e8-bbf3-313a51cc2e86" />
<img width="1912" height="1015" alt="Screenshot 2026-10-05 231749" src="https://github.com/user-attachments/assets/ccacd960-c55a-4ed9-8005-c5f30d980a56" />
<img width="1917" height="1015" alt="Screenshot 2026-10-05 231858" src="https://github.com/user-attachments/assets/62afb10f-b1f8-416b-a720-ba7c9a35480d" />
<img width="1917" height="1012" alt="Screenshot 2026-10-05 231911" src="https://github.com/user-attachments/assets/aa2a7605-57d8-42de-98fa-51baca872d28" />
<img width="1917" height="1016" alt="Screenshot 2026-10-05 231921" src="https://github.com/user-attachments/assets/ac4e236e-8e47-4568-be29-fe46573420d7" />
<img width="1917" height="1012" alt="Screenshot 2026-10-05 231940" src="https://github.com/user-attachments/assets/731096e8-8922-4427-bd9f-bbf66a068641" />

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
On the other hand, the leaderboard was made after I remembered how hard students work when they are motivated to win a competition, because that same energy belongs in our chemistry education as well!

Since then, Bond Balancer has grown to cover more of the O-Level syllabus: atomic structure, mole calculations, organic chemistry, and electrolysis.
Now, each have topics has their own tool, so a student can revise a whole topic in one app.
 
---

## Future Development
 
- [x] Expand equation database beyond 20 (now 50 reactions)
- [x] Add organic chemistry (homologous series explorer)
- [x] Redesigned main menu and interface with colour-themed tools

**Three new menu tools**
- [ ] 🧫 **Experiment Station** : virtual practicals: titration, salt preparation, gas tests, and qualitative analysis (identifying cations and anions), so students can rehearse the practical paper without a physical lab
- [ ] 📖 **Theory Library** : illustrated revision notes and flashcards for every 5070 topic (bonding, the periodic table, acids, bases and salts, rates, energetics), linked to the matching quiz chapter
- [ ] 📝 **Exam Zone** : exam-style structured questions with mark schemes and self-marking, to move from multiple choice to full written answers

**New topics and content**
- [ ] Add acids, bases and salts, rates of reaction, and energetics chapters to the quiz and tools
- [ ] Add organic chemistry reaction mechanisms
- [ ] Interactive periodic table with trends (reactivity, atomic radius, electronegativity)
- [ ] Expand the quiz bank beyond 84 questions, with difficulty levels (easy, medium, hard)
- [ ] More gas species and reaction types in Fizz Factory
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
 
This project was developed as an independent science fair entry, exploring the intersection of **computer science and chemistry education**. 
The rational nullspace balancing algorithm was researched and implemented from first principles with no chemistry libraries being used.
 
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
 
MIT License — free to use, modify, and distribute with attribution.
