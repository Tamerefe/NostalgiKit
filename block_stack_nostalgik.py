"""
NostalgiKit Block Stack (falling blocks puzzle)

Copyright (c) 2026 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import random
import tkinter as tk

import nostalgik_ui as ui

COLS = 10
ROWS = 16
BLOCK = 18

REPEAT_DELAY_MS = 170   # hold time before left/right starts repeating
REPEAT_RATE_MS = 60
SOFT_DROP_MS = 50

TETROMINOES = {
    "I": [[(0, 1), (1, 1), (2, 1), (3, 1)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
    "O": [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    "T": [[(1, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 2)], [(1, 0), (0, 1), (1, 1), (1, 2)]],
    "L": [[(2, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)], [(0, 0), (1, 0), (1, 1), (1, 2)]],
    "J": [[(0, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)], [(1, 0), (1, 1), (0, 2), (1, 2)]],
    "S": [[(1, 0), (2, 0), (0, 1), (1, 1)], [(1, 0), (1, 1), (2, 1), (2, 2)]],
    "Z": [[(0, 0), (1, 0), (1, 1), (2, 1)], [(2, 0), (1, 1), (2, 1), (1, 2)]],
}

# Monochrome block styles: (fill, inner mark or None)
STYLES = {
    "I": (ui.SCREEN_DARK, None),
    "O": (ui.SCREEN_MID, ui.SCREEN_DARK),
    "T": (ui.SCREEN_LIGHT, ui.SCREEN_DARK),
    "L": (ui.SCREEN_DARK, ui.SCREEN_LIGHT),
    "J": (ui.SCREEN_MID, None),
    "S": (ui.SCREEN_LIGHT, None),
    "Z": (ui.SCREEN_DARK, ui.SCREEN_MID),
}

LINE_SCORES = [0, 40, 100, 300, 800]


class NostalgiKitBlockStack(ui.NostalgiKitGame):
    TITLE = "BLOCK STACK"

    canvas_width = COLS * BLOCK
    canvas_height = ROWS * BLOCK

    def on_show(self):
        row = tk.Frame(self.body, bg=ui.SCREEN_BG)
        row.pack(expand=True)

        self.canvas = tk.Canvas(row, width=self.canvas_width, height=self.canvas_height,
                                bg=ui.SCREEN_BG, highlightthickness=2, highlightbackground=ui.SCREEN_DARK)
        self.canvas.pack(side='left', padx=(0, 12))

        side = tk.Frame(row, bg=ui.SCREEN_BG)
        side.pack(side='left', fill='y')
        ui.label(side, "NEXT", size='small').pack(anchor='w')
        self.preview = tk.Canvas(side, width=4 * 14 + 8, height=3 * 14 + 8, bg=ui.SCREEN_BG,
                                 highlightthickness=1, highlightbackground=ui.SCREEN_DARK)
        self.preview.pack(anchor='w', pady=(2, 14))
        self.stat_labels = {}
        for key in ("SCORE", "LINES", "LEVEL"):
            ui.label(side, key, size='tiny', anchor='w').pack(anchor='w')
            lbl = ui.label(side, "0", size='title', anchor='w')
            lbl.pack(anchor='w', pady=(0, 8))
            self.stat_labels[key] = lbl

        self.held = set()
        self.show_title_screen()

    def on_exit(self):
        self.state = "title"
        self.held = set()

    # ------------------------------------------------------------------
    # Screens / lifecycle
    # ------------------------------------------------------------------
    def show_title_screen(self):
        self.state = "title"
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.current_piece = None
        self.next_piece = None
        self.score = self.lines = 0
        self.level = 1
        self.update_hud()
        self.set_hint(ui.hint(("X", "START"), ("Y", "EXIT")))
        self.draw()
        ui.draw_overlay(self.canvas, "READY?", ["<> MOVE", "X  ROTATE",
                                                 "▼  SOFT DROP", "▲  HARD DROP"], "X:START")

    def new_game(self):
        self.state = "playing"
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.score = self.lines = 0
        self.level = 1
        self.next_piece = self.random_piece()
        self.set_hint(ui.hint(("X", "ROTATE"), ("▲", "DROP"), ("Y", "PAUSE")))
        self.spawn_piece()
        self.update_hud()
        self.schedule('gravity', self.drop_delay(), self.gravity)

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "paused"
            self.cancel('gravity')
            self.update_hud()
            ui.draw_overlay(self.canvas, "PAUSED", [], ui.hint(("START", "RESUME"), ("Y", "EXIT")))
        elif self.state == "paused":
            self.state = "playing"
            self.update_hud()
            self.draw()
            self.schedule('gravity', self.drop_delay(), self.gravity)

    def trigger_game_over(self):
        self.state = "over"
        for name in ('gravity', 'repeat_LEFT', 'repeat_RIGHT', 'repeat_DOWN'):
            self.cancel(name)
        self.update_hud()
        self.set_hint(ui.hint(("X", "RETRY"), ("Y", "EXIT")))
        self.draw()
        ui.draw_overlay(self.canvas, "GAME OVER", [f"SCORE {self.score}", f"LINES {self.lines}"], "X:RETRY")

    def drop_delay(self):
        return max(120, 700 - (self.level - 1) * 50)

    def gravity(self):
        if self.state != "playing":
            return
        self.soft_drop()
        if self.state == "playing":
            self.schedule('gravity', self.drop_delay(), self.gravity)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def on_dpad(self, direction, pressed=True):
        if not pressed:
            self.held.discard(direction)
            self.cancel(f'repeat_{direction}')
            return
        if direction in self.held:
            return  # OS key auto-repeat; we repeat on our own timer
        self.held.add(direction)
        if self.state != "playing":
            return
        if direction == "UP":
            self.hard_drop()
        else:
            self._repeat_action(direction, first=True)

    def _repeat_action(self, direction, first=False):
        if self.state != "playing" or direction not in self.held:
            return
        if direction == "LEFT":
            self.move_piece(-1, 0)
        elif direction == "RIGHT":
            self.move_piece(1, 0)
        elif direction == "DOWN":
            if self.soft_drop():
                self.score += 1
                self.update_hud()
        if direction == "DOWN":
            delay = SOFT_DROP_MS
        else:
            delay = REPEAT_DELAY_MS if first else REPEAT_RATE_MS
        self.schedule(f'repeat_{direction}', delay, lambda: self._repeat_action(direction))

    def on_button(self, button):
        if self.state == "playing":
            if button == "X":
                self.rotate_piece()
            elif button in ("START", "Y"):
                self.toggle_pause()
        elif self.state == "paused":
            if button in ("START", "X"):
                self.toggle_pause()
            elif button == "Y":
                self.exit_to_hub()
        else:  # title / over
            if button in ("X", "START"):
                self.new_game()
            elif button == "Y":
                self.exit_to_hub()

    # ------------------------------------------------------------------
    # Pieces
    # ------------------------------------------------------------------
    @staticmethod
    def random_piece():
        return {"shape": random.choice(list(TETROMINOES)), "rotation": 0}

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.random_piece()
        self.current_piece["x"] = COLS // 2 - 2
        self.current_piece["y"] = 0
        if not self.can_place(self.current_piece):
            self.trigger_game_over()
            return
        self.draw()

    @staticmethod
    def piece_cells(piece, rotation=None):
        states = TETROMINOES[piece["shape"]]
        rot = piece["rotation"] if rotation is None else rotation
        return [(piece["x"] + x, piece["y"] + y) for x, y in states[rot % len(states)]]

    def can_place(self, piece, dx=0, dy=0, rotation=None):
        for x, y in self.piece_cells(piece, rotation):
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= COLS or ny >= ROWS:
                return False
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False
        return True

    def move_piece(self, dx, dy):
        if self.current_piece and self.can_place(self.current_piece, dx, dy):
            self.current_piece["x"] += dx
            self.current_piece["y"] += dy
            self.draw()
            return True
        return False

    def rotate_piece(self):
        piece = self.current_piece
        if not piece:
            return
        new_rot = (piece["rotation"] + 1) % len(TETROMINOES[piece["shape"]])
        for kick in (0, -1, 1, -2, 2):
            if self.can_place(piece, dx=kick, rotation=new_rot):
                piece["x"] += kick
                piece["rotation"] = new_rot
                self.draw()
                return

    def soft_drop(self):
        """Move down one row; lock the piece if it can't. Returns True if it moved."""
        if not self.current_piece:
            return False
        if self.move_piece(0, 1):
            return True
        self.lock_piece()
        return False

    def hard_drop(self):
        if not self.current_piece:
            return
        while self.can_place(self.current_piece, 0, 1):
            self.current_piece["y"] += 1
            self.score += 2
        self.lock_piece()
        self.update_hud()

    def lock_piece(self):
        for x, y in self.piece_cells(self.current_piece):
            if y < 0:
                self.trigger_game_over()
                return
            self.grid[y][x] = self.current_piece["shape"]
        self.current_piece = None
        self.clear_lines()
        self.spawn_piece()
        # Reset gravity so the new piece gets a full tick
        if self.state == "playing":
            self.schedule('gravity', self.drop_delay(), self.gravity)

    def clear_lines(self):
        full = [i for i, row in enumerate(self.grid) if all(cell is not None for cell in row)]
        if not full:
            return
        self.grid = [row for i, row in enumerate(self.grid) if i not in full]
        self.grid = [[None] * COLS for _ in full] + self.grid
        self.lines += len(full)
        self.score += LINE_SCORES[len(full)] * self.level
        self.level = 1 + self.lines // 10
        self.update_hud()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def update_hud(self):
        self.stat_labels["SCORE"].config(text=f"{self.score}")
        self.stat_labels["LINES"].config(text=f"{self.lines}")
        self.stat_labels["LEVEL"].config(text=f"{self.level}")
        self.set_status({"title": "READY", "playing": "PLAY", "paused": "PAUSED",
                         "over": "GAME OVER"}.get(self.state, ""))

    def draw_block(self, canvas, px, py, size, shape):
        fill, inner = STYLES[shape]
        canvas.create_rectangle(px + 1, py + 1, px + size - 1, py + size - 1,
                                fill=fill, outline=ui.SCREEN_DARK)
        if inner:
            m = size // 3
            canvas.create_rectangle(px + m, py + m, px + size - m, py + size - m, fill=inner, outline='')

    def draw(self):
        c = self.canvas
        c.delete('all')
        # Faint dot grid
        for y in range(1, ROWS):
            for x in range(1, COLS):
                c.create_rectangle(x * BLOCK, y * BLOCK, x * BLOCK + 1, y * BLOCK + 1,
                                   fill=ui.SCREEN_MID, outline='')
        for y, row in enumerate(self.grid):
            for x, shape in enumerate(row):
                if shape:
                    self.draw_block(c, x * BLOCK, y * BLOCK, BLOCK, shape)
        if self.current_piece:
            for x, y in self.piece_cells(self.current_piece):
                if y >= 0:
                    self.draw_block(c, x * BLOCK, y * BLOCK, BLOCK, self.current_piece["shape"])
        self.draw_preview()

    def draw_preview(self):
        p = self.preview
        p.delete('all')
        if not self.next_piece:
            return
        size = 14
        for x, y in TETROMINOES[self.next_piece["shape"]][0]:
            self.draw_block(p, 4 + x * size, 4 + y * size, size, self.next_piece["shape"])


BlockStackGame = NostalgiKitBlockStack

if __name__ == "__main__":
    ui.run_standalone(BlockStackGame, "Block Stack")
