import re
import unicodedata

PT_EN = {
    "cardápio": "menu",
    "menu": "menu",
    "entrada": "starter",
    "entradas": "starters",
    "principal": "main",
    "sobremesa": "dessert",
    "bebida": "drink",
    "bebidas": "drinks",
    "água": "water",
    "suco": "juice",
    "refrigerante": "soda",
    "cerveja": "beer",
    "vinho": "wine",
    "café": "coffee",
    "chá": "tea",
    "pão": "bread",
    "manteiga": "butter",
    "queijo": "cheese",
    "frango": "chicken",
    "carne": "beef",
    "porco": "pork",
    "peixe": "fish",
    "salada": "salad",
    "sopa": "soup",
    "massa": "pasta",
    "molho": "sauce",
    "tomate": "tomato",
    "batata": "potato",
    "arroz": "rice",
    "feijão": "beans",
    "com": "with",
    "sem": "without",
    "e": "and",
    "de": "of",
}

EN_PT = {v: k for k, v in PT_EN.items()}

PHRASES_PT_EN = {
    "prato principal": "main course",
    "água com gás": "sparkling water",
    "agua com gas": "sparkling water",
    "água sem gás": "still water",
    "agua sem gas": "still water",
    "batata frita": "french fries",
    "molho de tomate": "tomato sauce",
    "arroz e feijão": "rice and beans",
    "arroz e feijao": "rice and beans",
}

PHRASES_EN_PT = {v: k for k, v in PHRASES_PT_EN.items()}

def normalize(s):
    nfkd = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

NORM_PT_EN = {normalize(k): v for k, v in PT_EN.items()}
NORM_EN_PT = {normalize(k): v for k, v in EN_PT.items()}
NORM_PH_PT_EN = {normalize(k): v for k, v in PHRASES_PT_EN.items()}
NORM_PH_EN_PT = {normalize(k): v for k, v in PHRASES_EN_PT.items()}

def match_casing(src, dst):
    if src.isupper():
        return dst.upper()
    if src.istitle():
        return " ".join(w.capitalize() for w in dst.split())
    return dst

def replace_phrases(text, mapping_norm):
    items = sorted(mapping_norm.items(), key=lambda kv: -len(kv[0]))
    pattern = re.compile(r"\b[\wÀ-ÖØ-öø-ÿ]+(?:\s+[\wÀ-ÖØ-öø-ÿ]+)+\b", flags=re.UNICODE)
    out = text
    for norm_src, dst in items:
        if normalize(out) == norm_src:
            return match_casing(out, dst)
        def repl(m):
            span = m.group(0)
            if normalize(span) == norm_src:
                return match_casing(span, dst)
            return span
        out = pattern.sub(repl, out)
    return out

def translate_tokens(text, lex_norm, reverse=False):
    words = [w for w in text.split() if w]
    result = []
    for w in words:
        base = normalize(w)
        tr = lex_norm.get(base, None)
        result.append(match_casing(w, tr if tr is not None else w))
    return " ".join(result)

def detect_direction(text):
    tokens = [w for w in text.split() if w]
    if not tokens:
        return "pt_en"
    score_pt = 0
    score_en = 0
    norm_line = normalize(text)
    if norm_line in NORM_PH_PT_EN:
        score_pt += 3
    if norm_line in NORM_PH_EN_PT:
        score_en += 3
    for w in tokens:
        b = normalize(w)
        if b in NORM_PT_EN:
            score_pt += 1
        if b in NORM_EN_PT:
            score_en += 1
    if score_en > score_pt:
        return "en_pt"
    return "pt_en"

def translate_item_auto(item):
    direction = detect_direction(item)
    if direction == "pt_en":
        pre = replace_phrases(item, NORM_PH_PT_EN)
        return translate_tokens(pre, NORM_PT_EN, reverse=False)
    else:
        pre = replace_phrases(item, NORM_PH_EN_PT)
        return translate_tokens(pre, NORM_EN_PT, reverse=True)

if __name__ == "__main__":
    print("=== Menu Translator - Level 3 (PT <-> EN, auto-detect) ===")
    print("Instructions:")
    print("- Type ONE menu item per line (Portuguese or English).")
    print("- Accents and trailing dots are optional.")
    print("- Press empty ENTER to finish.\n")
    print("Example sequence:")
    print("  prato principal")
    print("  french fries")
    print("  agua com gas")
    print("  rice and beans")
    print("  [empty ENTER to finish]\n")

    items = []
    while True:
        item = input("Item (ENTER to finish): ").strip()
        if not item:
            break
        if item.endswith("."):
            item = item[:-1].strip()
        if item:
            items.append(item)

    if items:
        out = [translate_item_auto(x) for x in items]
        print("\n--- Translation (auto PT <-> EN) ---")
        print(". ".join(out) + ".")
    else:
        print("\nNo items provided.")
