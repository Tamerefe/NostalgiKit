# 🎮 NostalgiKit - Vintage Handheld Gaming Hub 🎮

## 📱 Authentic Retro Handheld Experience

Transform your PC into a classic vintage handheld console! Enjoy three fully modernized retro games with authentic handheld styling, complete with the iconic green monochrome display and classic button controls.

## 🎯 Featured Games

### 1. 🔮 Number Oracle (Card Guess)
- **Genre**: Puzzle/Strategy
- **Gameplay**: Use magical deduction to guess the secret number
- **Features**: 
  - Retro handheld card display system
  - Intelligent hint system
  - Achievement tracking
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
- **Gameplay**: Classic space invaders-style shooter with unique pixel art design
- **Features**:
  - Fast-paced arcade action
  - Custom pixel art enemy designs (Squid, Diamond, Crab)
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
    - **PATROL Mode**: Enemy follows patrol route (dark red)
    - **CHASE Mode**: Spots player within 6-tile vision radius and pursues with A* pathfinding (bright red)
    - **SEARCH Mode**: Lost sight of player, searches last known location (orange)
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

### D-Pad Navigation
- **Arrow Keys / WASD**: Navigate menus and make selections
- **UP/DOWN**: Navigate through menu options
- **LEFT/RIGHT**: Additional navigation (game-specific)

### Action Buttons
- **X Button** (Space/Enter/X): Select, Confirm, Execute actions - **RED**
- **Y Button** (Escape/Backspace/Y): Cancel, Back, Exit to menu - **PURPLE**
- **START Button**: Begin games, confirm selections
- **SELECT Button** (Tab): Return to main menu from any game

### Authentic Handheld Features
- **400x600 Pixel Display**: Classic handheld screen proportions
- **Vintage Cream Theme**: Authentic #E8E0C7 vintage cream body
- **Monochrome Green Screen**: Classic #9BBB59 green display
- **Courier Font**: Pixelated monospace text for retro feel
- **Physical Button Layout**: Real handheld button arrangement
- **Retro-Style Branding**: Classic portable console aesthetics

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
- **pygame** for gamepad support (optional):
  ```cmd
  pip install pygame
  ```

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
├── 🎮 game_hub.py                # Main NostalgiKit interface
├── 🔮 card_guess_nostalgik.py    # Number Oracle game
├── ⚔️ war_game_nostalgik.py      # War Game combat
├── 🌊 river_game_nostalgik.py    # River Puzzle logic
├── 🚀 galaxy_war_pat.py          # Galaxy War Pat shooter
├── � crakers_nostalgik.py       # Crakers Grid Adventure
├── 🧱 tetris_nostalgik.py        # Block Stack falling blocks
├── �🏁 main.py                    # Application launcher with dependency checks
├── 🎯 start_games.bat            # Windows launcher with retro startup screen
├── 📖 README.md                  # This documentation
├── 📜 LICENSE.md                 # MIT License
├── 📜 VERSION.md                 # Version information
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

### Number Oracle Strategy
- Start with middle-range guesses (around 50)
- Use binary search logic for optimal efficiency
- Pay attention to hint patterns for faster solving

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
- **Watch enemy color changes**: Red = chasing you, Orange = searching, Dark red = patrolling
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
- **Screen Resolution**: 400x600 pixels (classic proportions)
- **Color Palette**: Authentic vintage cream and green theme
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
- **Quick Guess**: Solve in under 5 attempts
- **Perfect Logic**: Use optimal binary search strategy
- **Lucky Guess**: Hit the number on first try

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

Step back in time to the golden age of portable gaming! Our NostalgiKit recreates the magic of vintage handheld consoles while bringing five beloved games into the modern era - from classic puzzle and strategy to fast-paced arcade action. Whether you're a retro gaming enthusiast or discovering these gameplay styles for the first time, prepare for hours of engaging, nostalgic entertainment.

**🎯 Ready to Game? Launch your NostalgiKit and dive into retro gaming perfection!**

---

## 📜 License & Copyright

### Copyright Notice
Copyright (c) 2025-2026 NostalgiKit Project by B. Tamer Akipek. All rights reserved.

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
