"""
NostalgiKit Card Guess Game - Retro Style
Classic number guessing game with authentic retro handheld look and feel

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import random
import math
import pygame  # For gamepad support

class NostalgiKitCardGame:
    def __init__(self, parent, return_callback):
        self.parent = parent
        self.return_callback = return_callback
        
        # Game data (same as original)
        self.cards = {
            "CARD A": {1, 3, 5, 7, 9, 11, 13, 15, 17, 19},
            "CARD B": {2, 3, 6, 7, 10, 11, 14, 15, 18, 19},
            "CARD C": {4, 5, 6, 7, 12, 13, 14, 15, 20},
            "CARD D": {8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20},
            "CARD E": {1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
            "CARD F": {11, 12, 13, 14, 15, 16, 17, 18, 19, 20}
        }
        
        self.guessed_numbers = set(range(1, 21))
        self.current_card_index = 0
        self.card_names = list(self.cards.keys())
        self.game_stage = "intro"
        
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
            'retro_tiny': tkFont.Font(family="Courier", size=7, weight="bold"),
            'retro_number': tkFont.Font(family="Courier", size=9, weight="bold")
        }
        
    def setup_retro_interface(self):
        """Transform window to NostalgiKit style"""
        # Clear parent and setup NostalgiKit dimensions (matching game hub size)
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        self.parent.geometry("460x720")
        self.parent.configure(bg=self.colors['NostalgiKit_cream'])
        self.parent.resizable(False, False)
        
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
                                text="NUMBER ORACLE",
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
        
        # Start game
        self.show_intro()
        
    def create_retro_controls(self, parent):
        """Create NostalgiKit style controls"""
        control_frame = tk.Frame(parent, bg=self.colors['NostalgiKit_cream'])
        control_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Button layout
        button_layout = tk.Frame(control_frame, bg=self.colors['NostalgiKit_cream'])
        button_layout.pack()
        
        # Action buttons
        button_frame = tk.Frame(button_layout, bg=self.colors['NostalgiKit_cream'])
        button_frame.pack(side='right', padx=(50, 0))
        
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
                                 command=self.x_button_action)
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
                                 command=self.y_button_action)
        self.y_button.pack(side='right', padx=5)
        
        # Bottom control buttons
        bottom_controls = tk.Frame(control_frame, bg=self.colors['NostalgiKit_cream'])
        bottom_controls.pack(pady=(20, 0))
        
        select_btn = tk.Button(bottom_controls,
                              text="SELECT",
                              font=self.fonts['retro_small'],
                              bg=self.colors['button_gray'],
                              fg=self.colors['text_dark'],
                              relief='raised',
                              bd=2,
                              padx=8,
                              pady=3,
                              command=self.return_callback)
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
                             command=self.start_game)
        start_btn.pack(side='left', padx=10)
        
    def show_intro(self):
        """Show game introduction"""
        self.clear_screen()
        self.game_stage = "intro"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = tk.Label(content,
                              text="NUMBER ORACLE",
                              font=self.fonts['retro_title'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        title_label.pack(pady=(10, 5))
        
        # Instructions
        intro_text = """Think of a number
from 1 to 20.

I will show you
6 magic cards.

Tell me if your
number is on
each card.

Press START
to begin!"""
        
        intro_label = tk.Label(content,
                              text=intro_text,
                              font=self.fonts['retro_text'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'],
                              justify='center')
        intro_label.pack(expand=True)
        
        # Controls info
        controls_label = tk.Label(content,
                                 text="X=YES  Y=NO",
                                 font=self.fonts['retro_small'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=5)
        
    def start_game(self):
        """Start the card questioning"""
        self.game_stage = "asking"
        self.current_card_index = 0
        self.guessed_numbers = set(range(1, 21))
        self.show_card()
        
    def show_card(self):
        """Show current card"""
        self.clear_screen()
        
        if self.current_card_index >= len(self.card_names):
            self.make_guess()
            return
            
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Progress
        progress_text = f"CARD {self.current_card_index + 1}/6"
        progress_label = tk.Label(content,
                                 text=progress_text,
                                 font=self.fonts['retro_small'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        progress_label.pack(pady=5)
        
        # Card name
        card_name = self.card_names[self.current_card_index]
        card_numbers = self.cards[card_name]
        
        card_label = tk.Label(content,
                             text=card_name,
                             font=self.fonts['retro_title'],
                             fg=self.colors['screen_dark'],
                             bg=self.colors['screen_green'])
        card_label.pack(pady=5)
        
        # Numbers display
        numbers_frame = tk.Frame(content, bg=self.colors['screen_green'])
        numbers_frame.pack(expand=True, fill='both')
        
        # Display numbers in a grid
        sorted_numbers = sorted(card_numbers)
        rows = (len(sorted_numbers) + 4) // 5  # 5 numbers per row
        
        for i, number in enumerate(sorted_numbers):
            row = i // 5
            col = i % 5
            
            # Create grid if not exists
            if col == 0:
                if not hasattr(self, f'number_row_{row}'):
                    setattr(self, f'number_row_{row}', 
                           tk.Frame(numbers_frame, bg=self.colors['screen_green']))
                    getattr(self, f'number_row_{row}').pack()
            
            row_frame = getattr(self, f'number_row_{row}')
            
            number_label = tk.Label(row_frame,
                                   text=f"{number:2d}",
                                   font=self.fonts['retro_number'],
                                   fg=self.colors['screen_dark'],
                                   bg=self.colors['screen_green'],
                                   width=3)
            number_label.pack(side='left', padx=2)
        
        # Question
        question_label = tk.Label(content,
                                 text="Is your number\\non this card?",
                                 font=self.fonts['retro_text'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'],
                                 justify='center')
        question_label.pack(side='bottom', pady=10)
        
        # Controls
        controls_label = tk.Label(content,
                                 text="X=YES  Y=NO",
                                 font=self.fonts['retro_small'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack(side='bottom', pady=5)
        
    def make_guess(self):
        """Make final guess"""
        self.clear_screen()
        self.game_stage = "result"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        if self.guessed_numbers:
            guess = random.choice(list(self.guessed_numbers))
            
            # Success screen
            result_label = tk.Label(content,
                                   text="ORACLE SPEAKS:",
                                   font=self.fonts['retro_title'],
                                   fg=self.colors['screen_dark'],
                                   bg=self.colors['screen_green'])
            result_label.pack(pady=10)
            
            # Big number
            number_label = tk.Label(content,
                                   text=str(guess),
                                   font=tkFont.Font(family="Courier", size=32, weight="bold"),
                                   fg=self.colors['screen_dark'],
                                   bg=self.colors['screen_green'])
            number_label.pack(expand=True)
            
            success_label = tk.Label(content,
                                    text="Your secret\\nnumber is\\nrevealed!",
                                    font=self.fonts['retro_text'],
                                    fg=self.colors['screen_dark'],
                                    bg=self.colors['screen_green'],
                                    justify='center')
            success_label.pack(pady=10)
        else:
            # Error screen
            error_label = tk.Label(content,
                                  text="ERROR!",
                                  font=self.fonts['retro_title'],
                                  fg=self.colors['screen_dark'],
                                  bg=self.colors['screen_green'])
            error_label.pack(pady=10)
            
            message_label = tk.Label(content,
                                    text="Oracle cannot\\nread your mind.\\n\\nDid you change\\nyour number?",
                                    font=self.fonts['retro_text'],
                                    fg=self.colors['screen_dark'],
                                    bg=self.colors['screen_green'],
                                    justify='center')
            message_label.pack(expand=True)
        
        # Controls
        controls_label = tk.Label(content,
                                 text="START=Again\\nSELECT=Menu",
                                 font=self.fonts['retro_small'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'],
                                 justify='center')
        controls_label.pack(side='bottom', pady=5)
        
    def x_button_action(self):
        """Handle X button (YES)"""
        if self.game_stage == "asking":
            self.answer_card(True)
        elif self.game_stage == "intro":
            self.start_game()
            
    def y_button_action(self):
        """Handle Y button (NO)"""
        if self.game_stage == "asking":
            self.answer_card(False)
        else:
            self.return_callback()
            
    def answer_card(self, is_present):
        """Process card answer"""
        card_name = self.card_names[self.current_card_index]
        card_numbers = self.cards[card_name]
        
        if is_present:
            self.guessed_numbers &= card_numbers
        else:
            self.guessed_numbers -= card_numbers
            
        self.current_card_index += 1
        self.show_card()
        
    def clear_screen(self):
        """Clear the screen"""
        for widget in self.screen.winfo_children():
            widget.destroy()
        
        # Clean up dynamic attributes
        for attr in list(self.__dict__.keys()):
            if attr.startswith('number_row_'):
                delattr(self, attr)
    
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
                
                # X or A = YES
                if just_pressed(0) or just_pressed(2):
                    self.x_button_action()
                
                # Y or B = NO
                if just_pressed(1) or just_pressed(3):
                    self.y_button_action()
                
                # START = restart (from result screen)
                if just_pressed(7):
                    if self.game_stage == "result":
                        self.game_stage = "intro"
                        self.show_intro()
                    elif self.game_stage == "intro":
                        self.start_game()
        
        except Exception as e:
            if "bad window" not in str(e):
                print(f"Gamepad poll error: {e}")
        
        try:
            self.parent.after(30, self.poll_gamepad)
        except:
            pass

# Update the import in main hub to use NostalgiKit version
CardGuessGame = NostalgiKitCardGame
