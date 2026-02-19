# balance.rpy — все коэффициенты и настройки баланса игры

init -2 python:
    # --- Волны и прогресс ---
    WAVE_START = 1
    GOLD_BASE_PER_WAVE = 5
    GOLD_PER_WAVE = 3          # золото за волну = GOLD_BASE_PER_WAVE + wave * GOLD_PER_WAVE (или степенная формула)
    EXP_PER_WAVE_BASE = 8
    EXP_PER_WAVE_MULT = 2      # опыт за победу

    # --- Хлюп: базовые статы (уровень 1) и прирост за уровень ---
    SLOOMP_BASE = {
        "hp": 35,
        "defense": 3,
        "attack_speed": 0.9,
        "attack_power": 5,
        "crit_chance": 0.04,
        "crit_damage": 1.4,
        "vampirism": 0.0,
        "accuracy": 0.88,
        "evasion": 0.08,
    }
    SLOOMP_PER_LEVEL = {
        "hp": 6,
        "defense": 1,
        "attack_speed": 0.04,
        "attack_power": 1.5,
        "crit_chance": 0.008,
        "crit_damage": 0.03,
        "vampirism": 0.003,
        "accuracy": 0.008,
        "evasion": 0.008,
    }
    SLOOMP_EXP_BASE = 100
    SLOOMP_EXP_PER_LEVEL = 100

    # --- Враг: степенной прирост по волне (wave_power ~ 1.15–1.25) ---
    ENEMY_WAVE_POWER = 1.18
    ENEMY_BASE = {
        "hp": 28,
        "defense": 2,
        "attack_speed": 0.75,
        "attack_power": 4,
        "crit_chance": 0.02,
        "crit_damage": 1.35,
        "vampirism": 0.0,
        "accuracy": 0.82,
        "evasion": 0.04,
    }
    ENEMY_PER_WAVE = {
        "hp": 6,
        "defense": 0.8,
        "attack_speed": 0.03,
        "attack_power": 1.2,
        "crit_chance": 0.006,
        "crit_damage": 0.025,
        "vampirism": 0.0,
        "accuracy": 0.006,
        "evasion": 0.006,
    }

    # --- Особенности хлюпов: с какого уровня/волны и с какой вероятностью добавляются ---
    FEATURE_LEVELS = [
        ("color", 1, 1.0),
        ("form", 1, 1.0),
        ("face", 1, 1.0),
        ("hat", 4, 0.35),
        ("clothes", 7, 0.25),
        ("mask", 10, 0.2),
        ("weapon", 13, 0.18),
        ("aura", 16, 0.12),
    ]
    # Уровень для генерации хлюпа при выборе (всегда 1 для выбора в начале/боссе)
    SLOOMP_CHOICE_LEVEL = 1
    BOSS_SLOOMP_LEVEL_BONUS = 0  # + к уровню за босса (0 = все 1 ур)

    # --- Улучшения после волны (выбор одной из трёх) ---
    UPGRADE_STAT_OPTIONS = [
        ("hp", "Здоровье", 4),
        ("defense", "Защита", 1),
        ("attack_power", "Сила атаки", 1.5),
        ("attack_speed", "Скорость атаки", 0.08),
        ("crit_chance", "Шанс крита", 0.02),
        ("crit_damage", "Крит. урон", 0.05),
        ("vampirism", "Вампиризм", 0.015),
        ("accuracy", "Точность", 0.03),
        ("evasion", "Уклонение", 0.03),
    ]
    UPGRADE_CHOICES_COUNT = 3
    REROLLS_PER_RUN = 3

    # --- Магазин постоянных улучшений (для всех хлюпов) ---
    SHOP_STAT_COST_BASE = 12
    SHOP_STAT_COST_MULT = 8
    SHOP_STAT_MAX_LEVEL = 99
    SHOP_STAT_VALUE_PER_LEVEL = {
        "hp": 4, "defense": 1, "attack_speed": 0.05, "attack_power": 1,
        "crit_chance": 0.015, "crit_damage": 0.05, "vampirism": 0.01,
        "accuracy": 0.02, "evasion": 0.02,
    }

    # --- Бой ---
    MIN_DAMAGE = 1
    ATTACK_SPEED_MIN = 0.1
    HIT_EFFECT_DURATION = 0.2
    BATTLE_TICK_INTERVAL = 0.05
