# game_logic.rpy — генерация врагов/хлюпов, улучшения, слияние, бой

init -1 python:
    import random
    import math

    def _enemy_stat(wave, stat_key):
        B = store.ENEMY_BASE
        P = store.ENEMY_PER_WAVE
        power = getattr(store, "ENEMY_WAVE_POWER", 1.18)
        base = B.get(stat_key, 0)
        per = P.get(stat_key, 0)
        scale = math.pow(power, wave - 1) if wave > 1 else 1.0
        return base + per * (wave - 1) * scale

    def generate_enemy(wave):
        level = max(1, wave)
        base_stats = {
            "hp": int(_enemy_stat(wave, "hp")),
            "defense": _enemy_stat(wave, "defense"),
            "attack_speed": max(store.ATTACK_SPEED_MIN, _enemy_stat(wave, "attack_speed")),
            "attack_power": _enemy_stat(wave, "attack_power"),
            "crit_chance": _enemy_stat(wave, "crit_chance"),
            "crit_damage": _enemy_stat(wave, "crit_damage"),
            "vampirism": 0.0,
            "accuracy": _enemy_stat(wave, "accuracy"),
            "evasion": _enemy_stat(wave, "evasion"),
        }
        if base_stats.get("defense") is not None and isinstance(base_stats["defense"], float):
            base_stats["defense"] = int(base_stats["defense"])
        names = ["Гнилой слизень", "Колючий черт", "Огненный шар", "Ледяная кроха", "Каменный голем"]
        name = random.choice(names) + " (волна " + str(wave) + ")"
        image = random.choice(store.ENEMY_IMAGES)
        return store.Enemy(name, level, base_stats, image)

    def _sloomp_base_stats(level):
        B = store.SLOOMP_BASE
        P = store.SLOOMP_PER_LEVEL
        stats = {}
        for key in B:
            stats[key] = B[key] + P.get(key, 0) * (level - 1)
        return stats

    def generate_sloomp(level):
        level = max(1, level)
        base_stats = _sloomp_base_stats(level)
        feature_types = []
        for ftype, min_lvl, chance in getattr(store, "FEATURE_LEVELS", [("color", 1, 1.0), ("form", 1, 1.0), ("face", 1, 1.0)]):
            if level >= min_lvl and random.random() <= chance:
                feature_types.append(ftype)
        if not feature_types:
            feature_types = ["color", "form", "face"]
        features = []
        for ftype in feature_types:
            options = store.FEATURE_DB.get(ftype, {})
            if not options:
                continue
            chosen = random.choice(list(options.values())).copy()
            chosen["type"] = ftype
            features.append(chosen)
        name_parts = [f["display_name"] for f in features if f["type"] in ("color", "form", "face")]
        if not name_parts:
            name_parts = ["Хлюп"]
        name = " ".join(name_parts)
        return store.Sloomp(name, level, base_stats, features)

    def generate_upgrade_options(count=None, exclude_stats=None):
        count = count or store.UPGRADE_CHOICES_COUNT
        exclude_stats = set(exclude_stats or [])
        opts = list(store.UPGRADE_STAT_OPTIONS)
        chosen = []
        available = [(s, n, v) for s, n, v in opts if s not in exclude_stats]
        while len(chosen) < count and available:
            s, n, v = random.choice(available)
            chosen.append({
                "stat": s,
                "name": "+{} к {}".format(v, n),
                "value": v,
                "description": "Увеличивает {} на {}".format(n, v),
            })
            available = [(a, b, c) for a, b, c in available if a != s]
        return chosen

    def apply_upgrade(upgrade):
        player = persistent.current_sloomp
        if not player:
            return
        player.bonus_stats[upgrade["stat"]] = player.bonus_stats.get(upgrade["stat"], 0) + upgrade["value"]
        player.final_stats = player.calc_final_stats()
        player.current_hp = min(player.current_hp, player.final_stats["hp"])
        player.current_hp = max(player.current_hp, 0)
        renpy.restart_interaction()

    def give_gold_for_wave(wave):
        base = getattr(store, "GOLD_BASE_PER_WAVE", 5)
        per = getattr(store, "GOLD_PER_WAVE", 3)
        return base + wave * per

    def reset_run():
        store.wave = store.WAVE_START
        for s in persistent.sloomp_collection:
            s.final_stats = s.calc_final_stats()
            s.current_hp = s.final_stats["hp"]
        store.battle_aborted = False

    def do_reroll_upgrades():
        if store.rerolls_left <= 0:
            renpy.notify("Рероллы закончились")
            return
        store.rerolls_left -= 1
        exclude = [u["stat"] for u in store.current_upgrade_choices]
        store.current_upgrade_choices = generate_upgrade_options(store.UPGRADE_CHOICES_COUNT, exclude_stats=exclude)
        renpy.notify("Новые варианты! Осталось рероллов: " + str(store.rerolls_left))
        renpy.restart_interaction()

    def abort_battle():
        store.battle_active = False
        store.battle_finished = True
        store.battle_aborted = True

    def reset_game():
        persistent.sloomp_collection = []
        persistent.current_sloomp = None
        persistent.gold = 0
        if not hasattr(persistent, "shop_bonuses"):
            persistent.shop_bonuses = {}
        store.wave = store.WAVE_START
        store.battle_aborted = False
        store.battle_active = False
        store.battle_finished = False

    def buy_global_upgrade(stat_name):
        if not hasattr(persistent, "shop_bonuses"):
            persistent.shop_bonuses = {}
        cur = persistent.shop_bonuses.get(stat_name, 0)
        max_lvl = getattr(store, "SHOP_STAT_MAX_LEVEL", 99)
        if cur >= max_lvl:
            renpy.notify("Достигнут максимум улучшений")
            return
        base = getattr(store, "SHOP_STAT_COST_BASE", 12)
        mult = getattr(store, "SHOP_STAT_COST_MULT", 8)
        cost = base + mult * (cur + 1)
        if persistent.gold < cost:
            renpy.notify("Недостаточно золота")
            return
        persistent.gold -= cost
        persistent.shop_bonuses[stat_name] = cur + 1
        for s in persistent.sloomp_collection:
            s.final_stats = s.calc_final_stats()
            s.current_hp = min(s.current_hp, s.final_stats["hp"])
        if hasattr(store, "on_shop_bought"):
            store.on_shop_bought()
        renpy.notify("Улучшение куплено для всех хлюпов!")
        renpy.restart_interaction()
