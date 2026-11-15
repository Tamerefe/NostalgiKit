"""
NostalgiKit Card Guess Game - Number Oracle
Think of a number, answer YES/NO for each magic card and the oracle reads your mind.

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import tkinter as tk

import nostalgik_ui as ui

MAX_NUMBER = 20

# Binary magic cards: card k holds every number whose bit k is set, so the
# YES answers add up to exactly one number (the first number on each card).
CARDS = [
    (f"CARD {chr(ord('A') + bit)}", [n for n in range(1, MAX_NUMBER + 1) if n & (1 << bit)])
    for bit in range(MAX_NUMBER.bit_length())
]


class NostalgiKitCardGame(ui.NostalgiKitGame):
    TITLE = "NUMBER ORACLE"

    def on_show(self):
        self.show_intro()

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------
    def show_intro(self):
        self.stage = "intro"
        self.clear_body()
        self.set_status("")
        self.set_hint(ui.hint(("X", "START"), ("Y", "EXIT")))

        ui.heading(self.body, "THE ORACLE")
        text = (f"Think of a number\nfrom 1 to {MAX_NUMBER}.\n\n"
                f"I will show you\n{len(CARDS)} magic cards.\n\n"
                "Tell me if your\nnumber is on each card.")
        ui.label(self.body, text).pack(expand=True)

    def start_game(self):
        self.stage = "asking"
        self.card_index = 0
        self.answer = 0
        self.show_card()

    def show_card(self):
        if self.card_index >= len(CARDS):
            self.show_result()
            return
        self.clear_body()
        name, numbers = CARDS[self.card_index]
        self.set_status(f"CARD {self.card_index + 1}/{len(CARDS)}")
        self.set_hint(ui.hint(("X", "YES"), ("Y", "NO")))

        ui.heading(self.body, name)

        # Numbers in a bordered card
        card = tk.Frame(self.body, bg=ui.SCREEN_DARK, padx=2, pady=2)
        card.pack(pady=4)
        grid = tk.Frame(card, bg=ui.SCREEN_BG, padx=8, pady=6)
        grid.pack()
        per_row = 5
        for i, number in enumerate(numbers):
            ui.label(grid, f"{number:2d}", size='title', width=3).grid(row=i // per_row, column=i % per_row, padx=2, pady=2)

        ui.label(self.body, "Is your number\non this card?").pack(expand=True)

    def show_result(self):
        self.stage = "result"
        self.clear_body()
        self.set_status("")
        self.set_hint(ui.hint(("X", "AGAIN"), ("Y", "EXIT")))

        if 1 <= self.answer <= MAX_NUMBER:
            ui.heading(self.body, "ORACLE SPEAKS")
            ui.label(self.body, str(self.answer), size='huge').pack(expand=True)
            ui.label(self.body, "Your secret number\nis revealed!").pack(pady=(0, 16))
        else:
            ui.heading(self.body, "HMM...")
            ui.label(self.body, "The oracle cannot\nread your mind.\n\n"
                                "Did you change\nyour number?").pack(expand=True)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def on_button(self, button):
        if self.stage == "asking":
            if button == "X":
                self.answer_card(True)
            elif button == "Y":
                self.answer_card(False)
        elif button in ("X", "START"):
            self.start_game()
        elif button == "Y":
            self.exit_to_hub()

    def answer_card(self, is_present):
        if is_present:
            self.answer += CARDS[self.card_index][1][0]
        self.card_index += 1
        self.show_card()


CardGuessGame = NostalgiKitCardGame
