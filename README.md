# 🎮 NostalgiKit - Vintage Handheld Gaming Hub 🎮

## 📱 Authentic Retro Handheld Experience

Transform your PC into a classic vintage handheld console! Enjoy three fully modernized retro games with authentic handheld styling, complete with the iconic green monochrome display and classic button controls.

## 🎯 Featured Games

### 1. 🔮 Number Oracle (Card Guess)
- **Genre**: Puzzle/Strategy
- **Gameplay**: Think of a number from 1 to 20, answer YES/NO for 5 magic cards and the oracle reveals it
- **Features**: 
  - Retro handheld card display system
  - Binary magic cards - the oracle always finds the right number
  - Classic monochrome aesthetics

### 2. ⚔️ War Game (Turn-Based Combat)
- **Genre**: RPG/Strategy
- **Gameplay**: Engage in tactical turn-based battles
- **Features**:
  - Strategic combat system (Attack, Defend, Heal, Special)
  - ASCII art character sprites
  - Health bar visualization
  - Round-based progression
  - Special attack cooldown system

### 3. 🌊 River Puzzle (Logic Challenge)
- **Genre**: Logic Puzzle
- **Gameplay**: Classic farmer, wolf, goat, and cabbage river crossing puzzle
- **Features**:
  - Interactive river scene visualization
  - Character icon system (F=Farmer, W=Wolf, G=Goat, C=Cabbage)
  - Move counter and performance rating
  - Logic validation system
  - Multiple difficulty scenarios

### 4. 🚀 Galaxy War Pat (Space Shooter)
- **Genre**: Arcade/Action
- **Gameplay**: Retro arcade shooter - hold off descending formations of original pixel-art aliens
- **Features**:
  - Fast-paced arcade action
  - Custom pixel art enemy designs (Jelly, Prism, Beetle)
  - Wave-based progression system
  - Lives and scoring mechanics
  - Increasing difficulty with speed boosts
  - Particle explosion effects
  - Full gamepad support

### 5. 🍰 Crakers (Grid Adventure)
- **Genre**: Arcade/Action
- **Gameplay**: Top-down grid-based adventure with gems, enemies, and power-ups
- **Features**:
  - Retro grid-based movement system
  - Gem collection mechanics
  - **Intelligent Enemy AI with State Machine**
    - **PATROL Mode**: Enemy follows patrol route (hollow guard)
    - **CHASE Mode**: Spots player within 6-tile vision radius and pursues with A* pathfinding (solid dark guard)
    - **SEARCH Mode**: Lost sight of player, searches last known location (mid-tone guard)
    - Line-of-sight vision system (walls block vision)
    - Predictive movement targeting
  - A* pathfinding for smart wall navigation
  - Dash power-up ability
  - HUD with score and lives tracking
  - Win/Lose screen with retry system
  - Full keyboard and gamepad controls

### 6. 🧱 Block Stack (Falling Blocks)
- **Genre**: Puzzle/Arcade
- **Gameplay**: Classic falling tetromino puzzle tuned for the green monochrome display
- **Features**:
  - Smooth soft/hard drop with rotation
  - Next-piece preview and level-based speed
  - Score, line, and level HUD in retro styling
  - Gamepad-ready controls with pause and quick restart

## 🎮 NostalgiKit Controls

Every game uses the same buttons, the same screen layout (title bar on top, hints at the bottom)
and the same green four-shade palette. Keyboard, gamepad and the on-screen buttons all do the same thing.

| Button | Keyboard | Gamepad | What it does |
|--------|----------|---------|--------------|
| **D-Pad** | Arrow keys / WASD | D-Pad or left stick | Move, navigate menus |
| **X** (red) | Space / X | A or X | Confirm, primary action (fire, rotate, dash...) |
| **Y** (purple) | Esc / Backspace / Y | B or Y | Back; pauses action games (press again to exit) |
| **START** | Enter / P | START | Start a game, pause / resume |
| **SELECT** | Tab | BACK | Return to the hub menu from anywhere |

The bottom line of the screen always shows what X / Y / D-Pad do on the current screen.

### Authentic Handheld Features
- **Vintage Cream Theme**: Authentic #E8E0C7 vintage cream body
- **Four-Shade Green Screen**: Classic dot-matrix palette shared by every game
- **Courier Font**: Pixelated monospace text for retro feel
- **Physical Button Layout**: Real handheld button arrangement

## 🚀 Quick Start

### Method 1: Windows Batch File (Recommended)
```cmd
start_games.bat
```
Double-click the `start_games.bat` file for the complete NostalgiKit launcher experience with retro-style startup screen.

### Method 2: Python Main Launcher
```cmd
python main.py
```
Launches the hub with dependency checking and error handling.

### Method 3: Direct Hub Launch
```cmd
python game_hub.py
```
Direct access to the NostalgiKit gaming hub interface.

## 📋 System Requirements

- **Python 3.7+**
- **tkinter** (usually included with Python)
- **PIL/Pillow** for image processing:
  ```cmd
  pip install Pillow
  ```
- **pygame** for gamepad support (optional - games work without it):
  ```cmd
  pip install pygame
  ```
  On Python versions where `pygame` has no wheel yet (e.g. 3.14), use `pip install pygame-ce` instead.

## 🛠️ Installation

1. **Clone or Download** all game files to your directory
2. **Install Dependencies**:
   ```cmd
   pip install Pillow pygame
   ```
3. **Launch NostalgiKit**:
   - **Windows**: Double-click `start_games.bat`
   - **All Platforms**: Run `python main.py`
   - **Direct**: Run `python game_hub.py`

## 📁 File Structure

```
📦 NostalgiKit
├── 🎮 game_hub.py                # Main NostalgiKit interface (console, menus, input)
├── 🎨 nostalgik_ui.py            # Shared UI kit: palette, fonts, screen layout, input routing
├── 🕹️ console_widgets.py       # Console hardware: screen bezel, D-Pad, X/Y, SELECT/START
├── 🔮 card_guess_nostalgik.py    # Number Oracle game
├── ⚔️ war_game_nostalgik.py      # War Game combat
├── 🌊 river_game_nostalgik.py    # River Puzzle logic
├── 🚀 galaxy_war_pat.py          # Galaxy War Pat shooter
├── 🍰 crakers_nostalgik.py       # Crakers Grid Adventure
├── 🧱 block_stack_nostalgik.py   # Block Stack falling blocks
├── 🏁 main.py                    # Application launcher with dependency checks
├── 🎯 start_games.bat            # Windows launcher with retro startup screen
├── 📖 README.md                  # This documentation
├── 📜 LICENSE.md                 # MIT License
├── 📜 COPYRIGHT.md               # Copyright notice
└── 📜 DISCLAIMER                 # Legal disclaimer
```

## 🎨 Design Philosophy

### Authentic Retro Gaming
- **Pixel-Perfect Recreation**: Every element designed to match classic handheld aesthetics
- **Vintage Excellence**: Cream and green color palette for authentic retro feel
- **Physical Hardware Simulation**: Realistic button layout and screen proportions

### Modern Functionality
- **Enhanced Gameplay**: Original console games transformed with visual interfaces
- **Intuitive Controls**: Both keyboard and mouse support for accessibility
- **Progressive Difficulty**: Games designed for replayability and mastery

## 🎯 Gameplay Tips

### Number Oracle Secret
- Each card holds the numbers that share one binary bit (1, 2, 4, 8, 16)
- The oracle simply adds up the first number of every card you said YES to

### War Game Tactics
- Balance offense and defense strategically
- Save special attacks for critical moments
- Monitor enemy health for healing opportunities
- Use defend action when expecting heavy attacks

### River Puzzle Solutions
- Remember: Never leave wolf+goat or goat+cabbage alone
- Farmer must be present to prevent conflicts
- Optimal solution requires exactly 7 moves
- Think several moves ahead for efficient crossing

### Galaxy War Pat Strategy
- Keep moving to avoid enemy fire
- Focus on clearing bottom rows first
- Use edges for tactical positioning
- Watch enemy drop patterns for safe zones

### Crakers Adventure Tips
- Plan your route to collect all gems
- **Watch the guard's shade**: Solid dark = chasing you, mid-tone = searching, hollow = patrolling
- **Use line-of-sight**: Hide behind walls to break enemy vision and escape
- Save dash for emergencies or speedruns
- **Enemy AI is smart**: It uses A* pathfinding and predicts your movement
- Corner enemies to avoid confrontation, but remember they can see through 6 tiles
- Lead enemies away from gem clusters before collecting

### Block Stack Tips
- Keep a flat stack; leave a clean channel for hard drops
- Use soft drops to gently place pieces when speed rises
- Rotate before sliding into gaps to avoid wall kicks
- Clearing four lines (a "stack smash") yields the biggest rewards

## 🔧 Technical Features

### Retro Handheld Simulation
- **Window**: the whole 460x694 window is the console body, with a 334x367 game screen
- **Color Palette**: Authentic vintage cream body, four-shade green screen
- **One UI Kit**: `nostalgik_ui.py` gives every game the same layout, palette, fonts and controls
- **Font System**: Courier monospace for pixelated text rendering
- **Button Response**: Physical feedback simulation

### Modern Enhancements
- **Keyboard Binding System**: Comprehensive input handling
- **Focus Management**: Automatic window focus for input reception
- **Error Handling**: Graceful degradation and user feedback
- **Cross-Platform**: Works on Windows, Mac, and Linux

## 🎵 Retro Atmosphere

Experience the nostalgia of classic handheld gaming:
- **Authentic Visual Design**: Pixel-perfect retro handheld recreation
- **Classic Game Mechanics**: Time-tested gameplay patterns
- **Retro Typography**: Monospace fonts for that classic gaming feel
- **Period-Appropriate UI**: Menu systems that feel authentically retro

## 🏆 Achievement System

### Number Oracle Mastery
- **Mind Reader**: Work out how the oracle does it without reading the code

### War Game Victory
- **Swift Victory**: Win in under 5 rounds
- **Perfect Defense**: Win without taking damage
- **Tactical Master**: Win using all four action types

### River Puzzle Excellence
- **Optimal Solution**: Complete in exactly 7 moves
- **Efficiency Expert**: Complete in under 10 moves
- **Logic Master**: Complete without any failed attempts

### Galaxy War Pat Mastery
- **Sharp Shooter**: Achieve 90%+ accuracy
- **Survivor**: Complete 5 waves without losing a life
- **High Scorer**: Reach 10,000 points
- **Speed Demon**: Clear a wave in under 30 seconds

### Crakers Adventure Mastery
- **Gem Collector**: Collect all gems without taking damage
- **Speed Runner**: Complete level in under 60 seconds
- **Perfect Run**: Win with all 3 lives intact
- **Dash Master**: Complete using dash ability strategically

## 🎮 The Complete NostalgiKit Experience

Step back in time to the golden age of portable gaming! Our NostalgiKit recreates the magic of vintage handheld consoles while bringing six beloved games into the modern era - from classic puzzle and strategy to fast-paced arcade action. Whether you're a retro gaming enthusiast or discovering these gameplay styles for the first time, prepare for hours of engaging, nostalgic entertainment.

**🎯 Ready to Game? Launch your NostalgiKit and dive into retro gaming perfection!**

---

## 📜 License & Copyright

### Copyright Notice
Copyright (c) 2025-2026 NostalgiKit Project by B. Tamer Akipek.

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

### Intellectual Property
- All source code, graphics, documentation, and design elements are original works
- No copyrighted or trademarked materials from third parties are used
- The retro gaming aesthetic is inspired by classic handheld gaming without infringing on any existing intellectual property

### Legal Compliance
- ✅ **Original Content**: All code and assets are created from scratch
- ✅ **MIT Licensed**: Open source with permissive licensing
- ✅ **Trademark Safe**: No use of existing gaming company trademarks
- ✅ **Copyright Protected**: Proper attribution and licensing

### Usage Rights
Under the MIT License, you are free to:
- Use the software commercially and personally
- Modify and create derivative works
- Distribute copies of the software
- Include in proprietary software

**Condition**: The copyright notice and license must be included in all copies.

---

### 📝 Legal Notice
NostalgiKit is an original creation inspired by classic handheld gaming aesthetics. All code, design elements, and branding are original and do not infringe on any copyrighted material. The vintage handheld design is a homage to the golden era of portable gaming without using any trademarked names, logos, or proprietary elements.
