"""
NostalgiKit War Game - Retro Style
Turn-based combat with authentic retro handheld look and feel

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import random
import threading
import time
import pygame  # For gamepad support

class NostalgiKitWarGame:
    def __init__(self, parent, return_callback):
        self.parent = parent
        self.return_callback = return_callback
        
        # Character classes with different stats and abilities
        self.character_classes = {
            "WARRIOR": {
                "name": "WARRIOR",
                "sprite": "♠",
                "hp": 120,
                "attack": (18, 28),
                "heal": (15, 25),
                "special": {"name": "RAGE", "damage": (30, 40), "desc": "Berserker strike"},
                "desc": "High HP, strong attacks"
            },
            "MAGE": {
                "name": "MAGE",
                "sprite": "♦",
                "hp": 80,
                "attack": (12, 20),
                "heal": (25, 35),
                "special": {"name": "FIREBALL", "damage": (35, 45), "desc": "Magic blast"},
                "desc": "Low HP, powerful magic"
            },
            "ROGUE": {
                "name": "ROGUE",
                "sprite": "♣",
                "hp": 100,
                "attack": (15, 25),
                "heal": (20, 30),
                "special": {"name": "BACKSTAB", "damage": (40, 50), "desc": "Critical strike"},
                "desc": "Balanced, high crit"
            },
            "PALADIN": {
                "name": "PALADIN",
                "sprite": "♥",
                "hp": 110,
                "attack": (16, 24),
                "heal": (30, 40),
                "special": {"name": "HOLY LIGHT", "damage": (25, 35), "desc": "Light damage + heal"},
                "desc": "Good HP, best healing"
            }
        }
        
        # Game state
        self.selected_character = 0
        self.player_class = None
        self.player_hp = 100
        self.player_max_hp = 100
        self.enemy_hp = 100
        self.enemy_max_hp = 100
        self.player_name = "HERO"
        self.enemy_name = "ENEMY"
        self.enemy_class = None
        self.battle_log = []
        self.selected_action = 0
        self.game_over = False
        self.battle_round = 1
        self.wins = 0
        self.losses = 0
        
        # Dynamic actions based on character
        self.actions = []
        
        self.defending = False
        self.enemy_defending = False
        self.special_cooldown = 0
        
        # NostalgiKit colors (matching game_hub.py exactly)
        self.colors = {
            'NostalgiKit_cream': '#E8E0C7',      # Main vintage cream color
            'screen_green': '#9BBB59',        # Classic green screen
            'dark_green': '#8B9467',          # Dark accents
            'screen_dark': '#374224',         # Dark screen areas
            'button_gray': '#8E8E93',         # Button color
            'text_dark': '#1C1C1E',           # Dark text
            'highlight': '#FFD23F',           # Yellow highlight
            'red_button': '#FF3B30',          # X button (red)
            'purple_button': '#8E44AD'        # Y button (purple)
        }
        
        self.current_screen = "intro"
        self.gamepad_polling_active = True
        self.setup_fonts()
        self.setup_retro_interface()
        self.init_gamepad()
        
    def setup_character_actions(self, character_class):
        """Setup actions based on character class"""
        char_data = self.character_classes[character_class]
        attack_min, attack_max = char_data["attack"]
        heal_min, heal_max = char_data["heal"]
        special_data = char_data["special"]
        
        self.actions = [
            {"name": "ATTACK", "desc": f"Deal {attack_min}-{attack_max} damage"},
            {"name": "DEFEND", "desc": "Block 50% damage next turn"},
            {"name": "HEAL", "desc": f"Restore {heal_min}-{heal_max} HP"},
            {"name": special_data["name"], "desc": special_data["desc"]}
        ]
        
    def setup_fonts(self):
        """Setup NostalgiKit style fonts (matching game_hub.py exactly)"""
        self.fonts = {
            'retro_title': tkFont.Font(family="Courier", size=10, weight="bold"),
            'retro_text': tkFont.Font(family="Courier", size=9, weight="bold"),
            'retro_small': tkFont.Font(family="Courier", size=8, weight="bold"),
            'retro_large': tkFont.Font(family="Courier", size=12, weight="bold"),
            'retro_tiny': tkFont.Font(family="Courier", size=7, weight="bold")
        }
        
    def setup_retro_interface(self):
        """Create game interface inside hub's screen frame"""
        # Create main game frame inside hub's screen (parent is now the screen frame)
        # Only create once - reuse on subsequent calls
        if not hasattr(self, 'game_frame') or not self.game_frame.winfo_exists():
            self.game_frame = tk.Frame(self.parent, bg=self.colors['screen_green'])
            self.game_frame.pack(fill='both', expand=True)
        
        # Clear any previous content
        self.clear_screen()
        
        # Setup keyboard bindings to root window
        root = self.parent.winfo_toplevel()
        root.focus_set()
        root.bind('<Key>', self.on_key_press)
        root.bind('<Button-1>', lambda e: root.focus_set())
        
        # Start with intro
        self.show_intro()
        
        # Gamepad initialization will happen after this
    def init_gamepad(self):
        """Initialize gamepad support"""
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            
            self.joystick = None
            self.gamepad_enabled = True
            self.gamepad_polling_active = True
            self.last_button_state = {}
            self.last_hat = (0, 0)
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            
            # Start gamepad polling with root window
            root = self.parent.winfo_toplevel()
            root.after(30, self.poll_gamepad)
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to allow proper program termination
            raise
        except Exception as e:
            print(f"Gamepad init error: {e}")
            self.gamepad_enabled = False
    
    def poll_gamepad(self):
        """Poll gamepad input"""
        if not self.gamepad_enabled or not self.gamepad_polling_active:
            return
        
        try:
            self.parent.winfo_toplevel().winfo_exists()
        except:
            return
        
        try:
            pygame.event.pump()
            
            if self.joystick is not None and self.joystick.get_init():
                def is_pressed(btn):
                    try:
                        return self.joystick.get_button(btn) == 1
                    except:
                        return False
                
                def just_pressed(btn):
                    current = is_pressed(btn)
                    previous = self.last_button_state.get(btn, False)
                    self.last_button_state[btn] = current
                    return current and not previous
                
                # Simulate key presses
                if just_pressed(0) or just_pressed(2):  # A or X
                    event = type('Event', (), {'keysym': 'Return', 'char': '\r'})()
                    self.on_key_press(event)
                
                if just_pressed(1) or just_pressed(3):  # B or Y
                    event = type('Event', (), {'keysym': 'Escape', 'char': '\x1b'})()
                    self.on_key_press(event)
                
                # D-Pad
                try:
                    hat = self.joystick.get_hat(0)
                    if hat != self.last_hat:
                        if hat == (0, 1):  # UP
                            event = type('Event', (), {'keysym': 'Up', 'char': ''})()
                            self.on_key_press(event)
                        elif hat == (0, -1):  # DOWN
                            event = type('Event', (), {'keysym': 'Down', 'char': ''})()
                            self.on_key_press(event)
                        self.last_hat = hat
                except:
                    pass
        
        except KeyboardInterrupt:
            # Stop polling and re-raise to allow proper program termination
            self.gamepad_polling_active = False
            raise
        except Exception as e:
            if "bad window" not in str(e):
                print(f"Gamepad poll error: {e}")
        
        try:
            root = self.parent.winfo_toplevel()
            root.after(30, self.poll_gamepad)
        except:
            pass
    
    def on_key_press(self, event):
        """Handle keyboard input"""
        key = event.keysym.lower()
        
        # Direction keys
        if key in ['up', 'w']:
            self.dpad_up()
        elif key in ['down', 's']:
            self.dpad_down()
        elif key in ['left', 'a']:
            self.dpad_left()
        elif key in ['right', 'd']:
            self.dpad_right()
        # Action buttons
        elif key in ['return', 'space', 'x']:
            self.x_button_action()
        elif key in ['escape', 'backspace', 'y']:
            self.y_button_action()
        elif key in ['tab']:
            self.exit_game()
            
    def show_intro(self):
        """Show game introduction with character selection"""
        self.clear_screen()
        self.current_screen = "character_select"
        
        content = tk.Frame(self.game_frame, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = tk.Label(content,
                              text="WAR GAME",
                              font=self.fonts['retro_title'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        title_label.pack(pady=(5, 2))
        
        # Subtitle
        subtitle_label = tk.Label(content,
                                 text="Choose Your Fighter",
                                 font=self.fonts['retro_small'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        subtitle_label.pack(pady=(0, 5))
        
        # Character selection
        char_frame = tk.Frame(content, bg=self.colors['screen_green'])
        char_frame.pack(fill='both', expand=True, pady=5)
        
        # Display characters
        char_names = list(self.character_classes.keys())
        for i, char_name in enumerate(char_names):
            char_data = self.character_classes[char_name]
            
            if i == self.selected_character:
                display_text = f"> {char_data['sprite']} {char_name}"
                bg_color = self.colors['screen_dark']
                fg_color = self.colors['screen_green']
            else:
                display_text = f"  {char_data['sprite']} {char_name}"
                bg_color = self.colors['screen_green']
                fg_color = self.colors['screen_dark']
                
            char_label = tk.Label(char_frame,
                                 text=display_text,
                                 font=self.fonts['retro_text'],
                                 fg=fg_color,
                                 bg=bg_color,
                                 anchor='w')
            char_label.pack(fill='x', padx=10, pady=1)
            
        # Show selected character details
        selected_char = char_names[self.selected_character]
        char_data = self.character_classes[selected_char]
        
        # Character stats
        stats_frame = tk.Frame(content, bg=self.colors['screen_green'])
        stats_frame.pack(fill='x', pady=5)
        
        stats_text = f"""HP: {char_data['hp']}
ATK: {char_data['attack'][0]}-{char_data['attack'][1]}
HEAL: {char_data['heal'][0]}-{char_data['heal'][1]}
SPECIAL: {char_data['special']['name']}

{char_data['desc']}"""
        
        stats_label = tk.Label(stats_frame,
                              text=stats_text,
                              font=self.fonts['retro_tiny'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              justify='center')
        stats_label.pack()
        
        # Score display
        if self.wins > 0 or self.losses > 0:
            score_label = tk.Label(content,
                                  text=f"WINS: {self.wins}  LOSSES: {self.losses}",
                                  font=self.fonts['retro_tiny'],
                                  fg=self.colors['screen_dark'],
                                  bg=self.colors['screen_green'])
            score_label.pack(pady=2)
        
        # Controls info
        controls_label = tk.Label(content,
                                 text="UP/DOWN:Select  X:Choose  Y:Back",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=2)
        
    def start_battle(self):
        """Start a new battle with selected character"""
        char_names = list(self.character_classes.keys())
        self.player_class = char_names[self.selected_character]
        player_data = self.character_classes[self.player_class]
        
        # Set up player stats
        self.player_hp = player_data["hp"]
        self.player_max_hp = player_data["hp"]
        self.player_name = self.player_class
        
        # Select random enemy
        enemy_options = [name for name in char_names if name != self.player_class]
        self.enemy_class = random.choice(enemy_options)
        enemy_data = self.character_classes[self.enemy_class]
        
        self.enemy_hp = enemy_data["hp"]
        self.enemy_max_hp = enemy_data["hp"]
        self.enemy_name = self.enemy_class
        
        # Setup character-specific actions
        self.setup_character_actions(self.player_class)
        
        # Reset battle state
        self.battle_log = []
        self.selected_action = 0
        self.game_over = False
        self.battle_round = 1
        self.defending = False
        self.enemy_defending = False
        self.special_cooldown = 0
        self.current_screen = "battle"
        
        self.show_battle_screen()
        
    def show_battle_screen(self):
        """Show the main battle screen"""
        self.clear_screen()
        
        content = tk.Frame(self.game_frame, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Round counter
        round_label = tk.Label(content,
                              text=f"ROUND {self.battle_round}",
                              font=self.fonts['retro_small'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        round_label.pack(pady=2)
        
        # Health bars
        self.draw_health_bars(content)
        
        # Battle area
        self.draw_battle_area(content)
        
        # Action selection (if not game over)
        if not self.game_over:
            self.draw_action_menu(content)
        else:
            self.draw_game_over(content)
            
    def draw_health_bars(self, parent):
        """Draw health bars for both characters"""
        health_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        health_frame.pack(fill='x', pady=5)
        
        # Player health
        player_frame = tk.Frame(health_frame, bg=self.colors['screen_green'])
        player_frame.pack(fill='x')
        
        player_label = tk.Label(player_frame,
                               text=f"{self.player_name}: {self.player_hp}/{self.player_max_hp}",
                               font=self.fonts['retro_tiny'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'],
                               anchor='w')
        player_label.pack(side='left')
        
        # Player health bar
        player_bar = self.create_health_bar(player_frame, self.player_hp, self.player_max_hp)
        player_bar.pack(side='right', padx=5)
        
        # Enemy health
        enemy_frame = tk.Frame(health_frame, bg=self.colors['screen_green'])
        enemy_frame.pack(fill='x')
        
        enemy_label = tk.Label(enemy_frame,
                              text=f"{self.enemy_name}: {self.enemy_hp}/{self.enemy_max_hp}",
                              font=self.fonts['retro_tiny'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              anchor='w')
        enemy_label.pack(side='left')
        
        # Enemy health bar
        enemy_bar = self.create_health_bar(enemy_frame, self.enemy_hp, self.enemy_max_hp)
        enemy_bar.pack(side='right', padx=5)
        
    def create_health_bar(self, parent, current_hp, max_hp):
        """Create a text-based health bar"""
        bar_width = 10
        filled = int((current_hp / max_hp) * bar_width)
        empty = bar_width - filled
        
        bar_text = "█" * filled + "░" * empty
        
        bar_label = tk.Label(parent,
                            text=f"[{bar_text}]",
                            font=self.fonts['retro_tiny'],
                            fg=self.colors['screen_dark'],
                            bg=self.colors['screen_green'])
        return bar_label
        
    def draw_battle_area(self, parent):
        """Draw the battle visualization with character sprites"""
        battle_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        battle_frame.pack(fill='x', pady=5)
        
        # Player side with character sprite
        if self.player_class:
            player_sprite = f"""{self.character_classes[self.player_class]['sprite']}
/|\\
/ \\"""
        else:
            player_sprite = """♂
/|\\
/ \\"""
        
        player_label = tk.Label(battle_frame,
                               text=player_sprite,
                               font=self.fonts['retro_small'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'],
                               justify='center')
        player_label.pack(side='left', padx=10)
        
        # VS
        vs_label = tk.Label(battle_frame,
                           text="VS",
                           font=self.fonts['retro_text'],
                           fg=self.colors['screen_dark'],
                           bg=self.colors['screen_green'])
        vs_label.pack(side='left', expand=True)
        
        # Enemy side with character sprite
        if self.enemy_class:
            enemy_sprite = f"""{self.character_classes[self.enemy_class]['sprite']}
/|\\
/ \\"""
        else:
            enemy_sprite = """☠
/|\\
/ \\"""
        
        enemy_label = tk.Label(battle_frame,
                              text=enemy_sprite,
                              font=self.fonts['retro_small'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              justify='center')
        enemy_label.pack(side='right', padx=10)
        
        # Status effects
        status_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        status_frame.pack(fill='x')
        
        status_text = ""
        if self.defending:
            status_text += "YOU: DEFENDING "
        if self.enemy_defending:
            status_text += "ENEMY: DEFENDING "
        if self.special_cooldown > 0:
            status_text += f"COOLDOWN:{self.special_cooldown} "
            
        if status_text:
            status_label = tk.Label(status_frame,
                                   text=status_text.strip(),
                                   font=self.fonts['retro_tiny'],
                                   fg=self.colors['screen_dark'],
                                   bg=self.colors['screen_green'])
            status_label.pack()
            
    def draw_action_menu(self, parent):
        """Draw action selection menu"""
        menu_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        menu_frame.pack(fill='x', pady=5)
        
        menu_label = tk.Label(menu_frame,
                             text="Choose Action:",
                             font=self.fonts['retro_small'],
                             fg=self.colors['screen_dark'],
                             bg=self.colors['screen_green'])
        menu_label.pack()
        
        # Actions
        for i, action in enumerate(self.actions):
            # Check if action is available
            available = True
            if action["name"] in ["RAGE", "FIREBALL", "BACKSTAB", "HOLY LIGHT"] and self.special_cooldown > 0:
                available = False
                
            if i == self.selected_action and available:
                display_text = f"> {action['name']}"
                bg_color = self.colors['screen_dark']
                fg_color = self.colors['screen_green']
            else:
                if available:
                    display_text = f"  {action['name']}"
                    bg_color = self.colors['screen_green']
                    fg_color = self.colors['screen_dark']
                else:
                    display_text = f"  {action['name']} (CD)"
                    bg_color = self.colors['screen_green']
                    fg_color = self.colors['screen_dark']
                    
            action_label = tk.Label(menu_frame,
                                   text=display_text,
                                   font=self.fonts['retro_small'],
                                   fg=fg_color,
                                   bg=bg_color,
                                   anchor='w')
            action_label.pack(fill='x', padx=10)
            
        # Show description of selected action
        if self.selected_action < len(self.actions):
            desc_label = tk.Label(menu_frame,
                                 text=self.actions[self.selected_action]["desc"],
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
            desc_label.pack(pady=2)
            
        # Controls
        controls_label = tk.Label(menu_frame,
                                 text="UP/DOWN:Select X:Action",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=2)
        
    def draw_game_over(self, parent):
        """Draw game over screen"""
        result_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        result_frame.pack(fill='x', pady=10)
        
        if self.player_hp <= 0:
            result_text = "DEFEAT!"
            detail_text = f"{self.enemy_name} wins the battle!"
            self.losses += 1
        else:
            result_text = "VICTORY!"
            detail_text = f"You defeated {self.enemy_name}!"
            self.wins += 1
            
        result_label = tk.Label(result_frame,
                               text=result_text,
                               font=self.fonts['retro_title'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'])
        result_label.pack()
        
        detail_label = tk.Label(result_frame,
                               text=detail_text,
                               font=self.fonts['retro_small'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'],
                               justify='center')
        detail_label.pack(pady=5)
        
        # Battle stats
        stats_text = f"Rounds: {self.battle_round} Record: {self.wins}W-{self.losses}L"
        stats_label = tk.Label(result_frame,
                              text=stats_text,
                              font=self.fonts['retro_tiny'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              justify='center')
        stats_label.pack(pady=3)
        
        # Controls
        controls_label = tk.Label(result_frame,
                                 text="X=New Battle  Y=Character Select",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=5)
        
    def dpad_up(self):
        """Handle D-Pad up"""
        if self.current_screen == "character_select":
            self.selected_character = (self.selected_character - 1) % len(self.character_classes)
            self.show_intro()
        elif self.current_screen == "battle" and not self.game_over:
            self.selected_action = (self.selected_action - 1) % len(self.actions)
            self.show_battle_screen()
            
    def dpad_down(self):
        """Handle D-Pad down"""
        if self.current_screen == "character_select":
            self.selected_character = (self.selected_character + 1) % len(self.character_classes)
            self.show_intro()
        elif self.current_screen == "battle" and not self.game_over:
            self.selected_action = (self.selected_action + 1) % len(self.actions)
            self.show_battle_screen()
            
    def dpad_left(self):
        """Handle D-Pad left"""
        pass  # Not used in this game
        
    def dpad_right(self):
        """Handle D-Pad right"""
        pass  # Not used in this game
        
    def x_button_action(self):
        """Handle X button press"""
        if self.current_screen == "character_select":
            self.start_battle()
        elif self.current_screen == "battle":
            if self.game_over:
                self.start_battle()
            else:
                self.execute_action()
                
    def y_button_action(self):
        """Handle Y button press"""
        if self.current_screen == "character_select":
            self.exit_game()
        elif self.current_screen == "battle":
            if self.game_over:
                self.show_intro()
            else:
                self.show_intro()
        else:
            self.exit_game()
            
    def execute_action(self):
        """Execute the selected action based on character class"""
        action = self.actions[self.selected_action]
        
        # Check if action is available
        if action["name"] in ["RAGE", "FIREBALL", "BACKSTAB", "HOLY LIGHT"] and self.special_cooldown > 0:
            return
            
        player_data = self.character_classes[self.player_class]
        
        # Execute player action
        if action["name"] == "ATTACK":
            attack_min, attack_max = player_data["attack"]
            damage = random.randint(attack_min, attack_max)
            self.enemy_hp = max(0, self.enemy_hp - damage)
            self.battle_log.append(f"You attack for {damage} damage!")
            
        elif action["name"] == "DEFEND":
            self.defending = True
            self.battle_log.append("You prepare to defend!")
            
        elif action["name"] == "HEAL":
            heal_min, heal_max = player_data["heal"]
            heal_amount = random.randint(heal_min, heal_max)
            self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
            self.battle_log.append(f"You heal for {heal_amount} HP!")
            
        elif action["name"] in ["RAGE", "FIREBALL", "BACKSTAB", "HOLY LIGHT"]:
            special_data = player_data["special"]
            
            if action["name"] == "HOLY LIGHT":
                # Paladin special: damage + heal
                damage_min, damage_max = special_data["damage"]
                damage = random.randint(damage_min, damage_max)
                heal_amount = random.randint(15, 25)
                self.enemy_hp = max(0, self.enemy_hp - damage)
                self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
                self.battle_log.append(f"Holy Light deals {damage} damage and heals {heal_amount} HP!")
            else:
                # Other specials
                success_rate = 0.8 if action["name"] == "BACKSTAB" else 0.75
                if random.random() < success_rate:
                    damage_min, damage_max = special_data["damage"]
                    damage = random.randint(damage_min, damage_max)
                    self.enemy_hp = max(0, self.enemy_hp - damage)
                    self.battle_log.append(f"{action['name']} hits for {damage} damage!")
                else:
                    self.battle_log.append(f"{action['name']} missed!")
            
            self.special_cooldown = 3
            
        # Check if enemy is defeated
        if self.enemy_hp <= 0:
            self.game_over = True
            self.show_battle_screen()
            return
            
        # Enemy turn
        self.enemy_action()
        
        # Update round
        self.battle_round += 1
        
        # Reduce cooldowns
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
            
        # Check if player is defeated
        if self.player_hp <= 0:
            self.game_over = True
            
        self.show_battle_screen()
        
    def enemy_action(self):
        """Execute enemy AI action based on enemy character class"""
        enemy_data = self.character_classes[self.enemy_class]
        
        # Enhanced AI logic based on character class and situation
        action = "attack"  # default
        
        # Health-based decisions
        health_ratio = self.enemy_hp / self.enemy_max_hp
        
        if health_ratio < 0.3 and random.random() < 0.6:
            action = "heal"
        elif health_ratio < 0.5 and random.random() < 0.3:
            action = "defend" 
        elif random.random() < 0.2:  # 20% chance for special
            action = "special"
        elif random.random() < 0.1:  # 10% chance to defend
            action = "defend"
        # else attack (default)
        
        if action == "attack":
            attack_min, attack_max = enemy_data["attack"]
            damage = random.randint(attack_min, attack_max)
            if self.defending:
                damage = damage // 2
                self.battle_log.append(f"{self.enemy_name} attacks for {damage} damage! (blocked)")
                self.defending = False
            else:
                self.battle_log.append(f"{self.enemy_name} attacks for {damage} damage!")
            self.player_hp = max(0, self.player_hp - damage)
            
        elif action == "heal":
            heal_min, heal_max = enemy_data["heal"]
            heal_amount = random.randint(heal_min, heal_max)
            self.enemy_hp = min(self.enemy_max_hp, self.enemy_hp + heal_amount)
            self.battle_log.append(f"{self.enemy_name} heals for {heal_amount} HP!")
            
        elif action == "defend":
            self.enemy_defending = True
            self.battle_log.append(f"{self.enemy_name} prepares to defend!")
            
        elif action == "special":
            special_data = enemy_data["special"]
            special_name = special_data["name"]
            
            if special_name == "HOLY LIGHT":
                # Enemy paladin special
                damage_min, damage_max = special_data["damage"]
                damage = random.randint(damage_min, damage_max)
                heal_amount = random.randint(10, 20)
                
                if self.defending:
                    damage = damage // 2
                    self.defending = False
                    
                self.player_hp = max(0, self.player_hp - damage)
                self.enemy_hp = min(self.enemy_max_hp, self.enemy_hp + heal_amount)
                self.battle_log.append(f"{self.enemy_name} uses {special_name}! {damage} damage, heals {heal_amount}")
            else:
                # Other specials
                success_rate = 0.7 if special_name == "BACKSTAB" else 0.65
                if random.random() < success_rate:
                    damage_min, damage_max = special_data["damage"]
                    damage = random.randint(damage_min, damage_max)
                    
                    if self.defending:
                        damage = damage // 2
                        self.defending = False
                        self.battle_log.append(f"{self.enemy_name} uses {special_name} for {damage} damage! (blocked)")
                    else:
                        self.battle_log.append(f"{self.enemy_name} uses {special_name} for {damage} damage!")
                    self.player_hp = max(0, self.player_hp - damage)
                else:
                    self.battle_log.append(f"{self.enemy_name}'s {special_name} missed!")
            
    def clear_screen(self):
        """Clear the screen - remove all children but keep the frame"""
        # Only destroy children of game_frame, not the frame itself
        for widget in self.game_frame.winfo_children():
            widget.destroy()
    
    def exit_game(self):
        """Exit game and return to hub"""
        # Stop polling
        self.gamepad_polling_active = False
        
        # Unbind keyboard from root
        root = self.parent.winfo_toplevel()
        root.unbind('<Key>')
        root.unbind('<Button-1>')
        
        # Clear the game frame and exit
        self.clear_screen()
        self.return_callback()
    
    def show(self):
        """Show game again (reuse instance)"""
        # Oyun durumunu sıfırla
        self.current_screen = "character_select"
        self.selected_character = 0
        self.player_class = None
        self.player_hp = 0
        self.player_max_hp = 0
        self.enemy_hp = 0
        self.enemy_max_hp = 0
        self.enemy_name = ""
        self.enemy_class = None
        self.defending = False
        self.enemy_defending = False
        self.battle_log = []
        self.selected_action = 0
        self.game_over = False
        self.battle_round = 1
        self.special_cooldown = 0
        self.wins = 0
        self.losses = 0
        
        # Interface'i yeniden oluştur
        self.setup_retro_interface()
        
        # Gamepad'i yeniden başlat
        if self.gamepad_enabled:
            self.gamepad_polling_active = True
            root = self.parent.winfo_toplevel()
            root.after(100, self.poll_gamepad)

# Update the import
WarGame = NostalgiKitWarGame
