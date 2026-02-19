# script.rpy

init -2 python:
    # Словари особенностей
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
    ENEMY_IMAGES = [
        "images/enemies/enemy1.png"

    ]
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

init -1 python:
    import random
    import math

    class Sloomp:
        def __init__(self, name, level, base_stats, features):
            self.name = name
            self.level = level
            self.base_stats = base_stats.copy()
            self.features = features
            self.bonus_stats = {key: 0 for key in base_stats.keys()}
            self.exp = 0
            self.exp_to_next = 100  # первый уровень на 100 опыта
            self.final_stats = self.calc_final_stats()
            self.current_hp = self.final_stats["hp"]
            
        def calc_final_stats(self):
            raw_stats = {}
            for key in self.base_stats:
                raw_stats[key] = self.base_stats.get(key, 0) + self.bonus_stats.get(key, 0)
            multiplier = {
                "hp": 1.0,
                "defense": 1.0,
                "attack_speed": 1.0,
                "attack_power": 1.0,
                "crit_chance": 1.0,
                "crit_damage": 1.0,
                "vampirism": 1.0,
                "accuracy": 1.0,
                "evasion": 1.0
            }
            for feat in self.features:
                for stat, mult in feat.get("multipliers", {}).items():
                    multiplier[stat] *= mult
            final = {}
            for stat, val in raw_stats.items():
                final[stat] = val * multiplier[stat]
                if stat in ["hp", "defense", "attack_power"]:
                    final[stat] = int(final[stat])
            return final
        
        def level_up(self):
            self.level += 1
            self.base_stats["hp"] += 10
            self.base_stats["defense"] += 2
            self.base_stats["attack_speed"] += 0.5
            self.base_stats["attack_power"] += 3
            self.base_stats["crit_chance"] += 0.01
            self.base_stats["crit_damage"] += 0.05
            self.base_stats["vampirism"] += 0.005
            self.base_stats["accuracy"] += 0.01
            self.base_stats["evasion"] += 0.01
            self.final_stats = self.calc_final_stats()
            self.current_hp = self.final_stats["hp"]
        
        def add_exp(self, amount):
            self.exp += amount
            while self.exp >= self.exp_to_next:
                self.exp -= self.exp_to_next
                self.level_up()
                self.exp_to_next = 100 * self.level  # каждый уровень требует на 100 больше
    
    class Enemy:
        def __init__(self, name, level, base_stats, image):
            self.name = name
            self.level = level
            self.base_stats = base_stats.copy()
            self.final_stats = self.base_stats
            self.current_hp = self.final_stats["hp"]
            self.image = image
    

    
    def generate_enemy(wave):
        level = wave  # сложность зависит от волны
        base_stats = {
            "hp": 40 + level * 12,
            "defense": 3 + level * 2,
            "attack_speed": 0.8 + level * 0.1,
            "attack_power": 6 + level * 3,
            "crit_chance": 0.03 + level * 0.01,
            "crit_damage": 1.5 + level * 0.05,
            "vampirism": 0.0,
            "accuracy": 0.85 + level * 0.01,
            "evasion": 0.05 + level * 0.01
        }
        names = ["Гнилой слизень", "Колючий черт", "Огненный шар", "Ледяная кроха", "Каменный голем"]
        name = random.choice(names) + f" Lv.{level}"
        image = random.choice(ENEMY_IMAGES)
        return Enemy(name, level, base_stats, image)
    
    def generate_sloomp(level):
        base_stats = {
            "hp": 50 + level * 10,
            "defense": 5 + level * 2,
            "attack_speed": 1.0 + level * 0.1,
            "attack_power": 8 + level * 3,
            "crit_chance": 0.05 + level * 0.01,
            "crit_damage": 1.5 + level * 0.05,
            "vampirism": 0.0 + level * 0.005,
            "accuracy": 0.9 + level * 0.01,
            "evasion": 0.1 + level * 0.01
        }
        feature_types = ["color", "form", "face"]
        if level >= 3:
            feature_types.append("hat")
        if level >= 5:
            feature_types.append("clothes")
        if level >= 7:
            feature_types.append("mask")
        if level >= 9:
            feature_types.append("weapon")
        if level >= 10 and random.random() < 0.3:
            feature_types.append("aura")
        
        features = []
        for ftype in feature_types:
            options = FEATURE_DB[ftype]
            chosen = random.choice(list(options.values()))
            chosen_with_type = chosen.copy()
            chosen_with_type["type"] = ftype
            features.append(chosen_with_type)
        
        name_parts = []
        for feat in features:
            if feat["type"] in ("color", "form", "face"):
                name_parts.append(feat["display_name"])
        if not name_parts:
            name_parts = ["Хлюп"]
        name = " ".join(name_parts) + f" Lv.{level}"
        
        return Sloomp(name, level, base_stats, features)
    
    def generate_random_upgrade():
        stats = [
            ("hp", "Здоровье", 10),
            ("defense", "Защита", 2),
            ("attack_power", "Сила атаки", 3),
            ("attack_speed", "Скорость атаки", 0.2),
            ("crit_chance", "Шанс крита", 0.05),
            ("crit_damage", "Крит. урон", 0.1),
            ("vampirism", "Вампиризм", 0.03),
            ("accuracy", "Точность", 0.05),
            ("evasion", "Уклонение", 0.05)
        ]
        stat, name, value = random.choice(stats)
        return {
            "name": f"+{value} к {name}",
            "description": f"Увеличивает {name} на {value}",
            "stat": stat,
            "value": value
        }
    
    def apply_upgrade(upgrade):
        player = persistent.current_sloomp
        if player:
            player.bonus_stats[upgrade["stat"]] += upgrade["value"]
            player.final_stats = player.calc_final_stats()
            player.current_hp = player.final_stats["hp"]
            renpy.restart_interaction()
    
    def reset_game():
        persistent.sloomp_collection = []
        persistent.current_sloomp = None
        persistent.gold = 0
        store.wave = 1
        # опыт хранится в объекте хлюпа, здесь не нужен
default persistent.gold = 0
default persistent.sloomp_collection = []
default persistent.current_sloomp = None
default wave = 1

label start:
    if not persistent.sloomp_collection:
        $ start_choices = [generate_sloomp(1) for _ in range(3)]
        call screen choose_sloomp("Выбери своего первого хлюпа", start_choices, after_battle=False)
    else:
        if persistent.current_sloomp is None:
            $ persistent.current_sloomp = persistent.sloomp_collection[0]
        call screen main_menu
    return

label after_choice:
    call screen main_menu
    return

label after_choice_battle:
    jump start_battle

label start_battle:
    if persistent.current_sloomp is None:
        if persistent.sloomp_collection:
            $ persistent.current_sloomp = persistent.sloomp_collection[0]
        else:
            jump start
    $ current_enemy = generate_enemy(wave)
    $ persistent.current_sloomp.current_hp = persistent.current_sloomp.final_stats["hp"]
    $ current_enemy.current_hp = current_enemy.final_stats["hp"]
    $ battle_active = True
    $ battle_finished = False
    $ last_player_attack_time = 0.0
    $ last_enemy_attack_time = 0.0
    $ hit_effect_target = None
    $ hit_effect_type = None
    call screen battle_animation
    # Управление сюда не вернётся, потому что battle_animation делает Jump при завершении
    return

label battle_loop:
    $ player = persistent.current_sloomp
    $ e = current_enemy
    
    # Сбрасываем здоровье для честного боя
    $ player.current_hp = player.final_stats["hp"]
    $ e.current_hp = e.final_stats["hp"]
    
    # Отладка: начальные значения
    $ renpy.notify("Бой начат: игрок HP={}, враг HP={}".format(player.current_hp, e.current_hp))
    
    show screen battle_animation
    
    while player.current_hp > 0 and e.current_hp > 0:
        # Уменьшаем урон для наглядности (делим на 2, чтобы бой длился дольше)
        $ player_dmg = int((player.final_stats["attack_power"] * player.final_stats["attack_speed"]))
        $ enemy_dmg = int((e.final_stats["attack_power"] * e.final_stats["attack_speed"]))
        
        # Учитываем защиту
        $ player_dmg = max(1, player_dmg - e.final_stats["defense"])
        $ enemy_dmg = max(1, enemy_dmg - player.final_stats["defense"])
        
        $ e.current_hp -= player_dmg
        $ player.current_hp -= enemy_dmg
        
        # Принудительное обновление экрана
        $ renpy.restart_interaction()
        with None  # заставляет Ren'Py перерисовать всё
        
        # Отладка: показываем текущие значения
        $ renpy.notify("Ход: игрок HP={}, враг HP={}".format(player.current_hp, e.current_hp))
        
        # Пауза для визуализации (0.3 секунды, hard=False даёт возможность обрабатывать события)
        $ renpy.pause(0.3, hard=False)

    
    hide screen battle_animation
    
    # Отладка: результат
    if player.current_hp > 0:
        $ renpy.notify("Игрок победил!")
        $ victory = True
    else:
        $ renpy.notify("Игрок проиграл!")
        $ victory = False
        $ player.current_hp = max(1, player.final_stats["hp"] // 2)  # восстановление после поражения
    
    $ battle_victory = victory
    $ battle_log = []
    $ last_enemy = e
    
    jump show_battle_result

label show_battle_result:
    if battle_victory:
        $ exp_gain = 10 * wave
        $ persistent.current_sloomp.add_exp(exp_gain)
        $ wave += 1
        if wave % 10 == 0:
            $ boss_choices = [generate_sloomp(wave // 10) for _ in range(3)]
            call screen choose_sloomp("Выбери нового хлюпа", boss_choices, after_battle=True)
        else:
            call screen choose_upgrade
    else:
        call screen battle_result(False, battle_log, last_enemy)
    return

label after_battle:
    call screen main_menu
    return

label after_upgrade:
    jump start_battle