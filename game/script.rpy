# script.rpy — точка входа и сюжетные метки
# Коллекция и текущий хлюп живут в store; в persistent сохраняются только sloomp_data и current_sloomp_index.

default wave = 1
default battle_aborted = False
default battle_active = False
default battle_finished = False
default rerolls_left = 3
default current_upgrade_choices = []
default current_enemy = None
default battle_victory = False
default battle_log = []
default last_enemy = None

default shop_tab = "upgrades"
default egg_roll_active = False
default egg_roll_candidates = []
default egg_roll_index = 0
default egg_roll_spins_left = 0
default egg_roll_final = None
default egg_roll_egg = None

default sloomp_collection = []
default current_sloomp = None
default player_relics = []
default current_relic_choices = []
default battle_player_attack_count = 0
default battle_enemy_stunned_until = 0.0
default guardian_angel_used = False

default persistent.gold = 0
default persistent.shop_bonuses = {}
default persistent.in_run = False
default persistent.wave = 1
default persistent.sloomp_data = []
default persistent.current_sloomp_index = None

label start:
    $ load_sloomp_from_persistent()
    if current_sloomp is None and sloomp_collection:
        $ current_sloomp = sloomp_collection[0]
    if persistent.in_run:
        $ wave = persistent.wave
    call screen main_menu
    return

label need_first_sloomp:
    $ start_choices = [generate_sloomp(1) for _ in range(3)]
    call screen choose_sloomp("Выбери своего первого хлюпа", start_choices, after_battle=False)
    jump start_battle

label after_choice:
    jump start_battle

label after_boss_sloomp_then_relic:
    $ current_relic_choices = generate_relic_choices(3)
    call screen choose_relic
    jump start_battle

label after_choice_battle:
    jump start_battle

label start_battle:
    if current_sloomp is None:
        if sloomp_collection:
            $ current_sloomp = sloomp_collection[0]
        else:
            jump need_first_sloomp
    $ persistent.in_run = True
    $ persistent.wave = wave
    $ current_enemy = generate_enemy(wave)
    $ current_sloomp.current_hp = min(current_sloomp.current_hp, current_sloomp.final_stats["hp"])
    $ current_sloomp.current_hp = max(0, current_sloomp.current_hp)
    $ current_enemy.current_hp = current_enemy.final_stats["hp"]
    $ battle_active = True
    $ battle_finished = False
    $ battle_aborted = False
    $ last_player_attack_time = 0.0
    $ last_enemy_attack_time = 0.0
    $ hit_effect_target = None
    $ hit_effect_type = None
    $ battle_player_attack_count = 0
    $ battle_enemy_stunned_until = 0.0
    $ guardian_angel_used = False
    call screen battle_animation
    if battle_aborted:
        jump after_battle
    return

label show_battle_result:
    if battle_victory:
        $ was_boss_wave = (wave % BOSS_WAVE_EVERY == 0 and wave >= BOSS_WAVE_EVERY)
        $ exp_gain = EXP_PER_WAVE_BASE + wave * EXP_PER_WAVE_MULT
        $ current_sloomp.add_exp(exp_gain)
        $ gold_earned = give_gold_for_wave(wave)
        $ persistent.gold += gold_earned
        $ wave += 1
        $ persistent.wave = wave
        if was_boss_wave:
            $ boss_choices = [generate_sloomp(SLOOMP_CHOICE_LEVEL) for _ in range(3)]
            call screen choose_sloomp("Выбери нового хлюпа (после босса)", boss_choices, after_battle=True)
        else:
            if rerolls_left <= 0:
                $ rerolls_left = REROLLS_PER_RUN
            $ current_upgrade_choices = generate_upgrade_options(UPGRADE_CHOICES_COUNT, exclude_stats=None)
            call screen choose_upgrade
    else:
        $ dead = current_sloomp
        $ sloomp_collection = [s for s in sloomp_collection if s is not dead]
        if sloomp_collection:
            $ current_sloomp = sloomp_collection[0]
        else:
            $ current_sloomp = None
        $ player_relics = []
        $ guardian_angel_used = False
        $ sync_sloomp_to_persistent()
        $ persistent.in_run = False
        $ wave = WAVE_START
        $ persistent.wave = wave
        call screen battle_result(False, battle_log, last_enemy)
    return

label after_battle:
    $ persistent.in_run = False
    call screen main_menu
    return

label after_upgrade:
    jump start_battle
