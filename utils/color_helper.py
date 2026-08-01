NEUTRALS = {"black", "white", "grey", "gray", "beige", "navy", "brown", "tan", "cream"}

EARTH_TONES = {"brown", "olive", "khaki", "beige", "tan", "rust", "mustard"}

def is_safe_pair(color_a, color_b):
    """Very simple rule-based check: neutrals go with everything,
    earth tones go with earth tones, otherwise assume acceptable
    unless both are strong clashing brights."""
    a, b = color_a.lower(), color_b.lower()
    if a in NEUTRALS or b in NEUTRALS:
        return True
    if a in EARTH_TONES and b in EARTH_TONES:
        return True
    clashing_pairs = [
        {"red", "green"}, {"orange", "purple"}, {"pink", "orange"}
    ]
    if {a, b} in clashing_pairs:
        return False
    return True