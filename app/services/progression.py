def gain_xp(exp, gain, level, ap):
    exp += gain
    hp = None
    while exp >= max(1, level) * 100:
        exp -= level * 100
        level += 1
        ap += 5
        hp = 80 + level * 20
    return {
        "exp": exp,
        "level": level,
        "ap": ap,
        "hp": hp
    }