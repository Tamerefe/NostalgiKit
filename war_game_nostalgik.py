"""
NostalgiKit War Game
Turn-based combat between character classes.

Copyright (c) 2025 NostalgiKit Project
Licensed under MIT License - see LICENSE file for details
"""

import random
import tkinter as tk

import nostalgik_ui as ui

CHARACTER_CLASSES = {
    "WARRIOR": {
        "sprite": "♠", "hp": 120, "attack": (18, 28), "heal": (15, 25),
        "special": {"name": "RAGE", "damage": (30, 40), "desc": "Berserker strike"},
        "desc": "High HP, strong attacks",
    },
    "MAGE": {
        "sprite": "♦", "hp": 80, "attack": (12, 20), "heal": (25, 35),
        "special": {"name": "FIREBALL", "damage": (35, 45), "desc": "Magic blast"},
        "desc": "Low HP, powerful magic",
    },
    "ROGUE": {
        "sprite": "♣", "hp": 100, "attack": (15, 25), "heal": (20, 30),
        "special": {"name": "BACKSTAB", "damage": (40, 50), "desc": "Critical strike"},
        "desc": "Balanced, high crit",
    },
    "PALADIN": {
        "sprite": "♥", "hp": 110, "attack": (16, 24), "heal": (30, 40),
        "special": {"name": "HOLY LIGHT", "damage": (25, 35), "desc": "Damage + heal"},
        "desc": "Good HP, best healing",
    },
}
CLASS_NAMES = list(CHARACTER_CLASSES)
SPECIAL_COOLDOWN = 3


class NostalgiKitWarGame(ui.NostalgiKitGame):
    TITLE = "WAR GAME"

    def on_show(self):
        self.selected_character = 0
        self.wins = 0
        self.losses = 0
        self.show_intro()

    # ------------------------------------------------------------------
    # Character select
    # ------------------------------------------------------------------
    def show_intro(self):
        self.screen = "character_select"
        self.clear_body()
        self.set_status(f"W{self.wins} L{self.losses}")
        self.set_hint(ui.hint(("▲▼", "PICK"), ("X", "FIGHT"), ("Y", "EXIT")))

        ui.heading(self.body, "CHOOSE FIGHTER")
        items = [(f"{CHARACTER_CLASSES[n]['sprite']} {n}", None) for n in CLASS_NAMES]
        ui.menu_list(self.body, items, self.selected_character).pack(fill='x')

        data = CHARACTER_CLASSES[CLASS_NAMES[self.selected_character]]
        stats = (f"HP {data['hp']}   ATK {data['attack'][0]}-{data['attack'][1]}\n"
                 f"HEAL {data['heal'][0]}-{data['heal'][1]}   SP {data['special']['name']}\n\n"
                 f"{data['desc']}")
        ui.label(self.body, stats, size='small').pack(expand=True)

    # ------------------------------------------------------------------
    # Battle
    # ------------------------------------------------------------------
    def start_battle(self):
        self.player_class = CLASS_NAMES[self.selected_character]
        player = CHARACTER_CLASSES[self.player_class]
        self.player_hp = self.player_max_hp = player["hp"]

        self.enemy_class = random.choice([n for n in CLASS_NAMES if n != self.player_class])
        enemy = CHARACTER_CLASSES[self.enemy_class]
        self.enemy_hp = self.enemy_max_hp = enemy["hp"]

        special = player["special"]
        self.actions = [
            {"name": "ATTACK", "desc": f"Deal {player['attack'][0]}-{player['attack'][1]} damage"},
            {"name": "DEFEND", "desc": "Block 50% of next hit"},
            {"name": "HEAL", "desc": f"Restore {player['heal'][0]}-{player['heal'][1]} HP"},
            {"name": special["name"], "desc": special["desc"], "special": True},
        ]

        self.battle_log = ["The battle begins!"]
        self.selected_action = 0
        self.game_over = False
        self.battle_round = 1
        self.defending = False
        self.enemy_defending = False
        self.special_cooldown = 0
        self.screen = "battle"
        self.show_battle_screen()

    def show_battle_screen(self):
        self.clear_body()
        self.set_status(f"ROUND {self.battle_round}")

        # Fighters + HP bars
        arena = tk.Frame(self.body, bg=ui.SCREEN_BG)
        arena.pack(fill='x', padx=10, pady=(8, 2))
        self._fighter(arena, "YOU", self.player_class, self.player_hp, self.player_max_hp,
                      self.defending).pack(side='left')
        ui.label(arena, "VS", size='large').pack(side='left', expand=True)
        self._fighter(arena, "FOE", self.enemy_class, self.enemy_hp, self.enemy_max_hp,
                      self.enemy_defending).pack(side='right')

        # Battle log (last two messages)
        log = tk.Frame(self.body, bg=ui.SCREEN_DARK, padx=6, pady=4)
        log.pack(fill='x', padx=10, pady=4)
        for line in self.battle_log[-2:]:
            ui.label(log, line, size='tiny', inverted=True, anchor='w', wraplength=290).pack(fill='x')

        if self.game_over:
            self.show_game_over()
        else:
            self.show_action_menu()

    def _fighter(self, parent, who, class_name, hp, max_hp, defending):
        frame = tk.Frame(parent, bg=ui.SCREEN_BG)
        sprite = CHARACTER_CLASSES[class_name]["sprite"]
        ui.label(frame, f"{who}: {class_name}", size='tiny').pack()
        ui.label(frame, f"{sprite}\n/|\\\n/ \\", size='text').pack()
        ui.label(frame, ui.bar_text(hp, max_hp, 8), size='tiny').pack()
        ui.label(frame, f"{hp}/{max_hp}" + (" DEF" if defending else ""), size='tiny').pack()
        return frame

    def show_action_menu(self):
        self.set_hint(ui.hint(("▲▼", "PICK"), ("X", "ACT"), ("Y", "FLEE")))
        disabled = {i for i, a in enumerate(self.actions)
                    if a.get("special") and self.special_cooldown > 0}
        items = []
        for i, action in enumerate(self.actions):
            name = action["name"]
            if i in disabled:
                name += f" ({self.special_cooldown})"
            items.append((name, action["desc"]))
        ui.menu_list(self.body, items, self.selected_action, disabled=disabled).pack(fill='x', pady=2)

    def show_game_over(self):
        self.set_hint(ui.hint(("X", "REMATCH"), ("Y", "FIGHTERS")))
        won = self.enemy_hp <= 0
        box = tk.Frame(self.body, bg=ui.SCREEN_BG)
        box.pack(expand=True)
        ui.label(box, "VICTORY!" if won else "DEFEAT!", size='large').pack()
        ui.label(box, f"Rounds: {self.battle_round}   Record: {self.wins}W-{self.losses}L",
                 size='small').pack(pady=4)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def on_dpad(self, direction, pressed=True):
        if not pressed or direction not in ("UP", "DOWN"):
            return
        step = -1 if direction == "UP" else 1
        if self.screen == "character_select":
            self.selected_character = (self.selected_character + step) % len(CLASS_NAMES)
            self.show_intro()
        elif self.screen == "battle" and not self.game_over:
            self.selected_action = (self.selected_action + step) % len(self.actions)
            self.show_battle_screen()

    def on_button(self, button):
        if self.screen == "character_select":
            if button in ("X", "START"):
                self.start_battle()
            elif button == "Y":
                self.exit_to_hub()
        elif self.screen == "battle":
            if self.game_over:
                if button in ("X", "START"):
                    self.start_battle()
                elif button == "Y":
                    self.show_intro()
            elif button == "X":
                self.execute_action()
            elif button == "Y":
                self.show_intro()  # flee back to character select

    # ------------------------------------------------------------------
    # Combat rules
    # ------------------------------------------------------------------
    def _hit_enemy(self, damage):
        """Apply player damage, honouring the enemy's defend stance."""
        if self.enemy_defending:
            damage //= 2
            self.enemy_defending = False
        self.enemy_hp = max(0, self.enemy_hp - damage)
        return damage

    def _hit_player(self, damage):
        if self.defending:
            damage //= 2
            self.defending = False
        self.player_hp = max(0, self.player_hp - damage)
        return damage

    def execute_action(self):
        action = self.actions[self.selected_action]
        if action.get("special") and self.special_cooldown > 0:
            return

        player = CHARACTER_CLASSES[self.player_class]
        name = action["name"]

        if name == "ATTACK":
            dmg = self._hit_enemy(random.randint(*player["attack"]))
            self.battle_log.append(f"You attack for {dmg} damage!")
        elif name == "DEFEND":
            self.defending = True
            self.battle_log.append("You raise your guard!")
        elif name == "HEAL":
            amount = random.randint(*player["heal"])
            self.player_hp = min(self.player_max_hp, self.player_hp + amount)
            self.battle_log.append(f"You heal {amount} HP!")
        else:  # special
            special = player["special"]
            if name == "HOLY LIGHT":
                dmg = self._hit_enemy(random.randint(*special["damage"]))
                amount = random.randint(15, 25)
                self.player_hp = min(self.player_max_hp, self.player_hp + amount)
                self.battle_log.append(f"HOLY LIGHT: {dmg} dmg, +{amount} HP!")
            else:
                success = 0.8 if name == "BACKSTAB" else 0.75
                if random.random() < success:
                    dmg = self._hit_enemy(random.randint(*special["damage"]))
                    self.battle_log.append(f"{name} hits for {dmg} damage!")
                else:
                    self.battle_log.append(f"{name} missed!")
            self.special_cooldown = SPECIAL_COOLDOWN

        if self.enemy_hp <= 0:
            self.end_battle(won=True)
            return

        self.enemy_action()
        self.battle_round += 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

        if self.player_hp <= 0:
            self.end_battle(won=False)
            return
        self.show_battle_screen()

    def end_battle(self, won):
        self.game_over = True
        if won:
            self.wins += 1
            self.battle_log.append(f"{self.enemy_class} is defeated!")
        else:
            self.losses += 1
            self.battle_log.append(f"{self.enemy_class} wins the battle!")
        self.show_battle_screen()

    def enemy_action(self):
        enemy = CHARACTER_CLASSES[self.enemy_class]
        foe = self.enemy_class
        health_ratio = self.enemy_hp / self.enemy_max_hp

        action = "attack"
        if health_ratio < 0.3 and random.random() < 0.6:
            action = "heal"
        elif health_ratio < 0.5 and random.random() < 0.3:
            action = "defend"
        elif random.random() < 0.2:
            action = "special"
        elif random.random() < 0.1:
            action = "defend"

        if action == "attack":
            blocked = self.defending
            dmg = self._hit_player(random.randint(*enemy["attack"]))
            self.battle_log.append(f"{foe} attacks for {dmg}!" + (" (blocked)" if blocked else ""))
        elif action == "heal":
            amount = random.randint(*enemy["heal"])
            self.enemy_hp = min(self.enemy_max_hp, self.enemy_hp + amount)
            self.battle_log.append(f"{foe} heals {amount} HP!")
        elif action == "defend":
            self.enemy_defending = True
            self.battle_log.append(f"{foe} raises its guard!")
        else:
            special = enemy["special"]
            sp_name = special["name"]
            if sp_name == "HOLY LIGHT":
                dmg = self._hit_player(random.randint(*special["damage"]))
                amount = random.randint(10, 20)
                self.enemy_hp = min(self.enemy_max_hp, self.enemy_hp + amount)
                self.battle_log.append(f"{foe}: {sp_name}! {dmg} dmg, +{amount} HP")
            else:
                success = 0.7 if sp_name == "BACKSTAB" else 0.65
                if random.random() < success:
                    blocked = self.defending
                    dmg = self._hit_player(random.randint(*special["damage"]))
                    self.battle_log.append(f"{foe}: {sp_name} for {dmg}!" + (" (blocked)" if blocked else ""))
                else:
                    self.battle_log.append(f"{foe}'s {sp_name} missed!")


WarGame = NostalgiKitWarGame
