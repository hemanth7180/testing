import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

import random
import time
import sys
import json
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, description: str, value: int, damage: int = 0):
        self.name = name
        self.description = description
        self.value = value
        self.damage = damage

class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory: List[Item] = []
        self.current_room = None
        self.attack_power = 10
        self.armor = 0
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"\n{self.name} picked up {item.name}!")

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def gain_experience(self, exp: int):
        self.experience += exp
        print(f"\nGained {exp} experience points!")
        while self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack_power += 5
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        print(f"\n{self.name} leveled up to level {self.level}!")
        print(f"Health: {self.health}, Attack: {self.attack_power}")

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.armor)
        self.health -= actual_damage
        print(f"\n{self.name} takes {actual_damage} damage!")
        if self.health <= 0:
            print(f"\n{self.name} has been defeated!")
            sys.exit()

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"\n{self.name} healed for {amount} HP! Current health: {self.health}")

    def show_inventory(self):
        if not self.inventory:
            print("\nInventory is empty!")
        else:
            print("\nInventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description} (Value: {item.value})")

    def show_status(self):
        print(f"\n{self.name}'s Status:")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Attack: {self.attack_power}")
        print(f"Armor: {self.armor}")
        print(f"Gold: {self.gold}")
        print(f"Experience: {self.experience}/{self.exp_to_next_level}")

class Enemy:
    def __init__(self, name: str, health: int, attack: int, exp_reward: int, gold_reward: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        print(f"\n{self.name} takes {damage} damage! ({self.health}/{self.max_health} HP)")
        return self.health <= 0

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, Room] = {}
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_item(self, item: Item):
        self.items.append(item)

    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)

    def remove_item(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("Items in the room:")
            for item in self.items:
                print(f"- {item.name}: {item.description}")
        if self.enemies:
            print("Enemies in the room:")
            for enemy in self.enemies:
                print(f"- {enemy.name} ({enemy.health}/{enemy.max_health} HP)")
        if self.exits:
            print("Exits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.player = None
        self.rooms: Dict[str, Room] = {}
        self.running = False

    def setup_game(self):
        # Create items
        sword = Item("Sword", "A sharp steel blade", 50, 10)
        potion = Item("Health Potion", "Restores 30 HP", 20)
        shield = Item("Shield", "Increases armor by 5", 40)
        treasure = Item("Treasure Chest", "Contains 100 gold", 100)

        # Create enemies
        goblin = Enemy("Goblin", 30, 5, 20, 10)
        skeleton = Enemy("Skeleton", 40, 8, 30, 15)
        troll = Enemy("Troll", 60, 12, 50, 25)

        # Create rooms
        entrance = Room("Entrance Hall", "A grand hall with ancient carvings.")
        armory = Room("Armory", "A room filled with rusty weapons and armor.")
        treasury = Room("Treasury", "A glittering room filled with wealth.")
        dungeon = Room("Dungeon", "A dark, damp cell with chains on the walls.")

        # Set up exits
        entrance.add_exit("north", armory)
        entrance.add_exit("east", treasury)
        armory.add_exit("south", entrance)
        armory.add_exit("east", dungeon)
        treasury.add_exit("west", entrance)
        dungeon.add_exit("west", armory)

        # Add items and enemies
        entrance.add_item(potion)
        armory.add_item(sword)
        armory.add_item(shield)
        treasury.add_item(treasure)
        treasury.add_enemy(goblin)
        dungeon.add_enemy(skeleton)
        dungeon.add_enemy(troll)

        self.rooms = {
            "entrance": entrance,
            "armory": armory,
            "treasury": treasury,
            "dungeon": dungeon
        }

    def combat(self, player: Player, enemy: Enemy):
        print(f"\nCombat begins: {player.name} vs {enemy.name}!")
        while enemy.health > 0 and player.health > 0:
            # Player's turn
            damage = random.randint(player.attack_power - 5, player.attack_power + 5)
            if enemy.take_damage(damage):
                print(f"\n{enemy.name} defeated!")
                player.gain_experience(enemy.exp_reward)
                player.gold += enemy.gold_reward
                print(f"Earned {enemy.gold_reward} gold!")
                return True
            time.sleep(1)

            # Enemy's turn
            damage = random.randint(enemy.attack - 3, enemy.attack + 3)
            player.take_damage(damage)
            time.sleep(1)
        return False

    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "gold": self.player.gold,
                "inventory": [{"name": item.name, "description": item.description, 
                             "value": item.value, "damage": item.damage} 
                            for item in self.player.inventory],
                "current_room": self.player.current_room.name,
                "attack_power": self.player.attack_power,
                "armor": self.player.armor,
                "level": self.player.level,
                "experience": self.player.experience,
                "exp_to_next_level": self.player.exp_to_next_level
            }
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\nGame saved to {filename}")

    def load_game(self, filename: str = "savegame.json"):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data["player"]["name"])
            self.player.health = save_data["player"]["health"]
            self.player.max_health = save_data["player"]["max_health"]
            self.player.gold = save_data["player"]["gold"]
            self.player.attack_power = save_data["player"]["attack_power"]
            self.player.armor = save_data["player"]["armor"]
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.exp_to_next_level = save_data["player"]["exp_to_next_level"]
            
            for item_data in save_data["player"]["inventory"]:
                self.player.inventory.append(Item(
                    item_data["name"],
                    item_data["description"],
                    item_data["value"],
                    item_data.get("damage", 0)
                ))
            
            self.player.current_room = self.rooms[save_data["player"]["current_room"]]
            print(f"\nGame loaded from {filename}")
        except FileNotFoundError:
            print("\nNo save file found!")
            return False
        return True

    def start(self):
        print("\nWelcome to Dungeon Adventure!")
        name = input("Enter your character's name: ").strip()
        self.player = Player(name)
        self.setup_game()
        self.player.current_room = self.rooms["entrance"]
        self.running = True
        print("\nType 'help' for commands.")

        while self.running:
            self.player.current_room.describe()
            command = input("\nWhat do you want to do? ").strip().lower().split()
            if not command:
                continue

            action = command[0]
            args = command[1:] if len(command) > 1 else []

            if action == "go" and args:
                direction = args[0]
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                else:
                    print("\nCan't go that way!")
            
            elif action == "take" and args:
                item_name = " ".join(args)
                item = self.player.current_room.remove_item(item_name)
                if item:
                    self.player.add_item(item)
                    if item.name == "Shield":
                        self.player.armor += 5
                else:
                    print("\nNo such item in the room!")
            
            elif action == "use" and args:
                item_name = " ".join(args)
                item = self.player.remove_item(item_name)
                if item:
                    if item.name == "Health Potion":
                        self.player.heal(30)
                    else:
                        print("\nCan't use that item!")
                        self.player.add_item(item)
                else:
                    print("\nNo such item in inventory!")
            
            elif action == "attack" and args:
                enemy_name = " ".join(args)
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == enemy_name.lower():
                        if self.combat(self.player, enemy):
                            self.player.current_room.enemies.remove(enemy)
                        break
                else:
                    print("\nNo such enemy in the room!")
            
            elif action == "inventory":
                self.player.show_inventory()
            
            elif action == "status":
                self.player.show_status()
            
            elif action == "save":
                self.save_game()
            
            elif action == "load":
                self.load_game()
            
            elif action == "help":
                print("\nCommands:")
                print("go [direction] - Move to another room")
                print("take [item] - Pick up an item")
                print("use [item] - Use an item")
                print("attack [enemy] - Attack an enemy")
                print("inventory - Show inventory")
                print("status - Show player status")
                print("save - Save game")
                print("load - Load game")
                print("quit - Exit game")
            
            elif action == "quit":
                print("\nThanks for playing!")
                self.running = False
            
            else:
                print("\nUnknown command! Type 'help' for commands.")

