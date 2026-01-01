"""
NostalgiKit River Crossing Game - Retro Style
Classic farmer puzzle with authentic retro handheld look and feel

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

class NostalgiKitRiverGame:
    def __init__(self, parent, return_callback):
        self.parent = parent
        self.return_callback = return_callback
        
        # Game state
        self.west_side = ["Farmer", "Wolf", "Goat", "Cabbage"]
        self.east_side = []
        self.boat_position = "west"  # "west" or "east"
        self.boat_contents = []
        self.game_won = False
        self.move_count = 0
        self.selected_item = 0  # For D-Pad selection
        
        # Character data with NostalgiKit style icons
        self.characters = {
            "Farmer": {"icon": "F", "desc": "Farmer"},
            "Wolf": {"icon": "W", "desc": "Wolf"},
            "Goat": {"icon": "G", "desc": "Goat"},
            "Cabbage": {"icon": "C", "desc": "Cabbage"}
        }
        
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
        self.setup_fonts()
        self.setup_retro_interface()
        self.init_gamepad()
        
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
        """Transform window to NostalgiKit style"""
        # Clear parent and setup NostalgiKit dimensions (matching game hub size)
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        self.parent.geometry("460x720")
        self.parent.configure(bg=self.colors['NostalgiKit_cream'])
        self.parent.resizable(False, False)
        
        # Setup keyboard bindings
        self.parent.focus_set()
        self.parent.bind('<Key>', self.on_key_press)
        self.parent.bind('<Button-1>', lambda e: self.parent.focus_set())
        
        # Main NostalgiKit frame (larger with more padding)
        retro_frame = tk.Frame(self.parent, bg=self.colors['NostalgiKit_cream'], relief='raised', bd=3)
        retro_frame.pack(fill='both', expand=True, padx=18, pady=18)
        
        # Top section with branding area (taller for larger console)
        top_frame = tk.Frame(retro_frame, bg=self.colors['NostalgiKit_cream'], height=50)
        top_frame.pack(fill='x', pady=(12, 8))
        top_frame.pack_propagate(False)
        
        # NostalgiKit branding
        brand_label = tk.Label(top_frame,
                              text="NostalgiKit",
                              font=self.fonts['retro_title'],
                              fg=self.colors['text_dark'],
                              bg=self.colors['NostalgiKit_cream'])
        brand_label.pack()
        
        # Model designation  
        NostalgiKit_label = tk.Label(top_frame,
                                text="RIVER PUZZLE",
                                font=self.fonts['retro_small'],
                                fg=self.colors['text_dark'],
                                bg=self.colors['NostalgiKit_cream'])
        NostalgiKit_label.pack()
        
        # Screen frame (larger with more padding)
        screen_frame = tk.Frame(retro_frame, bg=self.colors['dark_green'], relief='sunken', bd=3)
        screen_frame.pack(fill='both', expand=True, padx=25, pady=12)
        
        # Screen label
        screen_label_frame = tk.Frame(screen_frame, bg=self.colors['dark_green'], height=25)
        screen_label_frame.pack(fill='x', padx=12, pady=6)
        screen_label_frame.pack_propagate(False)
        
        screen_info = tk.Label(screen_label_frame,
                              text="DOT MATRIX WITH STEREO SOUND",
                              font=self.fonts['retro_tiny'],
                              fg=self.colors['NostalgiKit_cream'],
                              bg=self.colors['dark_green'])
        screen_info.pack()
        
        # Actual screen (larger padding)
        self.screen = tk.Frame(screen_frame, bg=self.colors['screen_green'], relief='sunken', bd=2)
        self.screen.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        
        # Controls
        self.create_retro_controls(retro_frame)
        
        # Start with intro
        self.show_intro()
        
    def create_retro_controls(self, parent):
        """Create NostalgiKit style controls"""
        control_frame = tk.Frame(parent, bg=self.colors['NostalgiKit_cream'])
        control_frame.pack(fill='x', padx=25, pady=(0, 18))
        
        # Control layout
        controls_layout = tk.Frame(control_frame, bg=self.colors['NostalgiKit_cream'])
        controls_layout.pack()
        
        # D-Pad (left side) - more spacing
        dpad_frame = tk.Frame(controls_layout, bg=self.colors['NostalgiKit_cream'])
        dpad_frame.pack(side='left', padx=(0, 60))
        
        # Action buttons (right side)
        button_frame = tk.Frame(controls_layout, bg=self.colors['NostalgiKit_cream'])
        button_frame.pack(side='right')
        
        # Create D-Pad
        self.create_dpad(dpad_frame)
        
        # X and Y buttons
        self.x_button = tk.Button(button_frame,
                                 text="X",
                                 font=self.fonts['retro_text'],
                                 bg=self.colors['red_button'],
                                 fg='white',
                                 relief='raised',
                                 bd=3,
                                 width=4,
                                 height=2,
                                 command=self.x_button_action,
                                 takefocus=False)
        self.x_button.pack(side='right', padx=5)
        
        self.y_button = tk.Button(button_frame,
                                 text="Y",
                                 font=self.fonts['retro_text'],
                                 bg=self.colors['purple_button'],
                                 fg='white',
                                 relief='raised',
                                 bd=3,
                                 width=4,
                                 height=2,
                                 command=self.y_button_action,
                                 takefocus=False)
        self.y_button.pack(side='right', padx=5)
        
        # Bottom row controls - more spacing
        bottom_controls = tk.Frame(control_frame, bg=self.colors['NostalgiKit_cream'])
        bottom_controls.pack(pady=(25, 0))
        
        select_btn = tk.Button(bottom_controls,
                              text="SELECT",
                              font=self.fonts['retro_small'],
                              bg=self.colors['button_gray'],
                              fg=self.colors['text_dark'],
                              relief='raised',
                              bd=2,
                              padx=8,
                              pady=3,
                              command=self.return_callback,
                              takefocus=False)
        select_btn.pack(side='left', padx=10)
        
        start_btn = tk.Button(bottom_controls,
                             text="START",
                             font=self.fonts['retro_small'],
                             bg=self.colors['button_gray'],
                             fg=self.colors['text_dark'],
                             relief='raised',
                             bd=2,
                             padx=8,
                             pady=3,
                             command=self.start_game,
                             takefocus=False)
        start_btn.pack(side='left', padx=10)
        
    def create_dpad(self, parent):
        """Create D-Pad controller"""
        dpad_container = tk.Frame(parent, bg=self.colors['NostalgiKit_cream'])
        dpad_container.pack()
        
        # D-Pad buttons arranged in cross pattern
        # Top
        up_btn = tk.Button(dpad_container,
                          text="▲",
                          font=self.fonts['retro_text'],
                          bg=self.colors['button_gray'],
                          fg=self.colors['text_dark'],
                          relief='raised',
                          bd=3,
                          width=3,
                          height=1,
                          command=lambda: self.dpad_up(),
                          takefocus=False)
        up_btn.grid(row=0, column=1, padx=1, pady=1)
        
        # Left, Center, Right
        left_btn = tk.Button(dpad_container,
                            text="◄",
                            font=self.fonts['retro_text'],
                            bg=self.colors['button_gray'],
                            fg=self.colors['text_dark'],
                            relief='raised',
                            bd=3,
                            width=3,
                            height=1,
                            command=lambda: self.dpad_left(),
                            takefocus=False)
        left_btn.grid(row=1, column=0, padx=1, pady=1)
        
        center_frame = tk.Frame(dpad_container, bg=self.colors['button_gray'], width=30, height=20, relief='sunken', bd=1)
        center_frame.grid(row=1, column=1, padx=1, pady=1)
        center_frame.grid_propagate(False)
        
        right_btn = tk.Button(dpad_container,
                             text="►",
                             font=self.fonts['retro_text'],
                             bg=self.colors['button_gray'],
                             fg=self.colors['text_dark'],
                             relief='raised',
                             bd=3,
                             width=3,
                             height=1,
                             command=lambda: self.dpad_right(),
                             takefocus=False)
        right_btn.grid(row=1, column=2, padx=1, pady=1)
        
        # Bottom
        down_btn = tk.Button(dpad_container,
                            text="▼",
                            font=self.fonts['retro_text'],
                            bg=self.colors['button_gray'],
                            fg=self.colors['text_dark'],
                            relief='raised',
                            bd=3,
                            width=3,
                            height=1,
                            command=lambda: self.dpad_down(),
                            takefocus=False)
        down_btn.grid(row=2, column=1, padx=1, pady=1)
        
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
            self.return_callback()
            
    def show_intro(self):
        """Show game introduction"""
        self.clear_screen()
        self.current_screen = "intro"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = tk.Label(content,
                              text="RIVER PUZZLE",
                              font=self.fonts['retro_title'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        title_label.pack(pady=(5, 5))
        
        # Story
        story_text = """A farmer has:
Wolf, Goat, Cabbage

He must cross a
river by boat.

Boat holds farmer
+ 1 item only.

RULES:
- Wolf eats Goat
- Goat eats Cabbage
if left alone!

Get all across
safely!"""
        
        story_label = tk.Label(content,
                              text=story_text,
                              font=self.fonts['retro_small'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              justify='left')
        story_label.pack(expand=True)
        
        # Controls info
        controls_label = tk.Label(content,
                                 text="START=Begin Game",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=5)
        
    def start_game(self):
        """Start the actual game"""
        self.west_side = ["Farmer", "Wolf", "Goat", "Cabbage"]
        self.east_side = []
        self.boat_position = "west"
        self.boat_contents = []
        self.game_won = False
        self.move_count = 0
        self.selected_item = 0
        self.current_screen = "game"
        
        self.show_game_board()
        
    def show_game_board(self):
        """Show the main game board"""
        self.clear_screen()
        
        # Check for game end conditions
        loss_reason = self.check_loss()
        if loss_reason:
            self.show_loss(loss_reason)
            return
        elif self.check_win():
            self.show_victory()
            return
            
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Status bar
        status_text = f"Moves:{self.move_count}"
        status_label = tk.Label(content,
                               text=status_text,
                               font=self.fonts['retro_small'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'])
        status_label.pack(pady=2)
        
        # River visualization
        self.draw_river_scene(content)
        
        # Action area
        self.create_action_area(content)
        
    def draw_river_scene(self, parent):
        """Draw simplified river scene"""
        river_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        river_frame.pack(fill='x', pady=5)
        
        # West side
        west_frame = tk.Frame(river_frame, bg=self.colors['screen_green'])
        west_frame.pack(side='left', fill='x', expand=True)
        
        west_label = tk.Label(west_frame,
                             text="WEST",
                             font=self.fonts['retro_tiny'],
                             fg=self.colors['screen_dark'],
                             bg=self.colors['screen_green'])
        west_label.pack()
        
        west_chars = "".join([self.characters[char]["icon"] for char in self.west_side])
        if not west_chars:
            west_chars = "."
            
        west_display = tk.Label(west_frame,
                               text=west_chars,
                               font=self.fonts['retro_text'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'])
        west_display.pack()
        
        # River and boat
        river_frame_mid = tk.Frame(river_frame, bg=self.colors['screen_green'], width=60)
        river_frame_mid.pack(side='left')
        river_frame_mid.pack_propagate(False)
        
        river_label = tk.Label(river_frame_mid,
                              text="~~~~",
                              font=self.fonts['retro_small'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        river_label.pack()
        
        # Boat
        boat_contents = "".join([self.characters[char]["icon"] for char in self.boat_contents])
        if not boat_contents:
            boat_contents = "."
            
        boat_symbol = "<" if self.boat_position == "west" else ">"
        boat_text = f"{boat_symbol}{boat_contents}{boat_symbol}"
        
        boat_label = tk.Label(river_frame_mid,
                             text=boat_text,
                             font=self.fonts['retro_small'],
                             fg=self.colors['screen_dark'],
                             bg=self.colors['screen_green'])
        boat_label.pack()
        
        # East side
        east_frame = tk.Frame(river_frame, bg=self.colors['screen_green'])
        east_frame.pack(side='left', fill='x', expand=True)
        
        east_label = tk.Label(east_frame,
                             text="EAST",
                             font=self.fonts['retro_tiny'],
                             fg=self.colors['screen_dark'],
                             bg=self.colors['screen_green'])
        east_label.pack()
        
        east_chars = "".join([self.characters[char]["icon"] for char in self.east_side])
        if not east_chars:
            east_chars = "."
            
        east_display = tk.Label(east_frame,
                               text=east_chars,
                               font=self.fonts['retro_text'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'])
        east_display.pack()
        
    def create_action_area(self, parent):
        """Create action selection area"""
        action_frame = tk.Frame(parent, bg=self.colors['screen_green'])
        action_frame.pack(fill='x', pady=5)
        
        current_side = self.west_side if self.boat_position == "west" else self.east_side
        
        if "Farmer" not in current_side:
            # Farmer not on current side, can only move boat
            instruction_label = tk.Label(action_frame,
                                        text="X=Move Boat",
                                        font=self.fonts['retro_small'],
                                        fg=self.colors['screen_dark'],
                                        bg=self.colors['screen_green'])
            instruction_label.pack()
        else:
            # Farmer is on current side
            instruction_label = tk.Label(action_frame,
                                        text="Choose companion:",
                                        font=self.fonts['retro_small'],
                                        fg=self.colors['screen_dark'],
                                        bg=self.colors['screen_green'])
            instruction_label.pack()
            
            # Available options
            self.available_options = ["Alone"]
            for char in current_side:
                if char != "Farmer":
                    self.available_options.append(char)
                    
            # Ensure selected item is in bounds
            if self.selected_item >= len(self.available_options):
                self.selected_item = 0
                
            # Display options
            for i, option in enumerate(self.available_options):
                if i == self.selected_item:
                    display_text = f"> {option}"
                    bg_color = self.colors['screen_dark']
                    fg_color = self.colors['screen_green']
                else:
                    display_text = f"  {option}"
                    bg_color = self.colors['screen_green']
                    fg_color = self.colors['screen_dark']
                    
                option_label = tk.Label(action_frame,
                                       text=display_text,
                                       font=self.fonts['retro_small'],
                                       fg=fg_color,
                                       bg=bg_color,
                                       anchor='w')
                option_label.pack(fill='x', padx=10)
                
        # Controls
        controls_label = tk.Label(action_frame,
                                 text="UP/DOWN:Select X:Go",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=2)
        
    def dpad_up(self):
        """Handle D-Pad up"""
        if self.current_screen == "game":
            current_side = self.west_side if self.boat_position == "west" else self.east_side
            if "Farmer" in current_side and hasattr(self, 'available_options'):
                self.selected_item = (self.selected_item - 1) % len(self.available_options)
                self.show_game_board()
                
    def dpad_down(self):
        """Handle D-Pad down"""
        if self.current_screen == "game":
            current_side = self.west_side if self.boat_position == "west" else self.east_side
            if "Farmer" in current_side and hasattr(self, 'available_options'):
                self.selected_item = (self.selected_item + 1) % len(self.available_options)
                self.show_game_board()
                
    def dpad_left(self):
        """Handle D-Pad left"""
        pass  # Not used in this game
        
    def dpad_right(self):
        """Handle D-Pad right"""
        pass  # Not used in this game
        
    def x_button_action(self):
        """Handle X button press"""
        if self.current_screen == "intro":
            self.start_game()
        elif self.current_screen == "game":
            self.execute_move()
        elif self.current_screen in ["victory", "loss"]:
            self.start_game()
            
    def y_button_action(self):
        """Handle Y button press"""
        if self.current_screen == "game":
            self.show_intro()
        else:
            self.return_callback()
            
    def execute_move(self):
        """Execute the selected move"""
        current_side = self.west_side if self.boat_position == "west" else self.east_side
        other_side = self.east_side if self.boat_position == "west" else self.west_side
        
        if "Farmer" not in current_side:
            # Just move boat
            self.boat_position = "east" if self.boat_position == "west" else "west"
            self.move_count += 1
        else:
            # Move farmer with selected companion
            if hasattr(self, 'available_options'):
                selected_option = self.available_options[self.selected_item]
                
                # Move farmer
                current_side.remove("Farmer")
                other_side.append("Farmer")
                
                # Move companion if not alone
                if selected_option != "Alone":
                    current_side.remove(selected_option)
                    other_side.append(selected_option)
                    
                # Move boat
                self.boat_position = "east" if self.boat_position == "west" else "west"
                self.move_count += 1
                self.selected_item = 0
                
        self.show_game_board()
        
    def check_loss(self):
        """Check if game is lost"""
        # Check west side
        if "Farmer" not in self.west_side:
            if "Wolf" in self.west_side and "Goat" in self.west_side:
                return "Wolf ate Goat!"
            if "Goat" in self.west_side and "Cabbage" in self.west_side:
                return "Goat ate Cabbage!"
                
        # Check east side
        if "Farmer" not in self.east_side:
            if "Wolf" in self.east_side and "Goat" in self.east_side:
                return "Wolf ate Goat!"
            if "Goat" in self.east_side and "Cabbage" in self.east_side:
                return "Goat ate Cabbage!"
                
        return False
        
    def check_win(self):
        """Check if game is won"""
        return len(self.east_side) == 4 and all(char in self.east_side for char in ["Farmer", "Wolf", "Goat", "Cabbage"])
        
    def show_loss(self, reason):
        """Show loss screen"""
        self.clear_screen()
        self.current_screen = "loss"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Loss title
        title_label = tk.Label(content,
                              text="GAME OVER",
                              font=self.fonts['retro_title'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        title_label.pack(pady=10)
        
        # Reason
        reason_label = tk.Label(content,
                               text=reason,
                               font=self.fonts['retro_text'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'])
        reason_label.pack(pady=10)
        
        # Advice
        advice_text = """Remember:
Never leave:
- Wolf + Goat
- Goat + Cabbage
alone together!"""
        
        advice_label = tk.Label(content,
                               text=advice_text,
                               font=self.fonts['retro_small'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'],
                               justify='center')
        advice_label.pack(expand=True)
        
        # Controls
        controls_label = tk.Label(content,
                                 text="X=Try Again  Y=Menu",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=5)
        
    def show_victory(self):
        """Show victory screen"""
        self.clear_screen()
        self.current_screen = "victory"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Victory title
        title_label = tk.Label(content,
                              text="SUCCESS!",
                              font=self.fonts['retro_title'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        title_label.pack(pady=10)
        
        # Stats
        stats_text = f"Completed in\\n{self.move_count} moves!"
        stats_label = tk.Label(content,
                              text=stats_text,
                              font=self.fonts['retro_text'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              justify='center')
        stats_label.pack(pady=10)
        
        # Performance rating
        if self.move_count <= 7:
            rating = "PERFECT!\\nOptimal solution!"
        elif self.move_count <= 10:
            rating = "EXCELLENT!\\nVery efficient!"
        elif self.move_count <= 15:
            rating = "GOOD!\\nWell done!"
        else:
            rating = "COMPLETED!\\nGreat job!"
            
        rating_label = tk.Label(content,
                               text=rating,
                               font=self.fonts['retro_small'],
                               fg=self.colors['screen_dark'],
                               bg=self.colors['screen_green'],
                               justify='center')
        rating_label.pack(expand=True)
        
        # Characters celebration
        celebration_label = tk.Label(content,
                                     text="F W G C",
                                     font=self.fonts['retro_text'],
                                     fg=self.colors['screen_dark'],
                                     bg=self.colors['screen_green'])
        celebration_label.pack(pady=5)
        
        # Controls
        controls_label = tk.Label(content,
                                 text="X=Play Again  Y=Menu",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=5)
        
    def clear_screen(self):
        """Clear the screen"""
        for widget in self.screen.winfo_children():
            widget.destroy()    
    def init_gamepad(self):
        """Initialize gamepad support"""
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            
            self.joystick = None
            self.gamepad_enabled = True
            self.last_button_state = {}
            self.last_hat = (0, 0)
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            
            self.parent.after(30, self.poll_gamepad)
        except Exception as e:
            print(f"Gamepad init error: {e}")
            self.gamepad_enabled = False
    
    def poll_gamepad(self):
        """Poll gamepad input"""
        if not self.gamepad_enabled:
            return
        
        try:
            self.parent.winfo_exists()
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
        
        except Exception as e:
            if "bad window" not in str(e):
                print(f"Gamepad poll error: {e}")
        
        try:
            self.parent.after(30, self.poll_gamepad)
        except:
            pass
# Update the import
RiverGame = NostalgiKitRiverGame
