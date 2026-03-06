# features.rpy — справочники особенностей и изображений
# Новые модификаторы добавлены в конец каждого блока и закомментированы.

init -2 python:
    COLORS = {
        "red": {"name": "red", "display_name": "Красный", "multipliers": {"attack_power": 1.1, "crit_damage": 1.1}, "rarity": 1.2},
        "blue": {"name": "blue", "display_name": "Синий", "multipliers": {"defense": 1.1, "hp": 1.1}, "rarity": 1.2},
        "green": {"name": "green", "display_name": "Зелёный", "multipliers": {"vampirism": 1.2, "hp": 1.05}, "rarity": 1.0},
        "yellow": {"name": "yellow", "display_name": "Жёлтый", "multipliers": {"crit_chance": 1.2, "accuracy": 1.05}, "rarity": 0.8},
        # "orange": {"name": "orange", "display_name": "Оранжевый", "multipliers": {"attack_speed": 1.1, "attack_power": 1.05}},
        # "purple": {"name": "purple", "display_name": "Фиолетовый", "multipliers": {"evasion": 1.15, "crit_chance": 1.05}},
    }
    FORMS = {
        "round": {"name": "round", "display_name": "Круглый", "multipliers": {"hp": 1.2}, "rarity": 1.3},
        "spikey": {"name": "spikey", "display_name": "Колючий", "multipliers": {"attack_power": 1.15, "crit_damage": 1.1}, "rarity": 1.0},
        "drop": {"name": "drop", "display_name": "Капля", "multipliers": {"evasion": 1.2, "attack_speed": 1.1}, "rarity": 0.7},
        "donut": {"name": "donut", "display_name": "Тор", "multipliers": {"defense": 1.2, "hp": 1.05}},
        # "star": {"name": "star", "display_name": "Звёздчатый", "multipliers": {"crit_chance": 1.1, "crit_damage": 1.15}},
    }
    FACES = {
        "angry": {"name": "angry", "display_name": "Злой", "multipliers": {"attack_power": 1.1, "crit_chance": 1.1}, "image": "images/features/face/angry.png", "rarity": 1.1},
        "happy": {"name": "happy", "display_name": "Весёлый", "multipliers": {"evasion": 1.1, "accuracy": 1.05}, "image": "images/features/face/happy.png", "rarity": 1.1},
        "sad": {"name": "sad", "display_name": "Грустный", "multipliers": {"defense": 1.1, "hp": 1.1}, "image": "images/features/face/sad.png", "rarity": 0.8},
        # "cool": {"name": "cool", "display_name": "Крутой", "multipliers": {"crit_damage": 1.15, "accuracy": 1.1}, "image": "images/features/face/cool.png"},
        # "sleepy": {"name": "sleepy", "display_name": "Сонный", "multipliers": {"hp": 1.15, "evasion": 1.05}, "image": "images/features/face/sleepy.png"},
    }
    HATS = {
        "wizard": {"name": "wizard", "display_name": "Шляпа мага", "multipliers": {"crit_damage": 1.2, "attack_power": 1.05}, "image": "images/features/hat/wizard.png", "rarity": 1.0},
        "knight": {"name": "knight", "display_name": "Шлем рыцаря", "multipliers": {"defense": 1.2, "hp": 1.1}, "image": "images/features/hat/knight.png", "rarity": 1.2},
        # "crown": {"name": "crown", "display_name": "Корона", "multipliers": {"attack_power": 1.1, "defense": 1.1, "hp": 1.05}, "image": "images/features/hat/crown.png"},
        # "beret": {"name": "beret", "display_name": "Берет", "multipliers": {"accuracy": 1.15, "crit_chance": 1.05}, "image": "images/features/hat/beret.png"},
    }
    CLOTHES = {
        "robe": {"name": "robe", "display_name": "Мантия", "multipliers": {"hp": 1.1, "evasion": 1.1}, "image": "images/features/clothes/robe.png", "rarity": 1.1},
        "armor": {"name": "armor", "display_name": "Броня", "multipliers": {"defense": 1.2}, "image": "images/features/clothes/armor.png", "rarity": 0.9},
        # "cape": {"name": "cape", "display_name": "Плащ", "multipliers": {"evasion": 1.2, "attack_speed": 1.05}, "image": "images/features/clothes/cape.png"},
        # "vest": {"name": "vest", "display_name": "Жилет", "multipliers": {"hp": 1.1, "defense": 1.1}, "image": "images/features/clothes/vest.png"},
    }
    MASKS = {
        "skull": {"name": "skull", "display_name": "Маска черепа", "multipliers": {"crit_chance": 1.2, "vampirism": 1.1}, "image": "images/features/mask/skull.png", "rarity": 0.8},
        "hero": {"name": "hero", "display_name": "Маска героя", "multipliers": {"attack_power": 1.1, "accuracy": 1.1}, "image": "images/features/mask/hero.png", "rarity": 1.2},
        # "bandit": {"name": "bandit", "display_name": "Маска разбойника", "multipliers": {"evasion": 1.2, "attack_speed": 1.1}, "image": "images/features/mask/bandit.png"},
    }
    WEAPONS = {
        "sword": {"name": "sword", "display_name": "Меч", "multipliers": {"attack_power": 1.2}, "image": "images/features/weapon/sword.png", "rarity": 1.2},
        "staff": {"name": "staff", "display_name": "Посох", "multipliers": {"crit_damage": 1.2, "attack_speed": 1.1}, "image": "images/features/weapon/staff.png", "rarity": 0.8},
        # "axe": {"name": "axe", "display_name": "Топор", "multipliers": {"attack_power": 1.25, "attack_speed": 0.95}, "image": "images/features/weapon/axe.png"},
        # "bow": {"name": "bow", "display_name": "Лук", "multipliers": {"accuracy": 1.2, "crit_chance": 1.1}, "image": "images/features/weapon/bow.png"},
    }
    AURAS = {
        "fire": {"name": "fire", "display_name": "Огненная аура", "multipliers": {"attack_power": 1.2, "crit_chance": 1.1}, "image": "images/features/aura/fire.png", "rarity": 1.0},
        "ice": {"name": "ice", "display_name": "Ледяная аура", "multipliers": {"defense": 1.2, "evasion": 1.1}, "image": "images/features/aura/ice.png", "rarity": 1.0},
        # "lightning": {"name": "lightning", "display_name": "Аура молний", "multipliers": {"attack_speed": 1.15, "crit_damage": 1.1}, "image": "images/features/aura/lightning.png"},
        # "shadow": {"name": "shadow", "display_name": "Теневая аура", "multipliers": {"evasion": 1.2, "vampirism": 1.1}, "image": "images/features/aura/shadow.png"},
    }
    ALLIES = {
        "fairy": {"name": "fairy", "display_name": "Фея‑помощник", "multipliers": {"attack_power": 1.05, "accuracy": 1.05}, "rarity": 1.0},
        "spirit": {"name": "spirit", "display_name": "Дух‑спутник", "multipliers": {"hp": 1.05, "regen": 1.05}, "rarity": 1.0},
    }
    ENEMY_IMAGES = ["images/enemies/enemy1.png", "images/enemies/enemy2.png"]
    BOSS_IMAGES = ["images/enemies/boss1.png"]
    FEATURE_DB = {
        "color": COLORS,
        "form": FORMS,
        "face": FACES,
        "hat": HATS,
        "clothes": CLOTHES,
        "mask": MASKS,
        "weapon": WEAPONS,
        "aura": AURAS,
        "ally": ALLIES,
    }
