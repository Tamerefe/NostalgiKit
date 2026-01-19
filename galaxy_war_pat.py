"""
Galaxy War Pat - Space Invaders Style Retro Game
Original space shooter with unique pixel art design

Copyright (c) 2026 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import random
import time
import pygame  # For gamepad support

class GalaxyWarPat:
    def __init__(self, parent, return_callback):
        self.parent = parent
        self.return_callback = return_callback
        
        # Game configuration
        self.canvas_width = 330
        self.canvas_height = 290
        self.player_speed = 15
        self.bullet_speed = 20
        self.enemy_speed = 2
        self.enemy_bullet_speed = 12
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_active = False
        self.game_over = False
        self.paused = False
        
        # Game objects
        self.player = None
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.particles = []
        
        # Movement
        self.move_left = False
        self.move_right = False
        self.enemy_direction = 1  # 1 for right, -1 for left
        self.enemy_drop_distance = 25
        
        # Timing
        self.last_shot_time = 0
        self.shot_cooldown = 0.3
        self.last_enemy_shot_time = 0
        self.enemy_shot_cooldown = 1.5
        self.last_enemy_move_time = 0
        self.enemy_move_interval = 0.5
        
        # NostalgiKit colors
        self.colors = {
            'nostalgik_cream': '#E8E0C7',
            'screen_green': '#9BBB59',
            'dark_green': '#8B9467',
            'screen_dark': '#374224',
            'button_gray': '#8E8E93',
            'text_dark': '#1C1C1E',
            'highlight': '#FFD23F',
            'red_button': '#FF3B30',
            'purple_button': '#8E44AD',
            'player_color': '#00FFFF',      # Cyan for player
            'enemy_color': '#FF00FF',       # Magenta for enemies
            'bullet_color': '#FFFF00',      # Yellow for bullets
            'enemy_bullet_color': '#FF0000', # Red for enemy bullets
            'particle_color': '#FFA500'     # Orange for explosions
        }
        
        # Fonts - matching NostalgiKit style
        self.fonts = {
            'retro_title': tkFont.Font(family="Courier", size=10, weight="bold"),
            'retro_text': tkFont.Font(family="Courier", size=9, weight="bold"),
            'retro_small': tkFont.Font(family="Courier", size=8, weight="bold"),
            'retro_large': tkFont.Font(family="Courier", size=12, weight="bold"),
            'retro_tiny': tkFont.Font(family="Courier", size=7, weight="bold")
        }
        
        self.setup_game_screen()
        self.init_gamepad()
        self.setup_keyboard_bindings()
        self.show_start_screen()
        
    def setup_game_screen(self):
        """Create the game interface inside hub's screen frame"""
        # Create main game frame inside hub's screen (parent is now the screen frame)
        # Only create once - reuse on subsequent calls
        if not hasattr(self, 'game_frame') or not self.game_frame.winfo_exists():
            self.game_frame = tk.Frame(self.parent, bg=self.colors['screen_green'])
            self.game_frame.pack(fill='both', expand=True)
        
        # Clear any previous content
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # HUD (Score, Wave, Lives)
        hud_frame = tk.Frame(self.game_frame, bg=self.colors['screen_dark'], height=30)
        hud_frame.pack(fill='x', padx=2, pady=2)
        hud_frame.pack_propagate(False)
        
        self.score_label = tk.Label(hud_frame,
                                    text="SCORE:0000",
                                    font=self.fonts['retro_small'],
                                    fg=self.colors['highlight'],
                                    bg=self.colors['screen_dark'])
        self.score_label.pack(side='left', padx=5)
        
        self.level_label = tk.Label(hud_frame,
                                    text="WAVE:1",
                                    font=self.fonts['retro_small'],
                                    fg=self.colors['highlight'],
                                    bg=self.colors['screen_dark'])
        self.level_label.pack(side='left', padx=5)
        
        self.lives_label = tk.Label(hud_frame,
                                   text="LIVES:♥♥♥",
                                   font=self.fonts['retro_small'],
                                   fg=self.colors['nostalgik_cream'],
                                   bg=self.colors['screen_dark'])
        self.lives_label.pack(side='right', padx=5)
        
        # Game canvas
        self.canvas = tk.Canvas(self.game_frame,
                               width=self.canvas_width,
                               height=self.canvas_height,
                               bg=self.colors['screen_dark'],
                               highlightthickness=0)
        self.canvas.pack(padx=2, pady=2, expand=True)
        
    def setup_keyboard_bindings(self):
        """Setup keyboard controls - bind to root window"""
        # Get root window from parent frame
        root = self.parent.winfo_toplevel()
        root.bind('<Left>', lambda e: self.set_move_left(True))
        root.bind('<Right>', lambda e: self.set_move_right(True))
        root.bind('<KeyRelease-Left>', lambda e: self.set_move_left(False))
        root.bind('<KeyRelease-Right>', lambda e: self.set_move_right(False))
        root.bind('<space>', lambda e: self.shoot())
        root.bind('<p>', lambda e: self.toggle_pause())
        root.bind('<Escape>', lambda e: self.quit_game())
        root.bind('<Return>', lambda e: self.start_game_from_screen())
        root.bind('<Tab>', lambda e: self.quit_game())  # Select returns to hub
        root.focus_set()
    
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
            
            # Button mapping
            self.BTN_A = 0
            self.BTN_B = 1
            self.BTN_X = 2
            self.BTN_Y = 3
            self.BTN_START = 7
            
            # Connect gamepad
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"Gamepad connected to game: {self.joystick.get_name()}")
            
            # Start polling
            self.parent.winfo_toplevel().after(30, self.poll_gamepad)
            
        except Exception as e:
            print(f"Gamepad init error in game: {e}")
            self.gamepad_enabled = False
    
    def poll_gamepad(self):
        """Poll gamepad input"""
        if not self.gamepad_enabled or not self.gamepad_polling_active:
            return
        
        try:
            # Check if window exists
            self.parent.winfo_toplevel().winfo_exists()
        except:
            return
        
        try:
            pygame.event.pump()
            
            if self.joystick is not None and self.joystick.get_init():
                # Helper functions
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
                
                # Buttons
                if just_pressed(self.BTN_A) or just_pressed(self.BTN_X):
                    if not self.game_active:
                        self.start_game_from_screen()
                    else:
                        self.shoot()
                
                if just_pressed(self.BTN_B) or just_pressed(self.BTN_Y):
                    self.quit_game()
                
                if just_pressed(self.BTN_START):
                    self.toggle_pause()
                
                # D-Pad and analog stick for movement
                try:
                    hat = self.joystick.get_hat(0)
                    if hat[0] == -1:  # Left
                        self.set_move_left(True)
                        self.set_move_right(False)
                    elif hat[0] == 1:  # Right
                        self.set_move_right(True)
                        self.set_move_left(False)
                    else:
                        # Check analog stick
                        axis_x = self.joystick.get_axis(0)
                        if axis_x < -0.3:
                            self.set_move_left(True)
                            self.set_move_right(False)
                        elif axis_x > 0.3:
                            self.set_move_right(True)
                            self.set_move_left(False)
                        else:
                            self.set_move_left(False)
                            self.set_move_right(False)
                except:
                    pass
        
        except Exception as e:
            if "bad window" not in str(e):
                print(f"Gamepad poll error: {e}")
        
        # Continue polling
        try:
            self.parent.winfo_toplevel().after(30, self.poll_gamepad)
        except:
            pass
        
    def set_move_left(self, value):
        """Set left movement flag"""
        self.move_left = value
        
    def set_move_right(self, value):
        """Set right movement flag"""
        self.move_right = value
        
    def show_start_screen(self):
        """Display start screen"""
        self.canvas.delete('all')
        
        # Title
        self.canvas.create_text(self.canvas_width // 2, 100,
                               text="GALAXY WAR PAT",
                               font=self.fonts['retro_large'],
                               fill=self.colors['highlight'])
        
        # Draw a sample enemy
        self.draw_custom_enemy(self.canvas_width // 2 - 40, 180, 1)
        self.draw_custom_enemy(self.canvas_width // 2, 180, 2)
        self.draw_custom_enemy(self.canvas_width // 2 + 40, 180, 3)
        
        # Draw player ship
        self.draw_player_ship(self.canvas_width // 2, 280)
        
        # Instructions
        self.canvas.create_text(self.canvas_width // 2, 340,
                               text="DEFEND THE GALAXY!",
                               font=self.fonts['retro_text'],
                               fill=self.colors['player_color'])
        
        self.canvas.create_text(self.canvas_width // 2, 380,
                               text="PRESS ENTER TO START",
                               font=self.fonts['retro_text'],
                               fill=self.colors['highlight'])
        
        self.canvas.create_text(self.canvas_width // 2, 420,
                               text="← → MOVE  SPACE SHOOT",
                               font=self.fonts['retro_small'],
                               fill=self.colors['nostalgik_cream'])
        
    def start_game_from_screen(self):
        """Start game from start screen"""
        if not self.game_active:
            self.start_game()
            
    def start_game(self):
        """Initialize and start a new game"""
        self.game_active = True
        self.game_over = False
        self.paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        
        # Clear objects
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.particles = []
        
        # Create player
        self.player = {
            'x': self.canvas_width // 2,
            'y': self.canvas_height - 60,
            'width': 30,
            'height': 25
        }
        
        # Create first wave
        self.create_enemy_wave()
        
        # Update display
        self.update_hud()
        
        # Start game loop
        self.game_loop()
        
    def create_enemy_wave(self):
        """Create a wave of enemies"""
        self.enemies = []
        rows = 3 + (self.level - 1) // 2  # More rows as level increases
        cols = 7
        spacing_x = 45
        spacing_y = 40
        start_x = 40
        start_y = 35  # Spawn one tile higher
        
        for row in range(rows):
            for col in range(cols):
                enemy_type = (row % 3) + 1  # 3 different enemy types
                enemy = {
                    'x': start_x + col * spacing_x,
                    'y': start_y + row * spacing_y,
                    'width': 28,
                    'height': 22,
                    'type': enemy_type,
                    'alive': True
                }
                self.enemies.append(enemy)
                
    def draw_player_ship(self, x, y):
        """Draw custom player ship with unique pixel design"""
        # Main body (triangular spaceship)
        points = [
            x, y - 10,           # Top point
            x - 12, y + 10,      # Bottom left
            x + 12, y + 10       # Bottom right
        ]
        self.canvas.create_polygon(points, fill=self.colors['player_color'], outline=self.colors['highlight'])
        
        # Cockpit
        self.canvas.create_oval(x - 4, y - 2, x + 4, y + 4, 
                               fill=self.colors['highlight'], outline='')
        
        # Wings
        self.canvas.create_rectangle(x - 15, y + 2, x - 10, y + 8, 
                                     fill=self.colors['player_color'], outline='')
        self.canvas.create_rectangle(x + 10, y + 2, x + 15, y + 8, 
                                     fill=self.colors['player_color'], outline='')
        
        # Engine glow
        self.canvas.create_oval(x - 6, y + 8, x - 3, y + 12, 
                               fill='#FF6600', outline='')
        self.canvas.create_oval(x + 3, y + 8, x + 6, y + 12, 
                               fill='#FF6600', outline='')
                               
    def draw_custom_enemy(self, x, y, enemy_type):
        """Draw unique enemy designs based on type"""
        if enemy_type == 1:
            # Squid-like alien
            # Head
            self.canvas.create_oval(x - 10, y - 8, x + 10, y + 5, 
                                   fill=self.colors['enemy_color'], outline='')
            # Eyes
            self.canvas.create_oval(x - 6, y - 4, x - 3, y - 1, 
                                   fill=self.colors['highlight'], outline='')
            self.canvas.create_oval(x + 3, y - 4, x + 6, y - 1, 
                                   fill=self.colors['highlight'], outline='')
            # Tentacles
            for i in range(-8, 9, 4):
                self.canvas.create_rectangle(x + i - 1, y + 5, x + i + 1, y + 10, 
                                            fill=self.colors['enemy_color'], outline='')
                
        elif enemy_type == 2:
            # Geometric alien
            # Diamond body
            points = [
                x, y - 8,        # Top
                x - 10, y,       # Left
                x, y + 8,        # Bottom
                x + 10, y        # Right
            ]
            self.canvas.create_polygon(points, fill=self.colors['enemy_color'], 
                                      outline=self.colors['highlight'])
            # Core
            self.canvas.create_rectangle(x - 4, y - 4, x + 4, y + 4, 
                                        fill=self.colors['highlight'], outline='')
            
        else:  # type 3
            # Crab-like alien
            # Body
            self.canvas.create_rectangle(x - 10, y - 5, x + 10, y + 5, 
                                        fill=self.colors['enemy_color'], outline='')
            # Eyes on stalks
            self.canvas.create_rectangle(x - 7, y - 8, x - 5, y - 5, 
                                        fill=self.colors['enemy_color'], outline='')
            self.canvas.create_rectangle(x + 5, y - 8, x + 7, y - 5, 
                                        fill=self.colors['enemy_color'], outline='')
            self.canvas.create_oval(x - 8, y - 10, x - 4, y - 6, 
                                   fill=self.colors['highlight'], outline='')
            self.canvas.create_oval(x + 4, y - 10, x + 8, y - 6, 
                                   fill=self.colors['highlight'], outline='')
            # Claws
            self.canvas.create_rectangle(x - 12, y, x - 10, y + 5, 
                                        fill=self.colors['enemy_color'], outline='')
            self.canvas.create_rectangle(x + 10, y, x + 12, y + 5, 
                                        fill=self.colors['enemy_color'], outline='')
                                        
    def shoot(self):
        """Player shoots a bullet"""
        if not self.game_active or self.paused or self.game_over:
            return
            
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            bullet = {
                'x': self.player['x'],
                'y': self.player['y'] - 15,
                'width': 3,
                'height': 10,
                'speed': self.bullet_speed
            }
            self.bullets.append(bullet)
            self.last_shot_time = current_time
            
    def enemy_shoot(self):
        """Random enemy shoots at player"""
        if not self.enemies or not self.game_active or self.paused:
            return
            
        current_time = time.time()
        if current_time - self.last_enemy_shot_time >= self.enemy_shot_cooldown:
            # Choose a random alive enemy from bottom rows
            bottom_enemies = [e for e in self.enemies if e['alive']]
            if bottom_enemies:
                shooter = random.choice(bottom_enemies)
                bullet = {
                    'x': shooter['x'],
                    'y': shooter['y'] + 15,
                    'width': 3,
                    'height': 8,
                    'speed': self.enemy_bullet_speed
                }
                self.enemy_bullets.append(bullet)
                self.last_enemy_shot_time = current_time
                
    def move_player(self):
        """Move player based on input"""
        if self.move_left and self.player['x'] > 20:
            self.player['x'] -= self.player_speed
        if self.move_right and self.player['x'] < self.canvas_width - 20:
            self.player['x'] += self.player_speed
            
    def move_enemies(self):
        """Move all enemies in formation"""
        current_time = time.time()
        if current_time - self.last_enemy_move_time < self.enemy_move_interval:
            return
            
        self.last_enemy_move_time = current_time
        
        # Check if any enemy hits the edge
        hit_edge = False
        for enemy in self.enemies:
            if enemy['alive']:
                half_w = enemy['width'] // 2
                if (enemy['x'] - half_w <= 0 and self.enemy_direction == -1) or \
                   (enemy['x'] + half_w >= self.canvas_width and self.enemy_direction == 1):
                    hit_edge = True
                    break
        
        # Move enemies
        if hit_edge:
            # Drop down and reverse direction
            self.enemy_direction *= -1
            for enemy in self.enemies:
                if enemy['alive']:
                    enemy['y'] += self.enemy_drop_distance
                    half_w = enemy['width'] // 2
                    # Keep enemies fully on-screen after drops
                    enemy['x'] = max(half_w, min(self.canvas_width - half_w, enemy['x']))
                    
            # Speed up as enemies get closer
            self.enemy_move_interval *= 0.95
        else:
            # Move horizontally
            for enemy in self.enemies:
                if enemy['alive']:
                    half_w = enemy['width'] // 2
                    new_x = enemy['x'] + self.enemy_speed * self.enemy_direction
                    min_x = half_w
                    max_x = self.canvas_width - half_w
                    enemy['x'] = max(min_x, min(max_x, new_x))
                    
    def update_bullets(self):
        """Update bullet positions"""
        # Player bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed']
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
                
        # Enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet['y'] += bullet['speed']
            if bullet['y'] > self.canvas_height:
                self.enemy_bullets.remove(bullet)
                
    def check_collisions(self):
        """Check for all collisions"""
        # Player bullets hitting enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies:
                if enemy['alive'] and self.check_collision(bullet, enemy):
                    enemy['alive'] = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.score += 10 * enemy['type']
                    self.create_explosion(enemy['x'], enemy['y'])
                    break
                    
        # Enemy bullets hitting player
        for bullet in self.enemy_bullets[:]:
            if self.check_collision(bullet, self.player):
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                self.player_hit()
                
        # Check if enemies reached player
        for enemy in self.enemies:
            if enemy['alive'] and enemy['y'] + enemy['height'] >= self.player['y']:
                self.game_over = True
                self.show_game_over("ENEMIES INVADED!")
                
    def check_collision(self, obj1, obj2):
        """Check if two objects collide"""
        return (obj1['x'] - obj1.get('width', 5) // 2 < obj2['x'] + obj2['width'] // 2 and
                obj1['x'] + obj1.get('width', 5) // 2 > obj2['x'] - obj2['width'] // 2 and
                obj1['y'] - obj1.get('height', 5) // 2 < obj2['y'] + obj2['height'] // 2 and
                obj1['y'] + obj1.get('height', 5) // 2 > obj2['y'] - obj2['height'] // 2)
                
    def player_hit(self):
        """Handle player being hit"""
        self.lives -= 1
        self.create_explosion(self.player['x'], self.player['y'])
        
        if self.lives <= 0:
            self.game_over = True
            self.show_game_over("GAME OVER!")
        else:
            self.update_hud()
            
    def create_explosion(self, x, y):
        """Create explosion particles"""
        for _ in range(8):
            particle = {
                'x': x,
                'y': y,
                'dx': random.uniform(-3, 3),
                'dy': random.uniform(-3, 3),
                'life': 15
            }
            self.particles.append(particle)
            
    def update_particles(self):
        """Update explosion particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def check_wave_complete(self):
        """Check if all enemies are destroyed"""
        if all(not enemy['alive'] for enemy in self.enemies):
            self.level += 1
            self.enemy_move_interval = 0.5  # Reset speed
            self.create_enemy_wave()
            self.update_hud()
            
    def draw_game(self):
        """Draw all game objects"""
        self.canvas.delete('all')
        
        # Draw player
        if not self.game_over:
            self.draw_player_ship(self.player['x'], self.player['y'])
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy['alive']:
                self.draw_custom_enemy(enemy['x'], enemy['y'], enemy['type'])
        
        # Draw bullets
        for bullet in self.bullets:
            self.canvas.create_rectangle(
                bullet['x'] - bullet['width'] // 2,
                bullet['y'] - bullet['height'] // 2,
                bullet['x'] + bullet['width'] // 2,
                bullet['y'] + bullet['height'] // 2,
                fill=self.colors['bullet_color'],
                outline=''
            )
            
        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            self.canvas.create_oval(
                bullet['x'] - bullet['width'] // 2,
                bullet['y'] - bullet['height'] // 2,
                bullet['x'] + bullet['width'] // 2,
                bullet['y'] + bullet['height'] // 2,
                fill=self.colors['enemy_bullet_color'],
                outline=''
            )
            
        # Draw particles
        for particle in self.particles:
            alpha = particle['life'] / 15.0
            self.canvas.create_oval(
                particle['x'] - 3,
                particle['y'] - 3,
                particle['x'] + 3,
                particle['y'] + 3,
                fill=self.colors['particle_color'],
                outline=''
            )
            
        # Draw pause overlay
        if self.paused:
            self.canvas.create_text(
                self.canvas_width // 2,
                self.canvas_height // 2,
                text="PAUSED",
                font=self.fonts['retro_large'],
                fill=self.colors['highlight']
            )
            
    def update_hud(self):
        """Update score and lives display"""
        self.score_label.config(text=f"SCORE:{self.score:04d}")
        self.level_label.config(text=f"WAVE:{self.level}")
        hearts = "♥" * self.lives
        self.lives_label.config(text=f"LIVES:{hearts}")
        
    def toggle_pause(self):
        """Toggle pause state"""
        if self.game_active and not self.game_over:
            self.paused = not self.paused
            
    def show_game_over(self, message):
        """Display game over screen"""
        self.game_active = False
        self.canvas.delete('all')
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 - 60,
            text=message,
            font=self.fonts['retro_large'],
            fill=self.colors['enemy_color']
        )
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2,
            text=f"FINAL SCORE: {self.score}",
            font=self.fonts['retro_text'],
            fill=self.colors['highlight']
        )
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 40,
            text=f"WAVES SURVIVED: {self.level}",
            font=self.fonts['retro_text'],
            fill=self.colors['player_color']
        )
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 80,
            text="PRESS ENTER TO RESTART",
            font=self.fonts['retro_small'],
            fill=self.colors['nostalgik_cream']
        )
        
        self.canvas.create_text(
            self.canvas_width // 2,
            self.canvas_height // 2 + 110,
            text="PRESS ESC TO EXIT",
            font=self.fonts['retro_small'],
            fill=self.colors['nostalgik_cream']
        )
        
    def game_loop(self):
        """Main game loop"""
        if not self.game_active:
            return
            
        if not self.paused:
            # Update game state
            self.move_player()
            self.move_enemies()
            self.update_bullets()
            self.update_particles()
            self.check_collisions()
            self.check_wave_complete()
            
            # Random enemy shooting
            if random.random() < 0.02:  # 2% chance per frame
                self.enemy_shoot()
                
            # Update HUD
            self.update_hud()
            
        # Draw everything
        self.draw_game()
        
        # Continue loop if game is still active
        if self.game_active:
            self.parent.winfo_toplevel().after(50, self.game_loop)  # ~20 FPS
            
    def quit_game(self):
        """Return to main menu"""
        self.game_active = False
        self.game_over = False
        
        # Unbind keys from root window
        root_window = self.parent.winfo_toplevel()
        root_window.unbind('<Left>')
        root_window.unbind('<Right>')
        root_window.unbind('<KeyRelease-Left>')
        root_window.unbind('<KeyRelease-Right>')
        root_window.unbind('<space>')
        root_window.unbind('<p>')
        root_window.unbind('<Escape>')
        root_window.unbind('<Return>')
        
        self.return_callback()
    
    def show(self):
        """Show game again (reuse instance)"""
        # Oyun durumunu sıfırla
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_active = False
        self.game_over = False
        self.paused = False
        
        self.player = None
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.particles = []
        
        self.move_left = False
        self.move_right = False
        self.enemy_direction = 1
        
        self.last_shot_time = 0
        self.last_enemy_shot_time = 0
        self.last_enemy_move_time = 0
        self.level_start_time = 0
        
        # Interface'i yeniden oluştur
        self.setup_game_screen()
        self.show_start_screen()
        
        # Gamepad'i yeniden başlat
        if self.gamepad_enabled:
            self.gamepad_polling_active = True
            self.parent.winfo_toplevel().after(100, self.poll_gamepad)


def main():
    """Standalone test function"""
    root = tk.Tk()
    root.title("Galaxy War Pat - Test")
    root.geometry("460x680")
    
    # Create a frame for embedding
    screen_frame = tk.Frame(root, bg='#9BBB59')
    screen_frame.pack(fill='both', expand=True)
    
    def return_to_menu():
        print("Returning to menu...")
        root.quit()
    
    game = GalaxyWarPat(screen_frame, return_to_menu)
    root.mainloop()


if __name__ == "__main__":
    main()
