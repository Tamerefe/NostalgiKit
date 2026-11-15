"""
Galaxy War Pat - Retro Space Shooter
Original space shooter with unique pixel art enemies.

Copyright (c) 2026 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import random
import time
import tkinter as tk

import nostalgik_ui as ui

FRAME_MS = 50  # ~20 FPS


class GalaxyWarPat(ui.NostalgiKitGame):
    TITLE = "GALAXY WAR PAT"

    # Game configuration
    canvas_width = ui.SCREEN_WIDTH
    canvas_height = ui.BODY_HEIGHT
    player_speed = 8
    bullet_speed = 14
    enemy_speed = 4
    enemy_bullet_speed = 7
    enemy_drop_distance = 14
    shot_cooldown = 0.3
    enemy_shot_cooldown = 1.2
    base_enemy_interval = 0.5

    def on_show(self):
        self.canvas = tk.Canvas(self.body, width=self.canvas_width, height=self.canvas_height,
                                bg=ui.SCREEN_BG, highlightthickness=0)
        self.canvas.pack(expand=True)
        self.state = "title"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.move_left = False
        self.move_right = False
        self.show_start_screen()

    def on_exit(self):
        self.state = "title"

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------
    def update_hud(self):
        self.set_status(f"{self.score:04d}  W{self.level}  " + "♥" * self.lives)

    def show_start_screen(self):
        self.state = "title"
        self.update_hud()
        self.set_hint(ui.hint(("X", "START"), ("Y", "EXIT")))
        c = self.canvas
        c.delete('all')
        mid = self.canvas_width // 2
        c.create_text(mid, 50, text="GALAXY WAR PAT", font=self.fonts['large'], fill=ui.SCREEN_DARK)
        c.create_text(mid, 72, text="DEFEND THE GALAXY!", font=self.fonts['small'], fill=ui.SCREEN_MID)
        # Little scene: starfield, a ship firing at a lone alien
        stars = random.Random(7)
        for _ in range(40):
            sx, sy = stars.randrange(8, self.canvas_width - 8), stars.randrange(90, 220)
            c.create_rectangle(sx, sy, sx + 1, sy + 1, fill=ui.SCREEN_MID, outline='')
        self.draw_custom_enemy(mid + 30, 118, 2)
        for y in range(136, 182, 12):
            c.create_rectangle(mid - 1, y, mid + 2, y + 6, fill=ui.SCREEN_DARK, outline='')
        self.draw_player_ship(mid, 195)
        c.create_text(mid, 240, text="< > MOVE    X FIRE", font=self.fonts['small'], fill=ui.SCREEN_DARK)
        c.create_text(mid, 258, text="Y / START  PAUSE", font=self.fonts['small'], fill=ui.SCREEN_DARK)

    def show_game_over(self, message):
        self.state = "over"
        self.cancel('loop')
        self.set_hint(ui.hint(("X", "RETRY"), ("Y", "EXIT")))
        self.draw_game()
        ui.draw_overlay(self.canvas, message,
                        [f"SCORE {self.score}", f"WAVES REACHED {self.level}"],
                        ui.hint(("X", "RETRY"), ("Y", "EXIT")))

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------
    def start_game(self):
        self.state = "playing"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.bullets = []
        self.enemy_bullets = []
        self.particles = []
        self.player = {'x': self.canvas_width // 2, 'y': self.canvas_height - 24, 'width': 26, 'height': 20}
        self.last_shot_time = 0
        self.last_enemy_shot_time = time.time()
        self.create_enemy_wave()
        self.set_hint(ui.hint(("<>", "MOVE"), ("X", "FIRE"), ("Y", "PAUSE")))
        self.update_hud()
        self.schedule('loop', FRAME_MS, self.game_loop)

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "paused"
            self.cancel('loop')
            self.draw_game()
            ui.draw_overlay(self.canvas, "PAUSED", [], ui.hint(("START", "RESUME"), ("Y", "EXIT")))
        elif self.state == "paused":
            self.state = "playing"
            self.schedule('loop', FRAME_MS, self.game_loop)

    def create_enemy_wave(self):
        self.enemies = []
        rows = min(5, 3 + (self.level - 1) // 2)
        cols = 7
        spacing_x, spacing_y = 36, 26
        start_x = (self.canvas_width - (cols - 1) * spacing_x) // 2
        for row in range(rows):
            for col in range(cols):
                self.enemies.append({
                    'x': start_x + col * spacing_x,
                    'y': 24 + row * spacing_y,
                    'width': 24, 'height': 18,
                    'type': (row % 3) + 1,
                    'alive': True,
                })
        self.enemy_direction = 1
        self.enemy_move_interval = max(0.15, self.base_enemy_interval * (0.9 ** (self.level - 1)))
        self.last_enemy_move_time = time.time()

    def game_loop(self):
        if self.state != "playing":
            return
        self.move_player()
        self.move_enemies()
        self.update_bullets()
        self.update_particles()
        self.check_collisions()
        if self.state != "playing":
            return  # game over screen is already drawn
        self.check_wave_complete()
        if random.random() < 0.05:
            self.enemy_shoot()
        self.update_hud()
        self.draw_game()
        self.schedule('loop', FRAME_MS, self.game_loop)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def on_dpad(self, direction, pressed=True):
        if direction == "LEFT":
            self.move_left = pressed
        elif direction == "RIGHT":
            self.move_right = pressed

    def on_button(self, button):
        if self.state == "playing":
            if button == "X":
                self.shoot()
            elif button in ("START", "Y"):
                self.toggle_pause()
        elif self.state == "paused":
            if button in ("START", "X"):
                self.toggle_pause()
            elif button == "Y":
                self.exit_to_hub()
        else:  # title / over
            if button in ("X", "START"):
                self.start_game()
            elif button == "Y":
                self.exit_to_hub()

    # Kept for older callers
    def set_move_left(self, value):
        self.move_left = value

    def set_move_right(self, value):
        self.move_right = value

    # ------------------------------------------------------------------
    # Mechanics
    # ------------------------------------------------------------------
    def shoot(self):
        now = time.time()
        if self.state == "playing" and now - self.last_shot_time >= self.shot_cooldown:
            self.bullets.append({'x': self.player['x'], 'y': self.player['y'] - 14, 'width': 3, 'height': 9})
            self.last_shot_time = now

    def enemy_shoot(self):
        now = time.time()
        if now - self.last_enemy_shot_time < self.enemy_shot_cooldown:
            return
        # Only the lowest enemy in each column can shoot
        lowest = {}
        for e in self.enemies:
            if e['alive'] and (e['x'] not in lowest or e['y'] > lowest[e['x']]['y']):
                lowest[e['x']] = e
        if lowest:
            shooter = random.choice(list(lowest.values()))
            self.enemy_bullets.append({'x': shooter['x'], 'y': shooter['y'] + 12, 'width': 4, 'height': 8})
            self.last_enemy_shot_time = now

    def move_player(self):
        half = self.player['width'] // 2 + 2
        if self.move_left and not self.move_right:
            self.player['x'] = max(half, self.player['x'] - self.player_speed)
        elif self.move_right and not self.move_left:
            self.player['x'] = min(self.canvas_width - half, self.player['x'] + self.player_speed)

    def move_enemies(self):
        now = time.time()
        if now - self.last_enemy_move_time < self.enemy_move_interval:
            return
        self.last_enemy_move_time = now

        alive = [e for e in self.enemies if e['alive']]
        step = self.enemy_speed * self.enemy_direction
        hit_edge = any(e['x'] - e['width'] // 2 + step < 2 or e['x'] + e['width'] // 2 + step > self.canvas_width - 2
                       for e in alive)
        if hit_edge:
            self.enemy_direction *= -1
            for e in alive:
                e['y'] += self.enemy_drop_distance
            self.enemy_move_interval = max(0.08, self.enemy_move_interval * 0.92)
        else:
            for e in alive:
                e['x'] += step

    def update_bullets(self):
        for b in self.bullets[:]:
            b['y'] -= self.bullet_speed
            if b['y'] < 0:
                self.bullets.remove(b)
        for b in self.enemy_bullets[:]:
            b['y'] += self.enemy_bullet_speed
            if b['y'] > self.canvas_height:
                self.enemy_bullets.remove(b)

    def update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    @staticmethod
    def check_collision(a, b):
        return (abs(a['x'] - b['x']) * 2 < a['width'] + b['width'] and
                abs(a['y'] - b['y']) * 2 < a['height'] + b['height'])

    def check_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies:
                if enemy['alive'] and self.check_collision(bullet, enemy):
                    enemy['alive'] = False
                    self.bullets.remove(bullet)
                    self.score += 10 * enemy['type']
                    self.create_explosion(enemy['x'], enemy['y'])
                    break

        for bullet in self.enemy_bullets[:]:
            if self.check_collision(bullet, self.player):
                self.enemy_bullets.remove(bullet)
                self.player_hit()
                if self.state != "playing":
                    return

        for enemy in self.enemies:
            if enemy['alive'] and enemy['y'] + enemy['height'] // 2 >= self.player['y'] - self.player['height'] // 2:
                self.show_game_over("INVADED!")
                return

    def player_hit(self):
        self.lives -= 1
        self.create_explosion(self.player['x'], self.player['y'])
        self.update_hud()
        if self.lives <= 0:
            self.show_game_over("GAME OVER")
        else:
            self.enemy_bullets.clear()  # short breather after a hit

    def create_explosion(self, x, y):
        for _ in range(8):
            self.particles.append({'x': x, 'y': y, 'dx': random.uniform(-3, 3),
                                   'dy': random.uniform(-3, 3), 'life': 10})

    def check_wave_complete(self):
        if all(not e['alive'] for e in self.enemies):
            self.level += 1
            self.bullets.clear()
            self.enemy_bullets.clear()
            self.create_enemy_wave()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw_game(self):
        c = self.canvas
        c.delete('all')
        # Ground line
        c.create_line(0, self.canvas_height - 6, self.canvas_width, self.canvas_height - 6, fill=ui.SCREEN_MID)

        if self.lives > 0:
            self.draw_player_ship(self.player['x'], self.player['y'])
        for e in self.enemies:
            if e['alive']:
                self.draw_custom_enemy(e['x'], e['y'], e['type'])
        for b in self.bullets:
            c.create_rectangle(b['x'] - 1, b['y'] - 4, b['x'] + 2, b['y'] + 5, fill=ui.SCREEN_DARK, outline='')
        for b in self.enemy_bullets:
            c.create_rectangle(b['x'] - 2, b['y'] - 4, b['x'] + 2, b['y'] + 4, fill=ui.SCREEN_MID,
                               outline=ui.SCREEN_DARK)
        for p in self.particles:
            c.create_rectangle(p['x'] - 2, p['y'] - 2, p['x'] + 2, p['y'] + 2, fill=ui.SCREEN_MID, outline='')

    def draw_player_ship(self, x, y):
        c = self.canvas
        c.create_polygon(x, y - 10, x - 12, y + 8, x + 12, y + 8, fill=ui.SCREEN_DARK, outline=ui.SCREEN_DARK)
        c.create_rectangle(x - 15, y + 1, x - 10, y + 8, fill=ui.SCREEN_DARK, outline='')
        c.create_rectangle(x + 10, y + 1, x + 15, y + 8, fill=ui.SCREEN_DARK, outline='')
        c.create_oval(x - 3, y - 2, x + 3, y + 4, fill=ui.SCREEN_LIGHT, outline='')
        c.create_rectangle(x - 6, y + 8, x - 3, y + 11, fill=ui.SCREEN_MID, outline='')
        c.create_rectangle(x + 3, y + 8, x + 6, y + 11, fill=ui.SCREEN_MID, outline='')

    def draw_custom_enemy(self, x, y, enemy_type):
        c = self.canvas
        ink, eye = ui.SCREEN_DARK, ui.SCREEN_LIGHT
        if enemy_type == 1:  # Jelly
            c.create_oval(x - 10, y - 8, x + 10, y + 5, fill=ink, outline='')
            c.create_oval(x - 6, y - 4, x - 3, y - 1, fill=eye, outline='')
            c.create_oval(x + 3, y - 4, x + 6, y - 1, fill=eye, outline='')
            for i in range(-8, 9, 4):
                c.create_rectangle(x + i - 1, y + 5, x + i + 1, y + 9, fill=ink, outline='')
        elif enemy_type == 2:  # Prism
            c.create_polygon(x, y - 9, x - 11, y, x, y + 9, x + 11, y, fill=ui.SCREEN_MID, outline=ink, width=2)
            c.create_rectangle(x - 3, y - 3, x + 3, y + 3, fill=ink, outline='')
        else:  # Beetle
            c.create_rectangle(x - 10, y - 5, x + 10, y + 5, fill=ink, outline='')
            c.create_rectangle(x - 7, y - 9, x - 5, y - 5, fill=ink, outline='')
            c.create_rectangle(x + 5, y - 9, x + 7, y - 5, fill=ink, outline='')
            c.create_rectangle(x - 5, y - 2, x - 2, y + 1, fill=eye, outline='')
            c.create_rectangle(x + 2, y - 2, x + 5, y + 1, fill=eye, outline='')
            c.create_rectangle(x - 13, y, x - 10, y + 6, fill=ink, outline='')
            c.create_rectangle(x + 10, y, x + 13, y + 6, fill=ink, outline='')


if __name__ == "__main__":
    ui.run_standalone(GalaxyWarPat, "Galaxy War Pat")
