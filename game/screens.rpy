# screens.rpy

init python:
    import random
    fusion_slot1 = None
    fusion_slot2 = None

    battle_victory = False
    battle_log = []
    last_enemy = None
    selected_for_upgrade = None
    # Функции для слияния
    def sloomp_dragged(drags, drop):
        global fusion_slot1, fusion_slot2
        if not drop:
            return
        drag = drags[0]
        idx = int(drag.drag_name.split("_")[1])
        sloomp = persistent.sloomp_collection[idx]
        if drop.drag_name == "slot1":
            fusion_slot1 = sloomp
        elif drop.drag_name == "slot2":
            fusion_slot2 = sloomp
        renpy.restart_interaction()
        return True

    def slot_dragged(drags, drop):
        pass


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
        
        level = (p1.level + p2.level) // 2
        if level < 1:
            level = 1
        
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
        
        # Наследование бонусных характеристик
        bonus_stats = {}
        stat_keys = ["hp", "defense", "attack_speed", "attack_power", "crit_chance", "crit_damage", "vampirism", "accuracy", "evasion"]
        for key in stat_keys:
            choice = random.randint(0, 2)
            if choice == 0:
                bonus_stats[key] = p1.bonus_stats.get(key, 0)
            elif choice == 1:
                bonus_stats[key] = p2.bonus_stats.get(key, 0)
            else:
                if key in ["hp", "defense", "attack_power"]:
                    bonus_stats[key] = int((p1.bonus_stats.get(key,0) + p2.bonus_stats.get(key,0)) / 2)
                else:
                    bonus_stats[key] = (p1.bonus_stats.get(key,0) + p2.bonus_stats.get(key,0)) / 2.0
        
        # Наследование особенностей
        feat_by_type_p1 = {feat["type"]: feat for feat in p1.features}
        feat_by_type_p2 = {feat["type"]: feat for feat in p2.features}
        
        new_features = []
        all_types = set(feat_by_type_p1.keys()) | set(feat_by_type_p2.keys())
        
        for t in all_types:
            if t in feat_by_type_p1 and t in feat_by_type_p2:
                chosen = random.choice([feat_by_type_p1[t], feat_by_type_p2[t]])
                new_features.append(chosen.copy())
            elif t in feat_by_type_p1:
                new_features.append(feat_by_type_p1[t].copy())
            else:
                new_features.append(feat_by_type_p2[t].copy())
        
        # Мутация (20%)        ПРИДУМАТЬ СЛОЖНУЮ СИСТЕМУ МУТАЦИЙ, ТИПА СИНИЙ+КРАСНЫЙ РОДИТЕЛЬ = ШАНС НА ОРАНЖЕВОГО
        if random.random() < 0.2:
            possible_types = ["color", "form", "face", "hat", "clothes", "mask", "weapon", "aura"]
            existing = [feat["type"] for feat in new_features]
            available = [t for t in possible_types if t not in existing]
            if available:
                t = random.choice(available)
                options = FEATURE_DB[t]
                chosen = random.choice(list(options.values()))
                new_feat = chosen.copy()
                new_feat["type"] = t
                new_features.append(new_feat)
        
        # Имя
        name_parts = []
        for feat in new_features:
            if feat["type"] in ("color", "form", "face"):
                name_parts.append(feat["display_name"])
        if not name_parts:
            name_parts = ["Микс"]
        name = " ".join(name_parts) + f" Lv.{level}"
        
        # Создание нового хлюпа
        new_sloomp = Sloomp(name, level, base_stats, new_features)
        new_sloomp.bonus_stats = bonus_stats.copy()
        new_sloomp.final_stats = new_sloomp.calc_final_stats()
        new_sloomp.current_hp = new_sloomp.final_stats["hp"]
        
        # Удаление родителей
        persistent.sloomp_collection.remove(p1)
        persistent.sloomp_collection.remove(p2)
        persistent.sloomp_collection.append(new_sloomp)
        
        # Если текущий активный хлюп был родителем, заменяем
        if persistent.current_sloomp in (p1, p2):
            persistent.current_sloomp = new_sloomp
        
        fusion_selected_1 = None
        fusion_selected_2 = None
        
        renpy.notify(f"Создан {new_sloomp.name}!")
        renpy.restart_interaction()

    def buy_stat_upgrade(stat_name):
        global selected_for_upgrade
        if selected_for_upgrade is None:
            return
        sl = selected_for_upgrade
        if sl.bonus_stats[stat_name] >= sl.level:
            renpy.notify("Достигнут максимум улучшений для этого уровня")
            return
        cost = 10 * (sl.bonus_stats[stat_name] + 1)
        if persistent.gold < cost:
            renpy.notify("Недостаточно золота")
            return
        persistent.gold -= cost
        sl.bonus_stats[stat_name] += 1
        # Пересчитываем финальные статы
        sl.final_stats = sl.calc_final_stats()
        # Восстанавливаем HP до нового максимума (опционально)
        sl.current_hp = sl.final_stats["hp"]
        renpy.notify("Улучшение куплено!")
        renpy.restart_interaction()

    def buy_level_upgrade():
        global selected_for_upgrade
        if selected_for_upgrade is None:
            return
        sl = selected_for_upgrade
        cost = 50 * sl.level
        if persistent.gold < cost:
            renpy.notify("Недостаточно золота")
            return
        persistent.gold -= cost
        sl.level_up()  # level_up уже должен увеличивать base_stats и пересчитывать final_stats
        renpy.notify("Уровень повышен!")
        renpy.restart_interaction()
    def perform_fusion():
        global fusion_slot1, fusion_slot2
        if fusion_slot1 is None or fusion_slot2 is None or fusion_slot1 == fusion_slot2:
            renpy.notify("Нужны два разных хлюпа!")
            return
        
        p1 = fusion_slot1
        p2 = fusion_slot2
        
        level = (p1.level + p2.level) // 2
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
        
        features = []
        used_types = set()
        for parent in [p1, p2]:
            for feat in parent.features:
                if feat["type"] not in used_types:
                    new_feat = feat.copy()
                    features.append(new_feat)
                    used_types.add(feat["type"])
        
        all_types = ["color", "form", "face", "hat", "clothes", "mask", "weapon", "aura"]
        available = [t for t in all_types if t not in used_types and random.random() < 0.3]
        for ftype in available:
            options = FEATURE_DB[ftype]
            chosen = random.choice(list(options.values()))
            new_feat = chosen.copy()
            new_feat["type"] = ftype
            features.append(new_feat)
        
        name = f"Микс Lv.{level}"
        new_sloomp = Sloomp(name, level, base_stats, features)
        
        persistent.sloomp_collection.remove(p1)
        persistent.sloomp_collection.remove(p2)
        persistent.sloomp_collection.append(new_sloomp)
        
        if persistent.current_sloomp in (p1, p2):
            persistent.current_sloomp = new_sloomp
        
        fusion_slot1 = None
        fusion_slot2 = None
        
        renpy.notify(f"Создан {new_sloomp.name}!")
        renpy.restart_interaction()
    
    def add_sloomp_to_collection(sloomp):
        persistent.sloomp_collection.append(sloomp)
        if persistent.current_sloomp is None:
            persistent.current_sloomp = sloomp

    def render_sloomp_mini(sloomp):
        form_name = None
        color_name = None
        for feat in sloomp.features:
            if feat["type"] == "form":
                form_name = feat["name"]
            elif feat["type"] == "color":
                color_name = feat["name"]
        base = "images/sloomps/{}_{}.png".format(form_name, color_name) if (form_name and color_name) else "images/placeholder.png"
        layers = [(0,0), base]
        for ftype in ["face", "clothes", "hat", "mask", "weapon", "aura"]:
            for feat in sloomp.features:
                if feat["type"] == ftype and "image" in feat:
                    layers.append((0,0))
                    layers.append(feat["image"])
        return LiveComposite((100,100), *layers)

    battle_active = False
    battle_finished = False
    last_player_attack_time = 0.0
    last_enemy_attack_time = 0.0
    hit_effect_target = None  # "player" или "enemy"
    hit_effect_type = None    # "normal" или "crit"
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
        
        import time, random
        current_time = time.time()
        
        # Проверка гибели (если вдруг уже мертвы)
        if player.current_hp <= 0 or enemy.current_hp <= 0:
            battle_victory = (player.current_hp > 0)
            last_enemy = enemy
            battle_active = False
            battle_finished = True
            #renpy.hide_screen("battle_animation")
            return
        
        # Атака игрока
        if current_time - last_player_attack_time >= 1.0 / player.final_stats["attack_speed"]:
            last_player_attack_time = current_time
            # расчёт урона
            player_dmg = int(player.final_stats["attack_power"])
            # крит?
            is_crit = random.random() < player.final_stats["crit_chance"]
            if is_crit:
                player_dmg = int(player_dmg * player.final_stats["crit_damage"])
                hit_effect_type = "crit"
            else:
                hit_effect_type = "normal"
            player_dmg = max(1, player_dmg - enemy.final_stats["defense"])
            enemy.current_hp -= player_dmg
            # вампиризм
            player.current_hp += int(player_dmg * player.final_stats["vampirism"])
            # устанавливаем эффект на враге
            hit_effect_target = "enemy"
            hit_effect_timer = 0.2  # показывать 0.2 секунды
            
            # Проверка гибели после удара
            if enemy.current_hp <= 0:
                battle_victory = True
                last_enemy = enemy
                battle_active = False
                battle_finished = True
                #renpy.hide_screen("battle_animation")
                return
        
        # Атака врага (если враг ещё жив)
        if battle_active and current_time - last_enemy_attack_time >= 1.0 / enemy.final_stats["attack_speed"]:
            last_enemy_attack_time = current_time
            enemy_dmg = int(enemy.final_stats["attack_power"])
            # крит?
            is_crit = random.random() < enemy.final_stats["crit_chance"]
            if is_crit:
                enemy_dmg = int(enemy_dmg * enemy.final_stats["crit_damage"])
                # для эффекта используем тот же hit_effect_type, но для цели "player"
            # защита
            enemy_dmg = max(1, enemy_dmg - player.final_stats["defense"])
            player.current_hp -= enemy_dmg
            hit_effect_target = "player"
            hit_effect_type = "crit" if is_crit else "normal"
            hit_effect_timer = 0.2
            
            if player.current_hp <= 0:
                battle_victory = False
                last_enemy = enemy
                battle_active = False
                battle_finished = True
                #renpy.hide_screen("battle_animation")
                return
        
        # Уменьшаем таймер эффекта
        if hit_effect_timer > 0:
            hit_effect_timer -= 0.05  # примерно соответствует частоте тиков
            if hit_effect_timer <= 0:
                hit_effect_target = None
        
        renpy.restart_interaction()
# Экран-обёртка для меню (адаптирован под FHD)
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

# Главное меню
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
            textbutton "Начать игру" action Jump("start_battle") xminimum 250
            textbutton "Мои хлюпы" action ShowMenu("collection") xminimum 250
            textbutton "Слияние" action ShowMenu("fusion_simple") xminimum 250
            textbutton "Магазин" action ShowMenu("select_sloomp_for_upgrade") xminimum 250
            textbutton "Новая игра" action [Function(reset_game), Jump("start")] xminimum 250
            textbutton "Выход" action Quit() xminimum 250
            null height 20
            text "💰 [persistent.gold]" color "#FFD700" size 28 xalign 0.5
# Экран выбора уровня
screen level_select():
    tag menu
    use game_menu("Выбор уровня"):
        vbox:
            spacing 15
            textbutton "← В меню" action Return()
            null height 10
            viewport:
                draggable True
                mousewheel True
                ysize 600
                vbox:
                    spacing 10
                    for i in range(0, 100, 2):
                        hbox:
                            spacing 20
                            # уровень i+1
                            $ lev1 = i+1
                            $ bg1 = "#3366CC" if lev1 <= persistent.max_level else "#666666"
                            $ hover1 = "#4477DD" if lev1 <= persistent.max_level else "#666666"
                            button:
                                xminimum 200
                                yminimum 80
                                background bg1
                                hover_background hover1
                                action If(lev1 <= persistent.max_level, [SetVariable("persistent.selected_level", lev1), Jump("start_battle")], None)
                                has vbox
                                text "Уровень [lev1]" size 24
                                if lev1 <= persistent.max_level:
                                    text "Доступен" size 14
                                else:
                                    text "🔒 Закрыт" size 14
                            # уровень i+2, если существует
                            if i+2 <= 100:
                                $ lev2 = i+2
                                $ bg2 = "#3366CC" if lev2 <= persistent.max_level else "#666666"
                                $ hover2 = "#4477DD" if lev2 <= persistent.max_level else "#666666"
                                button:
                                    xminimum 200
                                    yminimum 80
                                    background bg2
                                    hover_background hover2
                                    action If(lev2 <= persistent.max_level, [SetVariable("persistent.selected_level", lev2), Jump("start_battle")], None)
                                    has vbox
                                    text "Уровень [lev2]" size 24
                                    if lev2 <= persistent.max_level:
                                        text "Доступен" size 14
                                    else:
                                        text "🔒 Закрыт" size 14

screen choose_upgrade():
    modal True
    add "images/gui/choose_bg.png"  # замените на свой фон или Solid
    
    $ player = persistent.current_sloomp
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 800
        background "#7c6e6e"
        has vbox
        text "Выбери улучшение" size 40 xalign 0.5
        null height 20
        
        hbox:
            xalign 0.5
            spacing 20
            use sloomp_display(player, (120,120))
            vbox:
                text "[player.name]" size 24
                text "Уровень: [player.level]" size 20
                text "❤️ HP: [player.current_hp]/[player.final_stats['hp']]" size 18
                text "Опыт: [player.exp]/[player.exp_to_next]" size 16
        
        null height 30
        
        $ upgrades = [generate_random_upgrade() for i in range(3)]
        hbox:
            xalign 0.5
            spacing 40
            for upgrade in upgrades:
                frame:
                    xysize (250, 400)
                    background "#ffa3a3"
                    has vbox
                    text upgrade["name"] size 20 xalign 0.5
                    text upgrade["description"] size 16
                    null height 20
                    textbutton "ВЫБРАТЬ" action [Function(apply_upgrade, upgrade), Hide("choose_upgrade"), Jump("after_upgrade")] xalign 0.5
                    
# Экран коллекции
screen collection():
    tag menu
    use game_menu("Коллекция хлюпов"):
        vbox:
            spacing 10
            textbutton "← Назад" action Return()
            if persistent.current_sloomp:
                frame:
                    xfill True
                    has hbox
                    use sloomp_display(persistent.current_sloomp, (120,120))
                    vbox:
                        text "[persistent.current_sloomp.name] (Ур. [persistent.current_sloomp.level])" size 20
                        text "❤️ [persistent.current_sloomp.current_hp]/[persistent.current_sloomp.final_stats['hp']]" size 16
                        textbutton "Подробнее" action ShowMenu("sloomp_detail", persistent.current_sloomp)
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
                            use sloomp_display(sloomp, (60,60))
                            vbox:
                                text "[sloomp.name]" size 18
                                text "Ур.[sloomp.level]" size 16
                            if sloomp != persistent.current_sloomp:
                                textbutton "Выбрать" action [SetField(persistent, "current_sloomp", sloomp), Return()]
                            else:
                                text "АКТИВЕН" size 16

screen fusion_simple():
    tag menu
    use game_menu("Алтарь слияния"):
        vbox:
            textbutton "← Назад" action Return()
            null height 20
            
            # Верхняя панель с выбранными хлюпами
            hbox:
                xalign 0.5
                spacing 100
                # Первый слот

                frame:
                    xysize (350, 500)
                    background "#442266"
                    has vbox
                    if fusion_selected_1:
                        use sloomp_display(fusion_selected_1, (200,200))
                        text "[fusion_selected_1.name]" size 18 xalign 0.5
                        text "Ур.[fusion_selected_1.level]" size 16 xalign 0.5
                        $ s1 = fusion_selected_1.final_stats
                        text "❤️ HP: [s1['hp']]" size 14
                        text "⚔️ Атака: [s1['attack_power']]" size 14
                        text "🛡️ Защита: [s1['defense']]" size 14
                        text "⚡ Скорость: [s1['attack_speed']]" size 14
                        text "🎯 Крит: [s1['crit_chance']*100]%" size 14
                        text "💥 Крит.урон: [s1['crit_damage']*100]%" size 14
                        text "💉 Вампиризм: [s1['vampirism']*100]%" size 14
                        textbutton "Снять выбор" action [SetVariable("fusion_selected_1", None), renpy.restart_interaction] xalign 0.5
                    else:
                        text "Выберите первого хлюпа" size 18 xalign 0.5 yalign 0.5
                
                # Второй слот
                frame:
                    xysize (350, 500)
                    background "#442266"
                    has vbox
                    if fusion_selected_2:
                        use sloomp_display(fusion_selected_2, (200,200))
                        text "[fusion_selected_2.name]" size 18 xalign 0.5
                        text "Ур.[fusion_selected_2.level]" size 16 xalign 0.5
                        $ s2 = fusion_selected_2.final_stats
                        text "❤️ HP: [s2['hp']]" size 14
                        text "⚔️ Атака: [s2['attack_power']]" size 14
                        text "🛡️ Защита: [s2['defense']]" size 14
                        text "⚡ Скорость: [s2['attack_speed']]" size 14
                        text "🎯 Крит: [s2['crit_chance']*100]%" size 14
                        text "💥 Крит.урон: [s2['crit_damage']*100]%" size 14
                        text "💉 Вампиризм: [s2['vampirism']*100]%" size 14
                        textbutton "Снять выбор" action [SetVariable("fusion_selected_2", None), renpy.restart_interaction] xalign 0.5
                    else:
                        text "Выберите второго хлюпа" size 18 xalign 0.5 yalign 0.5
            
            null height 30
            
            # Кнопка слияния
            if fusion_selected_1 and fusion_selected_2 and fusion_selected_1 != fusion_selected_2:
                textbutton "НАЧАТЬ СЛИЯНИЕ" action Function(perform_simple_fusion) xalign 0.5
            else:
                text "Выберите двух разных хлюпов" color "#888" xalign 0.5
            
            null height 30
            
            # Список всех хлюпов (как в коллекции)
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
                            use sloomp_display(sloomp, (50,50))
                            vbox:
                                text "[sloomp.name]" size 16
                                text "Ур.[sloomp.level]" size 14
                            # Кнопка выбора
                            if sloomp != fusion_selected_1 and sloomp != fusion_selected_2:
                                textbutton "Выбрать" action Function(select_for_fusion, sloomp) xalign 0.5
                            else:
                                text "Уже выбран" color "#888" xalign 0.5

# Детальный просмотр
screen sloomp_detail(sloomp):
    tag menu
    use game_menu("Характеристики"):
        vbox:
            textbutton "← Назад" action Return()
            use sloomp_display(sloomp, (250,250))
            text "Имя: [sloomp.name]" size 22
            text "Уровень: [sloomp.level]" size 20
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

# Экран отображения хлюпа (сборка из слоёв)
screen sloomp_display(sloomp, size=(100,100)):
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

# Экран битвы с кнопкой "Начать бой"
screen battle_screen(enemy):
    modal True
    add "images/gui/battle_bg.png"
    
    # Спрайт хлюпа
    fixed:
        xpos 400
        ypos 300
        use sloomp_display(persistent.current_sloomp, (300,300))
    
    # Спрайт врага (временная заглушка)
    fixed:
        xpos 1200
        ypos 300
        frame:
            xpos 1200
            ypos 300
            add enemy.image xysize (300,300)
            text "[enemy.name]" color "#FFF" size 30 xalign 0.5 yalign 0.5
    
    # Полоска здоровья хлюпа
    frame:
        xalign 0.0
        yalign 0.0
        xoffset 20
        yoffset 20
        background "#228822"
        padding (15, 10)
        has vbox
        text "[persistent.current_sloomp.name]" size 24
        bar:
            value persistent.current_sloomp.current_hp
            range persistent.current_sloomp.final_stats["hp"]
            xmaximum 300
            ymaximum 25
        text "❤️ [persistent.current_sloomp.current_hp]/[persistent.current_sloomp.final_stats['hp']]" size 16
    
    # Полоска здоровья врага
    frame:
        xalign 1.0
        yalign 0.0
        xoffset -20
        yoffset 20
        background "#882222"
        padding (15, 10)
        has vbox
        text "[enemy.name]" size 24
        bar:
            value enemy.current_hp
            range enemy.final_stats["hp"]
            xmaximum 300
            ymaximum 25
        text "❤️ [enemy.current_hp]/[enemy.final_stats['hp']]" size 16
    
    # Кнопка начала боя
    frame:
        xalign 0.5
        yalign 0.9
        background "#AAAAAA"
        padding (40, 20)
        textbutton "НАЧАТЬ БОЙ" action [Hide("battle_screen"), Jump("battle_loop")] text_size 36

# Экран анимации боя (без кнопки, обновляется в цикле)
screen battle_animation():
    modal True
    add "images/gui/battle_bg.png"
    
    $ player = persistent.current_sloomp
    $ enemy = current_enemy
    
    # Спрайт игрока слева с полоской здоровья
    fixed:
        xpos 400
        ypos 300
        use sloomp_display(player, (300,300))
        vbox:
            ypos 320
            bar:
                value player.current_hp
                range player.final_stats["hp"]
                xmaximum 300
                ymaximum 25
            text "❤️ [player.current_hp]/[player.final_stats['hp']]" size 16 xalign 0.5
    
    # Спрайт врага справа с полоской здоровья
    fixed:
        xpos 1200
        ypos 300
        add enemy.image xysize (300,300)
        vbox:
            ypos 320
            xalign 50
            text "[enemy.name]" size 24
            bar:
                value enemy.current_hp
                range enemy.final_stats["hp"]
                xmaximum 300
                ymaximum 25
            text "❤️ [enemy.current_hp]/[enemy.final_stats['hp']]" size 16 xalign 0.5
    
    # Эффекты удара
    if hit_effect_target == "enemy":
        fixed:
            xpos 1200
            ypos 300
            add "images/effects/hit_{}.png".format(hit_effect_type) xysize (300,300) alpha 0.8
    elif hit_effect_target == "player":
        fixed:
            xpos 400
            ypos 300
            add "images/effects/hit_{}.png".format(hit_effect_type) xysize (300,300) alpha 0.8
    
    # Характеристики игрока
    frame:
        xalign 0.0
        yalign 1.0
        xoffset 20
        yoffset -20
        background "#000000AA"
        padding (15, 10)
        has vbox
        text "Характеристики:" size 20
        text "Уровень: [player.level]" size 16
        text "Опыт: [player.exp]/[player.exp_to_next]" size 16
        text "⚔️ Атака: [player.final_stats['attack_power']]" size 16
        text "🛡️ Защита: [player.final_stats['defense']]" size 16
        text "⚡ Скорость: [player.final_stats['attack_speed']]" size 16
        text "🎯 Крит: [player.final_stats['crit_chance']*100]%" size 16
        text "💥 Крит.урон: [player.final_stats['crit_damage']*100]%" size 16
        text "💉 Вампиризм: [player.final_stats['vampirism']*100]%" size 16
        text "🎲 Точность: [player.final_stats['accuracy']*100]%" size 16
        text "🌀 Уклонение: [player.final_stats['evasion']*100]%" size 16
    
    # Таймер боя
    timer 0.05 repeat True action Function(battle_tick)
    
    # Кнопка прерывания
    frame:
        xalign 0.5
        yalign 0.95
        background "#AAAAAA"
        padding (20, 10)
        textbutton "Прервать бой" action [Function(lambda: setattr(store, 'battle_active', False)), Hide("battle_animation"), Return()] text_size 24

    if battle_finished:
        timer 0.3 action [Hide("battle_animation"), Jump("show_battle_result")]
# Экран результата боя
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
            text "Получено золота: [reward_gold]" size 20 xalign 0.5
            # Здесь можно добавить текст о повышении волны, но он будет виден в главном меню
            hbox:
                xalign 0.5
                spacing 40
                textbutton "В меню" action Jump("after_battle") text_size 24
        else:
            text "💔 Поражение..." color "#AA0000" size 32 xalign 0.5
            hbox:
                xalign 0.5
                spacing 40
                textbutton "В меню" action Jump("after_battle") text_size 24
                textbutton "Повторить" action Jump("start_battle") text_size 24

screen select_sloomp_for_upgrade():
    tag menu
    use game_menu("Выберите хлюпа для улучшения"):
        vbox:
            textbutton "← Назад" action Return()
            null height 20
            viewport:
                draggable True
                mousewheel True
                ysize 600
                vbox:
                    for sloomp in persistent.sloomp_collection:
                        frame:
                            xfill True
                            has hbox
                            use sloomp_display(sloomp, (80,80))
                            vbox:
                                text "[sloomp.name]" size 18
                                text "Ур.[sloomp.level]" size 16
                                text "❤️ [sloomp.current_hp]/[sloomp.final_stats['hp']]" size 14
                            textbutton "Улучшить" action [SetVariable("selected_for_upgrade", sloomp), ShowMenu("upgrade_shop")] xalign 0.5

screen upgrade_shop():
    tag menu
    use game_menu("Магазин улучшений"):
        if selected_for_upgrade:
            vbox:
                textbutton "← Назад" action Return()
                null height 10
                # Информация о выбранном хлюпе
                hbox:
                    use sloomp_display(selected_for_upgrade, (150,150))
                    vbox:
                        text "[selected_for_upgrade.name]" size 24
                        text "Уровень: [selected_for_upgrade.level]" size 18
                        text "Золото: [persistent.gold]" color "#FFD700" size 18
                
                null height 20
                text "Улучшение характеристик (макс. = уровень хлюпа):" size 20
                # Список статов для улучшения
                $ stats_list = [
                    ("❤️ HP", "hp"),
                    ("🛡️ Защита", "defense"),
                    ("⚡ Скорость атаки", "attack_speed"),
                    ("⚔️ Сила атаки", "attack_power"),
                    ("🎯 Шанс крита", "crit_chance"),
                    ("💥 Крит.урон", "crit_damage"),
                    ("💉 Вампиризм", "vampirism"),
                    ("🎲 Точность", "accuracy"),
                    ("🌀 Уклонение", "evasion")
                ]
                grid 2 5:
                    spacing 10
                    for label, stat in stats_list:
                        frame:
                            xsize 350
                            background "#333333"
                            has vbox
                            text "[label]" size 16
                            text "Текущий бонус: [selected_for_upgrade.bonus_stats[stat]]" size 14
                            if selected_for_upgrade.bonus_stats[stat] < selected_for_upgrade.level:
                                $ cost = 10 * (selected_for_upgrade.bonus_stats[stat] + 1)
                                text "Стоимость: [cost]💰" size 14
                                textbutton "Купить" action Function(buy_stat_upgrade, stat) xalign 0.5
                            else:
                                text "Максимум" color "#888" size 14
                
                null height 30
                # Повышение уровня
                frame:
                    xfill True
                    background "#444444"
                    has vbox
                    text "Повышение уровня" size 22
                    $ level_cost = 50 * selected_for_upgrade.level
                    text "Текущий уровень: [selected_for_upgrade.level]" size 16
                    text "Стоимость: [level_cost]💰" size 16
                    textbutton "Повысить уровень" action Function(buy_level_upgrade) xalign 0.5
        else:
            text "Ошибка: хлюп не выбран" color "#F00"
            textbutton "Назад" action Return()

screen choose_sloomp(title, sloomps, after_battle=False):
    modal True
    add "images/gui/choose_bg.png"          # замените на свой фон или используйте Solid
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
                    xysize (300, 600)
                    background "#332929"
                    has vbox
                    use sloomp_display(sloomp, (200,200))
                    text "[sloomp.name]" size 18 xalign 0.5
                    text "Ур. [sloomp.level]" size 16 xalign 0.5
                    text "❤️ HP: [sloomp.final_stats['hp']]" size 14
                    text "⚔️ Атака: [sloomp.final_stats['attack_power']]" size 14
                    text "🛡️ Защита: [sloomp.final_stats['defense']]" size 14
                    text "⚡ Скорость: [sloomp.final_stats['attack_speed']]" size 14
                    text "🎯 Крит: [sloomp.final_stats['crit_chance']*100]%" size 14
                    text "💥 Крит.урон: [sloomp.final_stats['crit_damage']*100]%" size 14
                    text "💉 Вампиризм: [sloomp.final_stats['vampirism']*100]%" size 14
                    null height 10
                    textbutton "ВЫБРАТЬ" action [Function(add_sloomp_to_collection, sloomp), Hide("choose_sloomp"), Jump("after_choice_battle" if after_battle else "after_choice")] xalign 0.5

# Экран слияния
screen fusion():
    tag menu
    use game_menu("Алтарь слияния"):
        $ slot1 = getattr(store, 'fusion_slot1', None)
        $ slot2 = getattr(store, 'fusion_slot2', None)
        vbox:
            textbutton "← Назад" action Return()
            null height 20
            text "Перетащи двух хлюпов в круги:" size 22
            frame:
                xsize 900
                ysize 400
                background "#442266"
                draggroup:
                    drag:
                        drag_name "slot1"
                        droppable True
                        xpos 200 ypos 100
                        child "images/gui/fusion_slot.png"
                        dragged slot_dragged
                        if slot1:
                            add Transform(child=render_sloomp_mini(slot1), size=(100,100)) pos (200,100)
                    drag:
                        drag_name "slot2"
                        droppable True
                        xpos 500 ypos 100
                        child "images/gui/fusion_slot.png"
                        dragged slot_dragged
                        if slot2:
                            add Transform(child=render_sloomp_mini(slot2), size=(100,100)) pos (500,100)
                    $ x_start = 100
                    $ y_start = 250
                    $ i = 0
                    for sloomp in persistent.sloomp_collection:
                        $ drag_id = "sloomp_" + str(i)
                        drag:
                            drag_name drag_id
                            draggable True
                            droppable False
                            xpos x_start + (i % 3) * 150
                            ypos y_start + (i // 3) * 120
                            child Transform(child=render_sloomp_mini(sloomp), size=(80,80))
                            dragged sloomp_dragged
                        $ i += 1
            if slot1 and slot2 and slot1 != slot2:
                textbutton "СЛИТЬ!" action Function(perform_fusion) xalign 0.5
            else:
                text "Выберите двух разных хлюпов" color "#888" xalign 0.5

# Экран улучшения
screen upgrade():
    tag menu
    use game_menu("Улучшение"):
        if persistent.current_sloomp:
            vbox:
                text "Текущий хлюп: [persistent.current_sloomp.name]" size 22
                text "Уровень: [persistent.current_sloomp.level]" size 20
                text "Цена улучшения: 50💰" size 20
                textbutton "Повысить уровень" action If(persistent.gold >= 50, [Function(persistent.current_sloomp.level_up), SetVariable("persistent.gold", persistent.gold - 50), renpy.notify("Уровень повышен!")]) xalign 0.5
                textbutton "Назад" action Return()