"""
NostalgiKit - Vintage Handheld Gaming Experience
Classic retro handheld style interface hosting all NostalgiKit games

The hub owns the console body, the screen and all input. Games are drawn
inside the screen using the shared look from nostalgik_ui and receive input
through on_dpad / on_button.

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import os
import tempfile
import tkinter as tk
from tkinter import messagebox

import nostalgik_ui as ui
from console_widgets import ActionButtons, DPad, MenuButtons, ScreenBezel, SpeakerGrille, ENGRAVED_TEXT as ENGRAVED

# Import NostalgiKit games
from card_guess_nostalgik import CardGuessGame
from war_game_nostalgik import WarGame
from river_game_nostalgik import RiverGame
from galaxy_war_pat import GalaxyWarPat
from crakers_nostalgik import CrakersGame
from block_stack_nostalgik import BlockStackGame

GAMES = [
    {"name": "NUMBER ORACLE", "desc": "Magical Number Quest", "cls": CardGuessGame},
    {"name": "WAR GAME", "desc": "Turn-Based Combat", "cls": WarGame},
    {"name": "RIVER PUZZLE", "desc": "Logic Challenge", "cls": RiverGame},
    {"name": "GALAXY WAR PAT", "desc": "Space Shooter", "cls": GalaxyWarPat},
    {"name": "CRAKERS QUEST", "desc": "Grid Adventure", "cls": CrakersGame},
    {"name": "BLOCK STACK", "desc": "Falling Blocks", "cls": BlockStackGame},
]

LOADING_TIME_MS = 700


class NostalgiKitHub:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NostalgiKit")
        self.setup_icon()

        self.root.resizable(False, False)

        self.colors = ui.COLORS
        self.fonts = ui.get_fonts(self.root)

        # Hub state
        self.current_screen = "blank"   # blank, welcome, menu, loading, game, off
        self.selected_game = 0
        self.games = GAMES
        self.game_instances = {}        # index -> game object (created once, reused)
        self.active_game = None
        self.chrome = None
        self._loading_job = None

        self.setup_nostalgik_interface()
        self.input = ui.InputRouter(self.root, self.dpad_action, self.button_action)

        # Blank screen first, then welcome screen
        self.show_blank_screen()
        self.root.after(500, self.show_welcome_screen)

    # ------------------------------------------------------------------
    # Window icon
    # ------------------------------------------------------------------
    def setup_icon(self):
        self.icon = None  # keep a reference so it is not garbage collected
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if not os.path.exists(icon_path):
            return
        try:
            from PIL import Image, ImageTk
            with Image.open(icon_path) as img:
                img = img.resize((32, 32), Image.Resampling.LANCZOS) if img.size != (32, 32) else img.copy()
            self.icon = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, self.icon)
            # Windows taskbar needs an .ico file
            try:
                ico_path = os.path.join(tempfile.gettempdir(), "nostalgikit_icon.ico")
                img.save(ico_path, format="ICO")
                self.root.iconbitmap(default=ico_path)
            except Exception:
                pass
        except Exception:
            try:
                self.icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, self.icon)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Console body
    # ------------------------------------------------------------------
    def setup_nostalgik_interface(self):
        """Build the console: the window itself is the cream plastic body."""
        cream = ui.BODY_CREAM
        self.root.configure(bg=cream)
        self.root.focus_set()

        # Branding
        brand = tk.Frame(self.root, bg=cream)
        brand.pack(fill='x', pady=(14, 8))
        tk.Label(brand, text="NostalgiKIT", font=self.fonts['large'],
                 fg='#2E3A6E', bg=cream).pack()
        tk.Label(brand, text="C L A S S I C", font=self.fonts['tiny'],
                 fg=ENGRAVED, bg=cream).pack()

        # Screen in its bezel; games draw into self.screen
        self.bezel = ScreenBezel(self.root)
        self.bezel.pack()
        self.screen = self.bezel.screen

        # D-Pad left, X/Y right, SELECT/START centred below
        controls = tk.Frame(self.root, bg=cream)
        controls.pack(fill='x', padx=30, pady=(16, 0))
        self.dpad = DPad(controls, self.dpad_action)
        self.dpad.pack(side='left')
        self.action_buttons = ActionButtons(controls, self.button_action)
        self.action_buttons.pack(side='right', pady=(0, 10))

        bottom = tk.Frame(self.root, bg=cream)
        bottom.pack(fill='x', pady=(6, 22))
        self.menu_buttons = MenuButtons(bottom, self.button_action)
        self.menu_buttons.pack()
        SpeakerGrille(self.root).place(relx=1.0, rely=1.0, x=-26, y=-18, anchor='se')

        self.root.update_idletasks()
        self.root.geometry(f"460x{self.root.winfo_reqheight()}")

    def flash_button(self, button):
        """Mirror X/Y/START/SELECT presses from any source on the console."""
        if button in ("X", "Y"):
            self.action_buttons.flash(button)
        else:
            self.menu_buttons.flash(button)

    # ------------------------------------------------------------------
    # Input routing
    # ------------------------------------------------------------------
    def dpad_action(self, direction, pressed=True):
        # Mirror every D-Pad input (mouse, keyboard, gamepad) on the console
        self.dpad.show(direction, pressed)
        if self.current_screen == "game" and self.active_game is not None:
            self.active_game.on_dpad(direction, pressed)
            return
        if not pressed:
            return
        if self.current_screen == "menu":
            if direction == "UP":
                self.selected_game = (self.selected_game - 1) % len(self.games)
                self.show_main_menu()
            elif direction == "DOWN":
                self.selected_game = (self.selected_game + 1) % len(self.games)
                self.show_main_menu()

    def button_action(self, button):
        """X / Y / START / SELECT from keyboard, gamepad or on-screen buttons."""
        self.flash_button(button)
        screen = self.current_screen
        if screen == "game" and self.active_game is not None:
            if button == "SELECT":
                self.active_game.exit_to_hub()
            else:
                self.active_game.on_button(button)
            return

        if screen == "welcome":
            if button in ("X", "START", "SELECT"):
                self.show_main_menu()
            elif button == "Y":
                self.power_off()
        elif screen == "menu":
            if button in ("X", "START"):
                self.launch_game(self.selected_game)
            elif button == "Y":
                self.show_welcome_screen()
        elif screen == "off":
            if button in ("X", "START"):
                self.show_welcome_screen()
        # "blank" and "loading" ignore input

    # Kept for compatibility with older code paths
    def x_button_action(self):
        self.button_action("X")

    def y_button_action(self):
        self.button_action("Y")

    def start_action(self):
        self.button_action("START")

    def select_action(self):
        self.button_action("SELECT")

    # ------------------------------------------------------------------
    # Hub screens
    # ------------------------------------------------------------------
    def clear_screen(self):
        self.chrome = None
        for widget in self.screen.winfo_children():
            widget.destroy()

    def new_chrome(self, title, status="", hint_text=""):
        self.clear_screen()
        self.chrome = ui.ScreenChrome(self.screen, title, show_select_hint=False)
        self.chrome.set_status(status)
        self.chrome.set_hint(hint_text)
        return self.chrome.body

    def show_blank_screen(self):
        self.clear_screen()
        self.current_screen = "blank"
        tk.Frame(self.screen, bg=ui.SCREEN_BG).pack(fill='both', expand=True)

    def show_welcome_screen(self):
        self.current_screen = "welcome"
        if not self.bezel.led_on:
            self.bezel.set_led(True)
        body = self.new_chrome("NOSTALGIKIT", "v0.3", ui.hint(("START", "MENU"), ("Y", "POWER OFF")))
        spacer = tk.Frame(body, bg=ui.SCREEN_BG)
        spacer.pack(expand=True)
        ui.label(spacer, "NostalgiKIT", size='huge').pack()
        ui.label(spacer, "C L A S S I C", size='title').pack(pady=(0, 18))
        ui.label(spacer, f"{len(self.games)} GAMES INSIDE", size='small').pack()
        ui.label(body, "PRESS START", size='text').pack(side='bottom', pady=14)

    def show_main_menu(self):
        self.current_screen = "menu"
        body = self.new_chrome("SELECT GAME", f"{self.selected_game + 1}/{len(self.games)}",
                               ui.hint(("▲▼", "PICK"), ("X", "PLAY"), ("Y", "BACK")))
        items = [(g["name"], g["desc"]) for g in self.games]
        ui.menu_list(body, items, self.selected_game).pack(fill='x', pady=12)

    def show_loading_screen(self, game_name):
        self.current_screen = "loading"
        body = self.new_chrome(game_name, "LOADING")
        box = tk.Frame(body, bg=ui.SCREEN_BG)
        box.pack(expand=True)
        ui.label(box, game_name, size='large').pack(pady=(0, 12))
        bar = ui.label(box, ui.bar_text(0, 10, 14), size='text')
        bar.pack()
        ui.label(box, "LOADING...", size='small').pack(pady=(10, 0))

        steps = 7

        def tick(i=1):
            if self.current_screen != "loading" or not bar.winfo_exists():
                return
            bar.config(text=ui.bar_text(i, steps, 14))
            if i < steps:
                self.root.after(LOADING_TIME_MS // steps, lambda: tick(i + 1))
        self.root.after(LOADING_TIME_MS // steps, tick)

    def power_off(self):
        self.clear_screen()
        self.current_screen = "off"
        self.bezel.set_led(False)
        tk.Frame(self.screen, bg=ui.SCREEN_DARK).pack(fill='both', expand=True)

    # ------------------------------------------------------------------
    # Game launching
    # ------------------------------------------------------------------
    def launch_game(self, index):
        if self.current_screen == "loading":
            return  # ignore double presses while loading
        game_info = self.games[index]
        self.input.release_all()
        self.show_loading_screen(game_info["name"])

        def start():
            if self.current_screen != "loading":
                return
            self.clear_screen()
            try:
                game = self.game_instances.get(index)
                if game is None:
                    game = game_info["cls"](self.screen, self.return_to_nostalgik)
                    self.game_instances[index] = game
                else:
                    game.show()
                self.active_game = game
                self.current_screen = "game"
            except Exception as e:
                print(f"Failed to launch {game_info['name']}: {e}")
                self.active_game = None
                self.game_instances.pop(index, None)
                try:
                    messagebox.showerror("Game Error", f"{game_info['name']} could not start:\n{e}")
                except Exception:
                    pass
                self.show_main_menu()

        self._loading_job = self.root.after(LOADING_TIME_MS, start)

    def return_to_nostalgik(self):
        """Called by games when they exit."""
        self.active_game = None
        self.input.release_all()
        self.show_main_menu()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    NostalgiKitHub().run()
