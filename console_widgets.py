"""
NostalgiKit console hardware widgets
The physical parts of the handheld: screen bezel, D-Pad, X/Y buttons,
SELECT/START buttons and speaker grille.

Everything is drawn with Pillow at 4x size and scaled down so edges are smooth,
and every control has a pressed state that also lights up when the same
button comes from the keyboard or a gamepad. Without Pillow a plain vector
version is drawn instead.

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import math
import tkinter as tk

import nostalgik_ui as ui

SS = 4  # supersampling factor

# Moulded recess colours in the cream plastic
RECESS_RIM = (196, 187, 158, 255)
RECESS_FLOOR = (220, 212, 186, 255)
ENGRAVED_TEXT = '#8A8168'


def _rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _shade(rgb, factor):
    """factor > 0 lightens towards white, < 0 darkens towards black."""
    if factor >= 0:
        return tuple(int(c + (255 - c) * factor) for c in rgb[:3]) + (255,)
    return tuple(int(c * (1 + factor)) for c in rgb[:3]) + (255,)


def _pil():
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
    return Image, ImageDraw, ImageFilter, ImageTk


def _capsule(draw, p1, p2, radius, fill):
    """Rounded bar from p1 to p2 (both ends rounded)."""
    draw.line([p1, p2], fill=fill, width=int(radius * 2))
    for x, y in (p1, p2):
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=fill)


def _soft_shadow(img, shape, offset, blur, color=(60, 52, 35), strength=150):
    """Blurred shadow of shape(draw, dx, dy, fill) under the current image."""
    Image, ImageDraw, ImageFilter, _ = _pil()
    mask = Image.new('L', img.size, 0)
    shape(ImageDraw.Draw(mask), offset[0], offset[1], strength)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    img.paste(color + (255,), (0, 0), mask)


def _bevel(draw, shape, body, light=0.35, dark=-0.55, k=SS):
    """Raised plastic: light top-left edge, dark bottom-right edge, body on top."""
    shape(draw, -k * 0.75, -k * 0.75, _shade(body, light))
    shape(draw, k, 1.5 * k, _shade(body, dark))
    shape(draw, 0, 0, body + (255,) if len(body) == 3 else body)



class _HardwareCanvas(tk.Canvas):
    """Canvas showing one pre-rendered image per state, with pressed-state logic."""

    STATES = (None,)

    def __init__(self, parent, width, height):
        super().__init__(parent, width=width, height=height, bg=ui.BODY_CREAM,
                         highlightthickness=0, bd=0)
        self.w, self.h = width, height
        self.state = None
        try:
            self.images = {s: self._to_photo(self.render(s)) for s in self.STATES}
        except Exception as e:  # Pillow missing or failed
            print(f"Console widget fallback ({type(self).__name__}): {e}")
            self.images = None
        if self.images:
            self.image_item = self.create_image(0, 0, anchor='nw', image=self.images[None])
        self.set_state(None)

    def _to_photo(self, img):
        Image, _, _, ImageTk = _pil()
        img = img.resize((self.w, self.h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img, master=self)

    def new_image(self):
        Image, ImageDraw, _, _ = _pil()
        img = Image.new('RGBA', (self.w * SS, self.h * SS), (0, 0, 0, 0))
        return img, ImageDraw.Draw(img)

    def set_state(self, state):
        self.state = state
        if self.images:
            self.itemconfig(self.image_item, image=self.images[state])
        else:
            self.delete('fallback')
            self.draw_fallback(state)
        self.delete('overlay')
        self.draw_overlay(state)

    # Subclasses
    def render(self, state):
        raise NotImplementedError

    def draw_fallback(self, state):
        pass

    def draw_overlay(self, state):
        pass


# ---------------------------------------------------------------------------
# Buttons (X/Y and SELECT/START)
# ---------------------------------------------------------------------------
class _ButtonCluster(_HardwareCanvas):
    """A group of momentary buttons. on_press(name) fires when one goes down."""

    BUTTONS = {}  # name -> dict(cx, cy, ...)

    def __init__(self, parent, width, height, on_press):
        self.on_press = on_press
        self.mouse_button = None
        self._flash_job = None
        super().__init__(parent, width, height)
        self.bind('<ButtonPress-1>', self._mouse_press)
        self.bind('<ButtonRelease-1>', self._mouse_release)

    def hit(self, x, y):
        raise NotImplementedError

    def _mouse_press(self, event):
        name = self.hit(event.x, event.y)
        if name:
            self.mouse_button = name
            self.set_state(name)
            self.on_press(name)

    def _mouse_release(self, event):
        self.mouse_button = None
        self.set_state(None)

    def flash(self, name, ms=110):
        """Show a press coming from the keyboard or a gamepad."""
        if name not in self.BUTTONS or self.mouse_button:
            return
        if self._flash_job:
            self.after_cancel(self._flash_job)
        self.set_state(name)

        def release():
            self._flash_job = None
            if not self.mouse_button:
                self.set_state(None)
        self._flash_job = self.after(ms, release)


class ActionButtons(_ButtonCluster):
    """Round X / Y buttons side by side in a horizontal recess."""

    BUTTONS = {
        "Y": {"cx": 40, "cy": 50, "color": ui.BUTTON_Y},
        "X": {"cx": 108, "cy": 50, "color": ui.BUTTON_X},
    }
    STATES = (None, "X", "Y")
    RADIUS = 19

    def __init__(self, parent, on_press):
        super().__init__(parent, 148, 100, on_press)

    def hit(self, x, y):
        for name, b in self.BUTTONS.items():
            if math.hypot(x - b["cx"], y - b["cy"]) <= self.RADIUS + 4:
                return name
        return None

    def render(self, pressed):
        img, d = self.new_image()
        k = SS
        y_btn, x_btn = self.BUTTONS["Y"], self.BUTTONS["X"]
        p1 = (y_btn["cx"] * k, y_btn["cy"] * k)
        p2 = (x_btn["cx"] * k, x_btn["cy"] * k)

        # Recess the two buttons sit in
        _capsule(d, p1, p2, 27 * k, RECESS_RIM)
        _capsule(d, (p1[0] + 1.5 * k, p1[1] + 2 * k), (p2[0] + 1.5 * k, p2[1] + 2 * k), 25.5 * k, RECESS_FLOOR)

        r = self.RADIUS * k
        for name, b in self.BUTTONS.items():
            cx, cy = b["cx"] * k, b["cy"] * k
            is_down = name == pressed
            sink = k if is_down else 0

            def circle(draw, dx, dy, fill, cx=cx, cy=cy + sink, r=r):
                draw.ellipse([cx - r + dx, cy - r + dy, cx + r + dx, cy + r + dy], fill=fill)

            _soft_shadow(img, circle, (k * 0.5, (1 if is_down else 3) * k), (1.5 if is_down else 2.5) * k)
            # Matte plastic: muted colour, soft edge light, no glossy highlight
            body = _shade(self._matte(_rgb(b["color"])), -0.15 if is_down else 0)
            _bevel(d, circle, body, light=0.08 if is_down else 0.14, dark=-0.45)
        return img

    @staticmethod
    def _matte(rgb, mute=0.3, darken=0.1):
        """Pull a colour towards its grey and darken it a little."""
        grey = 0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]
        return tuple(int((c * (1 - mute) + grey * mute) * (1 - darken)) for c in rgb[:3])

    def draw_fallback(self, state):
        for name, b in self.BUTTONS.items():
            r = self.RADIUS
            color = '#%02x%02x%02x' % self._matte(_rgb(b["color"]))
            off = 1 if name == state else 0
            self.create_oval(b["cx"] - r, b["cy"] - r + off, b["cx"] + r, b["cy"] + r + off,
                             fill=color, outline='#40303A', width=2, tags='fallback')

    def draw_overlay(self, state):
        font = ui.get_fonts(self)['large']
        for name, b in self.BUTTONS.items():
            sink = 1 if name == state else 0
            x, y = b["cx"], b["cy"] + sink
            self.create_text(x + 1, y + 1, text=name, font=font,
                             fill='#%02x%02x%02x' % _shade(self._matte(_rgb(b["color"])), -0.45)[:3],
                             tags='overlay')
            self.create_text(x, y, text=name, font=font, fill='#EDE6DA', tags='overlay')


class MenuButtons(_ButtonCluster):
    """Flat rubber SELECT / START pills with engraved labels."""

    BUTTONS = {
        "SELECT": {"cx": 56, "cy": 18},
        "START": {"cx": 120, "cy": 18},
    }
    STATES = (None, "SELECT", "START")
    HALF = 15        # half length of a pill
    THICK = 5.5      # pill radius
    ANGLE = 0        # degrees, rising to the right
    RUBBER = (122, 122, 130)

    def __init__(self, parent, on_press):
        super().__init__(parent, 176, 50, on_press)

    def _ends(self, b, k=1):
        a = math.radians(self.ANGLE)
        dx, dy = self.HALF * math.cos(a), self.HALF * math.sin(a)
        cx, cy = b["cx"], b["cy"]
        return (cx - dx) * k, (cy + dy) * k, (cx + dx) * k, (cy - dy) * k

    def hit(self, x, y):
        for name, b in self.BUTTONS.items():
            if abs(x - b["cx"]) <= self.HALF + 6 and abs(y - b["cy"]) <= 14:
                return name
        return None

    def render(self, pressed):
        img, d = self.new_image()
        k = SS
        for name, b in self.BUTTONS.items():
            x1, y1, x2, y2 = self._ends(b, k)
            is_down = name == pressed
            sink = 0.75 * k if is_down else 0

            _capsule(d, (x1, y1), (x2, y2), (self.THICK + 3.5) * k, RECESS_RIM)
            _capsule(d, (x1 + k, y1 + 1.5 * k), (x2 + k, y2 + 1.5 * k), (self.THICK + 2.5) * k, RECESS_FLOOR)

            def pill(draw, dx, dy, fill, x1=x1, y1=y1 + sink, x2=x2, y2=y2 + sink):
                _capsule(draw, (x1 + dx, y1 + dy), (x2 + dx, y2 + dy), self.THICK * k, fill)

            _soft_shadow(img, pill, (0, (0.5 if is_down else 2) * k), 1.5 * k)
            body = _shade(self.RUBBER, -0.2 if is_down else 0)
            _bevel(d, pill, body, light=0.3, dark=-0.6)
        return img

    def draw_fallback(self, state):
        for name, b in self.BUTTONS.items():
            x1, y1, x2, y2 = self._ends(b)
            color = '#5E5E66' if name == state else '#7A7A82'
            self.create_line(x1, y1, x2, y2, width=self.THICK * 2, capstyle='round',
                             fill=color, tags='fallback')

    def draw_overlay(self, state):
        font = ui.get_fonts(self)['tiny']
        for name, b in self.BUTTONS.items():
            self.create_text(b["cx"], 41, text=name, font=font, fill=ENGRAVED_TEXT, tags='overlay')


# ---------------------------------------------------------------------------
# D-Pad
# ---------------------------------------------------------------------------
class DPad(_HardwareCanvas):
    """One-piece cross-shaped D-Pad sitting in a round recess.

    Reports (direction, pressed) to on_change; show() lets other input
    sources (keyboard, gamepad) light it up too.
    """

    SIZE = 116
    ARM = 16        # half width of an arm
    REACH = 46      # half length of the cross
    RADIUS = 6      # corner rounding
    DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")
    STATES = (None,) + DIRECTIONS

    def __init__(self, parent, on_change):
        self.on_change = on_change
        self.mouse_direction = None
        self.held = []      # directions currently shown pressed, newest last
        super().__init__(parent, self.SIZE, self.SIZE)
        self.bind('<ButtonPress-1>', self._mouse_press)
        self.bind('<B1-Motion>', self._mouse_move)
        self.bind('<ButtonRelease-1>', self._mouse_release)

    def render(self, pressed):
        Image, ImageDraw, ImageFilter, _ = _pil()
        img, d = self.new_image()
        k = SS
        size = self.SIZE * k
        c = size / 2
        arm, reach, radius = self.ARM * k, self.REACH * k, self.RADIUS * k

        def cross(draw, dx=0, dy=0, fill=255):
            draw.rounded_rectangle([c - reach + dx, c - arm + dy, c + reach + dx, c + arm + dy], radius, fill=fill)
            draw.rounded_rectangle([c - arm + dx, c - reach + dy, c + arm + dx, c + reach + dy], radius, fill=fill)

        # Round recess
        rec = 55 * k
        d.ellipse([c - rec, c - rec, c + rec, c + rec], fill=RECESS_RIM)
        d.ellipse([c - rec + 2 * k, c - rec + 3 * k, c + rec + k, c + rec + k], fill=RECESS_FLOOR)

        _soft_shadow(img, cross, (2 * k, 4 * k), 3 * k)
        _bevel(d, cross, (50, 50, 57), light=0.3, dark=-0.65)

        mask = Image.new('L', (size, size), 0)
        cross(ImageDraw.Draw(mask))

        # Subtle top-to-bottom sheen
        sheen = Image.linear_gradient('L').resize((size, size)).point(lambda v: int(45 - v * 0.3) if v < 150 else 0)
        img.paste((255, 255, 255, 255), (0, 0), Image.composite(sheen, Image.new('L', (size, size), 0), mask))

        # Pressed arm sinks in
        if pressed:
            region = Image.new('L', (size, size), 0)
            inner = arm - 2 * k
            boxes = {
                "UP": [c - arm, c - reach, c + arm, c - inner],
                "DOWN": [c - arm, c + inner, c + arm, c + reach],
                "LEFT": [c - reach, c - arm, c - inner, c + arm],
                "RIGHT": [c + inner, c - arm, c + reach, c + arm],
            }
            ImageDraw.Draw(region).rectangle(boxes[pressed], fill=255)
            region = region.filter(ImageFilter.GaussianBlur(2 * k))
            region = Image.composite(region, Image.new('L', (size, size), 0), mask)
            img.paste((26, 26, 30, 255), (0, 0), region.point(lambda v: int(v * 0.5)))

        # Concave centre dimple
        dim = 9 * k
        d.ellipse([c - dim, c - dim, c + dim, c + dim], fill=(34, 34, 39, 255))
        d.ellipse([c - dim + k, c - dim + 1.5 * k, c + dim, c + dim], fill=(66, 66, 74, 255))
        d.ellipse([c - dim + k, c - dim + k, c + dim - k, c + dim - 1.5 * k], fill=(44, 44, 50, 255))

        # Embossed arrows
        tip, half, depth = 37 * k, 6 * k, 7 * k
        arrows = {
            "UP": [(c, c - tip), (c - half, c - tip + depth), (c + half, c - tip + depth)],
            "DOWN": [(c, c + tip), (c - half, c + tip - depth), (c + half, c + tip - depth)],
            "LEFT": [(c - tip, c), (c - tip + depth, c - half), (c - tip + depth, c + half)],
            "RIGHT": [(c + tip, c), (c + tip - depth, c - half), (c + tip - depth, c + half)],
        }
        for direction, pts in arrows.items():
            if direction == pressed:
                d.polygon([(x, y + k) for x, y in pts], fill=(12, 12, 14, 255))
            else:
                d.polygon([(x, y + k) for x, y in pts], fill=(88, 88, 96, 255))
                d.polygon(pts, fill=(22, 22, 26, 255))
        return img

    def draw_fallback(self, pressed):
        c, a, r = self.SIZE // 2, self.ARM, self.REACH
        body, dark = '#323239', '#18181C'
        self.create_rectangle(c - r, c - a, c + r, c + a, fill=body, outline=dark, width=2, tags='fallback')
        self.create_rectangle(c - a, c - r, c + a, c + r, fill=body, outline='', tags='fallback')
        self.create_line(c - a + 1, c - r + 1, c - a + 1, c + r - 1, fill=dark, width=2, tags='fallback')
        self.create_line(c + a - 1, c - r + 1, c + a - 1, c + r - 1, fill=dark, width=2, tags='fallback')
        t, h, dep = 37, 6, 7
        arrows = {
            "UP": (c, c - t, c - h, c - t + dep, c + h, c - t + dep),
            "DOWN": (c, c + t, c - h, c + t - dep, c + h, c + t - dep),
            "LEFT": (c - t, c, c - t + dep, c - h, c - t + dep, c + h),
            "RIGHT": (c + t, c, c + t - dep, c - h, c + t - dep, c + h),
        }
        for direction, pts in arrows.items():
            self.create_polygon(pts, fill='#8A8A93' if direction == pressed else dark, tags='fallback')

    def show(self, direction, pressed):
        if direction in self.held:
            self.held.remove(direction)
        if pressed:
            self.held.append(direction)
        self.set_state(self.held[-1] if self.held else None)

    def _direction_at(self, x, y):
        dx, dy = x - self.SIZE / 2, y - self.SIZE / 2
        slack = 4
        if max(abs(dx), abs(dy)) < 6 or max(abs(dx), abs(dy)) > self.REACH + slack:
            return None
        if abs(dx) > abs(dy):
            return ("RIGHT" if dx > 0 else "LEFT") if abs(dy) <= self.ARM + slack else None
        return ("DOWN" if dy > 0 else "UP") if abs(dx) <= self.ARM + slack else None

    def _set_mouse_direction(self, direction):
        if direction == self.mouse_direction:
            return
        if self.mouse_direction:
            self.on_change(self.mouse_direction, False)
        self.mouse_direction = direction
        if direction:
            self.on_change(direction, True)

    def _mouse_press(self, event):
        self._set_mouse_direction(self._direction_at(event.x, event.y))

    def _mouse_move(self, event):
        # Rolling the thumb across arms switches direction, like the real thing
        self._set_mouse_direction(self._direction_at(event.x, event.y))

    def _mouse_release(self, event):
        self._set_mouse_direction(None)


# ---------------------------------------------------------------------------
# Screen bezel
# ---------------------------------------------------------------------------
class ScreenBezel(_HardwareCanvas):
    """Evenly rounded screen surround holding the game screen.

    self.screen is the frame games draw into.
    """

    SCREEN_W = 334
    SCREEN_H = 367
    SIDE = 22
    TOP = 28
    BOTTOM = 26
    CORNER = 16
    LABEL = "NOSTALGIKIT DOT DISPLAY"

    def __init__(self, parent):
        self.led_on = True
        super().__init__(parent, self.SCREEN_W + 2 * self.SIDE, self.SCREEN_H + self.TOP + self.BOTTOM)
        self.screen = tk.Frame(self, bg=ui.SCREEN_BG, bd=0, highlightthickness=0)
        self.create_window(self.SIDE, self.TOP, window=self.screen, anchor='nw',
                           width=self.SCREEN_W, height=self.SCREEN_H)

    def _shape(self, draw, dx, dy, fill, k=SS):
        """Rounded rectangle with equal corners."""
        w, h = self.w * k, self.h * k
        draw.rounded_rectangle([3 * k + dx, 2 * k + dy, w - 3 * k + dx, h - 5 * k + dy],
                               self.CORNER * k, fill=fill)

    def render(self, state):
        img, d = self.new_image()
        k = SS
        bezel = _rgb(ui.BEZEL)
        _soft_shadow(img, self._shape, (0, 3 * k), 3 * k, strength=110)
        self._shape(d, 0, -k, _shade(bezel, 0.18))   # light top lip
        self._shape(d, 0, 0, bezel + (255,))

        # Screen window: a dark lip so the glass looks set into the bezel
        sx0, sy0 = self.SIDE * k, self.TOP * k
        sx1, sy1 = sx0 + self.SCREEN_W * k, sy0 + self.SCREEN_H * k
        d.rectangle([sx0 - 3 * k, sy0 - 3 * k, sx1 + 2 * k, sy1 + 2 * k], fill=_shade(bezel, -0.45))
        d.rectangle([sx0 - k, sy0 - k, sx1 + 2 * k, sy1 + 2 * k], fill=_shade(bezel, 0.12))
        return img

    def draw_fallback(self, state):
        self.create_rectangle(3, 2, self.w - 3, self.h - 5, fill=ui.BEZEL, outline='', tags='fallback')

    def draw_overlay(self, state):
        fonts = ui.get_fonts(self)
        self.create_text(self.w // 2, self.TOP // 2 + 1, text=self.LABEL, font=fonts['tiny'],
                         fill=ui.BEZEL_TEXT, tags='overlay')

        # Power LED (green, bottom-right) + label
        ly = self.TOP + self.SCREEN_H + self.BOTTOM // 2 - 1
        lx = self.w - 26
        led = '#8CFF5A' if self.led_on else '#3F4A33'
        self.create_text(lx - 8, ly, text="POWER", anchor='e', font=fonts['tiny'],
                         fill=ui.BEZEL_TEXT, tags='overlay')
        self.create_oval(lx - 4, ly - 4, lx + 4, ly + 4, fill=led, outline='#3E4430', tags='overlay')
        if self.led_on:
            self.create_oval(lx - 2, ly - 3, lx, ly - 1, fill='#E6FFD8', outline='', tags='overlay')

    def set_led(self, on):
        self.led_on = on
        self.set_state(None)


class SpeakerGrille(_HardwareCanvas):
    """Round speaker holes (hexagonal pattern) moulded into the body."""

    ROWS = 4
    COLS = 5
    PITCH = 9
    HOLE = 2.6

    def __init__(self, parent):
        super().__init__(parent, 56, 44)

    def _holes(self, k=1):
        for row in range(self.ROWS):
            offset = self.PITCH / 2 if row % 2 else 0
            count = self.COLS - (1 if row % 2 else 0)
            for col in range(count):
                yield (6 + offset + col * self.PITCH) * k, (8 + row * self.PITCH) * k

    def render(self, state):
        img, d = self.new_image()
        k = SS
        r = self.HOLE * k
        for x, y in self._holes(k):
            d.ellipse([x - r - 0.5 * k, y - r - 0.5 * k, x + r + 0.5 * k, y + r + 0.5 * k], fill=(196, 187, 158, 255))
            d.ellipse([x - r + 0.5 * k, y - r + 0.8 * k, x + r, y + r], fill=(110, 102, 82, 255))
        return img

    def draw_fallback(self, state):
        r = self.HOLE
        for x, y in self._holes():
            self.create_oval(x - r, y - r, x + r, y + r, fill='#8A8268', outline='', tags='fallback')
