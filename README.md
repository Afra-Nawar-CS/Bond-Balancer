# 🧪 Bond Balancer
### *Where Chemistry Comes Alive*
 
> **🏆 Winner — Best Chemistry Project, School Science Fair**  
> Built independently by a Grade 9 student of HURDCO International School, as an exploration of computational chemistry and interactive education.
 
---
 
## What Is Bond Balancer?
An app made by 16-year-old Afra Nawar for struggling students to enjoy relearning chemistry through 
the interface of a simple game.  
Bond Balancer is a fully interactive desktop chemistry learning application built in Python. It combines real mathematical equation-balancing (using rational nullspace computation) with a gamified quiz system and an interactive virtual laboratory; making chemistry accessible, visual, and competitive for students at any level.
 
---
 
## Features
 
### ⚔️ Bond Battle — MCQ Quiz
- 30-question pool with 10 randomly selected questions per session
- 20-second countdown timer per question with a **colour-changing progress bar** (green → yellow → orange → red)
- **Bonus +2 points** awarded for answering within the first 15 seconds
- "Reveal Answer" option that gracefully removes the question from scoring
- Real-time score tracking with audio feedback for correct, incorrect, bonus, and timeout events
- Player name entry with results saved to a **persistent leaderboard**
### ✨ EquiLab — Step-by-Step Equation Solver
- Balances 20 chemical equations using a **rational nullspace algorithm** (the same mathematical method used in professional chemistry software)
- Shows full working: element matrix construction, solution vector, and final balanced equation
- Alternating colour-coded steps for readability
- Audio and visual feedback on selection and solution
### ⚗️ Fizz Factory — Interactive Gas Reactor
- Select two reactants from 6 gas/element species (H₂, O₂, Cl₂, K, N₂, CH₄)
- Set molar amounts using interactive sliders (0.5–5 mol)
- Predicts reaction type (ionic, covalent, combustion) using element classification logic
- Animated label flashing on reaction run
- Scrollable output log with stoichiometric ratio display
### 🏆 Persistent Leaderboard
- All quiz scores saved to `leaderboard.json` with timestamps
- Top 10 displayed on the main menu at all times
- Full leaderboard accessible in a separate window
- Sorted by score descending, timestamp as tiebreaker
---
 
## The Science Behind It
 
### Equation Balancing — Rational Nullspace Method
 
Most equation balancers use trial and error. However, Bond Balancer is unique, because it uses **linear algebra**.
 
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
| GUI Framework | Tkinter + TTK |
| Mathematical Core | `fractions.Fraction`, `math.gcd` |
| Audio | `winsound` (Windows), threaded beep sequences |
| Persistence | JSON (leaderboard.json) |
| Concurrency | `threading` (non-blocking audio) |
| Chemistry Parser | Custom recursive tokenizer with regex |
 
---
 
## How to Run
 
### Requirements
- Python 3.7 or higher
- Windows OS (for `winsound` audio — app runs without audio on other platforms)
- No external libraries required (all standard library)
### Steps
```bash
# Clone the repository
git clone https://github.com/YOURUSERNAME/bond-balancer.git
 
# Navigate into the folder
cd bond-balancer
 
# Run the app
python bond_balancer.py
```
 
The leaderboard is automatically created as `leaderboard.json` in the same directory on first run.
 
---
 
## Visual Display

<img width="1239" height="978" alt="Screenshot 2026-05-23 164948" src="https://github.com/user-attachments/assets/dbc56748-8d09-44c5-8f96-5dc52d5791ea" />
<img width="1235" height="804" alt="Screenshot 2026-05-23 165112" src="https://github.com/user-attachments/assets/0f48329d-ffd3-49ae-af48-f0db479f31c6" />
<img width="1160" height="826" alt="Screenshot 2026-05-23 165136" src="https://github.com/user-attachments/assets/a3e11bfb-568a-440e-b19c-cc6fb9b6c5c4" />
<img width="1141" height="901" alt="Screenshot 2026-05-23 165208" src="https://github.com/user-attachments/assets/77eaf920-d18f-485f-ba1e-56d1ebc9e16f" />
 

 
---
 
## Project Structure
 
```
bond-balancer/
│
├── bond_balancer.py      # Main application (all features)
├── leaderboard.json      # Auto-generated on first run
└── README.md             # This file
```
 
---
 
## Why I Built This
 
Chemistry can feel intimidating; especially because of equation balancing, where students fail to remember how to use logical processes when they see complex compounds. I wanted to build something that showed the *mathematical structure* underneath chemical equations, while making practice genuinely engaging through competition and experimentation.
 
The gas reactor grew from my curiosity: what if students could experiment without a physical lab? 
On the other hand, The leaderboard was made after I remembered how hard students work when they are motivated to win a competition, because that same energy belongs in chemistry education as well!
 
---
 
## Future Development
 
- [ ] Expand equation database beyond 20
- [ ] Add organic chemistry reaction mechanisms
- [ ] Introduce 3D molecular visualisation
- [ ] Cross-platform audio (replace `winsound`)
- [ ] Web version for browser access
- [ ] Teacher dashboard for classroom leaderboard management
- [ ] More gas species and reaction types in Fizz Factory
---
 
## Academic Context
 
This project was developed as an independent science fair entry exploring the intersection of **computer science and chemistry education**. The rational nullspace balancing algorithm was researched and implemented from first principles — no chemistry libraries were used.
 
**Skills demonstrated:**
- Algorithm design and linear algebra implementation
- GUI application development
- Object-oriented programming
- Data persistence and file I/O
- Multi-threading for responsive UI
- Chemistry domain knowledge (stoichiometry, reaction types, element classification)
---
 
## Author
 
**Afra Nawar**  
Grade 9B Student | Cambridge O-Level Candidate 2027  
Interests: Computational Chemistry, Computer Science, Environmental Technology  
 
*Open to feedback, collaboration, and questions about the algorithm.*
 
---
 
## License
 
MIT License — free to use, modify, and distribute with attribution.
