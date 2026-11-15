"""
NostalgiKit Crakers Quest
Top-down grid adventure: collect every gem while a guard hunts you.

Copyright (c) 2026 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import random
import time
import tkinter as tk
from heapq import heappush, heappop

import nostalgik_ui as ui

# Grid settings
TILE_SIZE = 18
GRID_WIDTH = 18
GRID_HEIGHT = 12
CANVAS_WIDTH = GRID_WIDTH * TILE_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Game settings
PLAYER_LIVES = 3
PLAYER_MOVE_INTERVAL = 0.13   # seconds between steps while a direction is held
DASH_COOLDOWN = 3.0
DASH_DISTANCE = 2
ENEMY_MOVE_INTERVAL = 0.5
GAME_TICK = 50
GEM_COUNT = 15

TILE_FLOOR = 0
TILE_WALL = 1

DIRECTIONS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def astar_pathfind(game_map, start, goal):
    """A* pathfinding - returns list of (x, y) steps (excluding start) or None."""
    if start == goal:
        return []

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = [(heuristic(start, goal), start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        x, y = current
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            neighbor = (x + dx, y + dy)
            if not game_map.is_walkable(*neighbor):
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                heappush(open_set, (tentative_g + heuristic(neighbor, goal), neighbor))
    return None


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lives = PLAYER_LIVES
        self.invincible_until = 0
        self.last_direction = (0, 1)

    def move(self, dx, dy, game_map):
        if game_map.is_walkable(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            self.last_direction = (dx, dy)
            return True
        return False

    def is_invincible(self):
        return time.time() < self.invincible_until

    def take_hit(self):
        if self.is_invincible():
            return False
        self.lives -= 1
        self.invincible_until = time.time() + 1.5
        return True


class Enemy:
    STATE_PATROL = "patrol"
    STATE_CHASE = "chase"
    STATE_SEARCH = "search"

    def __init__(self, x, y, patrol_points):
        self.x = x
        self.y = y
        self.patrol_points = patrol_points
        self.current_target = 0
        self.last_move_time = time.time()
        self.state = self.STATE_PATROL
        self.vision_radius = 6
        self.last_seen_pos = None
        self.search_timer = 0
        self.search_duration = 3.0
        self.current_path = []

    def can_see_player(self, player, game_map):
        if abs(player.x - self.x) + abs(player.y - self.y) > self.vision_radius:
            return False
        steps = max(abs(player.x - self.x), abs(player.y - self.y))
        if steps == 0:
            return True
        for i in range(steps + 1):
            t = i / steps
            x = round(self.x + t * (player.x - self.x))
            y = round(self.y + t * (player.y - self.y))
            if not game_map.is_walkable(x, y):
                return False
        return True

    def update(self, game_map, player):
        now = time.time()
        if now - self.last_move_time < ENEMY_MOVE_INTERVAL:
            return
        self.last_move_time = now

        if self.can_see_player(player, game_map):
            if self.state != self.STATE_CHASE:
                self.state = self.STATE_CHASE
                self.current_path = []
            self.last_seen_pos = (player.x, player.y)
        elif self.state == self.STATE_CHASE:
            self.state = self.STATE_SEARCH
            self.search_timer = now
            self.current_path = []
        elif self.state == self.STATE_SEARCH and now - self.search_timer > self.search_duration:
            self.state = self.STATE_PATROL
            self.current_path = []

        if self.state == self.STATE_CHASE:
            self._chase_player(player, game_map)
        elif self.state == self.STATE_SEARCH:
            self._search_last_seen(game_map)
        else:
            self._patrol(game_map)

    def _step(self):
        if self.current_path:
            self.x, self.y = self.current_path.pop(0)

    def _chase_player(self, player, game_map):
        target = (player.x, player.y)
        pred = (player.x + player.last_direction[0], player.y + player.last_direction[1])
        if game_map.is_walkable(*pred) and pred != (self.x, self.y):
            target = pred
        if not self.current_path or self.current_path[-1] != target:
            self.current_path = astar_pathfind(game_map, (self.x, self.y), target) or []
        self._step()

    def _search_last_seen(self, game_map):
        if not self.last_seen_pos or (self.x, self.y) == self.last_seen_pos:
            self.last_seen_pos = None
            self.state = self.STATE_PATROL
            self.current_path = []
            return
        if not self.current_path:
            self.current_path = astar_pathfind(game_map, (self.x, self.y), self.last_seen_pos) or []
        if self.current_path:
            self._step()
        else:
            self.state = self.STATE_PATROL
            self.last_seen_pos = None

    def _patrol(self, game_map):
        if not self.patrol_points:
            return
        target = self.patrol_points[self.current_target]
        if (self.x, self.y) == target:
            self.current_target = (self.current_target + 1) % len(self.patrol_points)
            self.current_path = []
            return
        if not self.current_path:
            self.current_path = astar_pathfind(game_map, (self.x, self.y), target) or []
        self._step()


class GameMap:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.tiles = [[TILE_FLOOR] * self.width for _ in range(self.height)]
        self.gems = set()
        self.generate_map()

    def generate_map(self):
        for x in range(self.width):
            self.tiles[0][x] = self.tiles[self.height - 1][x] = TILE_WALL
        for y in range(self.height):
            self.tiles[y][0] = self.tiles[y][self.width - 1] = TILE_WALL

        for y in range(3, self.height - 3, 4):
            for x in range(2, self.width - 2, 3):
                if random.random() < 0.7:
                    self.tiles[y][x] = TILE_WALL

        attempts = 0
        while len(self.gems) < GEM_COUNT and attempts < 200:
            attempts += 1
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.tiles[y][x] == TILE_FLOOR and abs(x - 2) + abs(y - 2) > 3:
                self.gems.add((x, y))

    def is_walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and self.tiles[y][x] != TILE_WALL

    def collect_gem(self, x, y):
        if (x, y) in self.gems:
            self.gems.remove((x, y))
            return True
        return False


class CrakersGame(ui.NostalgiKitGame):
    TITLE = "CRAKERS QUEST"

    def on_show(self):
        self.canvas = tk.Canvas(self.body, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                bg=ui.SCREEN_BG, highlightthickness=0)
        self.canvas.pack(pady=(12, 6))
        self.info = ui.label(self.body, "", size='tiny')
        self.info.pack()
        self.dash_label = ui.label(self.body, "", size='small')
        self.dash_label.pack(pady=(8, 0))
        self.held = []          # held directions, last pressed last
        self.state = "title"
        self.score = 0
        self.player = None
        self.show_title()

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------
    def show_title(self):
        self.state = "title"
        self.set_status("")
        self.set_hint(ui.hint(("X", "START"), ("Y", "EXIT")))
        self.info.config(text="< > ▲ ▼  MOVE     X  DASH")
        self.dash_label.config(text="")
        self.game_map = GameMap()
        self.player = Player(2, 2)
        self.enemy = None
        self.draw_map()
        self.render()
        ui.draw_overlay(self.canvas, "CRAKERS QUEST",
                        ["Collect every gem.", "Don't get caught!"],
                        ui.hint(("X", "START")))

    def new_game(self):
        self.state = "playing"
        self.score = 0
        self.game_map = GameMap()
        self.player = Player(2, 2)
        patrol = [(GRID_WIDTH - 3, 2), (GRID_WIDTH - 3, GRID_HEIGHT - 3), (2, GRID_HEIGHT - 3), (2, 2)]
        self.enemy = Enemy(GRID_WIDTH - 3, 2, patrol)
        self.last_dash_time = 0
        self.last_player_move = 0
        self.set_hint(ui.hint(("X", "DASH"), ("Y", "PAUSE")))
        self.info.config(text="GUARD  ■ CHASE  ▣ SEARCH  □ PATROL")
        self.draw_map()
        self.update_hud()
        self.schedule('loop', GAME_TICK, self.game_loop)

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "paused"
            self.cancel('loop')
            ui.draw_overlay(self.canvas, "PAUSED", [], ui.hint(("START", "RESUME"), ("Y", "EXIT")))
        elif self.state == "paused":
            self.state = "playing"
            self.canvas.delete('overlay')
            self.schedule('loop', GAME_TICK, self.game_loop)

    def end_game(self, won):
        self.state = "won" if won else "over"
        self.cancel('loop')
        self.render()
        self.update_hud()
        self.set_hint(ui.hint(("X", "RETRY"), ("Y", "EXIT")))
        title = "VICTORY!" if won else "GAME OVER"
        lines = ["All gems collected!"] if won else []
        ui.draw_overlay(self.canvas, title, lines + [f"SCORE {self.score}"], ui.hint(("X", "RETRY"), ("Y", "EXIT")))

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def on_dpad(self, direction, pressed=True):
        was_held = direction in self.held
        if was_held:
            self.held.remove(direction)
        if pressed:
            self.held.append(direction)
            # Step immediately on a fresh press; key auto-repeat is paced by the loop
            if self.state == "playing" and not was_held:
                self.try_move(force=True)

    def on_button(self, button):
        if self.state == "playing":
            if button == "X":
                self.dash()
            elif button in ("START", "Y"):
                self.toggle_pause()
        elif self.state == "paused":
            if button in ("START", "X"):
                self.toggle_pause()
            elif button == "Y":
                self.exit_to_hub()
        else:  # title / won / over
            if button in ("X", "START"):
                self.new_game()
            elif button == "Y":
                self.exit_to_hub()

    def on_exit(self):
        self.state = "title"
        self.held = []

    # ------------------------------------------------------------------
    # Mechanics
    # ------------------------------------------------------------------
    def try_move(self, force=False):
        if not self.held:
            return
        now = time.time()
        if not force and now - self.last_player_move < PLAYER_MOVE_INTERVAL:
            return
        dx, dy = DIRECTIONS[self.held[-1]]
        self.last_player_move = now
        if self.player.move(dx, dy, self.game_map):
            self.after_player_step()
        else:
            self.player.last_direction = (dx, dy)  # still aim the dash

    def dash(self):
        now = time.time()
        if now - self.last_dash_time < DASH_COOLDOWN:
            return
        dx, dy = self.player.last_direction
        moved = False
        for _ in range(DASH_DISTANCE):
            if not self.player.move(dx, dy, self.game_map):
                break
            moved = True
            self.after_player_step()
            if self.state != "playing":
                return
        if moved:
            self.last_dash_time = now
            self.last_player_move = now

    def after_player_step(self):
        if self.game_map.collect_gem(self.player.x, self.player.y):
            self.score += 10
        self.check_contact()
        if self.state == "playing" and not self.game_map.gems:
            self.end_game(won=True)

    def check_contact(self):
        if self.enemy and (self.player.x, self.player.y) == (self.enemy.x, self.enemy.y):
            self.player.take_hit()
            if self.player.lives <= 0:
                self.end_game(won=False)

    def game_loop(self):
        if self.state != "playing":
            return
        self.try_move()
        if self.state == "playing":
            self.enemy.update(self.game_map, self.player)
            self.check_contact()
        if self.state == "playing":
            self.render()
            self.update_hud()
            self.schedule('loop', GAME_TICK, self.game_loop)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def update_hud(self):
        hearts = "♥" * self.player.lives + "♡" * (PLAYER_LIVES - self.player.lives)
        cooldown = DASH_COOLDOWN - (time.time() - self.last_dash_time) if self.state == "playing" else 0
        dash = "RDY" if cooldown <= 0 else f"{cooldown:.1f}"
        self.set_status(f"{self.score:03d}  ♦{len(self.game_map.gems):02d}  {hearts}")
        self.dash_label.config(text=f"DASH {dash}")

    def draw_map(self):
        """Walls never change during a round, so they are drawn once."""
        c = self.canvas
        c.delete('all')
        c.create_rectangle(0, 0, CANVAS_WIDTH - 1, CANVAS_HEIGHT - 1, outline=ui.SCREEN_DARK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.game_map.tiles[y][x] == TILE_WALL:
                    px, py = x * TILE_SIZE, y * TILE_SIZE
                    c.create_rectangle(px, py, px + TILE_SIZE, py + TILE_SIZE,
                                       fill=ui.SCREEN_DARK, outline=ui.SCREEN_MID, tags='static')

    def render(self):
        c = self.canvas
        c.delete('dyn')
        t = TILE_SIZE
        for gx, gy in self.game_map.gems:
            cx, cy = gx * t + t // 2, gy * t + t // 2
            c.create_polygon(cx, cy - 5, cx + 5, cy, cx, cy + 5, cx - 5, cy,
                             fill=ui.SCREEN_LIGHT, outline=ui.SCREEN_DARK, tags='dyn')

        if self.enemy:
            ex, ey = self.enemy.x * t + 2, self.enemy.y * t + 2
            state = self.enemy.state
            fill = {Enemy.STATE_CHASE: ui.SCREEN_DARK, Enemy.STATE_SEARCH: ui.SCREEN_MID}.get(state, ui.SCREEN_BG)
            c.create_rectangle(ex, ey, ex + t - 4, ey + t - 4, fill=fill, outline=ui.SCREEN_DARK, width=2, tags='dyn')
            eye = ui.SCREEN_LIGHT if state != Enemy.STATE_PATROL else ui.SCREEN_DARK
            c.create_rectangle(ex + 3, ey + 4, ex + 6, ey + 7, fill=eye, outline='', tags='dyn')
            c.create_rectangle(ex + t - 10, ey + 4, ex + t - 7, ey + 7, fill=eye, outline='', tags='dyn')

        if self.player and (not self.player.is_invincible() or int(time.time() * 10) % 2 == 0):
            px, py = self.player.x * t + 2, self.player.y * t + 2
            c.create_oval(px, py, px + t - 4, py + t - 4, fill=ui.SCREEN_LIGHT,
                          outline=ui.SCREEN_DARK, width=2, tags='dyn')
            c.create_rectangle(px + 4, py + 5, px + 6, py + 7, fill=ui.SCREEN_DARK, outline='', tags='dyn')
            c.create_rectangle(px + t - 10, py + 5, px + t - 8, py + 7, fill=ui.SCREEN_DARK, outline='', tags='dyn')


if __name__ == "__main__":
    ui.run_standalone(CrakersGame, "Crakers Quest")
