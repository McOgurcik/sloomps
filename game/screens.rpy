# screens.rpy

init python:
    import random
    battle_victory = False

    def fmt_pct(val):
        return "{:.0f}".format(round(float(val) * 100))

    def fmt_num(val):
        if isinstance(val, float):
            return "{:.1f}".format(round(val, 1)) if val != int(val) else str(int(val))
        return str(int(val))
    battle_log = []
    last_enemy = None
    fusion_selected_1 = None
    fusion_selected_2 = None

    def compute_feature_mults(sloomp):
        mult = {
            "hp": 1.0, "defense": 1.0, "attack_speed": 1.0, "attack_power": 1.0,
            "crit_chance": 1.0, "crit_damage": 1.0, "vampirism": 1.0,
            "accuracy": 1.0, "evasion": 1.0, "regen": 1.0,
        }
        for feat in getattr(sloomp, "features", []):
            for stat, m in feat.get("multipliers", {}).items():
                mult[stat] = mult.get(stat, 1.0) * m
        return mult

    def get_feat_bg_color(mult):
        if mult <= 1.0:
            return None
        # Нормализуем усиление: 1.0 → нет подсветки, 1.5+ → максимум.
        strength = min(1.0, (mult - 1.0) / 0.5)
        base_g = 60
        max_g = 140
        g = int(base_g + (max_g - base_g) * strength)
        # Тёмно-зелёный → умеренно-зелёный (не слишком ярко).
        return "#{:02x}{:02x}{:02x}".format(0, g, 0)

    def label_with_upgrade_count(sloomp, stat_key, base_label):
        counts = getattr(sloomp, "upgrade_counts", {}) or {}
        cnt = counts.get(stat_key, 0)
        if cnt > 0:
            return "{} (+{})".format(base_label, cnt)
        return base_label


# Общие стили для текстовых кнопок — центрирование и заметная рамка
# c использованием стандартных ресурсов gui/button.
style textbutton is default:
    xalign 0.5
    padding (10, 6)
    background Frame("gui/button/idle.png", gui.button_borders, tile=gui.button_tile)
    hover_background Frame("gui/button/hover.png", gui.button_borders, tile=gui.button_tile)
    insensitive_background Frame("gui/button/insensitive.png", gui.button_borders, tile=gui.button_tile)

style textbutton_text is default:
    xalign 0.5

init python:

    def start_egg_opening(egg_id):
        eggs = getattr(store, "EGG_TYPES", [])
        egg = next((e for e in eggs if e.get("id") == egg_id), None)
        if not egg:
            renpy.notify("Яйцо недоступно")
            return
        price = egg.get("price", 0)
        if persistent.gold < price:
            renpy.notify("Недостаточно золота")
            return
        persistent.gold -= price
        roll_count = egg.get("roll_count", 10)
        candidates = []
        for _ in range(roll_count):
            candidates.append(store.generate_sloomp_for_egg(egg))
        store.egg_roll_egg = egg
        store.egg_roll_candidates = candidates
        store.egg_roll_index = 0
        store.egg_roll_spins_left = max(roll_count * 3, 15)
        store.egg_roll_final = None
        store.egg_roll_active = True
        renpy.show_screen("egg_roll")

    def advance_egg_roll():
        if not getattr(store, "egg_roll_active", False):
            return
        if not getattr(store, "egg_roll_candidates", []):
            store.egg_roll_active = False
            return
        if store.egg_roll_spins_left <= 0:
            store.egg_roll_active = False
            if store.egg_roll_final is None:
                idx = max(0, min(len(store.egg_roll_candidates) - 1, store.egg_roll_index))
                store.egg_roll_final = store.egg_roll_candidates[idx]
            renpy.restart_interaction()
            return
        store.egg_roll_index = (store.egg_roll_index + 1) % len(store.egg_roll_candidates)
        store.egg_roll_spins_left -= 1
        if store.egg_roll_spins_left <= 0:
            store.egg_roll_active = False
            idx = max(0, min(len(store.egg_roll_candidates) - 1, store.egg_roll_index))
            store.egg_roll_final = store.egg_roll_candidates[idx]
        renpy.restart_interaction()

    def skip_egg_roll_animation():
        if not getattr(store, "egg_roll_candidates", []):
            return
        store.egg_roll_spins_left = 0
        store.egg_roll_active = False
        idx = max(0, min(len(store.egg_roll_candidates) - 1, store.egg_roll_index))
        store.egg_roll_final = store.egg_roll_candidates[idx]
        renpy.restart_interaction()
    
    def select_relic(relic):
        if not hasattr(store, "player_relics"):
            store.player_relics = []
        store.player_relics.append(relic.copy())
        if store.current_sloomp:
            store.current_sloomp.final_stats = store.current_sloomp.calc_final_stats()
        renpy.notify("Реликвия '{}' получена!".format(relic.get("name", "Реликвия")))

    def select_for_fusion(sloomp):
        global fusion_selected_1, fusion_selected_2
        if fusion_selected_1 is None:
            fusion_selected_1 = sloomp
        elif fusion_selected_2 is None and sloomp != fusion_selected_1:
            fusion_selected_2 = sloomp
        else:
            renpy.notify("Нельзя выбрать этого хлюпа")
        renpy.restart_interaction()

    def perform_simple_fusion():
        global fusion_selected_1, fusion_selected_2
        if fusion_selected_1 is None or fusion_selected_2 is None or fusion_selected_1 == fusion_selected_2:
            renpy.notify("Нужны два разных хлюпа!")
            return
        p1 = fusion_selected_1
        p2 = fusion_selected_2
        level = 1
        base_stats = store._sloomp_base_stats(level)
        bonus_stats = {}
        stat_keys = ["hp", "defense", "attack_speed", "attack_power", "crit_chance", "crit_damage", "vampirism", "accuracy", "evasion", "regen"]
        for key in stat_keys:
            choice = random.randint(0, 2)
            if choice == 0:
                bonus_stats[key] = p1.bonus_stats.get(key, 0)
            elif choice == 1:
                bonus_stats[key] = p2.bonus_stats.get(key, 0)
            else:
                a, b = p1.bonus_stats.get(key, 0), p2.bonus_stats.get(key, 0)
                if key in ["hp", "defense", "attack_power"]:
                    bonus_stats[key] = int((a + b) / 2)
                else:
                    bonus_stats[key] = (a + b) / 2.0
        feat_by_type_p1 = {feat["type"]: feat for feat in p1.features}
        feat_by_type_p2 = {feat["type"]: feat for feat in p2.features}
        new_features = []
        for t in set(feat_by_type_p1.keys()) | set(feat_by_type_p2.keys()):
            if t in feat_by_type_p1 and t in feat_by_type_p2:
                new_features.append(random.choice([feat_by_type_p1[t], feat_by_type_p2[t]]).copy())
            elif t in feat_by_type_p1:
                new_features.append(feat_by_type_p1[t].copy())
            else:
                new_features.append(feat_by_type_p2[t].copy())
        if random.random() < 0.2:
            possible = [t for t in ["color", "form", "face", "hat", "clothes", "mask", "weapon", "aura", "ally"] if t not in [f["type"] for f in new_features]]
            if possible:
                t = random.choice(possible)
                opt = FEATURE_DB.get(t, {})
                if opt:
                    ch = random.choice(list(opt.values())).copy()
                    ch["type"] = t
                    new_features.append(ch)
        name_parts = [f["display_name"] for f in new_features if f["type"] in ("color", "form", "face")]
        name = " ".join(name_parts) if name_parts else "Микс"
        new_sloomp = store.Sloomp(name, level, base_stats, new_features)
        new_sloomp.bonus_stats = bonus_stats
        new_sloomp.final_stats = new_sloomp.calc_final_stats()
        new_sloomp.current_hp = new_sloomp.final_stats["hp"]
        store.sloomp_collection.remove(p1)
        store.sloomp_collection.remove(p2)
        store.sloomp_collection.append(new_sloomp)
        if store.current_sloomp in (p1, p2):
            store.current_sloomp = new_sloomp
        fusion_selected_1 = None
        fusion_selected_2 = None
        if hasattr(store, "on_collection_changed"):
            store.on_collection_changed()
        renpy.notify("Создан " + new_sloomp.name + "!")
        renpy.restart_interaction()

    def add_sloomp_to_collection(sloomp):
        store.sloomp_collection.append(sloomp)
        if store.current_sloomp is None:
            store.current_sloomp = sloomp
        if hasattr(store, "on_collection_changed"):
            store.on_collection_changed()

    def clear_fusion_slot_1():
        global fusion_selected_1
        fusion_selected_1 = None
        renpy.restart_interaction()

    def clear_fusion_slot_2():
        global fusion_selected_2
        fusion_selected_2 = None
        renpy.restart_interaction()

    battle_active = False
    battle_finished = False
    last_player_attack_time = 0.0
    last_enemy_attack_time = 0.0
    hit_effect_target = None
    hit_effect_type = None
    hit_effect_timer = 0.0
    hit_effect_x = 0.0
    hit_effect_y = 0.0
    hit_effect_angle = 0.0
    hit_effect_image = None

    def _setup_hit_effect(target, hit_type):
        """
        Настраивает спрайт удара: случайная позиция вокруг цели,
        случайный угол и случайный вариант спрайта по типу удара.
        """
        global hit_effect_target, hit_effect_type, hit_effect_timer, hit_effect_x, hit_effect_y, hit_effect_angle, hit_effect_image
        hit_effect_target = target
        hit_effect_type = hit_type
        hit_effect_timer = getattr(store, "HIT_EFFECT_DURATION", 0.2)
        # Координаты центров спрайтов — из BATTLE_BACKGROUND_MAP (хранятся в store экраном боя).
        p_pos = getattr(store, "battle_player_pos", (400, 300))
        e_pos = getattr(store, "battle_enemy_pos", (1200, 300))
        if target == "enemy":
            base_x, base_y = e_pos[0] + 150, e_pos[1] + 150  # центр врага (300x300)
        else:
            base_x, base_y = p_pos[0] + 150, p_pos[1] + 150  # центр хлюпа (300x300)
        # Небольшой случайный разброс вокруг цели, чтобы эффект касался тела.
        dx = random.randint(-60, 60)
        dy = random.randint(-60, 60)
        hit_effect_x = base_x + dx
        hit_effect_y = base_y + dy
        hit_effect_angle = random.randint(-25, 25)
        sprites_map = getattr(store, "HIT_EFFECT_SPRITES", {})
        candidates = sprites_map.get(hit_type) or sprites_map.get("normal") or []
        if candidates:
            hit_effect_image = random.choice(candidates)
        else:
            hit_effect_image = "images/effects/hit_{}.png".format(hit_type)

    def battle_tick():
        global battle_active, battle_finished, last_player_attack_time, last_enemy_attack_time, hit_effect_target, hit_effect_type, hit_effect_timer, hit_effect_x, hit_effect_y, hit_effect_angle, hit_effect_image, battle_victory, last_enemy
        if not battle_active:
            return
        player = store.current_sloomp
        enemy = current_enemy
        if player is None or enemy is None:
            battle_active = False
            return
        import time
        current_time = time.time()
        min_speed = getattr(store, "ATTACK_SPEED_MIN", 0.1)
        min_dmg = getattr(store, "MIN_DAMAGE", 1)
        
        # Проверка на смерть с учётом ангела-хранителя
        if player.current_hp <= 0:
            relics = getattr(store, "player_relics", [])
            relic_ids = [r.get("id") if isinstance(r, dict) else r for r in relics]
            if "guardian_angel" in relic_ids and not getattr(store, "guardian_angel_used", False):
                store.guardian_angel_used = True
                player.current_hp = int(player.final_stats["hp"] * 0.3)
                # Потеря 20% бонусных статов и золота
                for key in player.bonus_stats:
                    player.bonus_stats[key] = int(player.bonus_stats[key] * 0.8)
                player.final_stats = player.calc_final_stats()
                persistent.gold = int(persistent.gold * 0.8)
            else:
                battle_victory = False
                last_enemy = enemy
                battle_active = False
                battle_finished = True
                return
        
        if enemy.current_hp <= 0:
            battle_victory = True
            last_enemy = enemy
            battle_active = False
            battle_finished = True
            return
        
        tick = getattr(store, "BATTLE_TICK_INTERVAL", 0.05)
        player_regen = player.final_stats.get("regen", 0) * tick
        if player_regen > 0:
            player.current_hp = min(player.current_hp + int(player_regen), player.final_stats["hp"])
        enemy_regen = enemy.final_stats.get("regen", 0) * tick
        if enemy_regen > 0:
            enemy.current_hp = min(enemy.current_hp + int(enemy_regen), enemy.final_stats["hp"])
        
        # Эффекты реликвий
        relics = getattr(store, "player_relics", [])
        relic_ids = [r.get("id") if isinstance(r, dict) else r for r in relics]
        
        # Проверка оглушения врага (подлый удар)
        enemy_stunned = current_time < getattr(store, "battle_enemy_stunned_until", 0.0)
        if enemy_stunned:
            enemy_speed_effective = min_speed * 1000  # Практически 0 скорость
        else:
            enemy_speed_effective = max(min_speed, enemy.final_stats["attack_speed"])
        
        player_speed = max(min_speed, player.final_stats["attack_speed"])
        if current_time - last_player_attack_time >= 1.0 / player_speed:
            last_player_attack_time = current_time
            store.battle_player_attack_count = getattr(store, "battle_player_attack_count", 0) + 1
            
            # Базовый урон
            player_dmg = int(player.final_stats["attack_power"])
            
            # Маска берсерка - урон зависит от HP
            if "berserker_mask" in relic_ids:
                hp_percent = float(player.current_hp) / float(player.final_stats["hp"])
                hp_factor = max(0.1, hp_percent)
                berserker_mult = 1.0 + (1.0 - hp_factor) * 0.4  # До +40% при 10% HP
                player_dmg = int(player_dmg * berserker_mult)
            
            # Стеклянная пушка - +15% урон
            if "glass_cannon" in relic_ids:
                player_dmg = int(player_dmg * 1.15)
            
            # Критический урон (если не заблокирован мощью титана)
            is_crit = False
            if "titan_power" not in relic_ids:
                is_crit = random.random() < player.final_stats["crit_chance"]
                if is_crit:
                    player_dmg = int(player_dmg * player.final_stats["crit_damage"])
                    hit_effect_type = "crit"
                    # Подлый удар - оглушение на 1 секунду
                    if "sneaky_strike" in relic_ids:
                        store.battle_enemy_stunned_until = current_time + 1.0
                else:
                    hit_effect_type = "normal"
            else:
                hit_effect_type = "normal"
            
            # Мощь титана - дополнительный урон от доп. здоровья
            if "titan_power" in relic_ids:
                bonus_hp = player.bonus_stats.get("hp", 0)
                if bonus_hp > 0:
                    titan_dmg = int(bonus_hp * 0.05)
                    player_dmg += titan_dmg
            
            # Грозовой клинок - каждая 5 атака
            if "storm_blade" in relic_ids and store.battle_player_attack_count % 5 == 0:
                storm_dmg = int(enemy.final_stats["hp"] * 0.05)
                player_dmg += storm_dmg
            
            player_dmg = max(min_dmg, player_dmg - enemy.final_stats["defense"])
            enemy.current_hp -= player_dmg
            
            vamp_heal = int(player_dmg * player.final_stats["vampirism"])
            max_hp = player.final_stats["hp"]
            vamp_heal = min(vamp_heal, max(0, max_hp - player.current_hp))
            player.current_hp += vamp_heal
            _setup_hit_effect("enemy", hit_effect_type)
            if enemy.current_hp <= 0:
                battle_victory = True
                last_enemy = enemy
                battle_active = False
                battle_finished = True
                return
        
        # Атака врага (если не оглушён)
        if battle_active and not enemy_stunned and current_time - last_enemy_attack_time >= 1.0 / enemy_speed_effective:
            last_enemy_attack_time = current_time
            enemy_dmg = int(enemy.final_stats["attack_power"])
            is_crit = random.random() < enemy.final_stats["crit_chance"]
            if is_crit:
                enemy_dmg = int(enemy_dmg * enemy.final_stats["crit_damage"])
            
            # Проверка уклонения
            evaded = random.random() < player.final_stats.get("evasion", 0)
            if evaded and "shadow_wings" in relic_ids:
                # Теневые крылья - ответный удар
                counter_dmg = int(player.final_stats["attack_power"] * 0.5)
                counter_dmg = max(min_dmg, counter_dmg - enemy.final_stats["defense"])
                enemy.current_hp -= counter_dmg
                _setup_hit_effect("enemy", "normal")
            elif not evaded:
                # Стеклянная пушка - +20% получаемый урон
                if "glass_cannon" in relic_ids:
                    enemy_dmg = int(enemy_dmg * 1.2)
                
                enemy_dmg = max(min_dmg, enemy_dmg - player.final_stats["defense"])
                player.current_hp -= enemy_dmg
                _setup_hit_effect("player", "crit" if is_crit else "normal")
                if player.current_hp <= 0:
                    # Проверка ангела-хранителя
                    if "guardian_angel" in relic_ids and not getattr(store, "guardian_angel_used", False):
                        store.guardian_angel_used = True
                        player.current_hp = int(player.final_stats["hp"] * 0.3)
                        for key in player.bonus_stats:
                            player.bonus_stats[key] = int(player.bonus_stats[key] * 0.8)
                        player.final_stats = player.calc_final_stats()
                        persistent.gold = int(persistent.gold * 0.8)
                    else:
                        battle_victory = False
                        last_enemy = enemy
                        battle_active = False
                        battle_finished = True
                        return
        
        if hit_effect_timer > 0:
            hit_effect_timer -= 0.05
            if hit_effect_timer <= 0:
                hit_effect_target = None
                hit_effect_image = None
        renpy.restart_interaction()

screen game_menu(title):
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1400
        ysize 900
        background "#C0C0C0"
        has vbox
        spacing 20
        text title size 40 xalign 0.5
        null height 10
        vbox:
            xalign 0.5
            transclude

screen main_menu():
    tag menu
    add "images/gui/main_menu_bg.png"
    frame:
        xalign 0.5
        yalign 0.5
        padding (50, 30)
        background "#8844AA"
        vbox:
            xalign 0.5
            spacing 20
            text "БОЕВЫЕ ХЛЮПЫ" size 48 color "#FFFFFF" xalign 0.5
            text "Волна: [wave]" size 24 xalign 0.5
            if persistent.in_run:
                textbutton "Продолжить" action Jump("start_battle") xminimum 250
            else:
                textbutton "Начать игру" action Jump("start_battle") xminimum 250
            textbutton "Загрузить" action ShowMenu("load") xminimum 250
            textbutton "Сохранить игру" action [Function(sync_sloomp_to_persistent), ShowMenu("save")] xminimum 250
            textbutton "Мои хлюпы" action ShowMenu("collection") xminimum 250
            textbutton "Слияние" action ShowMenu("fusion_simple") xminimum 250
            textbutton "Магазин" action ShowMenu("shop") xminimum 250
            textbutton "Новая игра" action Confirm(_("Начать новую игру? Весь прогресс будет потерян."), [Function(reset_game), Jump("start")]) xminimum 250
            textbutton "Выход" action Quit() xminimum 250
            null height 20
            text "💰 [persistent.gold]" color "#FFD700" size 28 xalign 0.5

screen choose_upgrade():
    modal True
    add "images/gui/choose_bg.png"
    $ player = current_sloomp
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 800
        background "#7c6e6e"
        padding (40, 30)
        has vbox
        xalign 0.5
        text "Выбери улучшение" size 40 xalign 0.5
        null height 10
        hbox:
            xalign 0.5
            spacing 20
            use sloomp_display(player, (120, 120))
            use sloomp_stats_full(player)
        null height 15
        text "Рероллов: [rerolls_left]" size 20 xalign 0.5
        hbox:
            xalign 0.5
            spacing 20
            if rerolls_left > 0:
                textbutton "Реролл (новые варианты)" action Function(do_reroll_upgrades) xminimum 260
        null height 20
        $ upgrade_icons = {
            "hp": "❤️",
            "defense": "🛡️",
            "attack_power": "⚔️",
            "attack_speed": "⚡",
            "crit_chance": "🎯",
            "crit_damage": "💥",
            "vampirism": "💉",
            "accuracy": "🎲",
            "evasion": "🌀",
            "regen": "💚",
            None: "🔄",
        }
        hbox:
            xalign 0.5
            spacing 40
            for upgrade in current_upgrade_choices:
                $ icon = upgrade_icons.get(upgrade.get("stat"), upgrade_icons[None])
                frame:
                    xysize (320, 420)
                    background "#ffa3a3"
                    has vbox
                    spacing 8
                    xalign 0.5
                    text icon size 60 xalign 0.5
                    null height 4
                    text upgrade["name"] size 22 xalign 0.5
                    null height 4
                    text upgrade["description"] size 16 xalign 0.5 text_align 0.5
                    null height 20
                    textbutton "ВЫБРАТЬ" action [Function(apply_upgrade, upgrade), Hide("choose_upgrade"), Jump("after_upgrade")] xalign 0.5 xminimum 220
        if len(current_upgrade_choices) < 3:
            text "Выбери одно улучшение" size 18 color "#444" xalign 0.5

screen collection():
    tag menu
    use game_menu("Коллекция хлюпов"):
        vbox:
            spacing 10
            xalign 0.5
            textbutton "← Назад" action Return() xminimum 160
            if current_sloomp:
                frame:
                    xfill True
                    has hbox
                    use sloomp_display(current_sloomp, (120, 120))
                    use sloomp_stats_full(current_sloomp)
                    textbutton "Подробнее" action ShowMenu("sloomp_detail", current_sloomp) xminimum 120
            null height 20
            text "Все хлюпы:" size 24
            viewport:
                draggable True
                mousewheel True
                ysize 400
                vbox:
                    for sloomp in sloomp_collection:
                        frame:
                            xfill True
                            has hbox
                            use sloomp_display(sloomp, (60, 60))
                            vbox:
                                text "[sloomp.name]" size 18
                            if sloomp != current_sloomp:
                                textbutton "Выбрать" action [SetField(store, "current_sloomp", sloomp), Function(sync_sloomp_to_persistent), Return()] xminimum 100
                            else:
                                text "АКТИВЕН" size 16

screen fusion_simple():
    tag menu
    use game_menu("Алтарь слияния"):
        vbox:
            xalign 0.5
            textbutton "← Назад" action Return() xminimum 160
            null height 20
            hbox:
                xalign 0.5
                spacing 100
                frame:
                    xysize (380, 620)
                    background "#442266"
                    has vbox
                    if fusion_selected_1:
                        use sloomp_display(fusion_selected_1, (180, 180))
                        text "[fusion_selected_1.name]" size 18 xalign 0.5
                        use sloomp_stats_full(fusion_selected_1)
                        textbutton "Снять выбор" action Function(clear_fusion_slot_1) xalign 0.5 xminimum 120
                    else:
                        text "Выберите первого хлюпа" size 18 xalign 0.5 yalign 0.5
                frame:
                    xysize (380, 620)
                    background "#442266"
                    has vbox
                    if fusion_selected_2:
                        use sloomp_display(fusion_selected_2, (180, 180))
                        text "[fusion_selected_2.name]" size 18 xalign 0.5
                        use sloomp_stats_full(fusion_selected_2)
                        textbutton "Снять выбор" action Function(clear_fusion_slot_2) xalign 0.5 xminimum 120
                    else:
                        text "Выберите второго хлюпа" size 18 xalign 0.5 yalign 0.5
            null height 30
            if fusion_selected_1 and fusion_selected_2 and fusion_selected_1 != fusion_selected_2:
                textbutton "НАЧАТЬ СЛИЯНИЕ" action Function(perform_simple_fusion) xalign 0.5 xminimum 200
            else:
                text "Выберите двух разных хлюпов" color "#888" xalign 0.5
            null height 30
            text "Все хлюпы:" size 22
            viewport:
                draggable True
                mousewheel True
                ysize 300
                vbox:
                    for sloomp in sloomp_collection:
                        frame:
                            xfill True
                            has hbox
                            use sloomp_display(sloomp, (50, 50))
                            vbox:
                                text "[sloomp.name]" size 16
                            if sloomp != fusion_selected_1 and sloomp != fusion_selected_2:
                                textbutton "Выбрать" action Function(select_for_fusion, sloomp) xalign 0.5 xminimum 100
                            else:
                                text "Уже выбран" color "#888" xalign 0.5

screen sloomp_detail(sloomp):
    tag menu
    use game_menu("Характеристики"):
        vbox:
            textbutton "← Назад" action Return() xminimum 120
            use sloomp_display(sloomp, (250, 250))
            text "Имя: [sloomp.name]" size 22
            null height 10
            text "Уровень: [sloomp.level]  Опыт: [sloomp.exp]/[sloomp.exp_to_next]" size 18
            null height 10
            text "Характеристики:" size 20
            $ feat_mults = compute_feature_mults(sloomp)
            $ lbl_hp = label_with_upgrade_count(sloomp, "hp", "❤️ HP")
            if feat_mults.get("hp", 1.0) > 1.0:
                $ bg_hp = get_feat_bg_color(feat_mults.get("hp", 1.0))
                frame:
                    background bg_hp
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_hp]: [sloomp.current_hp]/[sloomp.final_stats['hp']]" size 18
            else:
                text "  [lbl_hp]: [sloomp.current_hp]/[sloomp.final_stats['hp']]" size 18

            $ lbl_def = label_with_upgrade_count(sloomp, "defense", "🛡️ Защита")
            if feat_mults.get("defense", 1.0) > 1.0:
                $ bg_def = get_feat_bg_color(feat_mults.get("defense", 1.0))
                frame:
                    background bg_def
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_def]: [fmt_num(sloomp.final_stats['defense'])]" size 18
            else:
                text "  [lbl_def]: [fmt_num(sloomp.final_stats['defense'])]" size 18

            $ lbl_speed = label_with_upgrade_count(sloomp, "attack_speed", "⚡ Скорость")
            if feat_mults.get("attack_speed", 1.0) > 1.0:
                $ bg_speed = get_feat_bg_color(feat_mults.get("attack_speed", 1.0))
                frame:
                    background bg_speed
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_speed]: [fmt_num(sloomp.final_stats['attack_speed'])]" size 18
            else:
                text "  [lbl_speed]: [fmt_num(sloomp.final_stats['attack_speed'])]" size 18

            $ lbl_atk = label_with_upgrade_count(sloomp, "attack_power", "⚔️ Атака")
            if feat_mults.get("attack_power", 1.0) > 1.0:
                $ bg_atk = get_feat_bg_color(feat_mults.get("attack_power", 1.0))
                frame:
                    background bg_atk
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_atk]: [fmt_num(sloomp.final_stats['attack_power'])]" size 18
            else:
                text "  [lbl_atk]: [fmt_num(sloomp.final_stats['attack_power'])]" size 18

            $ lbl_cc = label_with_upgrade_count(sloomp, "crit_chance", "🎯 Крит")
            if feat_mults.get("crit_chance", 1.0) > 1.0:
                $ bg_cc = get_feat_bg_color(feat_mults.get("crit_chance", 1.0))
                frame:
                    background bg_cc
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_cc]: [fmt_pct(sloomp.final_stats['crit_chance'])]%" size 18
            else:
                text "  [lbl_cc]: [fmt_pct(sloomp.final_stats['crit_chance'])]%" size 18

            $ lbl_cd = label_with_upgrade_count(sloomp, "crit_damage", "💥 Крит.урон")
            if feat_mults.get("crit_damage", 1.0) > 1.0:
                $ bg_cd = get_feat_bg_color(feat_mults.get("crit_damage", 1.0))
                frame:
                    background bg_cd
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_cd]: [fmt_pct(sloomp.final_stats['crit_damage'])]%" size 18
            else:
                text "  [lbl_cd]: [fmt_pct(sloomp.final_stats['crit_damage'])]%" size 18

            $ lbl_vamp = label_with_upgrade_count(sloomp, "vampirism", "💉 Вампиризм")
            if feat_mults.get("vampirism", 1.0) > 1.0:
                $ bg_vamp = get_feat_bg_color(feat_mults.get("vampirism", 1.0))
                frame:
                    background bg_vamp
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_vamp]: [fmt_pct(sloomp.final_stats['vampirism'])]%" size 18
            else:
                text "  [lbl_vamp]: [fmt_pct(sloomp.final_stats['vampirism'])]%" size 18

            $ lbl_acc = label_with_upgrade_count(sloomp, "accuracy", "🎲 Точность")
            if feat_mults.get("accuracy", 1.0) > 1.0:
                $ bg_acc = get_feat_bg_color(feat_mults.get("accuracy", 1.0))
                frame:
                    background bg_acc
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_acc]: [fmt_pct(sloomp.final_stats['accuracy'])]%" size 18
            else:
                text "  [lbl_acc]: [fmt_pct(sloomp.final_stats['accuracy'])]%" size 18

            $ lbl_eva = label_with_upgrade_count(sloomp, "evasion", "🌀 Уклонение")
            if feat_mults.get("evasion", 1.0) > 1.0:
                $ bg_eva = get_feat_bg_color(feat_mults.get("evasion", 1.0))
                frame:
                    background bg_eva
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_eva]: [fmt_pct(sloomp.final_stats['evasion'])]%" size 18
            else:
                text "  [lbl_eva]: [fmt_pct(sloomp.final_stats['evasion'])]%" size 18

            $ lbl_regen = label_with_upgrade_count(sloomp, "regen", "💚 Восст. HP")
            if feat_mults.get("regen", 1.0) > 1.0:
                $ bg_regen = get_feat_bg_color(feat_mults.get("regen", 1.0))
                frame:
                    background bg_regen
                    padding (6, 2)
                    xmaximum 400
                    text "  [lbl_regen]: [fmt_num(sloomp.final_stats.get('regen', 0))]/сек" size 18
            else:
                text "  [lbl_regen]: [fmt_num(sloomp.final_stats.get('regen', 0))]/сек" size 18
            null height 10
            text "Особенности:" size 20
            for feat in sloomp.features:
                text "  • [feat['display_name']] ([feat['type']])" size 16
            null height 10
            text "Реликвии:" size 20
            if hasattr(store, "player_relics") and store.player_relics:
                for relic in store.player_relics:
                    if isinstance(relic, dict):
                        text "  • [relic.get('name', 'Реликвия')]" size 16
            else:
                text "  Нет реликвий" size 16 color "#888"
            null height 20
            textbutton "Назад" action Return() xminimum 120

screen sloomp_features_only(sloomp):
    vbox:
        spacing 4
        text "Особенности:" size 14
        for feat in sloomp.features:
            text "  • [feat['display_name']]" size 14

screen sloomp_stats_full(sloomp):
    vbox:
        spacing 2
        text "Ур. [sloomp.level]  Опыт: [sloomp.exp]/[sloomp.exp_to_next]" size 14
        $ feat_mults = compute_feature_mults(sloomp)

        $ lbl_hp = label_with_upgrade_count(sloomp, "hp", "❤️ HP")
        if feat_mults.get("hp", 1.0) > 1.0:
            $ bg_hp = get_feat_bg_color(feat_mults.get("hp", 1.0))
            frame:
                background bg_hp
                padding (4, 1)
                xmaximum 250
                text "[lbl_hp]: [sloomp.current_hp]/[sloomp.final_stats['hp']]" size 14
        else:
            text "[lbl_hp]: [sloomp.current_hp]/[sloomp.final_stats['hp']]" size 14

        $ lbl_def = label_with_upgrade_count(sloomp, "defense", "🛡️ Защита")
        if feat_mults.get("defense", 1.0) > 1.0:
            $ bg_def = get_feat_bg_color(feat_mults.get("defense", 1.0))
            frame:
                background bg_def
                padding (4, 1)
                xmaximum 250
                text "[lbl_def]: [fmt_num(sloomp.final_stats['defense'])]" size 14
        else:
            text "[lbl_def]: [fmt_num(sloomp.final_stats['defense'])]" size 14

        $ lbl_atk = label_with_upgrade_count(sloomp, "attack_power", "⚔️ Атака")
        if feat_mults.get("attack_power", 1.0) > 1.0:
            $ bg_atk = get_feat_bg_color(feat_mults.get("attack_power", 1.0))
            frame:
                background bg_atk
                padding (4, 1)
                xmaximum 250
                text "[lbl_atk]: [fmt_num(sloomp.final_stats['attack_power'])]" size 14
        else:
            text "[lbl_atk]: [fmt_num(sloomp.final_stats['attack_power'])]" size 14

        $ lbl_speed = label_with_upgrade_count(sloomp, "attack_speed", "⚡ Скорость")
        if feat_mults.get("attack_speed", 1.0) > 1.0:
            $ bg_speed = get_feat_bg_color(feat_mults.get("attack_speed", 1.0))
            frame:
                background bg_speed
                padding (4, 1)
                xmaximum 250
                text "[lbl_speed]: [fmt_num(sloomp.final_stats['attack_speed'])]" size 14
        else:
            text "[lbl_speed]: [fmt_num(sloomp.final_stats['attack_speed'])]" size 14

        $ lbl_cc = label_with_upgrade_count(sloomp, "crit_chance", "🎯 Крит")
        if feat_mults.get("crit_chance", 1.0) > 1.0:
            $ bg_cc = get_feat_bg_color(feat_mults.get("crit_chance", 1.0))
            frame:
                background bg_cc
                padding (4, 1)
                xmaximum 250
                text "[lbl_cc]: [fmt_pct(sloomp.final_stats['crit_chance'])]%" size 14
        else:
            text "[lbl_cc]: [fmt_pct(sloomp.final_stats['crit_chance'])]%" size 14

        $ lbl_cd = label_with_upgrade_count(sloomp, "crit_damage", "💥 Крит.урон")
        if feat_mults.get("crit_damage", 1.0) > 1.0:
            $ bg_cd = get_feat_bg_color(feat_mults.get("crit_damage", 1.0))
            frame:
                background bg_cd
                padding (4, 1)
                xmaximum 250
                text "[lbl_cd]: [fmt_pct(sloomp.final_stats['crit_damage'])]%" size 14
        else:
            text "[lbl_cd]: [fmt_pct(sloomp.final_stats['crit_damage'])]%" size 14

        $ lbl_vamp = label_with_upgrade_count(sloomp, "vampirism", "💉 Вампиризм")
        if feat_mults.get("vampirism", 1.0) > 1.0:
            $ bg_vamp = get_feat_bg_color(feat_mults.get("vampirism", 1.0))
            frame:
                background bg_vamp
                padding (4, 1)
                xmaximum 250
                text "[lbl_vamp]: [fmt_pct(sloomp.final_stats['vampirism'])]%" size 14
        else:
            text "[lbl_vamp]: [fmt_pct(sloomp.final_stats['vampirism'])]%" size 14

        $ lbl_acc = label_with_upgrade_count(sloomp, "accuracy", "🎲 Точность")
        if feat_mults.get("accuracy", 1.0) > 1.0:
            $ bg_acc = get_feat_bg_color(feat_mults.get("accuracy", 1.0))
            frame:
                background bg_acc
                padding (4, 1)
                xmaximum 250
                text "[lbl_acc]: [fmt_pct(sloomp.final_stats['accuracy'])]%" size 14
        else:
            text "[lbl_acc]: [fmt_pct(sloomp.final_stats['accuracy'])]%" size 14

        $ lbl_eva = label_with_upgrade_count(sloomp, "evasion", "🌀 Уклонение")
        if feat_mults.get("evasion", 1.0) > 1.0:
            $ bg_eva = get_feat_bg_color(feat_mults.get("evasion", 1.0))
            frame:
                background bg_eva
                padding (4, 1)
                xmaximum 250
                text "[lbl_eva]: [fmt_pct(sloomp.final_stats['evasion'])]%" size 14
        else:
            text "[lbl_eva]: [fmt_pct(sloomp.final_stats['evasion'])]%" size 14

        $ lbl_regen = label_with_upgrade_count(sloomp, "regen", "💚 Восст. HP")
        if feat_mults.get("regen", 1.0) > 1.0:
            $ bg_regen = get_feat_bg_color(feat_mults.get("regen", 1.0))
            frame:
                background bg_regen
                padding (4, 1)
                xmaximum 250
                text "[lbl_regen]: [fmt_num(sloomp.final_stats.get('regen', 0))]/сек" size 14
        else:
            text "[lbl_regen]: [fmt_num(sloomp.final_stats.get('regen', 0))]/сек" size 14

screen enemy_stats_full(enemy):
    vbox:
        spacing 4
        text "[enemy.name]" size 20 xalign 0.5
        text "❤️ HP: [int(enemy.current_hp)]/[int(enemy.final_stats['hp'])]" size 18
        text "🛡️ Защита: [fmt_num(enemy.final_stats['defense'])]" size 16
        text "⚔️ Атака: [fmt_num(enemy.final_stats['attack_power'])]" size 16
        text "⚡ Скорость: [fmt_num(enemy.final_stats['attack_speed'])]" size 16
        text "🎯 Крит: [fmt_pct(enemy.final_stats['crit_chance'])]%" size 16
        text "💥 Крит.урон: [fmt_pct(enemy.final_stats['crit_damage'])]%" size 16
        text "🎲 Точность: [fmt_pct(enemy.final_stats['accuracy'])]%" size 16
        text "🌀 Уклонение: [fmt_pct(enemy.final_stats['evasion'])]%" size 16
        text "💚 Восст. HP: [fmt_num(enemy.final_stats.get('regen', 0))]/сек" size 16

screen sloomp_display(sloomp, size=(100, 100)):
    fixed:
        xysize size
        $ form_name = None
        $ color_name = None
        $ face_name = None
        for feat in sloomp.features:
            if feat["type"] == "form":
                $ form_name = feat["name"]
            elif feat["type"] == "color":
                $ color_name = feat["name"]
            elif feat["type"] == "face":
                $ face_name = feat["name"]
        $ use_new = getattr(store, "USE_NEW_SLOOMP_SPRITES", False)
        if use_new and form_name and color_name:
            if not face_name:
                $ face_name = "default"
            $ base_image = "images/new_full/{}_{}_{}.png".format(form_name, color_name, face_name)
            add base_image xysize size
        elif form_name and color_name:
            $ base_image = "images/sloomps/{}_{}.png".format(form_name, color_name)
            add base_image xysize size
        else:
            add "images/placeholder.png" xysize size
        # ally пока отображать не будем (только статистически существует).
        $ overlay_types = ["clothes", "hat", "mask", "weapon", "aura"] if use_new else ["face", "clothes", "hat", "mask", "weapon", "aura"]
        for ftype in overlay_types:
            for feat in sloomp.features:
                if feat["type"] == ftype and "image" in feat:
                    add feat["image"] xysize size

transform hit_effect_rot(angle=0.0):
    anchor (0.5, 0.5)
    rotate angle

screen battle_animation():
    modal True
    $ bg_map = getattr(store, "BATTLE_BACKGROUND_MAP", [])
    $ bg_image = "images/gui/battle_bg.png"
    $ player_pos = (400, 300)
    $ enemy_pos = (1200, 300)
    if bg_map:
        $ player_pos = bg_map[-1][3]
        $ enemy_pos = bg_map[-1][4]
        $ bg_image = bg_map[-1][2]
        for w_from, w_to, img, p_pos, e_pos in bg_map:
            if w_from <= wave <= w_to:
                $ bg_image = img
                $ player_pos = p_pos
                $ enemy_pos = e_pos
                break
    $ store.battle_player_pos = player_pos
    $ store.battle_enemy_pos = enemy_pos
    add bg_image
    $ player = current_sloomp
    $ enemy = current_enemy
    frame:
        xalign 0.0
        yalign 0.0
        xoffset 20
        yoffset 20
        background "#000000AA"
        padding (12, 8)
        text "Волна [wave]" size 32 color "#FFF"
    fixed:
        xpos player_pos[0]
        ypos player_pos[1]
        use sloomp_display(player, (300, 300))
        vbox:
            ypos 300
            bar:
                value player.current_hp
                range player.final_stats["hp"]
                xmaximum 300
                ymaximum 25
            text "❤️ [player.current_hp]/[player.final_stats['hp']]" size 22 xalign 0.5
    fixed:
        xpos enemy_pos[0]
        ypos enemy_pos[1]
        xsize 300
        ysize 380
        vbox:
            spacing 4
            text "[enemy.name]" size 24 xalign 0.5
            bar:
                value enemy.current_hp
                range enemy.final_stats["hp"]
                xmaximum 280
                ymaximum 26
            text "❤️ [int(enemy.current_hp)]/[int(enemy.final_stats['hp'])]" size 22 xalign 0.5
        add enemy.image ypos 75 xysize (300, 300)
    if hit_effect_target and hit_effect_image:
        add hit_effect_image xpos hit_effect_x ypos hit_effect_y xanchor 0.5 yanchor 0.5 at hit_effect_rot(hit_effect_angle) alpha 0.8
    hbox:
        xalign 0.0
        yalign 1.0
        xoffset 20
        yoffset -20
        spacing 10
        frame:
            background "#000000AA"
            padding (15, 10)
            use sloomp_stats_full(player)
        frame:
            background "#000000AA"
            padding (10, 10)
            use relics_display
    frame:
        xalign 1.0
        yalign 1.0
        xoffset -20
        yoffset -20
        background "#000000AA"
        padding (15, 10)
        use enemy_stats_full(enemy)
    timer 0.05 repeat True action Function(battle_tick)
    frame:
        xalign 0.5
        yalign 0.95
        background "#AAAAAA"
        padding (20, 10)
        textbutton "Прервать бой" action [Function(abort_battle), Hide("battle_animation"), Return()] text_size 24 xminimum 180
    if battle_finished:
        timer 0.3 action [Hide("battle_animation"), Jump("show_battle_result")]

screen battle_result(victory, log, enemy):
    modal True
    add Solid("#000000", alpha=0.8)
    frame:
        xalign 0.5
        yalign 0.5
        xsize 800
        ysize 500
        background "#6e6868"
        has vbox
        text "Результат боя" size 36 xalign 0.5
        null height 10
        viewport:
            ysize 200
            mousewheel True
            vbox:
                for line in log:
                    text "[line]" size 18
        null height 10
        if victory:
            text "🎉 ПОБЕДА! 🎉" color "#00AA00" size 32 xalign 0.5
            textbutton "В меню" action Jump("after_battle") text_size 24 xalign 0.5 xminimum 150
        else:
            text "💔 Поражение..." color "#AA0000" size 32 xalign 0.5
            hbox:
                xalign 0.5
                spacing 40
                textbutton "В меню" action Jump("after_battle") text_size 24 xminimum 150
                textbutton "Повторить" action [Function(reset_run), Jump("start_battle")] text_size 24 xminimum 150

screen shop():
    tag menu
    use game_menu("Магазин (улучшения для всех хлюпов)"):
        vbox:
            xalign 0.5
            textbutton "← Назад" action Return() xminimum 160
            null height 10
            frame:
                xfill True
                background "#333333"
                padding (15, 10)
                has hbox
                text "Золото: [persistent.gold]" color "#FFD700" size 24
            null height 20

            hbox:
                xalign 0.5
                spacing 20
                textbutton "Улучшения" action SetVariable("shop_tab", "upgrades") xminimum 160
                textbutton "Яйца хлюпов" action SetVariable("shop_tab", "eggs") xminimum 160

            null height 20

            if shop_tab == "upgrades":
                text "Постоянные бонусы ко всем хлюпам. Уровень × бонус за уровень." size 18 xalign 0.5
                null height 15
                $ stats_list = [
                    ("❤️ Здоровье", "hp"),
                    ("🛡️ Защита", "defense"),
                    ("⚡ Скорость атаки", "attack_speed"),
                    ("⚔️ Сила атаки", "attack_power"),
                    ("🎯 Шанс крита", "crit_chance"),
                    ("💥 Крит. урон", "crit_damage"),
                    ("💉 Вампиризм", "vampirism"),
                    ("🎲 Точность", "accuracy"),
                    ("🌀 Уклонение", "evasion"),
                    ("💚 Восст. HP", "regen")
                ]
                for label, stat in stats_list:
                    frame:
                        xfill True
                        background "#444444"
                        padding (10, 8)
                        has hbox
                        vbox:
                            xsize 200
                            text "[label]" size 18
                            $ lvl = persistent.shop_bonuses.get(stat, 0)
                            text "Уровень: [lvl]" size 14 color "#AAA"
                        vbox:
                            if lvl < SHOP_STAT_MAX_LEVEL:
                                $ cost = SHOP_STAT_COST_BASE + SHOP_STAT_COST_MULT * (lvl + 1)
                                text "Стоимость: [cost] 💰" size 16
                                textbutton "Купить" action Function(buy_global_upgrade, stat) xminimum 100
                            else:
                                text "Максимум" color "#888" size 16
            elif shop_tab == "eggs":
                text "Яйца хлюпов: открывай кейсы и получай хлюпов разной редкости. Чем больше особенностей — тем более редкий хлюп." size 18 xalign 0.5
                null height 15
                $ eggs = getattr(store, "EGG_TYPES", [])
                if eggs:
                    hbox:
                        xalign 0.5
                        spacing 20
                        for egg in eggs:
                            frame:
                                xysize (360, 260)
                                background "#444444"
                                padding (12, 10)
                                vbox:
                                    spacing 6
                                    text "[egg['name']]" size 22 xalign 0.5
                                    if "description" in egg:
                                        text "[egg['description']]" size 14
                                    text "Цена: [egg['price']] 💰" size 18
                                    null height 6
                                    textbutton "Купить и открыть" action Function(start_egg_opening, egg["id"]) xalign 0.5 xminimum 200
                else:
                    text "Яйца пока недоступны." size 18 xalign 0.5

screen egg_roll():
    modal True
    add Solid("#000000", alpha=0.8)
    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        ysize 600
        background "#333333"
        padding (20, 16)
        has vbox
        spacing 10
        text "Открытие яйца хлюпа" size 32 xalign 0.5
        null height 10
        if egg_roll_active and egg_roll_candidates:
            $ cur = egg_roll_candidates[egg_roll_index]
            text "Прокрутка возможных хлюпов..." size 20 xalign 0.5
            null height 10
            hbox:
                xalign 0.5
                spacing 40
                frame:
                    xysize (260, 260)
                    background "#222222"
                    use sloomp_display(cur, (240, 240))
                vbox:
                    spacing 6
                    text "[cur.name]" size 22
                    use sloomp_features_only(cur)
                    text "Осталось прокруток: [egg_roll_spins_left]" size 16
            null height 10
            hbox:
                xalign 0.5
                spacing 20
                textbutton "Пропустить анимацию" action Function(skip_egg_roll_animation) xminimum 200
                textbutton "Отмена" action Hide("egg_roll") xminimum 160
            timer 0.12 repeat True action Function(advance_egg_roll)
        elif egg_roll_final:
            $ cur = egg_roll_final
            text "Выпал новый хлюп!" size 24 xalign 0.5
            null height 10
            hbox:
                xalign 0.5
                spacing 40
                frame:
                    xysize (260, 260)
                    background "#222222"
                    use sloomp_display(cur, (240, 240))
                vbox:
                    spacing 6
                    text "[cur.name]" size 22
                    use sloomp_features_only(cur)
            null height 20
            hbox:
                xalign 0.5
                spacing 30
                textbutton "Забрать хлюпа" action [Function(add_sloomp_to_collection, cur), SetVariable("egg_roll_final", None), Hide("egg_roll")] xminimum 220
                textbutton "Закрыть" action Hide("egg_roll") xminimum 160
        else:
            text "Что‑то пошло не так при открытии яйца." size 20 xalign 0.5
            null height 20
            textbutton "Закрыть" action Hide("egg_roll") xalign 0.5 xminimum 160

screen choose_sloomp(title, sloomps, after_battle=False):
    modal True
    add "images/gui/choose_bg.png"
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1280
        ysize 820
        background "#7c6e6e"
        padding (40, 30)
        has vbox
        xalign 0.5
        spacing 15
        text title size 40 xalign 0.5
        null height 15
        hbox:
            xalign 0.5
            spacing 30
            for sloomp in sloomps:
                frame:
                    xysize (380, 680)
                    background "#332929"
                    has vbox
                    use sloomp_display(sloomp, (200, 200))
                    text "[sloomp.name]" size 18 xalign 0.5
                    use sloomp_stats_full(sloomp)
                    null height 10
                    textbutton "ВЫБРАТЬ" action [Function(add_sloomp_to_collection, sloomp), Hide("choose_sloomp"), Jump("after_boss_sloomp_then_relic" if after_battle else "after_choice")] xalign 0.5 xminimum 200

screen choose_relic():
    modal True
    add "images/gui/choose_bg.png"
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 700
        background "#7c6e6e"
        padding (40, 30)
        has vbox
        xalign 0.5
        text "Выбери реликвию" size 40 xalign 0.5
        null height 15
        text "Реликвии — мощные предметы, которые сильно влияют на игру." size 18 xalign 0.5 text_align 0.5
        null height 20
        hbox:
            xalign 0.5
            spacing 30
            for relic in current_relic_choices:
                frame:
                    xysize (350, 500)
                    background "#332929"
                    has vbox
                    if relic.get("icon"):
                        add relic["icon"] xysize (200, 200) xalign 0.5
                    else:
                        frame:
                            xysize (200, 200)
                            xalign 0.5
                            background "#555555"
                            text "?" size 48 xalign 0.5 yalign 0.5
                    null height 10
                    text "[relic['name']]" size 22 xalign 0.5
                    null height 5
                    text "[relic['description']]" size 14 xalign 0.5 text_align 0.5
                    null height 20
                    textbutton "ВЫБРАТЬ" action [Function(select_relic, relic), Hide("choose_relic"), Jump("after_upgrade")] xalign 0.5 xminimum 200

screen relics_display():
    vbox:
        spacing 4
        text "Реликвии:" size 14
        if player_relics:
            hbox:
                spacing 4
                for relic in player_relics:
                    if isinstance(relic, dict):
                        $ icon = relic.get("icon", None)
                        if icon:
                            imagebutton:
                                idle icon
                                hover icon
                                action NullAction()
                                xysize (32, 32)
                                tooltip relic.get("name", "Реликвия")
                        else:
                            frame:
                                xysize (32, 32)
                                background "#555555"
                                text "?" size 12 xalign 0.5 yalign 0.5
        else:
            text "Нет реликвий" size 12 color "#888"


## Экраны сохранения/загрузки — стандартные file_slots #########################
style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text
style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5
    xalign 0.5

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


screen save():
    tag menu
    use file_slots(_("Save"))

screen load():
    tag menu
    use file_slots(_("Загрузить"))

screen file_slots(title):
    default page_name_value = FilePageNameInputValue(pattern=_("{} страница"), auto=_("Автосохранения"), quick=_("Быстрые сохранения"))

    use game_menu(title):
        fixed:
            order_reverse True

            button:
                style "page_label"
                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"
                xalign 0.5
                yalign 0.5
                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):
                    $ slot = i + 1
                    button:
                        action FileAction(slot)
                        has vbox
                        add FileScreenshot(slot) xalign 0.5
                        text FileTime(slot, format=_("{#file_time}%A, %d %B %Y, %H:%M"), empty=_("Пустой слот")):
                            style "slot_time_text"
                        text FileSaveName(slot):
                            style "slot_name_text"
                        key "save_delete" action FileDelete(slot)

            vbox:
                style_prefix "page"
                xalign 0.5
                yalign 1.0
                hbox:
                    xalign 0.5
                    spacing gui.page_spacing

                    textbutton _("<") action FilePagePrevious()
                    key "save_page_prev" action FilePagePrevious()

                    if config.has_autosave:
                        textbutton _("{#auto_page}А") action FilePage("auto")

                    if config.has_quicksave:
                        textbutton _("{#quick_page}Б") action FilePage("quick")

                    for page in range(1, 10):
                        textbutton "[page]" action FilePage(page)

                    textbutton _(">") action FilePageNext()
                    key "save_page_next" action FilePageNext()

                if config.has_sync:
                    if CurrentScreenName() == "save":
                        textbutton _("Загрузить Sync") action UploadSync() xalign 0.5
                    else:
                        textbutton _("Скачать Sync") action DownloadSync() xalign 0.5




