from random import randint

def calculate_damage(strength, luck, agility):
    return max(1, int(strength / 2 + randint(1, max(1, int(luck / 8))) - agility / 6))

def resolve_battle(att_stats: dict, def_stats: dict):
    won = False
    battle_logs = []
    ahp = att_stats["hp"]
    dhp = def_stats["hp"]
    while ahp > 0 and dhp > 0:
        damage = calculate_damage(att_stats["strength"], att_stats["luck"], def_stats["agility"])
        dhp -= damage
        battle_logs.append({
            "is_attacker": True,
            "dmg": damage
        })
        if dhp <= 0:
            won = True
        else:
            damage = calculate_damage(def_stats["strength"], def_stats["luck"], att_stats["agility"])
            ahp -= damage
            battle_logs.append({
                "is_attacker": False,
                "dmg": damage
            })
    return {
        "logs": battle_logs,
        "winner": won,
        "att_final_hp": max(0, ahp),
        "def_final_hp": max(0, dhp)
    }