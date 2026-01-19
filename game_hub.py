"""
NostalgiKit - Vintage Handheld Gaming Experience
Classic retro handheld style interface with three nostalgic games

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
from tkinter import PhotoImage
import random
import threading
import time
import os
import tempfile
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import io
import base64
import pygame  # For gamepad support

# Import NostalgiKit games
from card_guess_nostalgik import CardGuessGame
from war_game_nostalgik import WarGame
from river_game_nostalgik import RiverGame
from galaxy_war_pat import GalaxyWarPat
from crakers_nostalgik import CrakersGame
from tetris_nostalgik import TetrisGame

class NostalgiKitHub:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NostalgiKit")
        
        # Set window icon
        self.icon = None  # Keep reference to prevent garbage collection
        self.icon_taskbar_path = None
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
            if os.path.exists(icon_path):
                # Try with PIL first for better compatibility
                try:
                    pil_image = Image.open(icon_path)
                    # Resize if necessary for icon
                    if pil_image.size != (32, 32):
                        pil_image = pil_image.resize((32, 32), Image.Resampling.LANCZOS)
                    self.icon = ImageTk.PhotoImage(pil_image)
                    self.root.iconphoto(False, self.icon)

                    # Generate an .ico for taskbar if possible
                    self.icon_taskbar_path = self.generate_taskbar_icon(icon_path)
                    if self.icon_taskbar_path:
                        try:
                            self.root.iconbitmap(default=self.icon_taskbar_path)
                        except Exception:
                            pass
                except Exception:
                    # Fallback to PhotoImage
                    self.icon = PhotoImage(file=icon_path)
                    self.root.iconphoto(False, self.icon)
        except Exception:
            pass  # If icon loading fails, continue without it
        
        # Setup window properties (larger console size)
        self.root.geometry("460x720")
        self.root.resizable(False, False)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # NostalgiKit colors (vintage cream theme like original image)
        self.colors = {
            'nostalgik_cream': '#E8E0C7',      # Main vintage cream color
            'screen_green': '#9BBB59',        # Classic green screen
            'dark_green': '#8B9467',          # Dark accents
            'screen_dark': '#374224',         # Dark screen areas
            'button_gray': '#8E8E93',         # Button color
            'text_dark': '#1C1C1E',           # Dark text
            'highlight': '#FFD23F',           # Yellow highlight
            'red_button': '#FF3B30',          # X button (red)
            'purple_button': '#8E44AD'        # Y button (purple)
        }
        
        # Font setup
        self.fonts = {
            'retro_title': tkFont.Font(family="Courier", size=10, weight="bold"),
            'retro_text': tkFont.Font(family="Courier", size=9, weight="bold"),
            'retro_small': tkFont.Font(family="Courier", size=8, weight="bold"),
            'retro_large': tkFont.Font(family="Courier", size=12, weight="bold"),
            'retro_tiny': tkFont.Font(family="Courier", size=7, weight="bold")
        }
        
        # Game state
        self.current_screen = "menu"
        self.selected_game = 0
        self.games = [
            {"name": "NUMBER ORACLE", "desc": "Magical Number Quest"},
            {"name": "WAR GAME", "desc": "Turn-Based Combat"},
            {"name": "RIVER PUZZLE", "desc": "Logic Challenge"},
            {"name": "GALAXY WAR PAT", "desc": "Space Invaders"},
            {"name": "CRAKERS QUEST", "desc": "Grid Adventure"},
            {"name": "BLOCK STACK", "desc": "Falling Blocks"}
        ]
        
        # Game instances - her oyun sadece bir kez oluşturulur
        self.game_instances = {
            'card_game': None,
            'war_game': None,
            'river_game': None,
            'galaxy_war': None,
            'crakers_game': None,
            'tetris_game': None
        }
        
        # Battery level (simulation)
        self.battery_level = 3  # 0-4 blocks
        
        # Gamepad support
        self.init_gamepad()
        
        # Setup the interface
        self.setup_nostalgik_interface()
        self.setup_keyboard_bindings()

        # Show blank screen first, then welcome screen after 0.5 seconds
        self.show_blank_screen()
        self.root.after(500, self.show_welcome_screen)
        
        # Start gamepad polling
        if self.gamepad_enabled:
            self.gamepad_polling_active = True
            self.root.after(100, self.poll_gamepad)

    def setup_nostalgik_interface(self):
        """Create the authentic NostalgiKit handheld interface"""
        # Configure main window
        self.root.configure(bg=self.colors['nostalgik_cream'])        # Setup keyboard focus
        self.root.focus_set()
        
        # Main NostalgiKit frame (larger with more padding)
        main_frame = tk.Frame(self.root, bg=self.colors['nostalgik_cream'], relief='raised', bd=3)
        main_frame.pack(fill='both', expand=True, padx=18, pady=18)

        # Top section with branding area (taller for larger console)
        top_frame = tk.Frame(main_frame, bg=self.colors['nostalgik_cream'], height=50)
        top_frame.pack(fill='x', pady=(12, 8))
        top_frame.pack_propagate(False)

        # NostalgiKit branding
        brand_label = tk.Label(top_frame,
                              text="NostalgiKIT",
                              font=self.fonts['retro_title'],
                              fg=self.colors['text_dark'],
                              bg=self.colors['nostalgik_cream'])
        brand_label.pack()

        # Model designation
        nostalgik_label = tk.Label(top_frame,
                                text="CLASSIC",
                                font=self.fonts['retro_small'],
                                fg=self.colors['text_dark'],
                                bg=self.colors['nostalgik_cream'])
        nostalgik_label.pack()
        
        # Screen frame (larger with more padding)
        screen_frame = tk.Frame(main_frame, bg=self.colors['dark_green'], relief='sunken', bd=3)
        screen_frame.pack(fill='both', expand=True, padx=25, pady=12)
        
        # Screen label
        screen_label_frame = tk.Frame(screen_frame, bg=self.colors['dark_green'], height=25)
        screen_label_frame.pack(fill='x', padx=12, pady=6)
        screen_label_frame.pack_propagate(False)
        
        # Faded text at top
        screen_info = tk.Label(screen_label_frame,
                              text="DOT MATRIX WITH STEREO SOUND",
                              font=self.fonts['retro_tiny'],
                              fg='#6B7458',  # Faded greenish color
                              bg=self.colors['dark_green'])
        screen_info.pack()

        # Actual screen (larger padding)
        self.screen = tk.Frame(screen_frame, bg=self.colors['screen_green'], relief='sunken', bd=2)
        self.screen.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        
        # Battery indicator in bottom right corner
        battery_frame = tk.Frame(screen_frame, bg=self.colors['dark_green'])
        battery_frame.pack(side='bottom', anchor='e', padx=12, pady=(0, 6))
        
        battery_text = self.get_battery_display()
        self.battery_label = tk.Label(battery_frame,
                                      text=battery_text,
                                      font=self.fonts['retro_tiny'],
                                      fg='#6B7458',  # Faded color
                                      bg=self.colors['dark_green'])
        self.battery_label.pack()

        # Create controls
        self.create_controls(main_frame)

    def generate_taskbar_icon(self, png_path):
        """Create a temporary .ico from the png to show in taskbar (Windows)."""
        try:
            ico_dir = tempfile.gettempdir()
            ico_path = os.path.join(ico_dir, "nostalgikit_icon.ico")
            with Image.open(png_path) as img:
                # Ensure square 32x32 for ico
                if img.size != (32, 32):
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                img.save(ico_path, format="ICO")
            return ico_path
        except Exception:
            return None

    def create_controls(self, parent):
        """Create NostalgiKit control layout (larger spacing for bigger console)"""
        control_frame = tk.Frame(parent, bg=self.colors['nostalgik_cream'])
        control_frame.pack(fill='x', padx=25, pady=(0, 18))
        
        # Control layout
        controls_layout = tk.Frame(control_frame, bg=self.colors['nostalgik_cream'])
        controls_layout.pack()
        
        # D-Pad (left side) - more spacing
        dpad_frame = tk.Frame(controls_layout, bg=self.colors['nostalgik_cream'])
        dpad_frame.pack(side='left', padx=(0, 60))
        
        # Action buttons (right side)
        buttons_frame = tk.Frame(controls_layout, bg=self.colors['nostalgik_cream'])
        buttons_frame.pack(side='right')
        
        # Bottom row controls - more spacing
        bottom_controls = tk.Frame(control_frame, bg=self.colors['nostalgik_cream'])
        bottom_controls.pack(pady=(25, 0))
        
        # Create D-Pad and buttons
        self.create_dpad(dpad_frame)
        self.create_action_buttons(buttons_frame)
        self.create_select_start_buttons(bottom_controls)
        
    def create_dpad(self, parent):
        """Create D-Pad controller"""
        dpad_container = tk.Frame(parent, bg=self.colors['nostalgik_cream'])
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
                          command=lambda: self.dpad_action("UP"),
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
                            command=lambda: self.dpad_action("LEFT"),
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
                             command=lambda: self.dpad_action("RIGHT"),
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
                            command=lambda: self.dpad_action("DOWN"),
                            takefocus=False)
        down_btn.grid(row=2, column=1, padx=1, pady=1)
        
    def create_action_buttons(self, parent):
        """Create X and Y action buttons"""
        button_container = tk.Frame(parent, bg=self.colors['nostalgik_cream'])
        button_container.pack()
        
        # X button (bottom right, red)
        x_button = tk.Button(button_container,
                            text="X",
                            font=self.fonts['retro_text'],
                            bg=self.colors['red_button'],
                            fg='white',
                            relief='raised',
                            bd=4,
                            width=4,
                            height=2,
                            command=self.x_button_action,
                            takefocus=False)
        x_button.grid(row=1, column=1, padx=8, pady=5)
        
        # Y button (bottom left, purple)
        y_button = tk.Button(button_container,
                            text="Y",
                            font=self.fonts['retro_text'],
                            bg=self.colors['purple_button'],
                            fg='white',
                            relief='raised',
                            bd=4,
                            width=4,
                            height=2,
                            command=self.y_button_action,
                            takefocus=False)
        y_button.grid(row=1, column=0, padx=8, pady=5)
        
    def create_select_start_buttons(self, parent):
        """Create SELECT and START buttons"""
        # SELECT and START in classic layout
        select_start_frame = tk.Frame(parent, bg=self.colors['nostalgik_cream'])
        select_start_frame.pack()
        
        # SELECT button
        select_btn = tk.Button(select_start_frame,
                              text="SELECT",
                              font=self.fonts['retro_small'],
                              bg=self.colors['button_gray'],
                              fg=self.colors['text_dark'],
                              relief='raised',
                              bd=2,
                              padx=8,
                              pady=3,
                              command=self.select_action,
                              takefocus=False)
        select_btn.pack(side='left', padx=15)
        
        # START button
        start_btn = tk.Button(select_start_frame,
                             text="START",
                             font=self.fonts['retro_small'],
                             bg=self.colors['button_gray'],
                             fg=self.colors['text_dark'],
                             relief='raised',
                             bd=2,
                             padx=8,
                             pady=3,
                             command=self.start_action,
                             takefocus=False)
        start_btn.pack(side='left', padx=15)
        
    def setup_keyboard_bindings(self):
        """Setup comprehensive keyboard controls"""
        # Arrow keys and WASD for D-Pad
        self.root.bind('<Up>', lambda e: self.dpad_action("UP"))
        self.root.bind('<Down>', lambda e: self.dpad_action("DOWN"))
        self.root.bind('<Left>', lambda e: self.dpad_action("LEFT"))
        self.root.bind('<Right>', lambda e: self.dpad_action("RIGHT"))
        self.root.bind('<w>', lambda e: self.dpad_action("UP"))
        self.root.bind('<s>', lambda e: self.dpad_action("DOWN"))
        self.root.bind('<a>', lambda e: self.dpad_action("LEFT"))
        self.root.bind('<d>', lambda e: self.dpad_action("RIGHT"))
        
        # Action buttons
        self.root.bind('<Return>', lambda e: self.x_button_action())  # Enter = X button
        self.root.bind('<space>', lambda e: self.x_button_action())   # Space = X button
        self.root.bind('<x>', lambda e: self.x_button_action())       # X = X button
        self.root.bind('<Escape>', lambda e: self.y_button_action())  # Escape = Y button
        self.root.bind('<BackSpace>', lambda e: self.y_button_action()) # Backspace = Y button
        self.root.bind('<y>', lambda e: self.y_button_action())       # Y = Y button
        
        # SELECT and START
        self.root.bind('<Tab>', lambda e: self.select_action())       # Tab = SELECT
        
        # Ensure focus
        self.root.bind('<Button-1>', lambda e: self.root.focus_set())
        
        # Key press event handler
        self.root.bind('<Key>', self.on_key_press)
    
    def remove_keyboard_bindings(self):
        """Remove keyboard bindings when game is running"""
        # Unbind D-Pad keys
        self.root.unbind('<Up>')
        self.root.unbind('<Down>')
        self.root.unbind('<Left>')
        self.root.unbind('<Right>')
        self.root.unbind('<w>')
        self.root.unbind('<s>')
        self.root.unbind('<a>')
        self.root.unbind('<d>')
        
        # Unbind action buttons (games will handle these)
        self.root.unbind('<Return>')
        self.root.unbind('<space>')
        self.root.unbind('<x>')
        self.root.unbind('<Escape>')
        self.root.unbind('<BackSpace>')
        self.root.unbind('<y>')
        
        # Unbind SELECT and START
        self.root.unbind('<Tab>')
        
        # Keep Button-1 and Key bindings for focus management
        
    def get_active_game_instance(self):
        """Return the currently active game object if a game is running"""
        screen_to_key = {
            'card_game': 'card_game',
            'war_game': 'war_game',
            'river_game': 'river_game',
            'galaxy_war': 'galaxy_war',
            'crakers_game': 'crakers_game',
            'tetris_game': 'tetris_game'
        }
        game_key = screen_to_key.get(self.current_screen)
        if game_key:
            return self.game_instances.get(game_key)
        return None

    def simulate_keypress_to_game(self, game, keysym, release_delay=120):
        """Forward a lightweight keypress event to the active game"""
        if game is None:
            return False
        if hasattr(game, 'on_key_press'):
            try:
                event = type('Event', (), {'keysym': keysym, 'char': ''})()
                game.on_key_press(event)
                if hasattr(game, 'on_key_release'):
                    self.root.after(release_delay, lambda: self.safe_key_release(game, keysym))
                return True
            except Exception as e:
                print(f"Forward keypress failed: {e}")
        return False

    def safe_key_release(self, game, keysym):
        """Safely forward a key release event if the game supports it"""
        try:
            if hasattr(game, 'on_key_release'):
                event = type('Event', (), {'keysym': keysym, 'char': ''})()
                game.on_key_release(event)
        except Exception as e:
            print(f"Forward key release failed: {e}")

    def safe_stop_move(self, game, method_name):
        """Call a movement stop method on a game if present"""
        try:
            if hasattr(game, method_name):
                getattr(game, method_name)(False)
        except Exception as e:
            print(f"Forward stop move failed: {e}")

    def forward_action_to_game(self, button):
        """Route X/Y button presses to the active game"""
        game = self.get_active_game_instance()
        if not game:
            return False
        try:
            if button == 'x':
                if hasattr(game, 'x_button_action'):
                    game.x_button_action()
                    return True
                if hasattr(game, 'start_game_from_screen') and hasattr(game, 'game_active'):
                    if not getattr(game, 'game_active', False):
                        game.start_game_from_screen()
                        return True
                if hasattr(game, 'shoot'):
                    game.shoot()
                    return True
                return self.simulate_keypress_to_game(game, 'Return')
            if button == 'y':
                if hasattr(game, 'y_button_action'):
                    game.y_button_action()
                    return True
                if hasattr(game, 'quit_game'):
                    game.quit_game()
                    return True
                if hasattr(game, 'exit_to_hub'):
                    game.exit_to_hub()
                    return True
                return self.simulate_keypress_to_game(game, 'Escape')
        except Exception as e:
            print(f"Forward button failed: {e}")
        return False
        
    def get_battery_display(self):
        """Generate battery display text"""
        filled_blocks = '▓' * self.battery_level
        empty_blocks = '▒' * (4 - self.battery_level)
        return f"BATTERY {filled_blocks}{empty_blocks}"
    
    def init_gamepad(self):
        """Initialize pygame gamepad support"""
        try:
            pygame.init()
            pygame.joystick.init()
            
            # Gamepad state
            self.joystick = None
            self.gamepad_enabled = True
            
            # Button mapping (XInput standard)
            self.BTN_A = 0      # A button (OK/Confirm)
            self.BTN_B = 1      # B button (Back)
            self.BTN_X = 2      # X button
            self.BTN_Y = 3      # Y button
            self.BTN_LB = 4     # Left bumper
            self.BTN_RB = 5     # Right bumper
            self.BTN_BACK = 6   # Back/Select button
            self.BTN_START = 7  # Start button
            
            # State tracking for edge-trigger (prevent spam)
            self.last_button_state = {}
            self.last_hat = (0, 0)
            self.gamepad_polling_active = False
            
            # Try to connect gamepad
            self.ensure_gamepad()
            
        except Exception as e:
            print(f"Gamepad initialization failed: {e}")
            self.gamepad_enabled = False
    
    def ensure_gamepad(self):
        """Check and connect gamepad if available"""
        if not self.gamepad_enabled:
            return None
            
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"Gamepad connected: {self.joystick.get_name()}")
                return self.joystick
            else:
                self.joystick = None
                return None
        except Exception as e:
            print(f"Gamepad connection error: {e}")
            self.joystick = None
            return None
    
    def poll_gamepad(self):
        """Poll gamepad input and trigger actions"""
        if not self.gamepad_enabled or not self.gamepad_polling_active:
            return
        
        # Check if window still exists
        try:
            self.root.winfo_exists()
        except:
            return
        
        # Check for gamepad connection (hot-plug support)
        if self.joystick is None or not self.joystick.get_init():
            self.ensure_gamepad()
        
        try:
            pygame.event.pump()  # Update events
            
            if self.joystick is not None:
                # --- Button Handling (with edge-trigger) ---
                def is_pressed(btn_index):
                    try:
                        return self.joystick.get_button(btn_index) == 1
                    except pygame.error:
                        return False
                
                def button_just_pressed(btn_index):
                    """Check if button was just pressed (edge-trigger)"""
                    current = is_pressed(btn_index)
                    previous = self.last_button_state.get(btn_index, False)
                    self.last_button_state[btn_index] = current
                    return current and not previous
                
                # Map buttons to actions (menu and welcome)
                if self.current_screen in ("menu", "welcome"):
                    if button_just_pressed(self.BTN_START):
                        self.start_action()
                    if button_just_pressed(self.BTN_BACK):
                        self.select_action()
                    if button_just_pressed(self.BTN_A) or button_just_pressed(self.BTN_X):
                        self.x_button_action()
                    if button_just_pressed(self.BTN_B) or button_just_pressed(self.BTN_Y):
                        self.y_button_action()
                
                # --- D-Pad (Hat) Handling ---
                try:
                    hat = self.joystick.get_hat(0)  # (x, y)
                except pygame.error:
                    hat = (0, 0)
                
                # Trigger only on state change (edge-trigger)
                # Only handle D-Pad in menu, not during games
                if self.current_screen == "menu" and hat != self.last_hat:
                    if hat == (0, 1):      # UP
                        self.dpad_action("UP")
                    elif hat == (0, -1):   # DOWN
                        self.dpad_action("DOWN")
                    elif hat == (-1, 0):   # LEFT
                        self.dpad_action("LEFT")
                    elif hat == (1, 0):    # RIGHT
                        self.dpad_action("RIGHT")
                    self.last_hat = hat
                elif self.current_screen != "menu":
                    # Update last_hat even in games to prevent stuck states
                    self.last_hat = hat
        
        except Exception as e:
            print(f"Gamepad polling error: {e}")
        
        # Poll every 30ms (~33 FPS)
        self.root.after(30, self.poll_gamepad)
    
    def on_key_press(self, event):
        """Handle key press events"""
        key = event.keysym.lower()
        print(f"Key pressed: {key}")
        
    def dpad_action(self, direction):
        """Handle D-Pad direction actions"""
        if self.current_screen == "menu":
            print(f"D-Pad pressed: {direction}")
            if direction == "UP":
                self.selected_game = (self.selected_game - 1) % len(self.games)
                self.show_main_menu()
                print(f"Menu selection: {self.selected_game}")
            elif direction == "DOWN":
                self.selected_game = (self.selected_game + 1) % len(self.games)
                self.show_main_menu()
                print(f"Menu selection: {self.selected_game}")
            return

        # Forward to active game when not in menu
        game = self.get_active_game_instance()
        if not game:
            return

        method_name = f"dpad_{direction.lower()}"
        if hasattr(game, method_name):
            try:
                getattr(game, method_name)()
                return
            except Exception as e:
                print(f"Forward D-Pad to game failed: {e}")

        # Crakers uses dpad_pressed(direction)
        if hasattr(game, 'dpad_pressed'):
            try:
                game.dpad_pressed(direction)
                return
            except Exception as e:
                print(f"Forward D-Pad pressed to game failed: {e}")

        # Galaxy War & similar movement helpers
        if direction in ("LEFT", "RIGHT") and (hasattr(game, 'set_move_left') or hasattr(game, 'set_move_right')):
            if direction == "LEFT":
                try:
                    if hasattr(game, 'set_move_right'):
                        game.set_move_right(False)
                    game.set_move_left(True)
                    self.root.after(150, lambda: self.safe_stop_move(game, 'set_move_left'))
                except Exception as e:
                    print(f"Forward LEFT failed: {e}")
            else:
                try:
                    if hasattr(game, 'set_move_left'):
                        game.set_move_left(False)
                    game.set_move_right(True)
                    self.root.after(150, lambda: self.safe_stop_move(game, 'set_move_right'))
                except Exception as e:
                    print(f"Forward RIGHT failed: {e}")
            return

        key_map = {"UP": "Up", "DOWN": "Down", "LEFT": "Left", "RIGHT": "Right"}
        self.simulate_keypress_to_game(game, key_map.get(direction, ''))
                
    def x_button_action(self):
        """Handle X button press"""
        print(f"X button pressed, screen: {self.current_screen}")
        
        if self.current_screen == "welcome":
            self.show_main_menu()
        elif self.current_screen == "menu":
            print(f"Selected index: {self.selected_game}")
            if self.selected_game == 0:
                self.start_card_game()
            elif self.selected_game == 1:
                self.start_war_game()
            elif self.selected_game == 2:
                self.start_river_game()
            elif self.selected_game == 3:
                self.start_galaxy_war_game()
            elif self.selected_game == 4:
                self.start_crakers_game()
            elif self.selected_game == 5:
                self.start_tetris_game()
        else:
            self.forward_action_to_game('x')

    def a_button_action(self):
        """Alias for X button (some controllers map A as confirm)"""
        self.x_button_action()
                
    def y_button_action(self):
        """Handle Y button press"""
        if self.current_screen == "menu":
            self.show_welcome_screen()
        elif self.current_screen == "welcome":
            self.power_off()
        else:
            self.forward_action_to_game('y')
            
    def select_action(self):
        """Handle SELECT button press"""
        # Return to hub menu from any state
        if self.current_screen == "welcome":
            self.show_main_menu()
            return
        if self.current_screen == "menu":
            return

        game = self.get_active_game_instance()
        if game:
            try:
                if hasattr(game, 'exit_to_hub'):
                    game.exit_to_hub()
                    return
                if hasattr(game, 'quit_game'):
                    game.quit_game()
                    return
            except Exception as e:
                print(f"Select exit to hub failed: {e}")

        # Fallback: force hub UI
        self.return_to_nostalgik()
        
    def start_action(self):
        """Handle START button press"""
        if self.current_screen == "welcome":
            self.show_main_menu()
        elif self.current_screen == "menu":
            self.x_button_action()  # Same as X button in menu
        else:
            game = self.get_active_game_instance()
            if not game:
                return
            try:
                # If game inactive and has start screen
                if hasattr(game, 'game_active') and hasattr(game, 'start_game_from_screen'):
                    if not getattr(game, 'game_active', False):
                        game.start_game_from_screen()
                        return
                # Pause toggle if available
                if hasattr(game, 'toggle_pause'):
                    game.toggle_pause()
                    return
                # Generic start
                if hasattr(game, 'start_game'):
                    game.start_game()
                    return
                # Fallback to Return key simulation
                self.simulate_keypress_to_game(game, 'Return')
            except Exception as e:
                print(f"Start action forward failed: {e}")
            
    def show_blank_screen(self):
        """Show blank screen on startup"""
        self.clear_screen()
        self.current_screen = "blank"
        
        # Just empty screen
        blank_frame = tk.Frame(self.screen, bg=self.colors['screen_green'])
        blank_frame.pack(fill='both', expand=True)
    
    def show_welcome_screen(self):
        """Show NostalgiKit welcome screen"""
        self.clear_screen()
        self.current_screen = "welcome"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Welcome message
        welcome_label = tk.Label(content,
                                text="NostalgiKIT\nCLASSIC",
                                font=self.fonts['retro_large'],
                                fg=self.colors['screen_dark'],
                                bg=self.colors['screen_green'],
                                justify='center')
        welcome_label.pack(expand=True)
        
        # NostalgiKit logo simulation
        logo_label = tk.Label(content,
                             text="🎮",
                             font=self.fonts['retro_large'],
                             fg=self.colors['screen_dark'],
                             bg=self.colors['screen_green'])
        logo_label.pack()
        
        # Instructions
        instruction_label = tk.Label(content,
                                    text="Press START\nor X to begin",
                                    font=self.fonts['retro_small'],
                                    fg=self.colors['screen_dark'],
                                    bg=self.colors['screen_green'],
                                    justify='center')
        instruction_label.pack(side='bottom', pady=10)
        
    def show_main_menu(self):
        """Show main game selection menu"""
        self.clear_screen()
        self.current_screen = "menu"
        
        content = tk.Frame(self.screen, bg=self.colors['screen_green'])
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = tk.Label(content,
                              text="SELECT GAME",
                              font=self.fonts['retro_text'],
                              fg=self.colors['screen_dark'],
                              bg=self.colors['screen_green'])
        title_label.pack(pady=(5, 10))
        
        # Game list
        for i, game in enumerate(self.games):
            if i == self.selected_game:
                # Selected game
                game_frame = tk.Frame(content, bg=self.colors['screen_dark'], relief='raised', bd=1)
                game_frame.pack(fill='x', padx=10, pady=2)
                
                game_label = tk.Label(game_frame,
                                     text=f"► {game['name']}",
                                     font=self.fonts['retro_small'],
                                     fg=self.colors['screen_green'],
                                     bg=self.colors['screen_dark'],
                                     anchor='w')
                game_label.pack(fill='x', padx=5, pady=2)
                
                desc_label = tk.Label(game_frame,
                                     text=f"  {game['desc']}",
                                     font=self.fonts['retro_tiny'],
                                     fg=self.colors['screen_green'],
                                     bg=self.colors['screen_dark'],
                                     anchor='w')
                desc_label.pack(fill='x', padx=5)
            else:
                # Unselected game
                game_label = tk.Label(content,
                                     text=f"  {game['name']}",
                                     font=self.fonts['retro_small'],
                                     fg=self.colors['screen_dark'],
                                     bg=self.colors['screen_green'],
                                     anchor='w')
                game_label.pack(fill='x', padx=10, pady=1)
                
        # Controls info
        controls_frame = tk.Frame(content, bg=self.colors['screen_green'])
        controls_frame.pack(side='bottom', fill='x', pady=5)
        
        controls_label = tk.Label(controls_frame,
                                 text="↑↓: Select  X: Play  Y: Back",
                                 font=self.fonts['retro_tiny'],
                                 fg=self.colors['screen_dark'],
                                 bg=self.colors['screen_green'])
        controls_label.pack()
        
    def power_off(self):
        """Simulate power off"""
        self.clear_screen()
        
        off_frame = tk.Frame(self.screen, bg=self.colors['screen_dark'])
        off_frame.pack(fill='both', expand=True)
        
        self.current_screen = "off"
        
    def clear_screen(self):
        """Clear the NostalgiKit screen"""
        for widget in self.screen.winfo_children():
            widget.destroy()
            
    def show_loading_screen(self, game_name):
        """Show loading screen for games"""
        self.clear_screen()
        loading_frame = tk.Frame(self.screen, bg=self.colors['screen_green'])
        loading_frame.pack(fill='both', expand=True)
        
        loading_label = tk.Label(loading_frame,
                                text=f"LOADING...\n{game_name}\n\nPress Y to return",
                                font=self.fonts['retro_text'],
                                fg=self.colors['screen_dark'],
                                bg=self.colors['screen_green'],
                                justify='center')
        loading_label.pack(expand=True)
        
    def start_card_game(self):
        """Start the Card Guess Game"""
        # Stop gamepad polling while game is running
        self.gamepad_polling_active = False
        print("Starting Number Oracle (card game)...")
        
        # Show loading screen
        self.show_loading_screen("NUMBER ORACLE")
        
        # Launch actual game after brief delay
        def launch_game():
            try:
                print("Launching Number Oracle now...")
                # Remove hub keyboard bindings so game can handle input
                self.remove_keyboard_bindings()
                # Ekranı temizle
                self.clear_screen()
                # Oyun instance yoksa oluştur, varsa tekrar kullan
                if self.game_instances['card_game'] is None:
                    self.game_instances['card_game'] = CardGuessGame(self.screen, self.return_to_nostalgik)
                else:
                    # Mevcut oyunu göster ve resetle
                    self.game_instances['card_game'].show()
                # Track current screen to avoid menu handlers during game
                self.current_screen = "card_game"
            except Exception as e:
                print(f"Failed to launch card game: {e}")
                try:
                    messagebox.showerror("Card Game Error", str(e))
                except Exception:
                    pass
                # Return to menu so user isn't stuck
                self.show_main_menu()
                self.current_screen = "menu"
                # Resume gamepad polling for hub
                self.gamepad_polling_active = True
        
        # Shorter delay so it feels instant
        self.root.after(300, launch_game)
        
    def start_war_game(self):
        """Start the War Game"""
        # Stop gamepad polling while game is running
        self.gamepad_polling_active = False
        
        # Show loading screen
        self.show_loading_screen("WAR GAME")
        
        # Launch actual game after brief delay
        def launch_game():
            # Remove hub keyboard bindings so game can handle input
            self.remove_keyboard_bindings()
            # Ekranı temizle
            self.clear_screen()
            # Oyun instance yoksa oluştur, varsa tekrar kullan
            if self.game_instances['war_game'] is None:
                self.game_instances['war_game'] = WarGame(self.screen, self.return_to_nostalgik)
            else:
                # Mevcut oyunu göster ve resetle
                self.game_instances['war_game'].show()
            # Track active screen for input routing
            self.current_screen = "war_game"
        
        self.root.after(1500, launch_game)
        
    def start_river_game(self):
        """Start the River Crossing Game"""
        # Stop gamepad polling while game is running
        self.gamepad_polling_active = False
        
        # Show loading screen
        self.show_loading_screen("RIVER PUZZLE")
        
        # Launch actual game after brief delay
        def launch_game():
            # Remove hub keyboard bindings so game can handle input
            self.remove_keyboard_bindings()
            # Ekranı temizle
            self.clear_screen()
            # Oyun instance yoksa oluştur, varsa tekrar kullan
            if self.game_instances['river_game'] is None:
                self.game_instances['river_game'] = RiverGame(self.screen, self.return_to_nostalgik)
            else:
                # Mevcut oyunu göster ve resetle
                self.game_instances['river_game'].show()
            # Track active screen for input routing
            self.current_screen = "river_game"
        
        self.root.after(1500, launch_game)

    def start_galaxy_war_game(self):
        """Start the Galaxy War Pat Game"""
        # Stop gamepad polling while game is running
        self.gamepad_polling_active = False
        
        # Show loading screen
        self.show_loading_screen("GALAXY WAR PAT")
        
        # Launch actual game after brief delay
        def launch_game():
            # Remove hub keyboard bindings so game can handle input
            self.remove_keyboard_bindings()
            # Ekranı temizle
            self.clear_screen()
            # Oyun instance yoksa oluştur, varsa tekrar kullan
            if self.game_instances['galaxy_war'] is None:
                self.game_instances['galaxy_war'] = GalaxyWarPat(self.screen, self.return_to_nostalgik)
            else:
                # Mevcut oyunu göster ve resetle
                self.game_instances['galaxy_war'].show()
            # Track active screen for input routing
            self.current_screen = "galaxy_war"
        
        self.root.after(1500, launch_game)

    def start_crakers_game(self):
        """Start the Crakers Quest Game"""
        # Stop gamepad polling while game is running
        self.gamepad_polling_active = False
        
        # Show loading screen
        self.show_loading_screen("CRAKERS QUEST")
        
        # Launch actual game after brief delay
        def launch_game():
            # Remove hub keyboard bindings so game can handle input
            self.remove_keyboard_bindings()
            # Ekranı temizle
            self.clear_screen()
            # Oyun instance yoksa oluştur, varsa tekrar kullan
            if self.game_instances['crakers_game'] is None:
                self.game_instances['crakers_game'] = CrakersGame(self.screen, self.return_to_nostalgik)
            else:
                # Mevcut oyunu göster ve resetle
                self.game_instances['crakers_game'].show()
            # Track active screen for input routing
            self.current_screen = "crakers_game"
        
        self.root.after(1500, launch_game)

    def start_tetris_game(self):
        """Start the Block Stack (Tetris) Game"""
        self.gamepad_polling_active = False

        self.show_loading_screen("BLOCK STACK")

        def launch_game():
            self.remove_keyboard_bindings()
            self.clear_screen()
            if self.game_instances['tetris_game'] is None:
                self.game_instances['tetris_game'] = TetrisGame(self.screen, self.return_to_nostalgik)
            else:
                self.game_instances['tetris_game'].show()
            self.current_screen = "tetris_game"

        self.root.after(1500, launch_game)

    def return_to_nostalgik(self):
        """Return to NostalgiKit interface"""
        # Clear only the screen area (not the entire root)
        self.clear_screen()
        
        # Show main menu
        self.show_main_menu()
        
        # Re-enable hub keyboard bindings
        self.setup_keyboard_bindings()
        
        # Restart gamepad polling
        if self.gamepad_enabled and not self.gamepad_polling_active:
            self.gamepad_polling_active = True
            self.root.after(100, self.poll_gamepad)
        
    def run(self):
        """Start the NostalgiKit"""
        self.root.mainloop()

if __name__ == "__main__":
    # Create and run the NostalgiKit
    NostalgiKIT = NostalgiKitHub()
    NostalgiKIT.run()
