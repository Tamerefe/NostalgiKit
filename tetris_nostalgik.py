"""
NostalgiKit Block Stack (Tetris-inspired)
Falling tetromino puzzle in classic NostalgiKit style

Copyright (c) 2026 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk
import tkinter.font as tkFont
import random
import time
import pygame  # For gamepad support


class NostalgiKitTetris:
    def __init__(self, parent, return_callback):
        self.parent = parent
        self.return_callback = return_callback

        # Grid settings
        self.cols = 10
        self.rows = 16
        self.block = 16
        self.canvas_width = self.cols * self.block
        self.canvas_height = self.rows * self.block

        # Game timing
        self.drop_delay = 650
        self.loop_job = None

        # State
        self.grid = None
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_active = False
        self.game_over = False
        self.paused = False

        # Colors (monochrome-friendly palette)
        self.colors = {
            "nostalgik_cream": "#E8E0C7",
            "screen_green": "#9BBB59",
            "dark_green": "#8B9467",
            "screen_dark": "#374224",
            "button_gray": "#8E8E93",
            "text_dark": "#1C1C1E",
            "highlight": "#FFD23F",
        }
        self.piece_palette = ["#dcefb1", "#cde687", "#bcd971", "#a8cc61", "#8fb54c"]

        # Fonts
        self.fonts = {
            "retro_title": tkFont.Font(family="Courier", size=10, weight="bold"),
            "retro_text": tkFont.Font(family="Courier", size=9, weight="bold"),
            "retro_small": tkFont.Font(family="Courier", size=8, weight="bold"),
            "retro_tiny": tkFont.Font(family="Courier", size=7, weight="bold"),
        }

        # Pieces (rotation states)
        self.tetrominoes = {
            "I": [
                [(0, 1), (1, 1), (2, 1), (3, 1)],
                [(2, 0), (2, 1), (2, 2), (2, 3)],
            ],
            "O": [[(1, 0), (2, 0), (1, 1), (2, 1)]],
            "T": [
                [(1, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (1, 1), (2, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (1, 2)],
                [(1, 0), (0, 1), (1, 1), (1, 2)],
            ],
            "L": [
                [(0, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (2, 0), (1, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (2, 2)],
                [(1, 0), (1, 1), (0, 2), (1, 2)],
            ],
            "J": [
                [(2, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (1, 1), (1, 2), (2, 2)],
                [(0, 1), (1, 1), (2, 1), (0, 2)],
                [(0, 0), (1, 0), (1, 1), (1, 2)],
            ],
            "S": [
                [(1, 0), (2, 0), (0, 1), (1, 1)],
                [(1, 0), (1, 1), (2, 1), (2, 2)],
            ],
            "Z": [
                [(0, 0), (1, 0), (1, 1), (2, 1)],
                [(2, 0), (1, 1), (2, 1), (1, 2)],
            ],
        }

        self.bound_keys = []
        self.setup_ui()
        self.init_gamepad()
        self.show_title_screen()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        if not hasattr(self, "game_frame") or not self.game_frame.winfo_exists():
            self.game_frame = tk.Frame(self.parent, bg=self.colors["screen_green"])
            self.game_frame.pack(fill="both", expand=True)

        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # HUD
        hud = tk.Frame(self.game_frame, bg=self.colors["screen_dark"], height=32)
        hud.pack(fill="x", padx=3, pady=3)
        hud.pack_propagate(False)

        self.score_label = tk.Label(
            hud,
            text="SCORE:0000",
            font=self.fonts["retro_small"],
            fg=self.colors["highlight"],
            bg=self.colors["screen_dark"],
        )
        self.score_label.pack(side="left", padx=5)

        self.lines_label = tk.Label(
            hud,
            text="LINES:0",
            font=self.fonts["retro_small"],
            fg=self.colors["nostalgik_cream"],
            bg=self.colors["screen_dark"],
        )
        self.lines_label.pack(side="left", padx=5)

        self.level_label = tk.Label(
            hud,
            text="LVL:1",
            font=self.fonts["retro_small"],
            fg=self.colors["nostalgik_cream"],
            bg=self.colors["screen_dark"],
        )
        self.level_label.pack(side="left", padx=5)

        self.status_label = tk.Label(
            hud,
            text="READY",
            font=self.fonts["retro_small"],
            fg=self.colors["highlight"],
            bg=self.colors["screen_dark"],
        )
        self.status_label.pack(side="right", padx=5)

        body = tk.Frame(self.game_frame, bg=self.colors["screen_green"])
        body.pack(fill="both", expand=True)

        # Playfield
        self.canvas = tk.Canvas(
            body,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.colors["screen_dark"],
            highlightthickness=0,
        )
        self.canvas.pack(side="left", padx=6, pady=6)

        # Next preview
        sidebar = tk.Frame(body, bg=self.colors["screen_green"], width=80)
        sidebar.pack(side="left", fill="y", padx=4, pady=6)
        sidebar.pack_propagate(False)

        preview_title = tk.Label(
            sidebar,
            text="NEXT",
            font=self.fonts["retro_small"],
            fg=self.colors["screen_dark"],
            bg=self.colors["screen_green"],
        )
        preview_title.pack(pady=(4, 2))

        self.preview = tk.Canvas(
            sidebar,
            width=72,
            height=72,
            bg=self.colors["screen_green"],
            highlightthickness=0,
        )
        self.preview.pack()

        controls = tk.Label(
            self.game_frame,
            text="←/→ MOVE   ↑ ROTATE   ↓ SOFT DROP   SPACE HARD DROP   Y=HUB",
            font=self.fonts["retro_tiny"],
            fg=self.colors["screen_dark"],
            bg=self.colors["screen_green"],
        )
        controls.pack(side="bottom", pady=(0, 4))

        self.bind_keys()

    def bind_keys(self):
        self.unbind_keys()
        root = self.parent.winfo_toplevel()
        bindings = {
            "<Left>": lambda e: self.dpad_left(),
            "<Right>": lambda e: self.dpad_right(),
            "<Down>": lambda e: self.dpad_down(),
            "<Up>": lambda e: self.dpad_up(),
            "<space>": lambda e: self.hard_drop(),
            "<Return>": lambda e: self.start_game_from_screen(),
            "<p>": lambda e: self.toggle_pause(),
            "<Escape>": lambda e: self.exit_to_hub(),
            "<Tab>": lambda e: self.exit_to_hub(),
            "<x>": lambda e: self.x_button_action(),
            "<X>": lambda e: self.x_button_action(),
            "<y>": lambda e: self.y_button_action(),
            "<Y>": lambda e: self.y_button_action(),
        }
        for seq, handler in bindings.items():
            root.bind(seq, handler)
            self.bound_keys.append(seq)
        root.focus_set()

    def unbind_keys(self):
        if not self.bound_keys:
            return
        try:
            root = self.parent.winfo_toplevel()
        except Exception:
            return
        for seq in self.bound_keys:
            try:
                root.unbind(seq)
            except Exception:
                pass
        self.bound_keys = []

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------
    def show_title_screen(self):
        self.game_active = False
        self.game_over = False
        self.paused = False
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.canvas.delete("all")
        self.preview.delete("all")
        self.status_label.config(text="READY")
        self.score = 0
        self.lines = 0
        self.level = 1
        self.update_hud()

        mid_x = self.canvas_width // 2
        self.canvas.create_text(
            mid_x,
            110,
            text="BLOCK STACK",
            font=self.fonts["retro_title"],
            fill=self.colors["highlight"],
        )
        self.canvas.create_text(
            mid_x,
            150,
            text="PRESS START / ENTER",
            font=self.fonts["retro_text"],
            fill=self.colors["nostalgik_cream"],
        )
        self.canvas.create_text(
            mid_x,
            190,
            text="X ROTATE  SPACE HARD DROP",
            font=self.fonts["retro_tiny"],
            fill=self.colors["nostalgik_cream"],
        )

    def start_game_from_screen(self):
        if self.game_active and not self.game_over:
            return
        self.new_game()

    def new_game(self):
        self.game_active = True
        self.game_over = False
        self.paused = False
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.update_drop_speed()
        self.next_piece = self.random_piece()
        self.spawn_piece()
        self.update_hud()
        self.status_label.config(text="PLAY")
        self.start_loop()

    def start_loop(self):
        self.cancel_loop()
        self.loop_job = self.parent.after(self.drop_delay, self.game_loop)

    def cancel_loop(self):
        if self.loop_job is not None:
            try:
                self.parent.after_cancel(self.loop_job)
            except Exception:
                pass
            self.loop_job = None

    def game_loop(self):
        if not self.game_active or self.paused:
            self.start_loop()
            return
        self.soft_drop()
        self.start_loop()

    # ------------------------------------------------------------------
    # Pieces and movement
    # ------------------------------------------------------------------
    def random_piece(self):
        shape = random.choice(list(self.tetrominoes.keys()))
        color = random.choice(self.piece_palette)
        return {"shape": shape, "rotation": 0, "color": color}

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.random_piece()
        self.current_piece["x"] = self.cols // 2 - 2
        self.current_piece["y"] = 0
        if not self.can_place(self.current_piece):
            self.trigger_game_over()
            return
        self.draw()

    def piece_cells(self, piece, rotation=None):
        rot = piece["rotation"] if rotation is None else rotation
        shape_states = self.tetrominoes[piece["shape"]]
        cells = shape_states[rot % len(shape_states)]
        return [(piece["x"] + x, piece["y"] + y) for x, y in cells]

    def can_place(self, piece, dx=0, dy=0, rotation=None):
        for x, y in self.piece_cells(piece, rotation):
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= self.cols or ny >= self.rows:
                return False
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False
        return True

    def move_piece(self, dx, dy):
        if not self.current_piece:
            return False
        if self.can_place(self.current_piece, dx, dy):
            self.current_piece["x"] += dx
            self.current_piece["y"] += dy
            self.draw()
            return True
        return False

    def rotate_piece(self):
        if not self.current_piece:
            return
        new_rot = (self.current_piece["rotation"] + 1) % len(
            self.tetrominoes[self.current_piece["shape"]]
        )
        if self.can_place(self.current_piece, rotation=new_rot):
            self.current_piece["rotation"] = new_rot
        elif self.can_place(self.current_piece, dx=-1, rotation=new_rot):
            self.current_piece["x"] -= 1
            self.current_piece["rotation"] = new_rot
        elif self.can_place(self.current_piece, dx=1, rotation=new_rot):
            self.current_piece["x"] += 1
            self.current_piece["rotation"] = new_rot
        self.draw()

    def soft_drop(self):
        if not self.current_piece:
            return
        if not self.move_piece(0, 1):
            self.lock_piece()

    def hard_drop(self):
        if not self.current_piece:
            return
        while self.move_piece(0, 1):
            self.score += 1
        self.lock_piece()
        self.update_hud()

    def lock_piece(self):
        if not self.current_piece:
            return
        for x, y in self.piece_cells(self.current_piece):
            if y < 0:
                self.trigger_game_over()
                return
            self.grid[y][x] = self.current_piece["color"]
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        full_rows = [i for i, row in enumerate(self.grid) if all(cell is not None for cell in row)]
        if not full_rows:
            return
        for idx in reversed(full_rows):
            del self.grid[idx]
        for _ in full_rows:
            self.grid.insert(0, [None for _ in range(self.cols)])
        cleared = len(full_rows)
        self.lines += cleared
        self.score += [0, 40, 100, 300, 800][cleared] * max(1, self.level)
        self.level = 1 + self.lines // 10
        self.update_drop_speed()
        self.update_hud()

    def update_drop_speed(self):
        self.drop_delay = max(140, 700 - (self.level - 1) * 45)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw(self):
        self.canvas.delete("all")
        # Settled blocks
        for y in range(self.rows):
            for x in range(self.cols):
                color = self.grid[y][x]
                if color:
                    self.draw_block(x, y, color)
        # Active piece
        if self.current_piece:
            for x, y in self.piece_cells(self.current_piece):
                if y >= 0:
                    self.draw_block(x, y, self.current_piece["color"])
        # Grid lines for clarity
        for x in range(self.cols + 1):
            px = x * self.block
            self.canvas.create_line(px, 0, px, self.canvas_height, fill=self.colors["screen_dark"], width=1)
        for y in range(self.rows + 1):
            py = y * self.block
            self.canvas.create_line(0, py, self.canvas_width, py, fill=self.colors["screen_dark"], width=1)
        self.draw_preview()

    def draw_block(self, x, y, color):
        px = x * self.block
        py = y * self.block
        self.canvas.create_rectangle(
            px + 1,
            py + 1,
            px + self.block - 1,
            py + self.block - 1,
            fill=color,
            outline=self.colors["screen_green"],
        )

    def draw_preview(self):
        self.preview.delete("all")
        if not self.next_piece:
            return
        cells = self.tetrominoes[self.next_piece["shape"]][0]
        offset_x = 18
        offset_y = 18
        for x, y in cells:
            px = offset_x + x * self.block
            py = offset_y + y * self.block
            self.preview.create_rectangle(
                px + 1,
                py + 1,
                px + self.block - 1,
                py + self.block - 1,
                fill=self.next_piece["color"],
                outline=self.colors["screen_dark"],
            )

    def update_hud(self):
        self.score_label.config(text=f"SCORE:{self.score:04d}")
        self.lines_label.config(text=f"LINES:{self.lines}")
        self.level_label.config(text=f"LVL:{self.level}")

    def trigger_game_over(self):
        self.game_over = True
        self.game_active = False
        self.status_label.config(text="GAME OVER")
        self.cancel_loop()
        self.canvas.create_rectangle(0, 110, self.canvas_width, 180, fill=self.colors["screen_dark"], outline="")
        self.canvas.create_text(
            self.canvas_width // 2,
            140,
            text="GAME OVER",
            font=self.fonts["retro_title"],
            fill=self.colors["highlight"],
        )
        self.canvas.create_text(
            self.canvas_width // 2,
            165,
            text="X=RESTART  Y=MENU",
            font=self.fonts["retro_tiny"],
            fill=self.colors["nostalgik_cream"],
        )

    # ------------------------------------------------------------------
    # Input actions
    # ------------------------------------------------------------------
    def dpad_left(self):
        if self.game_active and not self.paused:
            self.move_piece(-1, 0)

    def dpad_right(self):
        if self.game_active and not self.paused:
            self.move_piece(1, 0)

    def dpad_down(self):
        if self.game_active and not self.paused:
            if not self.move_piece(0, 1):
                self.lock_piece()

    def dpad_up(self):
        if self.game_active and not self.paused:
            self.rotate_piece()

    def x_button_action(self):
        if self.game_over:
            self.new_game()
            return
        if not self.game_active:
            self.start_game_from_screen()
            return
        if not self.paused:
            self.rotate_piece()

    def y_button_action(self):
        if self.game_over:
            self.exit_to_hub()
            return
        if not self.game_active:
            self.exit_to_hub()
            return
        if not self.paused:
            self.hard_drop()

    def toggle_pause(self):
        if not self.game_active or self.game_over:
            return
        self.paused = not self.paused
        self.status_label.config(text="PAUSED" if self.paused else "PLAY")

    def exit_to_hub(self):
        self.cancel_loop()
        self.game_active = False
        self.gamepad_polling_active = False
        self.unbind_keys()
        self.return_callback()

    # ------------------------------------------------------------------
    # Gamepad support
    # ------------------------------------------------------------------
    def init_gamepad(self):
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            self.joystick = None
            self.gamepad_enabled = True
            self.gamepad_polling_active = True
            self.last_button_state = {}
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            self.parent.winfo_toplevel().after(40, self.poll_gamepad)
        except Exception as e:
            print(f"Gamepad init error (tetris): {e}")
            self.gamepad_enabled = False
            self.gamepad_polling_active = False

    def poll_gamepad(self):
        if not getattr(self, "gamepad_enabled", False) or not getattr(self, "gamepad_polling_active", False):
            return
        try:
            pygame.event.pump()
            if self.joystick is not None and self.joystick.get_init():
                def is_pressed(btn):
                    try:
                        return self.joystick.get_button(btn) == 1
                    except Exception:
                        return False

                def just_pressed(btn):
                    current = is_pressed(btn)
                    previous = self.last_button_state.get(btn, False)
                    self.last_button_state[btn] = current
                    return current and not previous

                if just_pressed(0) or just_pressed(2):  # A or X
                    self.x_button_action()
                if just_pressed(1) or just_pressed(3):  # B or Y
                    self.y_button_action()
                if just_pressed(7):  # START
                    if self.game_active:
                        self.toggle_pause()
                    else:
                        self.start_game_from_screen()

                try:
                    hat = self.joystick.get_hat(0)
                except Exception:
                    hat = (0, 0)
                if hat == (-1, 0):
                    self.dpad_left()
                elif hat == (1, 0):
                    self.dpad_right()
                elif hat == (0, -1):
                    self.dpad_down()
                elif hat == (0, 1):
                    self.dpad_up()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if "bad window" not in str(e):
                print(f"Gamepad poll error (tetris): {e}")

        try:
            self.parent.winfo_toplevel().after(40, self.poll_gamepad)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Reuse
    # ------------------------------------------------------------------
    def show(self):
        self.setup_ui()
        self.show_title_screen()
        if getattr(self, "gamepad_enabled", False):
            self.gamepad_polling_active = True
            self.parent.winfo_toplevel().after(80, self.poll_gamepad)


# Alias for hub import
TetrisGame = NostalgiKitTetris
