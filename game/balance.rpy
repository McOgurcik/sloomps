# balance.rpy — все коэффициенты и настройки баланса игры
# HP, атака и защита в 1000 раз больше. Пассивное восстановление (regen) — HP в секунду.
# Враги: первые 30 волн — монотонный рост (линейный по статам); с 31-й добавляется степенной; боссы отдельно усилены.
# Для каждого стата свои коэффициенты прироста (хлюп и враг).

define STAT_SCALE = 1000

init -2 python:
    # --- Волны и прогресс ---
    WAVE_START = 1
    GOLD_BASE_PER_WAVE = 5
    GOLD_PER_WAVE = 3
    EXP_PER_WAVE_BASE = 8
    EXP_PER_WAVE_MULT = 2

    # --- Лимиты характеристик (проценты 0–1; regen — макс HP/сек) ---
    STAT_CAPS = {
        "crit_chance": 1.0,
        "accuracy": 1.0,
        "evasion": 1.0,
        "vampirism": 1.0,
        "crit_damage": 5.0,
        "regen": 6000,
    }

    # --- Хлюп: базовые статы и прирост за уровень; для каждого стата свой множитель прироста ---
    SLOOMP_BASE = {
        "hp": 38000,
        "defense": 3200,
        "attack_speed": 0.95,
        "attack_power": 5200,
        "crit_chance": 0.05,
        "crit_damage": 1.45,
        "vampirism": 0.0,
        "accuracy": 0.9,
        "evasion": 0.1,
        "regen": 400,
    }
    SLOOMP_PER_LEVEL = {
        "hp": 5500,
        "defense": 900,
        "attack_speed": 0.04,
        "attack_power": 1400,
        "crit_chance": 0.008,
        "crit_damage": 0.03,
        "vampirism": 0.003,
        "accuracy": 0.008,
        "evasion": 0.008,
        "regen": 80,
    }
    SLOOMP_LEVEL_MULT = {
        "hp": 1.0, "defense": 1.0, "attack_speed": 1.0, "attack_power": 1.0,
        "crit_chance": 1.0, "crit_damage": 1.0, "vampirism": 1.0,
        "accuracy": 1.0, "evasion": 1.0, "regen": 1.0,
    }
    SLOOMP_EXP_BASE = 80
    SLOOMP_EXP_PER_LEVEL = 80
    SLOOMP_LEVEL_POWER_MIN = 0.35
    SLOOMP_LEVEL_POWER_MAX_LEVEL = 20

    # --- Враг: база и прирост за волну; первые 30 волн — только линейный рост (монотонно), с 31-й — степенной ---
    ENEMY_WAVE_MONOTONIC_UNTIL = 30
    EARLY_WAVE_MULT = {
        1: 0.58, 2: 0.64, 3: 0.70, 4: 0.76, 5: 0.82, 6: 0.87, 7: 0.91, 8: 0.94, 9: 0.97, 10: 1.0,
    }
    ENEMY_BASE = {
        "hp": 22000,
        "defense": 1400,
        "attack_speed": 0.7,
        "attack_power": 3200,
        "crit_chance": 0.018,
        "crit_damage": 1.3,
        "vampirism": 0.0,
        "accuracy": 0.8,
        "evasion": 0.03,
        "regen": 0,
    }
    ENEMY_PER_WAVE = {
        "hp": 4800,
        "defense": 150,
        "attack_speed": 0.022,
        "attack_power": 820,
        "crit_chance": 0.0045,
        "crit_damage": 0.018,
        "vampirism": 0.0,
        "accuracy": 0.0045,
        "evasion": 0.004,
        "regen": 20,
    }
    ENEMY_LINEAR_BY_STAT = {
        "hp": 0.042, "defense": 0.025, "attack_speed": 0.028, "attack_power": 0.024,
        "crit_chance": 0.025, "crit_damage": 0.04, "vampirism": 0.0,
        "accuracy": 0.032, "evasion": 0.03, "regen": 0.04,
    }
    ENEMY_POWER_BY_STAT = {
        "hp": 1.08, "defense": 1.07, "attack_speed": 1.05, "attack_power": 1.05,
        "crit_chance": 1.06, "crit_damage": 1.065, "vampirism": 1.0,
        "accuracy": 1.055, "evasion": 1.05, "regen": 1.07,
    }
    BOSS_STAT_MULT = 1.75
    BOSS_WAVE_EVERY = 10

    # --- Особенности хлюпов ---
    FEATURE_LEVELS = [
        ("color", 1, 1.0),
        ("form", 1, 1.0),
        ("face", 1, 1.0),
        ("hat", 10, 0.35),
        ("clothes", 20, 0.25),
        ("mask", 30, 0.2),
        ("weapon", 40, 0.18),
        ("aura", 50, 0.12),
    ]
    SLOOMP_CHOICE_LEVEL = 1
    BOSS_SLOOMP_LEVEL_BONUS = 0

    # --- Улучшения после волны ---
    UPGRADE_STAT_OPTIONS = [
        ("hp", "Здоровье", 4000),
        ("defense", "Защита", 1000),
        ("attack_power", "Сила атаки", 1500),
        ("attack_speed", "Скорость атаки", 0.08),
        ("crit_chance", "Шанс крита", 0.02),
        ("crit_damage", "Крит. урон", 0.05),
        ("vampirism", "Вампиризм", 0.025),
        ("accuracy", "Точность", 0.03),
        ("evasion", "Уклонение", 0.03),
        ("regen", "Восстановление HP", 120),
    ]
    UPGRADE_CHOICES_COUNT = 3
    REROLLS_PER_RUN = 3
    UPGRADE_REROLL_CHANCE = 0.12

    # --- Магазин постоянных улучшений ---
    SHOP_STAT_COST_BASE = 12
    SHOP_STAT_COST_MULT = 8
    SHOP_STAT_MAX_LEVEL = 99
    SHOP_STAT_VALUE_PER_LEVEL = {
        "hp": 4000, "defense": 1000, "attack_speed": 0.05, "attack_power": 1000,
        "crit_chance": 0.015, "crit_damage": 0.05, "vampirism": 0.01,
        "accuracy": 0.02, "evasion": 0.02, "regen": 100,
    }

    # --- Яйца хлюпов (кейсы с разной редкостью) ---
    EGG_TYPES = [
        {
            "id": "common",
            "name": "Простое яйцо",
            "description": "Недорогое яйцо, даёт хлюпов начального уровня с 2–4 особенностями.",
            "price": 60,
            "level": SLOOMP_CHOICE_LEVEL + 10,
            "level_spread": 2,
            "roll_count": 10,
        },
        {
            "id": "rare",
            "name": "Редкое яйцо",
            "description": "Хлюпы выше уровнем и с большим количеством особенностей.",
            "price": 150,
            "level": SLOOMP_CHOICE_LEVEL + 30,
            "level_spread": 4,
            "roll_count": 12,
        },
        {
            "id": "mythic",
            "name": "Мифическое яйцо",
            "description": "Очень редкие хлюпы с максимальным числом особенностей.",
            "price": 320,
            "level": SLOOMP_CHOICE_LEVEL + 50,
            "level_spread": 5,
            "roll_count": 15,
        },
    ]
    
    # --- Типы врагов ---
    ENEMY_TYPES = [
        {
            "id": "slime",
            "name": "Гнилой слизень",
            "image": "images/enemies/enemy1.png",
            "stat_multipliers": {
                "hp": 1.0, "defense": 1.0, "attack_speed": 1.0, "attack_power": 1.0,
                "crit_chance": 1.0, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 1.0, "regen": 1.0,
            },
        },
        {
            "id": "spike",
            "name": "Колючий черт",
            "image": "images/enemies/enemy2.png",
            "stat_multipliers": {
                "hp": 0.9, "defense": 1.1, "attack_speed": 1.1, "attack_power": 1.0,
                "crit_chance": 1.2, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 0.9, "regen": 1.0,
            },
        },
        {
            "id": "fire",
            "name": "Огненный шар",
            "image": "images/enemies/enemy1.png",
            "stat_multipliers": {
                "hp": 0.95, "defense": 0.9, "attack_speed": 1.0, "attack_power": 1.15,
                "crit_chance": 1.0, "crit_damage": 1.1, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 1.0, "regen": 0.5,
            },
        },
        {
            "id": "ice",
            "name": "Ледяная кроха",
            "image": "images/enemies/enemy2.png",
            "stat_multipliers": {
                "hp": 1.1, "defense": 1.15, "attack_speed": 0.85, "attack_power": 0.9,
                "crit_chance": 0.9, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 1.1, "regen": 1.2,
            },
        },
        {
            "id": "stone",
            "name": "Каменный голем",
            "image": "images/enemies/enemy1.png",
            "stat_multipliers": {
                "hp": 1.3, "defense": 1.25, "attack_speed": 0.75, "attack_power": 1.05,
                "crit_chance": 0.8, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 0.95, "evasion": 0.7, "regen": 0.8,
            },
        },
    ]
    
    BOSS_ENEMY_TYPES = [
        {
            "id": "boss_slime",
            "name": "Повелитель слизней",
            "image": "images/enemies/boss1.png",
            "stat_multipliers": {
                "hp": 1.0, "defense": 1.0, "attack_speed": 1.0, "attack_power": 1.0,
                "crit_chance": 1.0, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 1.0, "regen": 1.0,
            },
        },
        {
            "id": "boss_demon",
            "name": "Демон битвы",
            "image": "images/enemies/boss1.png",
            "stat_multipliers": {
                "hp": 0.95, "defense": 0.9, "attack_speed": 1.2, "attack_power": 1.15,
                "crit_chance": 1.3, "crit_damage": 1.2, "vampirism": 1.0,
                "accuracy": 1.1, "evasion": 1.1, "regen": 0.8,
            },
        },
        {
            "id": "boss_ice",
            "name": "Ледяной титан",
            "image": "images/enemies/boss1.png",
            "stat_multipliers": {
                "hp": 1.2, "defense": 1.3, "attack_speed": 0.8, "attack_power": 0.95,
                "crit_chance": 0.9, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 1.0, "regen": 1.5,
            },
        },
        {
            "id": "boss_fire",
            "name": "Огненный владыка",
            "image": "images/enemies/boss1.png",
            "stat_multipliers": {
                "hp": 0.9, "defense": 0.85, "attack_speed": 1.1, "attack_power": 1.25,
                "crit_chance": 1.1, "crit_damage": 1.3, "vampirism": 1.0,
                "accuracy": 1.05, "evasion": 0.95, "regen": 0.6,
            },
        },
        {
            "id": "boss_stone",
            "name": "Каменный страж",
            "image": "images/enemies/boss1.png",
            "stat_multipliers": {
                "hp": 1.4, "defense": 1.4, "attack_speed": 0.7, "attack_power": 1.1,
                "crit_chance": 0.85, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 0.9, "evasion": 0.6, "regen": 1.0,
            },
        },
    ]

    # --- Бой (regen применяется каждый тик: HP += regen * BATTLE_TICK_INTERVAL) ---
    MIN_DAMAGE = 1000
    ATTACK_SPEED_MIN = 0.1
    HIT_EFFECT_DURATION = 0.2
    BATTLE_TICK_INTERVAL = 0.05
