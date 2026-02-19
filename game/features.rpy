# features.rpy — справочники особенностей и изображений

init -2 python:
    COLORS = {
        "red": {"name": "red", "display_name": "Красный", "multipliers": {"attack_power": 1.1, "crit_damage": 1.1}},
        "blue": {"name": "blue", "display_name": "Синий", "multipliers": {"defense": 1.1, "hp": 1.1}},
        "green": {"name": "green", "display_name": "Зелёный", "multipliers": {"vampirism": 1.2, "hp": 1.05}},
        "yellow": {"name": "yellow", "display_name": "Жёлтый", "multipliers": {"crit_chance": 1.2, "accuracy": 1.05}},
    }
    FORMS = {
        "round": {"name": "round", "display_name": "Круглый", "multipliers": {"hp": 1.2}},
        "spiky": {"name": "spiky", "display_name": "Колючий", "multipliers": {"attack_power": 1.15, "crit_damage": 1.1}},
        "drop": {"name": "drop", "display_name": "Капля", "multipliers": {"evasion": 1.2, "attack_speed": 1.1}},
    }
    FACES = {
        "angry": {"name": "angry", "display_name": "Злой", "multipliers": {"attack_power": 1.1, "crit_chance": 1.1}, "image": "images/features/face/angry.png"},
        "happy": {"name": "happy", "display_name": "Весёлый", "multipliers": {"evasion": 1.1, "accuracy": 1.05}, "image": "images/features/face/happy.png"},
        "sad": {"name": "sad", "display_name": "Грустный", "multipliers": {"defense": 1.1, "hp": 1.1}, "image": "images/features/face/sad.png"},
    }
    HATS = {
        "wizard": {"name": "wizard", "display_name": "Шляпа мага", "multipliers": {"crit_damage": 1.2, "attack_power": 1.05}, "image": "images/features/hat/wizard.png"},
        "knight": {"name": "knight", "display_name": "Шлем рыцаря", "multipliers": {"defense": 1.2, "hp": 1.1}, "image": "images/features/hat/knight.png"},
    }
    CLOTHES = {
        "robe": {"name": "robe", "display_name": "Мантия", "multipliers": {"hp": 1.1, "evasion": 1.1}, "image": "images/features/clothes/robe.png"},
        "armor": {"name": "armor", "display_name": "Броня", "multipliers": {"defense": 1.2}, "image": "images/features/clothes/armor.png"},
    }
    MASKS = {
        "skull": {"name": "skull", "display_name": "Маска черепа", "multipliers": {"crit_chance": 1.2, "vampirism": 1.1}, "image": "images/features/mask/skull.png"},
        "hero": {"name": "hero", "display_name": "Маска героя", "multipliers": {"attack_power": 1.1, "accuracy": 1.1}, "image": "images/features/mask/hero.png"},
    }
    WEAPONS = {
        "sword": {"name": "sword", "display_name": "Меч", "multipliers": {"attack_power": 1.2}, "image": "images/features/weapon/sword.png"},
        "staff": {"name": "staff", "display_name": "Посох", "multipliers": {"crit_damage": 1.2, "attack_speed": 1.1}, "image": "images/features/weapon/staff.png"},
    }
    AURAS = {
        "fire": {"name": "fire", "display_name": "Огненная аура", "multipliers": {"attack_power": 1.2, "crit_chance": 1.1}, "image": "images/features/aura/fire.png"},
        "ice": {"name": "ice", "display_name": "Ледяная аура", "multipliers": {"defense": 1.2, "evasion": 1.1}, "image": "images/features/aura/ice.png"},
    }
    ENEMY_IMAGES = ["images/enemies/enemy1.png"]
    FEATURE_DB = {
        "color": COLORS,
        "form": FORMS,
        "face": FACES,
        "hat": HATS,
        "clothes": CLOTHES,
        "mask": MASKS,
        "weapon": WEAPONS,
        "aura": AURAS,
    }
