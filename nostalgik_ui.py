"""
NostalgiKit shared UI kit
One palette, one set of fonts, one screen layout and one input contract
for the hub and every game, so all screens look and behave the same.

Screen layout used everywhere (inside the console's green screen):

    +--------------------------------------+
    | TITLE                         STATUS |  <- HUD bar (dark)
    +--------------------------------------+
    |                                      |
    |               body                   |  <- game content
    |                                      |
    +--------------------------------------+
    | X:ACTION  Y:BACK              SEL:HUB|  <- hint bar
    +--------------------------------------+

Button contract (keyboard / gamepad / on-screen buttons all map to these):
    D-PAD  : move / navigate            (arrows, WASD, gamepad hat or stick)
    X      : confirm / primary action   (Space, X, gamepad A or X)
    Y      : back / pause               (Esc, Backspace, Y, gamepad B or Y)
    START  : start / pause              (Enter, P, gamepad START)
    SELECT : return to hub              (Tab, gamepad BACK) - handled by hub

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import atexit
import os
import queue
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkFont

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
# Screen: four shades of green, like a classic dot-matrix display.
SCREEN_BG = '#9BBB59'      # lightest - screen background
SCREEN_LIGHT = '#C5D98B'   # highlights on dark surfaces
SCREEN_MID = '#6B8A3A'     # secondary ink
SCREEN_DARK = '#374224'    # main ink

# Console body
BODY_CREAM = '#E8E0C7'
BEZEL = '#8B9467'
BEZEL_TEXT = '#6B7458'
BUTTON_GRAY = '#8E8E93'
TEXT_DARK = '#1C1C1E'
BUTTON_X = '#FF3B30'
BUTTON_Y = '#8E44AD'

COLORS = {
    'screen_bg': SCREEN_BG,
    'screen_light': SCREEN_LIGHT,
    'screen_mid': SCREEN_MID,
    'screen_dark': SCREEN_DARK,
    'body_cream': BODY_CREAM,
    'bezel': BEZEL,
    'bezel_text': BEZEL_TEXT,
    'button_gray': BUTTON_GRAY,
    'text_dark': TEXT_DARK,
    'button_x': BUTTON_X,
    'button_y': BUTTON_Y,
}

# Usable game area inside the screen (below HUD, above hint bar)
SCREEN_WIDTH = 330
BODY_HEIGHT = 326

HUD_HEIGHT = 20
HINT_HEIGHT = 16

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_FAMILY = "Courier"
_FONT_SIZES = {
    'huge': 28,
    'large': 12,
    'title': 10,
    'text': 9,
    'small': 8,
    'tiny': 7,
}


def get_fonts(widget):
    """Return the shared font set (created once per Tk root)."""
    root = widget.winfo_toplevel()
    fonts = getattr(root, '_nostalgik_fonts', None)
    if fonts is None:
        fonts = {name: tkFont.Font(root=root, family=FONT_FAMILY, size=size, weight="bold")
                 for name, size in _FONT_SIZES.items()}
        root._nostalgik_fonts = fonts
    return fonts


# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------
def hint(*pairs):
    """Format control hints the same way everywhere: hint(("X", "PLAY"), ("Y", "BACK"))."""
    return "  ".join(f"{button}:{action}" for button, action in pairs)


# ---------------------------------------------------------------------------
# Screen chrome (HUD + body + hint bar)
# ---------------------------------------------------------------------------
class ScreenChrome:
    """Builds the standard HUD / body / hint layout inside a parent frame."""

    def __init__(self, parent, title, show_select_hint=True):
        self.fonts = get_fonts(parent)
        self.frame = tk.Frame(parent, bg=SCREEN_BG)
        self.frame.pack(fill='both', expand=True)

        # HUD
        hud = tk.Frame(self.frame, bg=SCREEN_DARK, height=HUD_HEIGHT)
        hud.pack(side='top', fill='x')
        hud.pack_propagate(False)
        # Status is packed first so a long title gets clipped, never the status
        self.status_label = tk.Label(hud, text="", font=self.fonts['small'],
                                     fg=SCREEN_BG, bg=SCREEN_DARK, anchor='e')
        self.status_label.pack(side='right', padx=6)
        self.title_label = tk.Label(hud, text=title, font=self.fonts['small'],
                                    fg=SCREEN_LIGHT, bg=SCREEN_DARK, anchor='w')
        self.title_label.pack(side='left', padx=6)

        # Hint bar
        hints = tk.Frame(self.frame, bg=SCREEN_BG, height=HINT_HEIGHT)
        hints.pack(side='bottom', fill='x')
        hints.pack_propagate(False)
        tk.Frame(self.frame, bg=SCREEN_MID, height=1).pack(side='bottom', fill='x')
        self.hint_label = tk.Label(hints, text="", font=self.fonts['tiny'],
                                   fg=SCREEN_DARK, bg=SCREEN_BG, anchor='w')
        self.hint_label.pack(side='left', padx=6)
        if show_select_hint:
            tk.Label(hints, text="SEL:HUB", font=self.fonts['tiny'],
                     fg=SCREEN_MID, bg=SCREEN_BG).pack(side='right', padx=6)

        # Body
        self.body = tk.Frame(self.frame, bg=SCREEN_BG)
        self.body.pack(side='top', fill='both', expand=True)

    def set_title(self, text):
        self.title_label.config(text=text)

    def set_status(self, text):
        self.status_label.config(text=text)

    def set_hint(self, text):
        self.hint_label.config(text=text)

    def clear_body(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def destroy(self):
        if self.frame.winfo_exists():
            self.frame.destroy()


# ---------------------------------------------------------------------------
# Widgets for text-based screens
# ---------------------------------------------------------------------------
def label(parent, text, size='text', inverted=False, **kwargs):
    """Screen text in the shared style. inverted=True draws light text on dark."""
    fonts = get_fonts(parent)
    fg, bg = (SCREEN_BG, SCREEN_DARK) if inverted else (SCREEN_DARK, SCREEN_BG)
    options = dict(text=text, font=fonts[size], fg=fg, bg=bg, justify='center')
    options.update(kwargs)
    return tk.Label(parent, **options)


def heading(parent, text, pady=(10, 4)):
    """Section heading: large text with a thin rule under it."""
    lbl = label(parent, text, size='large')
    lbl.pack(pady=pady)
    tk.Frame(parent, bg=SCREEN_DARK, height=2, width=140).pack(pady=(0, 6))
    return lbl


def menu_list(parent, items, selected, disabled=()):
    """Vertical selection list. Selected row is inverted and marked with '>'.

    items: list of (label, description-or-None)
    """
    frame = tk.Frame(parent, bg=SCREEN_BG)
    for i, (text, desc) in enumerate(items):
        is_selected = i == selected
        is_disabled = i in disabled
        row = tk.Frame(frame, bg=SCREEN_DARK if is_selected else SCREEN_BG)
        row.pack(fill='x', padx=14, pady=1)
        marker = "> " if is_selected else "  "
        lbl = label(row, f"{marker}{text}", size='small', inverted=is_selected, anchor='w')
        if is_disabled and not is_selected:
            lbl.config(fg=SCREEN_MID)
        lbl.pack(fill='x', padx=4, pady=1)
        if is_selected and desc:
            label(row, f"  {desc}", size='tiny', inverted=True, anchor='w').pack(fill='x', padx=4, pady=(0, 2))
    return frame


def bar_text(value, maximum, width=10):
    """Text progress bar like [#####.....]."""
    maximum = max(1, maximum)
    filled = max(0, min(width, round(width * value / maximum)))
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Canvas helpers
# ---------------------------------------------------------------------------
def draw_overlay(canvas, title, lines=(), hint_text=None):
    """Centered dark message box on a canvas (title / pause / game over)."""
    fonts = get_fonts(canvas)
    w = int(canvas.cget('width'))
    h = int(canvas.cget('height'))
    canvas.delete('overlay')

    line_h = 16
    box_h = 46 + line_h * len(lines) + (24 if hint_text else 0)
    box_w = min(w - 20, 260)
    x0, y0 = (w - box_w) // 2, (h - box_h) // 2
    canvas.create_rectangle(x0, y0, x0 + box_w, y0 + box_h, fill=SCREEN_DARK,
                            outline=SCREEN_LIGHT, width=2, tags='overlay')
    y = y0 + 22
    canvas.create_text(w // 2, y, text=title, font=fonts['large'],
                       fill=SCREEN_LIGHT, tags='overlay')
    y += 24
    for line in lines:
        canvas.create_text(w // 2, y, text=line, font=fonts['text'],
                           fill=SCREEN_BG, tags='overlay')
        y += line_h
    if hint_text:
        canvas.create_text(w // 2, y + 6, text=hint_text, font=fonts['small'],
                           fill=SCREEN_LIGHT, tags='overlay')


# ---------------------------------------------------------------------------
# Base class for games
# ---------------------------------------------------------------------------
class NostalgiKitGame:
    """Common base for every game.

    The hub owns all input (keyboard, gamepad, on-screen buttons) and calls:
        on_dpad(direction, pressed)  direction in UP/DOWN/LEFT/RIGHT
        on_button(button)            button in X/Y/START
        exit_to_hub()                SELECT, or when the game wants to leave

    Subclasses implement on_show() to build their first screen, and use
    self.chrome (HUD / body / hints) and self.schedule() for timers so
    everything is cleaned up automatically on exit.
    """

    TITLE = "GAME"

    def __init__(self, parent, return_callback):
        self.parent = parent
        self.return_callback = return_callback
        self.root = parent.winfo_toplevel()
        self.fonts = get_fonts(parent)
        self.colors = COLORS
        self.chrome = None
        self._jobs = {}
        self.show()

    # -- lifecycle --------------------------------------------------------
    def show(self):
        """(Re)build the game UI inside the hub screen and reset to the title."""
        self.cancel_all()
        if self.chrome is not None:
            self.chrome.destroy()
        self.chrome = ScreenChrome(self.parent, self.TITLE)
        self.body = self.chrome.body
        self.on_show()

    def on_show(self):
        raise NotImplementedError

    def on_exit(self):
        """Hook for subclasses to stop game state before leaving."""

    def exit_to_hub(self):
        self.cancel_all()
        self.on_exit()
        if self.chrome is not None:
            self.chrome.destroy()
            self.chrome = None
        self.return_callback()

    # -- input (overridden by games) ----------------------------------------
    def on_dpad(self, direction, pressed=True):
        pass

    def on_button(self, button):
        pass

    # -- helpers ----------------------------------------------------------
    def set_status(self, text):
        if self.chrome:
            self.chrome.set_status(text)

    def set_hint(self, text):
        if self.chrome:
            self.chrome.set_hint(text)

    def clear_body(self):
        if self.chrome:
            self.chrome.clear_body()

    def schedule(self, name, delay_ms, callback):
        """Run callback after delay_ms; only one pending job per name."""
        self.cancel(name)

        def run():
            self._jobs.pop(name, None)
            if self.chrome is not None:
                callback()

        self._jobs[name] = self.root.after(delay_ms, run)

    def cancel(self, name):
        job = self._jobs.pop(name, None)
        if job is not None:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass

    def cancel_all(self):
        for name in list(self._jobs):
            self.cancel(name)


# ---------------------------------------------------------------------------
# Input: keyboard + gamepad -> D-PAD / X / Y / START / SELECT
# ---------------------------------------------------------------------------
KEY_DIRECTIONS = {
    'up': 'UP', 'w': 'UP',
    'down': 'DOWN', 's': 'DOWN',
    'left': 'LEFT', 'a': 'LEFT',
    'right': 'RIGHT', 'd': 'RIGHT',
}
KEY_BUTTONS = {
    'space': 'X', 'x': 'X',
    'escape': 'Y', 'backspace': 'Y', 'y': 'Y',
    'return': 'START', 'kp_enter': 'START', 'p': 'START',
    'tab': 'SELECT',
}

# XInput-style gamepad layout
PAD_BUTTONS = {0: 'X', 2: 'X', 1: 'Y', 3: 'Y', 7: 'START', 6: 'SELECT'}
STICK_DEADZONE = 0.5


class InputRouter:
    """Turns keyboard and gamepad input into on_dpad / on_button calls."""

    def __init__(self, root, on_dpad, on_button):
        self.root = root
        self.on_dpad = on_dpad
        self.on_button = on_button
        self.held_keys = set()

        root.bind('<KeyPress>', self._key_press)
        root.bind('<KeyRelease>', self._key_release)

        self._pad = None
        self._pad_buttons = {}
        self._pad_dirs = set()
        self._pad_reset = False
        self._pad_next_scan = 0
        self._pad_events = queue.Queue()
        self._pad_running = False
        self._init_gamepad()

    # -- keyboard ---------------------------------------------------------
    def _key_press(self, event):
        key = event.keysym.lower()
        if key in KEY_DIRECTIONS:
            self.held_keys.add(key)
            self.on_dpad(KEY_DIRECTIONS[key], True)
            return 'break'
        if key in KEY_BUTTONS:
            # Ignore OS auto-repeat for buttons
            if key in self.held_keys:
                return 'break'
            self.held_keys.add(key)
            self.on_button(KEY_BUTTONS[key])
            return 'break'
        return None

    def _key_release(self, event):
        key = event.keysym.lower()
        self.held_keys.discard(key)
        if key in KEY_DIRECTIONS:
            self.on_dpad(KEY_DIRECTIONS[key], False)

    # -- gamepad ----------------------------------------------------------
    # pygame/SDL is only used to read the controller. On Windows SDL's event
    # pump dispatches every window message of the calling thread, including
    # Tk's, while pygame has released the GIL - which can crash Python. So on
    # Windows the controller is read on its own thread (each thread has its
    # own message queue) and results are handed to Tk through a queue.
    # Elsewhere SDL does not touch Tk's windows, so polling stays on Tk's thread.
    POLL_SECONDS = 0.03

    def _init_gamepad(self):
        try:
            os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
            import pygame
        except ImportError:
            self._pygame = None
            return
        self._pygame = pygame
        self._pad_running = True
        if sys.platform == 'win32':
            thread = threading.Thread(target=self._pad_thread, name="gamepad", daemon=True)
            thread.start()
            # Stop before pygame's own exit hook shuts SDL down under the thread
            atexit.register(self._stop_pad_thread, thread)
        elif not self._start_pygame():
            return
        else:
            self.root.after(30, self._poll_on_tk_thread)
        self.root.after(30, self._deliver_pad_events)

    def _start_pygame(self):
        try:
            self._pygame.init()
            self._pygame.joystick.init()
            return True
        except Exception as e:
            print(f"Gamepad init failed: {e}")
            self._pad_running = False
            return False

    def _stop_pad_thread(self, thread):
        self._pad_running = False
        thread.join(timeout=0.5)

    def _pad_thread(self):
        if not self._start_pygame():
            return
        while self._pad_running:
            self._poll_once()
            time.sleep(self.POLL_SECONDS)

    def _poll_on_tk_thread(self):
        if not self._pad_running:
            return
        self._poll_once()
        try:
            self.root.after(int(self.POLL_SECONDS * 1000), self._poll_on_tk_thread)
        except tk.TclError:
            self._pad_running = False

    def _deliver_pad_events(self):
        """Runs on Tk's thread: forward queued controller input to the hub."""
        while True:
            try:
                kind, name, pressed = self._pad_events.get_nowait()
            except queue.Empty:
                break
            if kind == 'button':
                self.on_button(name)
            else:
                self.on_dpad(name, pressed)
        try:
            self.root.after(20, self._deliver_pad_events)
        except tk.TclError:
            self._pad_running = False  # window closed: stop the reader thread

    def _connect(self):
        pygame = self._pygame
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                pad = pygame.joystick.Joystick(0)
                pad.init()
                print(f"Gamepad connected: {pad.get_name()}")
                return pad
        except Exception as e:
            print(f"Gamepad connection error: {e}")
        return None

    def _poll_once(self):
        try:
            self._pygame.event.pump()
            if self._pad is None:
                # Hot-plug check about once a second
                self._pad_next_scan -= 1
                if self._pad_next_scan <= 0:
                    self._pad_next_scan = 33
                    self._pad = self._connect()
            if self._pad is not None:
                self._read_pad()
        except Exception as e:
            print(f"Gamepad polling error: {e}")
            self._pad = None

    def _read_pad(self):
        pad = self._pad
        emit = self._pad_events.put
        # Buttons (edge-triggered)
        fired = set()
        for index, name in PAD_BUTTONS.items():
            try:
                pressed = index < pad.get_numbuttons() and pad.get_button(index) == 1
            except Exception:
                pressed = False
            was = self._pad_buttons.get(index, False)
            self._pad_buttons[index] = pressed
            if pressed and not was and name not in fired:
                fired.add(name)
                emit(('button', name, True))

        # Directions: hat first, analog stick as fallback
        dirs = set()
        try:
            hx, hy = pad.get_hat(0) if pad.get_numhats() > 0 else (0, 0)
        except Exception:
            hx, hy = 0, 0
        if hx == 0 and hy == 0:
            try:
                ax = pad.get_axis(0) if pad.get_numaxes() > 0 else 0
                ay = pad.get_axis(1) if pad.get_numaxes() > 1 else 0
            except Exception:
                ax, ay = 0, 0
            hx = -1 if ax < -STICK_DEADZONE else (1 if ax > STICK_DEADZONE else 0)
            hy = 1 if ay < -STICK_DEADZONE else (-1 if ay > STICK_DEADZONE else 0)
        if hx < 0:
            dirs.add('LEFT')
        elif hx > 0:
            dirs.add('RIGHT')
        if hy > 0:
            dirs.add('UP')
        elif hy < 0:
            dirs.add('DOWN')

        if self._pad_reset:
            # Screen changed: forget held directions without re-pressing them
            self._pad_reset = False
            self._pad_dirs = dirs
            return
        for d in self._pad_dirs - dirs:
            emit(('dpad', d, False))
        for d in dirs - self._pad_dirs:
            emit(('dpad', d, True))
        self._pad_dirs = dirs

    def release_all(self):
        """Send release events for anything still held (used on screen changes)."""
        for key in list(self.held_keys):
            if key in KEY_DIRECTIONS:
                self.on_dpad(KEY_DIRECTIONS[key], False)
        self.held_keys.clear()
        for d in list(self._pad_dirs):
            self.on_dpad(d, False)
        self._pad_reset = True


def run_standalone(game_class, title="NostalgiKit"):
    """Run one game in a bare window (for development/testing)."""
    root = tk.Tk()
    root.title(title)
    root.configure(bg=BEZEL)
    screen = tk.Frame(root, bg=SCREEN_BG, width=SCREEN_WIDTH + 4,
                      height=BODY_HEIGHT + HUD_HEIGHT + HINT_HEIGHT + 8)
    screen.pack(padx=12, pady=12)
    screen.pack_propagate(False)

    state = {}

    def back():
        root.destroy()

    def dpad(direction, pressed):
        state['game'].on_dpad(direction, pressed)

    def button(name):
        if name == 'SELECT':
            state['game'].exit_to_hub()
        else:
            state['game'].on_button(name)

    state['game'] = game_class(screen, back)
    InputRouter(root, dpad, button)
    root.mainloop()
