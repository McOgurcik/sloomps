# classes.rpy — классы Sloomp и Enemy

init -1 python:
    import random

    class Sloomp:
        def __init__(self, name, level, base_stats, features):
            self.name = name
            self.level = level
            self.base_stats = base_stats.copy()
            self.features = features
            self.bonus_stats = {key: 0 for key in base_stats.keys()}
            self.upgrade_counts = {key: 0 for key in base_stats.keys()}
            self.exp = 0
            self.exp_to_next = 100
            if hasattr(store, 'SLOOMP_EXP_BASE'):
                self.exp_to_next = store.SLOOMP_EXP_BASE
            self.final_stats = self.calc_final_stats()
            self.current_hp = self.final_stats["hp"]

        def calc_final_stats(self):
            raw_stats = {}
            # Масштабирование силы пассивных бонусов уровнем хлюпа:
            # на низких уровнях вклад бонусов и магазина уменьшен, на высоких — выходит на 100%.
            level_factor = 1.0
            min_factor = getattr(store, "SLOOMP_LEVEL_POWER_MIN", 1.0)
            max_lvl = getattr(store, "SLOOMP_LEVEL_POWER_MAX_LEVEL", 1)
            if min_factor < 1.0 and max_lvl > 1:
                t = float(max(1, self.level) - 1) / float(max_lvl - 1)
                t = max(0.0, min(1.0, t))
                level_factor = min_factor + (1.0 - min_factor) * t

            for key in self.base_stats:
                base_val = self.base_stats.get(key, 0)
                bonus_val = self.bonus_stats.get(key, 0)
                raw_stats[key] = base_val + bonus_val * level_factor
            shop_levels = getattr(persistent, "shop_bonuses", None) or {}
            shop_values = getattr(store, "SHOP_STAT_VALUE_PER_LEVEL", None) or {}
            for key in raw_stats:
                lvl = shop_levels.get(key, 0)
                val = shop_values.get(key, 0)
                raw_stats[key] = raw_stats.get(key, 0) + lvl * val * level_factor
            multiplier = {
                "hp": 1.0, "defense": 1.0, "attack_speed": 1.0, "attack_power": 1.0,
                "crit_chance": 1.0, "crit_damage": 1.0, "vampirism": 1.0,
                "accuracy": 1.0, "evasion": 1.0, "regen": 1.0
            }
            for feat in self.features:
                for stat, mult in feat.get("multipliers", {}).items():
                    multiplier[stat] *= mult
            final = {}
            caps = getattr(store, "STAT_CAPS", {})
            for stat, val in raw_stats.items():
                final[stat] = val * multiplier.get(stat, 1.0)
                if stat in ["hp", "defense", "attack_power", "regen"]:
                    final[stat] = int(final[stat])
                if stat in caps:
                    final[stat] = min(final[stat], caps[stat])
            
            self.final_stats = final
            # Применяем эффекты реликвий к уже заполненным final_stats
            if hasattr(store, "apply_relic_effects") and hasattr(store, "player_relics"):
                store.apply_relic_effects(self, store.player_relics)
            return self.final_stats

        def level_up(self):
            self.level += 1
            B = store.SLOOMP_PER_LEVEL
            for key, delta in B.items():
                self.base_stats[key] = self.base_stats.get(key, 0) + delta
            self.final_stats = self.calc_final_stats()
            self.current_hp = min(self.current_hp, self.final_stats["hp"])
            self.exp_to_next = store.SLOOMP_EXP_BASE + store.SLOOMP_EXP_PER_LEVEL * self.level

        def add_exp(self, amount):
            self.exp += amount
            while self.exp >= self.exp_to_next:
                self.exp -= self.exp_to_next
                self.level_up()

        def to_dict(self):
            return {
                "name": self.name,
                "level": self.level,
                "base_stats": self.base_stats.copy(),
                "features": [f.copy() for f in self.features],
                "bonus_stats": self.bonus_stats.copy(),
                "upgrade_counts": self.upgrade_counts.copy(),
                "exp": self.exp,
                "exp_to_next": self.exp_to_next,
                "current_hp": self.current_hp,
            }

        @classmethod
        def from_dict(cls, d):
            obj = cls(
                d["name"],
                d["level"],
                d["base_stats"],
                d["features"],
            )
            obj.bonus_stats = d.get("bonus_stats", obj.bonus_stats)
            obj.upgrade_counts = d.get(
                "upgrade_counts",
                {key: 0 for key in d.get("base_stats", {}).keys()}
            )
            obj.exp = d.get("exp", 0)
            obj.exp_to_next = d.get("exp_to_next", store.SLOOMP_EXP_BASE)
            obj.final_stats = obj.calc_final_stats()
            obj.current_hp = min(d.get("current_hp", obj.final_stats["hp"]), obj.final_stats["hp"])
            return obj

        def __getstate__(self):
            return self.to_dict()

        def __setstate__(self, state):
            o = Sloomp.from_dict(state)
            self.name = o.name
            self.level = o.level
            self.base_stats = o.base_stats
            self.features = o.features
            self.bonus_stats = o.bonus_stats
            self.upgrade_counts = o.upgrade_counts
            self.exp = o.exp
            self.exp_to_next = o.exp_to_next
            self.final_stats = o.calc_final_stats()
            self.current_hp = min(o.current_hp, self.final_stats["hp"])

        def __eq__(self, other):
            if not isinstance(other, Sloomp):
                return False
            return self is other

        def __hash__(self):
            return id(self)

    class Enemy:
        def __init__(self, name, level, base_stats, image):
            self.name = name
            self.level = level
            self.base_stats = base_stats.copy()
            self.final_stats = self.base_stats.copy()
            self.current_hp = int(self.final_stats["hp"])
            self.image = image
