# screens.rpy

init python:
    import random
    battle_victory = False
    battle_log = []
    last_enemy = None
    fusion_selected_1 = None
    fusion_selected_2 = None

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
        level = max(1, (p1.level + p2.level) // 2)
        base_stats = store._sloomp_base_stats(level)
        bonus_stats = {}
        stat_keys = ["hp", "defense", "attack_speed", "attack_power", "crit_chance", "crit_damage", "vampirism", "accuracy", "evasion"]
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
            possible = [t for t in ["color", "form", "face", "hat", "clothes", "mask", "weapon", "aura"] if t not in [f["type"] for f in new_features]]
            if possible:
                t = random.choice(possible)
                opt = store.FEATURE_DB.get(t, {})
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
        persistent.sloomp_collection.remove(p1)
        persistent.sloomp_collection.remove(p2)
        persistent.sloomp_collection.append(new_sloomp)
        if persistent.current_sloomp in (p1, p2):
            persistent.current_sloomp = new_sloomp
        fusion_selected_1 = None
        fusion_selected_2 = None
        if hasattr(store, "on_collection_changed"):
            store.on_collection_changed()
        renpy.notify("Создан " + new_sloomp.name + "!")
        renpy.restart_interaction()

    def add_sloomp_to_collection(sloomp):
        persistent.sloomp_collection.append(sloomp)
        if persistent.current_sloomp is None:
            persistent.current_sloomp = sloomp
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

    def battle_tick():
        global battle_active, battle_finished, last_player_attack_time, last_enemy_attack_time, hit_effect_target, hit_effect_type, hit_effect_timer, battle_victory, last_enemy
        if not battle_active:
            return
        player = persistent.current_sloomp
        enemy = current_enemy
        if player is None or enemy is None:
            battle_active = False
            return
        import time
        current_time = time.time()
        min_speed = getattr(store, "ATTACK_SPEED_MIN", 0.1)
        min_dmg = getattr(store, "MIN_DAMAGE", 1)
        if player.current_hp <= 0 or enemy.current_hp <= 0:
            battle_victory = (player.current_hp > 0)
            last_enemy = enemy
            battle_active = False
            battle_finished = True
            return
        player_speed = max(min_speed, player.final_stats["attack_speed"])
        if current_time - last_player_attack_time >= 1.0 / player_speed:
            last_player_attack_time = current_time
            player_dmg = int(player.final_stats["attack_power"])
            is_crit = random.random() < player.final_stats["crit_chance"]
            if is_crit:
                player_dmg = int(player_dmg * player.final_stats["crit_damage"])
                hit_effect_type = "crit"
            else:
                hit_effect_type = "normal"
            player_dmg = max(min_dmg, player_dmg - enemy.final_stats["defense"])
            enemy.current_hp -= player_dmg
            vamp_heal = int(player_dmg * player.final_stats["vampirism"])
            max_hp = player.final_stats["hp"]
            vamp_heal = min(vamp_heal, max(0, max_hp - player.current_hp))
            player.current_hp += vamp_heal
            hit_effect_target = "enemy"
            hit_effect_timer = getattr(store, "HIT_EFFECT_DURATION", 0.2)
            if enemy.current_hp <= 0:
                battle_victory = True
                last_enemy = enemy
                battle_active = False
                battle_finished = True
                return
        enemy_speed = max(min_speed, enemy.final_stats["attack_speed"])
        if battle_active and current_time - last_enemy_attack_time >= 1.0 / enemy_speed:
            last_enemy_attack_time = current_time
            enemy_dmg = int(enemy.final_stats["attack_power"])
            is_crit = random.random() < enemy.final_stats["crit_chance"]
            if is_crit:
                enemy_dmg = int(enemy_dmg * enemy.final_stats["crit_damage"])
            enemy_dmg = max(min_dmg, enemy_dmg - player.final_stats["defense"])
            player.current_hp -= enemy_dmg
            hit_effect_target = "player"
            hit_effect_type = "crit" if is_crit else "normal"
            hit_effect_timer = getattr(store, "HIT_EFFECT_DURATION", 0.2)
            if player.current_hp <= 0:
                battle_victory = False
                last_enemy = enemy
                battle_active = False
                battle_finished = True
                return
        if hit_effect_timer > 0:
            hit_effect_timer -= 0.05
            if hit_effect_timer <= 0:
                hit_effect_target = None
        renpy.restart_interaction()

screen game_menu(title):
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1400
        ysize 900
        background "#C0C0C0"
        has vbox
        text title size 40 xalign 0.5
        null height 20
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
            spacing 20
            text "БОЕВЫЕ ХЛЮПЫ" size 48 color "#FFFFFF" xalign 0.5
            text "Волна: [wave]" size 24 xalign 0.5
            if battle_aborted:
                textbutton "Продолжить" action Jump("start_battle") xminimum 250
            else:
                textbutton "Начать игру" action Jump("start_battle") xminimum 250
            textbutton "Мои хлюпы" action ShowMenu("collection") xminimum 250
            textbutton "Слияние" action ShowMenu("fusion_simple") xminimum 250
            textbutton "Магазин" action ShowMenu("shop") xminimum 250
            textbutton "Новая игра" action [Function(reset_game), Jump("start")] xminimum 250
            textbutton "Выход" action Quit() xminimum 250
            null height 20
            text "💰 [persistent.gold]" color "#FFD700" size 28 xalign 0.5

screen choose_upgrade():
    modal True
    add "images/gui/choose_bg.png"
    $ player = persistent.current_sloomp
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 800
        background "#7c6e6e"
        has vbox
        text "Выбери улучшение" size 40 xalign 0.5
        null height 10
        hbox:
            xalign 0.5
            spacing 20
            use sloomp_display(player, (120, 120))
            vbox:
                text "[player.name]" size 24
                text "❤️ HP: [player.current_hp]/[player.final_stats['hp']]" size 18
        null height 15
        text "Рероллов: [rerolls_left]" size 20 xalign 0.5
        hbox:
            xalign 0.5
            spacing 20
            if rerolls_left > 0:
                textbutton "Реролл (новые варианты)" action Function(do_reroll_upgrades) xminimum 220
        null height 20
        hbox:
            xalign 0.5
            spacing 40
            for upgrade in current_upgrade_choices:
                frame:
                    xysize (260, 380)
                    background "#ffa3a3"
                    has vbox
                    text upgrade["name"] size 20 xalign 0.5
                    text upgrade["description"] size 16
                    null height 20
                    textbutton "ВЫБРАТЬ" action [Function(apply_upgrade, upgrade), Hide("choose_upgrade"), Jump("after_upgrade")] xalign 0.5 xminimum 200
        if len(current_upgrade_choices) < 3:
            text "Выбери одно улучшение" size 18 color "#444" xalign 0.5

screen collection():
    tag menu
    use game_menu("Коллекция хлюпов"):
        vbox:
            spacing 10
            textbutton "← Назад" action Return() xminimum 120
            if persistent.current_sloomp:
                frame:
                    xfill True
                    has hbox
                    use sloomp_display(persistent.current_sloomp, (120, 120))
                    vbox:
                        text "[persistent.current_sloomp.name]" size 20
                        text "❤️ [persistent.current_sloomp.current_hp]/[persistent.current_sloomp.final_stats['hp']]" size 16
                    textbutton "Подробнее" action ShowMenu("sloomp_detail", persistent.current_sloomp) xminimum 120
            null height 20
            text "Все хлюпы:" size 24
            viewport:
                draggable True
                mousewheel True
                ysize 400
                vbox:
                    for sloomp in persistent.sloomp_collection:
                        frame:
                            xfill True
                            has hbox
                            use sloomp_display(sloomp, (60, 60))
                            vbox:
                                text "[sloomp.name]" size 18
                            if sloomp != persistent.current_sloomp:
                                textbutton "Выбрать" action [SetField(persistent, "current_sloomp", sloomp), Return()] xminimum 100
                            else:
                                text "АКТИВЕН" size 16

screen fusion_simple():
    tag menu
    use game_menu("Алтарь слияния"):
        vbox:
            textbutton "← Назад" action Return() xminimum 120
            null height 20
            hbox:
                xalign 0.5
                spacing 100
                frame:
                    xysize (350, 500)
                    background "#442266"
                    has vbox
                    if fusion_selected_1:
                        use sloomp_display(fusion_selected_1, (200, 200))
                        text "[fusion_selected_1.name]" size 18 xalign 0.5
                        $ s1 = fusion_selected_1.final_stats
                        text "❤️ HP: [s1['hp']]" size 14
                        text "⚔️ Атака: [s1['attack_power']]" size 14
                        text "🛡️ Защита: [s1['defense']]" size 14
                        textbutton "Снять выбор" action Function(clear_fusion_slot_1) xalign 0.5 xminimum 120
                    else:
                        text "Выберите первого хлюпа" size 18 xalign 0.5 yalign 0.5
                frame:
                    xysize (350, 500)
                    background "#442266"
                    has vbox
                    if fusion_selected_2:
                        use sloomp_display(fusion_selected_2, (200, 200))
                        text "[fusion_selected_2.name]" size 18 xalign 0.5
                        $ s2 = fusion_selected_2.final_stats
                        text "❤️ HP: [s2['hp']]" size 14
                        text "⚔️ Атака: [s2['attack_power']]" size 14
                        text "🛡️ Защита: [s2['defense']]" size 14
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
                    for sloomp in persistent.sloomp_collection:
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
            text "Характеристики:" size 20
            text "  ❤️ HP: [sloomp.final_stats['hp']]" size 18
            text "  🛡️ Защита: [sloomp.final_stats['defense']]" size 18
            text "  ⚡ Скорость атаки: [sloomp.final_stats['attack_speed']]" size 18
            text "  ⚔️ Сила атаки: [sloomp.final_stats['attack_power']]" size 18
            text "  🎯 Шанс крита: [sloomp.final_stats['crit_chance']*100]%" size 18
            text "  💥 Крит урон: [sloomp.final_stats['crit_damage']*100]%" size 18
            text "  💉 Вампиризм: [sloomp.final_stats['vampirism']*100]%" size 18
            text "  🎲 Точность: [sloomp.final_stats['accuracy']*100]%" size 18
            text "  🌀 Уклонение: [sloomp.final_stats['evasion']*100]%" size 18
            null height 10
            text "Особенности:" size 20
            for feat in sloomp.features:
                text "  • [feat['display_name']] ([feat['type']])" size 16
            null height 20
            textbutton "Назад" action Return() xminimum 120

screen sloomp_display(sloomp, size=(100, 100)):
    fixed:
        xysize size
        $ form_name = None
        $ color_name = None
        for feat in sloomp.features:
            if feat["type"] == "form":
                $ form_name = feat["name"]
            elif feat["type"] == "color":
                $ color_name = feat["name"]
        if form_name and color_name:
            $ base_image = "images/sloomps/{}_{}.png".format(form_name, color_name)
            add base_image xysize size
        else:
            add "images/placeholder.png" xysize size
        for ftype in ["face", "clothes", "hat", "mask", "weapon", "aura"]:
            for feat in sloomp.features:
                if feat["type"] == ftype and "image" in feat:
                    add feat["image"] xysize size

screen battle_animation():
    modal True
    add "images/gui/battle_bg.png"
    $ player = persistent.current_sloomp
    $ enemy = current_enemy
    fixed:
        xpos 400
        ypos 300
        use sloomp_display(player, (300, 300))
        vbox:
            ypos 320
            bar:
                value player.current_hp
                range player.final_stats["hp"]
                xmaximum 300
                ymaximum 25
            text "❤️ [player.current_hp]/[player.final_stats['hp']]" size 16 xalign 0.5
    fixed:
        xpos 1200
        ypos 300
        add enemy.image xysize (300, 300)
        vbox:
            ypos 320
            xalign 0.5
            text "[enemy.name]" size 24
            bar:
                value enemy.current_hp
                range enemy.final_stats["hp"]
                xmaximum 300
                ymaximum 25
            text "❤️ [enemy.current_hp]/[enemy.final_stats['hp']]" size 16 xalign 0.5
    if hit_effect_target == "enemy":
        fixed:
            xpos 1200
            ypos 300
            add "images/effects/hit_{}.png".format(hit_effect_type) xysize (300, 300) alpha 0.8
    elif hit_effect_target == "player":
        fixed:
            xpos 400
            ypos 300
            add "images/effects/hit_{}.png".format(hit_effect_type) xysize (300, 300) alpha 0.8
    frame:
        xalign 0.0
        yalign 1.0
        xoffset 20
        yoffset -20
        background "#000000AA"
        padding (15, 10)
        has vbox
        text "⚔️ Атака: [player.final_stats['attack_power']]" size 16
        text "🛡️ Защита: [player.final_stats['defense']]" size 16
        text "⚡ Скорость: [player.final_stats['attack_speed']]" size 16
        text "🎯 Крит: [player.final_stats['crit_chance']*100]%" size 16
        text "💉 Вампиризм: [player.final_stats['vampirism']*100]%" size 16
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
            textbutton "← Назад" action Return() xminimum 120
            null height 10
            frame:
                xfill True
                background "#333333"
                padding (15, 10)
                has hbox
                text "Золото: [persistent.gold]" color "#FFD700" size 24
            null height 20
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
                ("🌀 Уклонение", "evasion")
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

screen choose_sloomp(title, sloomps, after_battle=False):
    modal True
    add "images/gui/choose_bg.png"
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 800
        background "#7c6e6e"
        has vbox
        text title size 40 xalign 0.5
        null height 20
        hbox:
            xalign 0.5
            spacing 40
            for sloomp in sloomps:
                frame:
                    xysize (300, 560)
                    background "#332929"
                    has vbox
                    use sloomp_display(sloomp, (200, 200))
                    text "[sloomp.name]" size 18 xalign 0.5
                    text "❤️ HP: [sloomp.final_stats['hp']]" size 14
                    text "⚔️ Атака: [sloomp.final_stats['attack_power']]" size 14
                    text "🛡️ Защита: [sloomp.final_stats['defense']]" size 14
                    text "⚡ Скорость: [sloomp.final_stats['attack_speed']]" size 14
                    null height 10
                    textbutton "ВЫБРАТЬ" action [Function(add_sloomp_to_collection, sloomp), Hide("choose_sloomp"), Jump("after_choice_battle" if after_battle else "after_choice")] xalign 0.5 xminimum 200
