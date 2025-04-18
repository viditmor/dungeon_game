import random
import json
import os
import hashlib

# --------- Level Class ----------
class Level:
    def __init__(self, hero): 
        self.size = 5
        self.level = 1
        self.grid = [['#' for _ in range(self.size)] for _ in range(self.size)]
        self.hero = hero
        self.hero_won = False
        self.events_triggered = {}
        self.grid[0][0] = '_'
        self.events_triggered[(0, 0)] = True
        self.special_rooms = {
            'trap': [],
            'treasure': [],
            'battle': [],
            'exit': None
        }
        self.place_special_rooms()

    def place_special_rooms(self):
        positions = [(x, y) for x in range(self.size) for y in range(self.size) if (x, y) != (0, 0)]
        random.shuffle(positions)
        self.special_rooms['trap'] = [positions.pop() for _ in range(1 + self.level)]
        self.special_rooms['treasure'] = [positions.pop() for _ in range(1 + self.level)]
        self.special_rooms['battle'] = [positions.pop() for _ in range(1 + self.level)]
        self.special_rooms['exit'] = positions.pop()

    def print_grid(self):
        for y in range(self.size):
            for x in range(self.size):
                if (x, y) == self.hero.position:
                    print('🧍', end='')
                elif (x, y) == self.special_rooms['exit']:
                    
                    if self.grid[y][x] == '_':
                        print('🚪', end='')  
                    else:
                        print(self.grid[y][x], end=' ')
                else:
                    print(self.grid[y][x], end=' ')
            print()

    def check_game_over(self):
        if self.hero.health <= 0:
            print("\n💀 Your HP dropped to 0. Game Over!")
            exit()

    def move_player(self, direction):
        old_position = self.hero.position
        new_position = self.hero.move(direction, self.size)

        if new_position != old_position:
            x, y = new_position
            self.grid[y][x] = '_'
            self.trigger_event(x, y)
            self.print_grid()
        else:
            print("⚠️ You hit a wall.")

    def trigger_event(self, x, y):
        if (x, y) in self.events_triggered:
            return

        self.events_triggered[(x, y)] = True

        if (x, y) in self.special_rooms['trap']:
            print("⚠️ You stepped into a trap! -5 HP")
            self.hero.health -= 5 + (2 * self.level)
            self.check_game_over()

        elif (x, y) in self.special_rooms['treasure']:
            index = self.special_rooms['treasure'].index((x, y))
            if index == 0:
                print("🎁 Treasure Room 1: Choose reward:")
                print("1. Sword (+10 Attack)")
                print("2. Shield (+10 HP)")
                choice = input("Enter 1 or 2: ")
                if choice == '1':
                    self.hero.attack_power += 10 + (5 * self.level)
                    print("🗡️ You equipped a Sword! Attack Power increased by 10")
                else:
                    self.hero.health += 10 + (5 * self.level)
                    print("🛡️ You equipped a Shield! Health increased by 10")
            else:
                print("🎁 Treasure Room 2: Choose item to collect:")
                print("1. Healing Potion (+30 HP when used)")
                print("2. Strength Elixir (+5 Attack when used)")
                choice = input("Enter 1 or 2: ")
                if choice == '1':
                    self.hero.inventory.append("Healing Potion")
                    print("🧪 Healing Potion added to inventory.")
                else:
                    self.hero.inventory.append("Strength Elixir")
                    print("💪 Strength Elixir added to inventory.")

        elif (x, y) in self.special_rooms['battle']:
            print("⚔️ You found a battle site.")
            enemy = Monster(self.level)
            self.battle(self.hero, enemy)
            self.check_game_over()

        elif (x, y) == self.special_rooms['exit']:
            print("🚪 You've reached the dungeon exit.")
            print("What do you want to do?")
            print("1. Fight the Final Boss")
            print("2. Explore More")
            choice = input("Enter 1 or 2: ")
            if choice == '1':
                print("⚔️ Prepare for the final battle!")
                final_boss = Boss(self.level)
                self.battle(self.hero, final_boss)
                self.check_game_over()
                if self.hero.health > 0:
                    self.hero_won = True
                    print("🎉 You have defeated the Boss. Level Cleared! Level Up! 🎉")
                    self.hero.gain_xp(100)
            else:
                print("🧭 Continuing exploration.")
                self.grid[y][x] = '🚪'  
                self.special_rooms['exit'] = (x, y) 
                self.events_triggered.pop((x, y), None)

    def battle(self, player, mob):
        while player.health > 0 and mob.health > 0:
            try:
                action = int(input("\nChoose action: 1) Attack  2) Defend  3) Use Item\n> "))
            except ValueError:
                print("❌ Invalid input.")
                continue

            if action == 1:
                player.attack(mob)
            elif action == 2:
                player.defend()
            elif action == 3:
                print(f"Inventory: {player.inventory}")
                item = input("Enter item name to use:\n> ").strip()
                player.use_item(item)
            else:
                print("❌ Invalid action.")
                continue

            if mob.health > 0:
                mob_action = random.choice(["attack", "defend"])
                if mob_action == "attack":
                    mob.attack(player)
                else:
                    mob.defend()

            player.show_stats()
            mob.show_stats()

        if player.health > 0:
            print("\n🎉 You defeated the monster! +50xp")
            player.gain_xp(50)
        else:
            print("\n💀 You have been defeated.")


# --------- Base Class ----------
class Entity:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.defending = False 


# --------- Hero Class ----------
class Hero(Entity):
    def __init__(self):
        super().__init__(name="Hero", health=100, attack_power=10)
        self.level = 1
        self.xp = 0
        self.inventory = ["Healing Potion", "Strength Elixir"]  # list with possible duplicates
        self.position = (0, 0)

    def show_inventory(self):
        if not self.inventory:
            print("🎒 Inventory is empty.")
            return

        print("🎒 Inventory:")
        unique_items = set(self.inventory)
        for item in unique_items:
            count = self.inventory.count(item)
            print(f"- {item} x{count}")

    def use_item(self, item_name):
        if item_name in self.inventory:
            if item_name == "Healing Potion":
                self.health += 30
                print(f"{self.name} used a Healing Potion! +30 HP")
            elif item_name == "Strength Elixir":
                self.attack_power += 5
                print(f"{self.name} drank a Strength Elixir! +5 Attack Power")
            self.inventory.remove(item_name)  # removes only one instance
        else:
            print(f"❌ {item_name} not found in inventory!")

    def attack(self, other):
        damage = self.attack_power
        if other.defending:
            damage /= 2
            print(f"{other.name} is defending! Damage reduced to {damage:.1f}")
            other.defending = False
        print(f"{self.name} attacks {other.name} for {damage:.1f} damage!")
        other.health -= damage

    def defend(self):
        self.defending = True
        print(f"{self.name} is defending and will take reduced damage next turn.")

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.health += 20
        self.attack_power += 5
        print(f"🆙 {self.name} leveled up! Now Level {self.level} | ❤️ +20 | ⚔️ +5")

    def move(self, direction, size):
        dx, dy = 0, 0
        if direction == "north":
            dy = -1
        elif direction == "south":
            dy = 1
        elif direction == "east":
            dx = 1
        elif direction == "west":
            dx = -1
        else:
            print("❌ Invalid direction.")
            return self.position

        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        if 0 <= new_x < size and 0 <= new_y < size:
            self.position = (new_x, new_y)
            print(f"📍 Moved to {self.position}")
        else:
            print("Choose another direction\n")
        return self.position

    def show_stats(self):
        print(f"👤 {self.name} | ❤️ {self.health:.1f} | ⚔️ {self.attack_power} | 🧠 XP: {self.xp} | 🎖️ Level: {self.level}")


# --------- Monster Class ----------
class Monster(Entity):
    def __init__(self, world_level):
        name = "Monster"
        health = 50 + (world_level * 10)
        attack = 5 + (world_level * 5)
        super().__init__(name, health, attack)

    def attack(self, other):
        damage = self.attack_power
        if other.defending:
            damage /= 2
            print(f"{other.name} is defending! Damage reduced to {damage:.1f}")
            other.defending = False
        print(f"{self.name} attacks {other.name} for {damage:.1f} damage!")
        other.health -= damage

    def defend(self):
        self.defending = True
        print(f"{self.name} is defending and will take reduced damage next turn.")

    def show_stats(self):
        print(f"👤 {self.name} | ❤️ {self.health:.1f}")


# --------- Boss Class ----------
class Boss(Entity):
    def __init__(self, world_level):
        name = "Boss"
        health = 100 + (world_level * 10)
        attack = 10 + (world_level * 5)
        super().__init__(name, health, attack)

    def attack(self, other):
        damage = self.attack_power
        if other.defending:
            damage /= 2
            print(f"{other.name} is defending! Damage reduced to {damage:.1f}")
            other.defending = False
        print(f"{self.name} attacks {other.name} for {damage:.1f} damage!")
        other.health -= damage

    def defend(self, damage=None):
        self.defending = True
        print(f"{self.name} is defending and will take reduced damage next turn.")
    
    def show_stats(self):
        print(f"👤 {self.name} | ❤️ {self.health:.1f}")


# --------- Save and Load ----------
def save_game(hero, level):
        data = {
            "hero": {
                "name": hero.name,
                "health": hero.health,
                "attack_power": hero.attack_power,
                "xp": hero.xp,
                "level": hero.level,
                "inventory": hero.inventory,
                "position": hero.position
            },
            "level": {
                "level_num": level.level,
                "grid": level.grid,
                "events_triggered": [list(pos) for pos in level.events_triggered.keys()],
                "special_rooms": {
                    "trap": level.special_rooms['trap'],
                    "treasure": level.special_rooms['treasure'],
                    "battle": level.special_rooms['battle'],
                    "exit": level.special_rooms['exit']
                }
            }
        }

        # Serialize and hash the data
        json_data = json.dumps(data, indent=4)
        hash_digest = hashlib.sha256(json_data.encode()).hexdigest()

        with open("savegame.json", "w") as file:
            file.write(json_data)

        with open("savegame.hash", "w") as hash_file:
            hash_file.write(hash_digest)

        print("💾 Game saved successfully!")


def load_game():
    if not os.path.exists("savegame.json") or not os.path.exists("savegame.hash"):
        print("❌ No save file found.")
        return None, None

    with open("savegame.json", "r") as file:
        json_data = file.read()

    with open("savegame.hash", "r") as hash_file:
        saved_hash = hash_file.read()

    current_hash = hashlib.sha256(json_data.encode()).hexdigest()
    if current_hash != saved_hash:
        print("⚠️ Save file is corrupted or has been tampered with!")
        return None, None

    data = json.loads(json_data)
    hero_data = data["hero"]
    level_data = data["level"]

    # Rebuild hero
    hero = Hero()
    hero.name = hero_data["name"]
    hero.health = hero_data["health"]
    hero.attack_power = hero_data["attack_power"]
    hero.xp = hero_data["xp"]
    hero.level = hero_data["level"]
    hero.inventory = hero_data["inventory"]
    hero.position = tuple(hero_data["position"])

    # Rebuild level
    level = Level(hero)
    level.level = level_data["level_num"]
    level.grid = level_data["grid"]
    level.events_triggered = {tuple(pos): True for pos in level_data["events_triggered"]}
    level.special_rooms = {
        'trap': [tuple(pos) for pos in level_data["special_rooms"]["trap"]],
        'treasure': [tuple(pos) for pos in level_data["special_rooms"]["treasure"]],
        'battle': [tuple(pos) for pos in level_data["special_rooms"]["battle"]],
        'exit': tuple(level_data["special_rooms"]["exit"])
    }

    print("📂 Game loaded successfully!")
    return hero, level




# --------- Run Game ----------
def game_loop():
    player = Hero()
    current_level_number = 1
    max_level = 3

    print("🎮 Welcome to the Dungeon Adventure!")
    player.show_stats()

    while current_level_number <= max_level:
        print(f"\n🌍 Entering Dungeon Level {current_level_number}...")
        level = Level(player)
        level.level = current_level_number
        level.print_grid()

        while True:
            print("\n🧭 What would you like to do?")
            print("1. Move (north, south, east, west)")
            print("2. Show Hero Stats")
            print("3. Show Inventory")
            print("4. Use Item")
            print("5. Show Dungeon Map")
            print("6. Save Game")
            print("7. Load Game")
            print("8. Quit Game")

            choice = input("> ").strip().lower()

            if choice == '1':
                direction = input("Enter direction (north/south/east/west): ").strip().lower()
                level.move_player(direction)

                if level.hero_won:
                    print(f"\n✅ You've completed Dungeon Level {current_level_number}!")
                    current_level_number += 1
                    player.position = (0, 0)  
                    break

            elif choice == '2':
                player.show_stats()

            elif choice == '3':
                player.show_inventory()

            elif choice == '4':
                if not player.inventory:
                    print("🎒 Your inventory is empty.")
                else:
                    player.show_inventory()
                    item = input("Enter item name to use:\n> ").strip()
                    player.use_item(item)

            elif choice == '5':
                level.print_grid()

            elif choice == '6':
                save_game(player, level)

            elif choice == '7':
                loaded_hero, loaded_level = load_game()
                if loaded_hero and loaded_level:
                    player = loaded_hero
                    level = loaded_level
                    current_level_number = loaded_level.level

            elif choice == '8':
                print("👋 Thanks for playing! See you next time.")
                return

            else:
                print("❌ Invalid choice. Try again.")

    print("🎉 Congratulations! You've cleared all dungeon levels! 🎊")



if __name__ == "__main__":
    game_loop()
