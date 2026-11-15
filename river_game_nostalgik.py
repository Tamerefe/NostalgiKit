"""
NostalgiKit River Puzzle
Classic farmer, wolf, goat and cabbage river crossing puzzle.

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk

import nostalgik_ui as ui

ITEMS = ["Farmer", "Wolf", "Goat", "Cabbage"]
ICONS = {"Farmer": "F", "Wolf": "W", "Goat": "G", "Cabbage": "C"}
OPTIMAL_MOVES = 7


class NostalgiKitRiverGame(ui.NostalgiKitGame):
    TITLE = "RIVER PUZZLE"

    def on_show(self):
        self.show_intro()

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------
    def show_intro(self):
        self.screen = "intro"
        self.clear_body()
        self.set_status("")
        self.set_hint(ui.hint(("X", "START"), ("Y", "EXIT")))

        ui.heading(self.body, "CROSS THE RIVER")
        story = ("A farmer must take a\n"
                 "Wolf, a Goat and a Cabbage\n"
                 "across the river.\n\n"
                 "The boat holds the farmer\n"
                 "and ONE passenger.\n\n"
                 "Left alone together:\n"
                 "Wolf eats Goat,\n"
                 "Goat eats Cabbage!")
        ui.label(self.body, story, size='small').pack(expand=True)

    def start_game(self):
        self.west_side = list(ITEMS)
        self.east_side = []
        self.boat_position = "west"
        self.move_count = 0
        self.selected_item = 0
        self.screen = "game"
        self.show_game_board()

    def current_side(self):
        return self.west_side if self.boat_position == "west" else self.east_side

    def other_side(self):
        return self.east_side if self.boat_position == "west" else self.west_side

    def options(self):
        return ["Alone"] + [c for c in self.current_side() if c != "Farmer"]

    def show_game_board(self):
        loss_reason = self.check_loss()
        if loss_reason:
            self.show_end(won=False, reason=loss_reason)
            return
        if self.check_win():
            self.show_end(won=True)
            return

        self.clear_body()
        self.set_status(f"MOVES {self.move_count}")
        self.set_hint(ui.hint(("▲▼", "PICK"), ("X", "ROW"), ("Y", "QUIT")))

        self.draw_river_scene()

        ui.label(self.body, "Take across:", size='small').pack(pady=(8, 2))
        options = self.options()
        self.selected_item = min(self.selected_item, len(options) - 1)
        ui.menu_list(self.body, [(o, None) for o in options], self.selected_item).pack(fill='x')

    def draw_river_scene(self):
        width, height = ui.SCREEN_WIDTH - 20, 120
        canvas = tk.Canvas(self.body, width=width, height=height, bg=ui.SCREEN_BG, highlightthickness=0)
        canvas.pack(pady=(10, 0))
        bank_w = 90
        river_x0, river_x1 = bank_w, width - bank_w

        # Banks and river
        canvas.create_rectangle(0, 0, bank_w, height, fill=ui.SCREEN_LIGHT, outline=ui.SCREEN_DARK)
        canvas.create_rectangle(river_x1, 0, width, height, fill=ui.SCREEN_LIGHT, outline=ui.SCREEN_DARK)
        for y in range(14, height, 18):
            for x in range(river_x0 + 6, river_x1 - 10, 22):
                canvas.create_text(x + (y // 18 % 2) * 8, y, text="~", font=self.fonts['text'], fill=ui.SCREEN_MID)

        canvas.create_text(bank_w // 2, 10, text="WEST", font=self.fonts['tiny'], fill=ui.SCREEN_DARK)
        canvas.create_text(river_x1 + bank_w // 2, 10, text="EAST", font=self.fonts['tiny'], fill=ui.SCREEN_DARK)

        def draw_bank(items, x_center):
            for i, item in enumerate(items):
                canvas.create_text(x_center, 30 + i * 22, text=f"{ICONS[item]} {item.upper()}",
                                   font=self.fonts['small'], fill=ui.SCREEN_DARK)

        draw_bank([i for i in ITEMS if i in self.west_side], bank_w // 2)
        draw_bank([i for i in ITEMS if i in self.east_side], river_x1 + bank_w // 2)

        # Boat docked at the farmer's bank
        bx = river_x0 + 30 if self.boat_position == "west" else river_x1 - 30
        by = height // 2 + 10
        canvas.create_polygon(bx - 24, by - 8, bx + 24, by - 8, bx + 16, by + 8, bx - 16, by + 8,
                              fill=ui.SCREEN_DARK, outline=ui.SCREEN_DARK)
        canvas.create_text(bx, by, text="BOAT", font=self.fonts['tiny'], fill=ui.SCREEN_BG)

    def show_end(self, won, reason=""):
        self.screen = "end"
        self.clear_body()
        self.set_hint(ui.hint(("X", "RETRY"), ("Y", "EXIT")))
        if won:
            ui.heading(self.body, "SUCCESS!")
            if self.move_count <= OPTIMAL_MOVES:
                rating = "PERFECT! Optimal solution!"
            elif self.move_count <= 10:
                rating = "EXCELLENT! Very efficient!"
            elif self.move_count <= 15:
                rating = "GOOD! Well done!"
            else:
                rating = "COMPLETED! Great job!"
            ui.label(self.body, f"Completed in {self.move_count} moves").pack(pady=6)
            ui.label(self.body, rating, size='small').pack(expand=True)
            ui.label(self.body, "F  W  G  C", size='large').pack(pady=(0, 20))
        else:
            ui.heading(self.body, "GAME OVER")
            ui.label(self.body, reason, size='title').pack(pady=6)
            ui.label(self.body, "Never leave alone:\n\nWolf + Goat\nGoat + Cabbage",
                     size='small').pack(expand=True)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def on_dpad(self, direction, pressed=True):
        if not pressed or self.screen != "game" or direction not in ("UP", "DOWN"):
            return
        step = -1 if direction == "UP" else 1
        self.selected_item = (self.selected_item + step) % len(self.options())
        self.show_game_board()

    def on_button(self, button):
        if self.screen == "game":
            if button == "X":
                self.execute_move()
            elif button == "Y":
                self.show_intro()
        elif button in ("X", "START"):
            self.start_game()
        elif button == "Y":
            self.exit_to_hub()

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------
    def execute_move(self):
        passenger = self.options()[self.selected_item]
        current, other = self.current_side(), self.other_side()
        for item in ("Farmer",) if passenger == "Alone" else ("Farmer", passenger):
            current.remove(item)
            other.append(item)
        self.boat_position = "east" if self.boat_position == "west" else "west"
        self.move_count += 1
        self.selected_item = 0
        self.show_game_board()

    def check_loss(self):
        for side in (self.west_side, self.east_side):
            if "Farmer" not in side:
                if "Wolf" in side and "Goat" in side:
                    return "Wolf ate Goat!"
                if "Goat" in side and "Cabbage" in side:
                    return "Goat ate Cabbage!"
        return None

    def check_win(self):
        return len(self.east_side) == len(ITEMS)


RiverGame = NostalgiKitRiverGame
