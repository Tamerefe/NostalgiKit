"""
NostalgiKit Crakers Game - Retro Style
Game Boy-style top-down grid adventure with collectibles and enemies

Copyright (c) 2026 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import random
import time
import pygame  # For gamepad support

# ============================================================================
# CONSTANTS
# ============================================================================

# NostalgiKit colors (matching game hub exactly)
COLOR_NOSTALGIK_CREAM = '#E8E0C7'    # Main vintage cream color
COLOR_SCREEN_GREEN = '#9BBB59'       # Classic green screen
COLOR_DARK_GREEN = '#8B9467'         # Dark accents
COLOR_SCREEN_DARK = '#374224'        # Dark screen areas
COLOR_BUTTON_GRAY = '#8E8E93'        # Button color
COLOR_TEXT_DARK = '#1C1C1E'          # Dark text
COLOR_HIGHLIGHT = '#FFD23F'          # Yellow highlight
COLOR_RED_BUTTON = '#FF3B30'         # X button (red)
COLOR_PURPLE_BUTTON = '#8E44AD'      # Y button (purple)

# Grid settings
TILE_SIZE = 14
GRID_WIDTH = 18
GRID_HEIGHT = 12
CANVAS_WIDTH = GRID_WIDTH * TILE_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Game settings
PLAYER_LIVES = 3
DASH_COOLDOWN = 3.0
DASH_DISTANCE = 2
ENEMY_MOVE_INTERVAL = 0.5
GAME_TICK = 50

# Tile types
TILE_FLOOR = 0
TILE_WALL = 1

# ============================================================================
# HELPER CLASSES
# ============================================================================

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lives = PLAYER_LIVES
        self.invincible_until = 0
        
    def move(self, dx, dy, game_map):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if game_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def dash(self, dx, dy, game_map):
        for _ in range(DASH_DISTANCE):
            if not self.move(dx, dy, game_map):
                break
    
    def is_invincible(self):
        return time.time() < self.invincible_until
    
    def take_hit(self):
        if not self.is_invincible():
            self.lives -= 1
            self.invincible_until = time.time() + 1.5
            return True
        return False


class Enemy:
    def __init__(self, x, y, patrol_points):
        self.x = x
        self.y = y
        self.patrol_points = patrol_points
        self.current_target = 0
        self.last_move_time = time.time()
    
    def update(self, game_map):
        now = time.time()
        if now - self.last_move_time < ENEMY_MOVE_INTERVAL:
            return
        
        self.last_move_time = now
        
        if self.patrol_points:
            target_x, target_y = self.patrol_points[self.current_target]
            
            dx = 0 if self.x == target_x else (1 if target_x > self.x else -1)
            dy = 0 if self.y == target_y else (1 if target_y > self.y else -1)
            
            if dx != 0 and game_map.is_walkable(self.x + dx, self.y):
                self.x += dx
            elif dy != 0 and game_map.is_walkable(self.x, self.y + dy):
                self.y += dy
            
            if self.x == target_x and self.y == target_y:
                self.current_target = (self.current_target + 1) % len(self.patrol_points)


class GameMap:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.tiles = [[TILE_FLOOR for _ in range(self.width)] for _ in range(self.height)]
        self.gems = set()
        self.generate_map()
    
    def generate_map(self):
        # Border walls
        for x in range(self.width):
            self.tiles[0][x] = TILE_WALL
            self.tiles[self.height - 1][x] = TILE_WALL
        for y in range(self.height):
            self.tiles[y][0] = TILE_WALL
            self.tiles[y][self.width - 1] = TILE_WALL
        
        # Interior walls
        for y in range(3, self.height - 3, 4):
            for x in range(2, self.width - 2, 3):
                if random.random() < 0.7:
                    self.tiles[y][x] = TILE_WALL
        
        # Place gems
        gem_count = 15
        placed = 0
        attempts = 0
        while placed < gem_count and attempts < 100:
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self.tiles[y][x] == TILE_FLOOR and (x, y) not in self.gems:
                if abs(x - 2) + abs(y - 2) > 3:
                    self.gems.add((x, y))
                    placed += 1
            attempts += 1
    
    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x] != TILE_WALL
        return False
    
    def collect_gem(self, x, y):
        if (x, y) in self.gems:
            self.gems.remove((x, y))
            return True
        return False


# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class CrakersGame:
    def __init__(self, parent, on_exit_callback):
        self.parent = parent
        self.on_exit_callback = on_exit_callback
        
        # Game state
        self.running = False
        self.game_over = False
        self.game_won = False
        self.score = 0
        
        # Game objects
        self.game_map = None
        self.player = None
        self.enemy = None
        self.last_dash_time = 0
        
        # UI references
        self.main_frame = None
        self.canvas = None
        self.hud_labels = {}
        
        # Input state
        self.keys_pressed = set()
        self.last_movement_direction = (0, 1)  # Default down
        
        # Setup fonts
        self.fonts = {
            'retro_title': tkFont.Font(family="Courier", size=10, weight="bold"),
            'retro_text': tkFont.Font(family="Courier", size=9, weight="bold"),
            'retro_small': tkFont.Font(family="Courier", size=8, weight="bold"),
            'retro_large': tkFont.Font(family="Courier", size=14, weight="bold"),
        }
        
        # Gamepad support
        self.init_gamepad()
        
        # Initialize game
        self.setup_ui()
        self.new_game()
    
    def init_gamepad(self):
        """Initialize pygame gamepad support"""
        try:
            pygame.init()
            pygame.joystick.init()
            
            self.joystick = None
            self.gamepad_enabled = True
            self.BTN_A = 0
            self.BTN_B = 1
            self.BTN_X = 2
            self.BTN_Y = 3
            self.BTN_START = 7
            self.last_button_state = {}
            self.last_hat = (0, 0)
            self.gamepad_polling_active = False
            
            self.ensure_gamepad()
        except Exception as e:
            print(f"Gamepad init failed: {e}")
            self.gamepad_enabled = False
    
    def ensure_gamepad(self):
        if not self.gamepad_enabled:
            return None
        
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                return self.joystick
            else:
                self.joystick = None
                return None
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to allow proper program termination
            raise
        except Exception:
            # Catch all other exceptions
            self.joystick = None
            return None
    
    def poll_gamepad(self):
        if not self.gamepad_enabled or not self.gamepad_polling_active:
            return
        
        try:
            self.parent.winfo_toplevel().winfo_exists()
        except:
            return
        
        # Check and ensure gamepad connection
        if self.joystick is None or not self.joystick.get_init():
            try:
                self.ensure_gamepad()
            except KeyboardInterrupt:
                # Stop polling and re-raise to allow proper program termination
                self.gamepad_polling_active = False
                raise
            except Exception as e:
                # Stop polling on other errors
                self.gamepad_polling_active = False
                if "bad window" not in str(e):
                    print(f"Gamepad ensure error: {e}")
                return
        
        try:
            pygame.event.pump()
            
            if self.joystick is not None:
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
                
                if just_pressed(self.BTN_A) or just_pressed(self.BTN_X):
                    self.x_button_pressed()
                
                if just_pressed(self.BTN_B) or just_pressed(self.BTN_Y):
                    self.y_button_pressed()
                
                if just_pressed(self.BTN_START):
                    self.start_action()
                
                try:
                    hat = self.joystick.get_hat(0)
                except:
                    hat = (0, 0)
                
                if hat != self.last_hat:
                    if hat == (0, 1):
                        self.dpad_pressed("UP")
                    elif hat == (0, -1):
                        self.dpad_pressed("DOWN")
                    elif hat == (-1, 0):
                        self.dpad_pressed("LEFT")
                    elif hat == (1, 0):
                        self.dpad_pressed("RIGHT")
                    self.last_hat = hat
        except Exception as e:
            if "bad window" not in str(e):
                print(f"Gamepad poll error: {e}")
        
        try:
            self.parent.winfo_toplevel().after(30, self.poll_gamepad)
        except:
            pass
    
    def setup_ui(self):
        """Setup game UI inside hub's screen frame"""
        # Create main game frame inside hub's screen (parent is now the screen frame)
        # Only create once - reuse on subsequent calls
        if not hasattr(self, 'game_frame') or not self.game_frame.winfo_exists():
            self.game_frame = tk.Frame(self.parent, bg=COLOR_SCREEN_GREEN)
            self.game_frame.pack(fill='both', expand=True)
        
        # Clear any previous content
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Setup keyboard bindings to root window
        root_window = self.parent.winfo_toplevel()
        root_window.focus_set()
        root_window.bind('<Key>', self.on_key_press)
        root_window.bind('<Button-1>', lambda e: root_window.focus_set())
        
        # HUD
        hud_frame = tk.Frame(self.game_frame, bg=COLOR_SCREEN_DARK, height=30)
        hud_frame.pack(fill='x', padx=2, pady=2)
        hud_frame.pack_propagate(False)
        
        self.hud_labels['score'] = tk.Label(hud_frame, text="SCORE: 0",
                                           font=self.fonts['retro_small'],
                                           fg=COLOR_SCREEN_GREEN, bg=COLOR_SCREEN_DARK, anchor='w')
        self.hud_labels['score'].pack(side='left', padx=5)
        
        self.hud_labels['lives'] = tk.Label(hud_frame, text="♥♥♥",
                                           font=self.fonts['retro_small'],
                                           fg=COLOR_SCREEN_GREEN, bg=COLOR_SCREEN_DARK)
        self.hud_labels['lives'].pack(side='left', padx=10)
        
        self.hud_labels['dash'] = tk.Label(hud_frame, text="DASH: RDY",
                                          font=self.fonts['retro_small'],
                                          fg=COLOR_SCREEN_GREEN, bg=COLOR_SCREEN_DARK, anchor='e')
        self.hud_labels['dash'].pack(side='right', padx=5)
        
        # Canvas
        self.canvas = tk.Canvas(self.game_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                               bg=COLOR_SCREEN_GREEN, highlightthickness=0)
        self.canvas.pack(padx=2, pady=2)
        
        # Key bindings
        root_window.bind('<KeyPress>', self.on_key_press)
        root_window.bind('<KeyRelease>', self.on_key_release)
        root_window.bind('<Escape>', lambda e: self.exit_to_hub())
    
    def dpad_pressed(self, direction):
        """Handle D-Pad"""
        if self.game_over or self.game_won:
            return
        
        dx, dy = 0, 0
        if direction == "UP":
            dy = -1
        elif direction == "DOWN":
            dy = 1
        elif direction == "LEFT":
            dx = -1
        elif direction == "RIGHT":
            dx = 1
        
        if dx != 0 or dy != 0:
            self.last_movement_direction = (dx, dy)
        
        if self.player and self.player.move(dx, dy, self.game_map):
            if self.game_map.collect_gem(self.player.x, self.player.y):
                self.score += 10
    
    def x_button_pressed(self):
        """Handle X button (Dash)"""
        if self.game_over or self.game_won:
            return
        
        now = time.time()
        if now - self.last_dash_time >= DASH_COOLDOWN and self.player:
            dx, dy = self.last_movement_direction
            if dx != 0 or dy != 0:
                self.player.dash(dx, dy, self.game_map)
                self.last_dash_time = now
    
    def y_button_pressed(self):
        """Handle Y button (Exit)"""
        self.exit_to_hub()
    
    def select_action(self):
        """Handle SELECT button"""
        # Could be used for pause or options
        pass
    
    def start_action(self):
        """Handle START button"""
        if self.game_over or self.game_won:
            self.restart_game()
    
    def new_game(self):
        """Start new game"""
        self.running = True
        self.game_over = False
        self.game_won = False
        self.score = 0
        
        self.game_map = GameMap()
        self.player = Player(2, 2)
        
        patrol_points = [(GRID_WIDTH - 3, 2), (GRID_WIDTH - 3, GRID_HEIGHT - 3),
                        (2, GRID_HEIGHT - 3), (2, 2)]
        self.enemy = Enemy(GRID_WIDTH - 3, 2, patrol_points)
        
        self.last_dash_time = 0
        self.keys_pressed.clear()
        self.last_movement_direction = (0, 1)
        
        self.update_hud()
        
        if self.gamepad_enabled:
            self.gamepad_polling_active = True
            self.parent.winfo_toplevel().after(100, self.poll_gamepad)
        
        self.game_loop()
    
    def game_loop(self):
        """Main game loop"""
        if not self.running:
            return

        # Stop if UI is gone (e.g., hub switched screens)
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            self.running = False
            self.gamepad_polling_active = False
            return
        
        if not self.game_over and not self.game_won:
            self.handle_input()
            self.update_game()
            self.check_conditions()
            self.render()
            self.update_hud()
        
        self.parent.winfo_toplevel().after(GAME_TICK, self.game_loop)
    
    def handle_input(self):
        """Handle player input"""
        dx, dy = 0, 0
        
        if 'w' in self.keys_pressed or 'Up' in self.keys_pressed:
            dy = -1
        elif 's' in self.keys_pressed or 'Down' in self.keys_pressed:
            dy = 1
        
        if 'a' in self.keys_pressed or 'Left' in self.keys_pressed:
            dx = -1
        elif 'd' in self.keys_pressed or 'Right' in self.keys_pressed:
            dx = 1
        
        if dx != 0 or dy != 0:
            self.last_movement_direction = (dx, dy)
            if self.player.move(dx, dy, self.game_map):
                if self.game_map.collect_gem(self.player.x, self.player.y):
                    self.score += 10
        
        if 'space' in self.keys_pressed:
            now = time.time()
            if now - self.last_dash_time >= DASH_COOLDOWN:
                dx, dy = self.last_movement_direction
                if dx != 0 or dy != 0:
                    self.player.dash(dx, dy, self.game_map)
                    self.last_dash_time = now
                    self.keys_pressed.discard('space')
    
    def update_game(self):
        """Update game state"""
        if self.enemy:
            self.enemy.update(self.game_map)
            
            if self.player.x == self.enemy.x and self.player.y == self.enemy.y:
                self.player.take_hit()
    
    def check_conditions(self):
        """Check win/lose"""
        if self.player.lives <= 0:
            self.game_over = True
            self.show_game_over()
        
        if len(self.game_map.gems) == 0 and not self.game_won:
            self.game_won = True
            self.show_victory()
    
    def render(self):
        """Render game"""
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            self.running = False
            self.gamepad_polling_active = False
            return
        self.canvas.delete('all')
        
        # Draw map
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                
                self.canvas.create_rectangle(px, py, px + TILE_SIZE, py + TILE_SIZE,
                                            fill=COLOR_SCREEN_GREEN, outline='')
                
                if self.game_map.tiles[y][x] == TILE_WALL:
                    self.canvas.create_rectangle(px, py, px + TILE_SIZE, py + TILE_SIZE,
                                                fill=COLOR_SCREEN_DARK, outline=COLOR_DARK_GREEN)
        
        # Draw gems
        for cx, cy in self.game_map.gems:
            px = cx * TILE_SIZE + TILE_SIZE // 2
            py = cy * TILE_SIZE + TILE_SIZE // 2
            size = 4
            self.canvas.create_rectangle(px - size, py - size, px + size, py + size,
                                        fill=COLOR_SCREEN_GREEN, outline=COLOR_DARK_GREEN)
        
        # Draw enemy
        if self.enemy:
            ex = self.enemy.x * TILE_SIZE + 2
            ey = self.enemy.y * TILE_SIZE + 2
            
            self.canvas.create_rectangle(ex, ey, ex + TILE_SIZE - 4, ey + TILE_SIZE - 4,
                                        fill='#ff0000', outline=COLOR_SCREEN_DARK, width=2)
            
            eye_size = 2
            self.canvas.create_oval(ex + 3, ey + 4, ex + 3 + eye_size, ey + 4 + eye_size,
                                   fill=COLOR_SCREEN_GREEN, outline='')
            self.canvas.create_oval(ex + 8, ey + 4, ex + 8 + eye_size, ey + 4 + eye_size,
                                   fill=COLOR_SCREEN_GREEN, outline='')
        
        # Draw player
        px = self.player.x * TILE_SIZE + 2
        py = self.player.y * TILE_SIZE + 2
        
        if not self.player.is_invincible() or int(time.time() * 10) % 2 == 0:
            player_color = COLOR_SCREEN_GREEN if self.player.is_invincible() else COLOR_SCREEN_GREEN
            
            self.canvas.create_oval(px, py, px + TILE_SIZE - 4, py + TILE_SIZE - 4,
                                   fill=player_color, outline=COLOR_SCREEN_DARK, width=2)
            
            eye_y = py + 4
            self.canvas.create_oval(px + 3, eye_y, px + 5, eye_y + 2,
                                   fill=COLOR_SCREEN_DARK, outline='')
            self.canvas.create_oval(px + 8, eye_y, px + 10, eye_y + 2,
                                   fill=COLOR_SCREEN_DARK, outline='')
    
    def update_hud(self):
        """Update HUD"""
        self.hud_labels['score'].config(text=f"SCORE: {self.score}")
        
        hearts = '♥' * self.player.lives + '♡' * (PLAYER_LIVES - self.player.lives)
        self.hud_labels['lives'].config(text=hearts)
        
        now = time.time()
        cooldown = DASH_COOLDOWN - (now - self.last_dash_time)
        if cooldown <= 0:
            self.hud_labels['dash'].config(text="DASH: RDY", fg=COLOR_SCREEN_GREEN)
        else:
            self.hud_labels['dash'].config(text=f"DASH: {cooldown:.1f}s", fg=COLOR_DARK_GREEN)
    
    def show_victory(self):
        """Show victory screen"""
        self.running = False
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            self.gamepad_polling_active = False
            return
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
                                     fill=COLOR_DARK_GREEN, outline='')
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 40,
                               text="VICTORY!", font=self.fonts['retro_large'],
                               fill=COLOR_SCREEN_GREEN)
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                               text=f"All gems collected!",
                               font=self.fonts['retro_text'], fill=COLOR_SCREEN_GREEN)
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 30,
                               text=f"Final Score: {self.score}",
                               font=self.fonts['retro_text'], fill=COLOR_SCREEN_GREEN)
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 60,
                               text="Press R to restart",
                               font=self.fonts['retro_small'], fill=COLOR_SCREEN_GREEN)
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 80,
                               text="Press ESC to exit",
                               font=self.fonts['retro_small'], fill=COLOR_SCREEN_GREEN)
        
        self.parent.winfo_toplevel().bind('<r>', lambda e: self.restart_game())
    
    def show_game_over(self):
        """Show game over screen"""
        self.running = False
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            self.gamepad_polling_active = False
            return
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
                                     fill=COLOR_SCREEN_DARK, outline='')
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 40,
                               text="GAME OVER", font=self.fonts['retro_large'],
                               fill='#ff0000')
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                               text=f"Score: {self.score}",
                               font=self.fonts['retro_text'], fill=COLOR_SCREEN_GREEN)
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 40,
                               text="Press R to restart",
                               font=self.fonts['retro_small'], fill=COLOR_SCREEN_GREEN)
        
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 60,
                               text="Press ESC to exit",
                               font=self.fonts['retro_small'], fill=COLOR_SCREEN_GREEN)
        
        self.parent.winfo_toplevel().bind('<r>', lambda e: self.restart_game())
    
    def restart_game(self):
        """Restart game"""
        self.new_game()
    
    def on_key_press(self, event):
        """Handle key press"""
        key = event.keysym.lower()
        self.keys_pressed.add(key)
    
    def on_key_release(self, event):
        """Handle key release"""
        key = event.keysym.lower()
        self.keys_pressed.discard(key)
    
    def exit_to_hub(self):
        """Exit to hub"""
        self.running = False
        self.gamepad_polling_active = False
        
        root_window = self.parent.winfo_toplevel()
        root_window.unbind('<KeyPress>')
        root_window.unbind('<KeyRelease>')
        root_window.unbind('<Escape>')
        root_window.unbind('<r>')
        
        # Clear the game frame (don't destroy it) and exit
        self.clear_screen()
        self.on_exit_callback()
    
    def show(self):
        """Show game again (reuse instance)"""
        self.gamepad_polling_active = False
        self.last_button_state = {}
        self.last_hat = (0, 0)
        self.setup_ui()
        self.new_game()


def main():
    """Standalone test"""
    root = tk.Tk()
    root.title("Crakers Quest - Test")
    
    # Create a frame for embedding
    screen_frame = tk.Frame(root, bg=COLOR_SCREEN_GREEN)
    screen_frame.pack(fill='both', expand=True)
    
    def return_to_menu():
        print("Returning to menu...")
        root.quit()
    
    game = CrakersGame(screen_frame, return_to_menu)
    root.mainloop()


if __name__ == "__main__":
    main()
