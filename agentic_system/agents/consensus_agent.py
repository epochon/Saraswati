def decide(dialogue):
    scores = {}

    for msg in dialogue:
        cat = msg["payload"]["category"]
        conf = msg["payload"]["confidence"]
        scores[cat] = scores.get(cat, 0) + conf

    return max(scores, key=scores.get)
