# script.rpy — точка входа и сюжетные метки

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

default persistent.gold = 0
default persistent.sloomp_collection = []
default persistent.current_sloomp = None
default persistent.shop_bonuses = {}

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
    jump start_battle

label after_choice_battle:
    jump start_battle

label start_battle:
    if persistent.current_sloomp is None:
        if persistent.sloomp_collection:
            $ persistent.current_sloomp = persistent.sloomp_collection[0]
        else:
            jump start
    $ current_enemy = generate_enemy(wave)
    $ persistent.current_sloomp.current_hp = min(persistent.current_sloomp.current_hp, persistent.current_sloomp.final_stats["hp"])
    $ persistent.current_sloomp.current_hp = max(persistent.current_sloomp.current_hp, persistent.current_sloomp.final_stats["hp"])
    $ current_enemy.current_hp = current_enemy.final_stats["hp"]
    $ battle_active = True
    $ battle_finished = False
    $ battle_aborted = False
    $ last_player_attack_time = 0.0
    $ last_enemy_attack_time = 0.0
    $ hit_effect_target = None
    $ hit_effect_type = None
    call screen battle_animation
    if battle_aborted:
        jump after_battle
    return

label show_battle_result:
    if battle_victory:
        $ exp_gain = EXP_PER_WAVE_BASE + wave * EXP_PER_WAVE_MULT
        $ persistent.current_sloomp.add_exp(exp_gain)
        $ gold_earned = give_gold_for_wave(wave)
        $ persistent.gold += gold_earned
        $ wave += 1
        if wave % 10 == 0:
            $ boss_choices = [generate_sloomp(SLOOMP_CHOICE_LEVEL) for _ in range(3)]
            call screen choose_sloomp("Выбери нового хлюпа", boss_choices, after_battle=True)
        else:
            $ rerolls_left = REROLLS_PER_RUN
            $ current_upgrade_choices = generate_upgrade_options(UPGRADE_CHOICES_COUNT, exclude_stats=None)
            call screen choose_upgrade
    else:
        $ wave = WAVE_START
        call screen battle_result(False, battle_log, last_enemy)
    return

label after_battle:
    call screen main_menu
    return

label after_upgrade:
    jump start_battle
