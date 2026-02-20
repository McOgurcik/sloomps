# game_logic.rpy — генерация врагов/хлюпов, улучшения, слияние, бой

init -1 python:
    import random
    import math

    def _enemy_stat(wave, stat_key):
        B = store.ENEMY_BASE
        P = store.ENEMY_PER_WAVE
        linear_by = getattr(store, "ENEMY_LINEAR_BY_STAT", {})
        power_by = getattr(store, "ENEMY_POWER_BY_STAT", {})
        early = getattr(store, "EARLY_WAVE_MULT", {}).get(min(wave, 10), 1.0)
        monotonic_until = getattr(store, "ENEMY_WAVE_MONOTONIC_UNTIL", 30)
        base = B.get(stat_key, 0)
        per = P.get(stat_key, 0)
        linear_c = linear_by.get(stat_key, 0.04)
        power_c = power_by.get(stat_key, 1.06)
        raw = base + per * (wave - 1)
        scale_linear = 1.0 + linear_c * (wave - 1)
        if wave <= monotonic_until:
            scale_power = 1.0
        else:
            scale_power = math.pow(power_c, wave - monotonic_until)
        return raw * scale_linear * scale_power * early

    def _apply_stat_caps(stats):
        caps = getattr(store, "STAT_CAPS", {})
        for stat, cap in caps.items():
            if stat in stats:
                stats[stat] = min(stats[stat], cap)
        return stats

    def generate_enemy(wave):
        level = max(1, wave)
        is_boss = (wave % getattr(store, "BOSS_WAVE_EVERY", 10)) == 0 and wave >= getattr(store, "BOSS_WAVE_EVERY", 10)
        mult = getattr(store, "BOSS_STAT_MULT", 1.8) if is_boss else 1.0
        
        # Выбираем тип врага
        enemy_types = getattr(store, "BOSS_ENEMY_TYPES", []) if is_boss else getattr(store, "ENEMY_TYPES", [])
        if not enemy_types:
            # Fallback на старую логику
            names = ["Гнилой слизень", "Колючий черт", "Огненный шар", "Ледяная кроха", "Каменный голем"]
            boss_names = ["Повелитель слизней", "Демон битвы", "Ледяной титан", "Огненный владыка", "Каменный страж"]
            name = (random.choice(boss_names) if is_boss else random.choice(names)) + " (волна " + str(wave) + ")"
            img_list = getattr(store, "BOSS_IMAGES", store.ENEMY_IMAGES) if is_boss else store.ENEMY_IMAGES
            image = random.choice(img_list) if img_list else store.ENEMY_IMAGES[0]
            base_stats = {
                "hp": int(_enemy_stat(wave, "hp") * mult),
                "defense": int(_enemy_stat(wave, "defense") * mult),
                "attack_speed": max(store.ATTACK_SPEED_MIN, _enemy_stat(wave, "attack_speed") * mult),
                "attack_power": int(_enemy_stat(wave, "attack_power") * mult),
                "crit_chance": min(1.0, _enemy_stat(wave, "crit_chance") * mult),
                "crit_damage": _enemy_stat(wave, "crit_damage") * mult,
                "vampirism": 0.0,
                "accuracy": min(1.0, _enemy_stat(wave, "accuracy") * mult),
                "evasion": min(1.0, _enemy_stat(wave, "evasion") * mult),
                "regen": int(_enemy_stat(wave, "regen") * mult),
            }
            base_stats = _apply_stat_caps(base_stats)
            return store.Enemy(name, level, base_stats, image)
        
        enemy_type = random.choice(enemy_types)
        type_mults = enemy_type.get("stat_multipliers", {})
        
        # Базовые статы без множителей типа
        base_stats = {
            "hp": int(_enemy_stat(wave, "hp") * mult),
            "defense": int(_enemy_stat(wave, "defense") * mult),
            "attack_speed": max(store.ATTACK_SPEED_MIN, _enemy_stat(wave, "attack_speed") * mult),
            "attack_power": int(_enemy_stat(wave, "attack_power") * mult),
            "crit_chance": min(1.0, _enemy_stat(wave, "crit_chance") * mult),
            "crit_damage": _enemy_stat(wave, "crit_damage") * mult,
            "vampirism": 0.0,
            "accuracy": min(1.0, _enemy_stat(wave, "accuracy") * mult),
            "evasion": min(1.0, _enemy_stat(wave, "evasion") * mult),
            "regen": int(_enemy_stat(wave, "regen") * mult),
        }
        
        # Применяем множители типа
        for stat_key, type_mult in type_mults.items():
            if stat_key in base_stats:
                base_stats[stat_key] *= type_mult
        
        # Целочисленные статы для отображения и боя
        for key in ("hp", "defense", "attack_power", "regen"):
            if key in base_stats:
                base_stats[key] = int(base_stats[key])
        
        base_stats = _apply_stat_caps(base_stats)
        name = enemy_type.get("name", "Враг") + " (волна " + str(wave) + ")"
        image = enemy_type.get("image", store.ENEMY_IMAGES[0] if hasattr(store, "ENEMY_IMAGES") else "images/enemies/enemy1.png")
        return store.Enemy(name, level, base_stats, image)

    def _sloomp_base_stats(level):
        B = store.SLOOMP_BASE
        P = store.SLOOMP_PER_LEVEL
        mult_by = getattr(store, "SLOOMP_LEVEL_MULT", {})
        stats = {}
        for key in B:
            lvl_mult = mult_by.get(key, 1.0)
            stats[key] = B[key] + P.get(key, 0) * (level - 1) * lvl_mult
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
                "type": "stat",
                "name": "+{} к {}".format(v, n),
                "value": v,
                "description": "Увеличивает {} на {}".format(n, v),
            })
            available = [(a, b, c) for a, b, c in available if a != s]
        reroll_chance = getattr(store, "UPGRADE_REROLL_CHANCE", 0.15)
        if chosen and random.random() < reroll_chance:
            i = random.randint(0, len(chosen) - 1)
            chosen[i] = {
                "stat": None,
                "type": "reroll",
                "name": "+2 реролла",
                "value": 2,
                "description": "Добавляет 2 реролла на выбор улучшений после волн.",
            }
        return chosen

    def apply_upgrade(upgrade):
        if upgrade.get("type") == "reroll":
            store.rerolls_left += upgrade.get("value", 1)
            return
        player = store.current_sloomp
        if not player or not upgrade.get("stat"):
            return
        player.bonus_stats[upgrade["stat"]] = player.bonus_stats.get(upgrade["stat"], 0) + upgrade["value"]
        if hasattr(player, "upgrade_counts"):
            player.upgrade_counts[upgrade["stat"]] = player.upgrade_counts.get(upgrade["stat"], 0) + 1
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
        persistent.wave = store.WAVE_START
        for s in store.sloomp_collection:
            s.final_stats = s.calc_final_stats()
            s.current_hp = s.final_stats["hp"]
        store.battle_aborted = False

    def do_reroll_upgrades():
        if store.rerolls_left <= 0:
            renpy.notify("Рероллы закончились")
            return
        store.rerolls_left -= 1
        exclude = [u["stat"] for u in store.current_upgrade_choices if u.get("stat")]
        store.current_upgrade_choices = generate_upgrade_options(store.UPGRADE_CHOICES_COUNT, exclude_stats=exclude)
        renpy.notify("Новые варианты! Осталось рероллов: " + str(store.rerolls_left))
        renpy.restart_interaction()

    def abort_battle():
        store.battle_active = False
        store.battle_finished = True
        store.battle_aborted = True

    def reset_game():
        store.sloomp_collection = []
        store.current_sloomp = None
        store.player_relics = []
        store.guardian_angel_used = False
        persistent.sloomp_data = []
        persistent.current_sloomp_index = None
        persistent.gold = 0
        persistent.in_run = False
        persistent.wave = store.WAVE_START
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
        for s in store.sloomp_collection:
            s.final_stats = s.calc_final_stats()
            s.current_hp = min(s.current_hp, s.final_stats["hp"])
        if hasattr(store, "on_shop_bought"):
            store.on_shop_bought()
        renpy.notify("Улучшение куплено для всех хлюпов!")
        renpy.restart_interaction()
