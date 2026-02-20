# relics.rpy — система реликвий

init -1 python:
    import random
    
    # Определение всех реликвий
    RELICS_DB = {
        "titan_power": {
            "id": "titan_power",
            "name": "Мощь титана",
            "description": "Хлюп наносит 5% от дополнительного здоровья как дополнительный урон, но не может наносить критический урон.",
            "icon": "images/relics/titan_power.png",
        },
        "sneaky_strike": {
            "id": "sneaky_strike",
            "name": "Подлый удар",
            "description": "Критические удары оглушают врагов на 1 секунду, но критический шанс не может быть больше 25%, а крит урон больше 140%.",
            "icon": "images/relics/sneaky_strike.png",
        },
        "shadow_wings": {
            "id": "shadow_wings",
            "name": "Теневые крылья",
            "description": "После уклонения хлюп наносит ответный удар (50% от обычного урона). Итоговая защита снижена на 15%.",
            "icon": "images/relics/shadow_wings.png",
        },
        "glass_cannon": {
            "id": "glass_cannon",
            "name": "Стеклянная пушка",
            "description": "Увеличивает весь наносимый урон на 15%, но также увеличивает получаемый урон на 20%.",
            "icon": "images/relics/glass_cannon.png",
        },
        "guardian_angel": {
            "id": "guardian_angel",
            "name": "Ангел-хранитель",
            "description": "Возрождает хлюпа при смерти 1 раз, но хлюп теряет 20% дополнительных характеристик и заработанного золота.",
            "icon": "images/relics/guardian_angel.png",
        },
        "berserker_mask": {
            "id": "berserker_mask",
            "name": "Маска берсерка",
            "description": "Чем меньше здоровья у хлюпа, тем выше его урон (до +40% при 10% HP). Но защита становится 0 на всю игру.",
            "icon": "images/relics/berserker_mask.png",
        },
        "storm_blade": {
            "id": "storm_blade",
            "name": "Грозовой клинок",
            "description": "Каждая 5 атака наносит дополнительный урон в виде 5% максимального здоровья врага, но точность атаки уменьшается на 50%.",
            "icon": "images/relics/storm_blade.png",
        },
    }
    
    def generate_relic_choices(count=3):
        """Генерирует случайные реликвии для выбора"""
        available = list(RELICS_DB.keys())
        chosen = random.sample(available, min(count, len(available)))
        return [RELICS_DB[rid].copy() for rid in chosen]
    
    def apply_relic_effects(player, relics):
        """Применяет эффекты реликвий к хлюпу (вызывается при пересчёте статов)"""
        if not relics:
            return
        
        relic_ids = [r.get("id") if isinstance(r, dict) else r for r in relics]
        
        # Мощь титана - блокирует криты
        if "titan_power" in relic_ids:
            player.final_stats["crit_chance"] = 0.0
        
        # Подлый удар - ограничивает крит шанс и урон
        if "sneaky_strike" in relic_ids:
            player.final_stats["crit_chance"] = min(player.final_stats.get("crit_chance", 0), 0.25)
            player.final_stats["crit_damage"] = min(player.final_stats.get("crit_damage", 1.0), 1.4)
        
        # Теневые крылья - снижает защиту на 15%
        if "shadow_wings" in relic_ids:
            player.final_stats["defense"] = int(player.final_stats.get("defense", 0) * 0.85)
        
        # Стеклянная пушка - увеличивает урон на 15% (применяется в бою)
        # Увеличение получаемого урона на 20% (применяется в бою)
        
        # Маска берсерка - защита становится 0
        if "berserker_mask" in relic_ids:
            player.final_stats["defense"] = 0
        
        # Грозовой клинок - точность уменьшается на 50%
        if "storm_blade" in relic_ids:
            player.final_stats["accuracy"] = max(0.0, player.final_stats.get("accuracy", 1.0) * 0.5)
