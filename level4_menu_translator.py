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
    "peixes": "fish",
    "salada": "salad",
    "sopa": "soup",
    "massa": "pasta",
    "molho": "sauce",
    "tomate": "tomato",
    "batata": "potato",
    "batatas": "potatoes",
    "arroz": "rice",
    "feijão": "beans",
    "feijões": "beans",
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
    "águas com gás": "sparkling water",
    "aguas com gas": "sparkling water",
    "água sem gás": "still water",
    "agua sem gas": "still water",
    "batata frita": "french fries",
    "batatas fritas": "french fries",
    "molho de tomate": "tomato sauce",
    "arroz e feijão": "rice and beans",
    "arroz e feijao": "rice and beans",
}

PHRASES_EN_PT = {v: k for k, v in PHRASES_PT_EN.items()}

UNCOUNTABLE_EN = {"rice", "fish", "water", "coffee", "tea", "bread"}
UNCOUNTABLE_PT = {"arroz", "peixe", "água", "agua", "café", "cha", "chá", "pão"}

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

def is_plural_pt(word):
    b = normalize(word)
    return len(b) > 1 and b.endswith("s")

def depluralize_pt(word):
    b = normalize(word)
    if b.endswith("s") and len(b) > 1:
        return b[:-1]
    return b

def pluralize_en(word):
    w = word
    if w in UNCOUNTABLE_EN:
        return w
    if re.search(r"(s|x|z|ch|sh)$", w):
        return w + "es"
    if re.search(r"[^aeiou]y$", w):
        return w[:-1] + "ies"
    if w.endswith("potato"):
        return "potatoes"
    return w + "s"

def depluralize_en(word):
    w = normalize(word)
    if re.search(r"(ches|shes|xes|zes|ses)$", w):
        return re.sub(r"(ches|shes|xes|zes|ses)$", "", w)
    if w.endswith("ies"):
        return w[:-3] + "y"
    if w.endswith("s") and len(w) > 1:
        return w[:-1]
    return w

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

def translate_tokens_pt_en(text):
    words = [w for w in text.split() if w]
    result = []
    for w in words:
        base = normalize(w)
        tr = NORM_PT_EN.get(base)
        if tr is None and is_plural_pt(w):
            singular_base = depluralize_pt(w)
            tr_sing = NORM_PT_EN.get(singular_base)
            if tr_sing:
                tr = pluralize_en(tr_sing)
        result.append(match_casing(w, tr if tr else w))
    return " ".join(result)

def translate_tokens_en_pt(text):
    words = [w for w in text.split() if w]
    result = []
    for w in words:
        base = normalize(w)
        tr = NORM_EN_PT.get(base)
        if tr is None:
            singular_base = depluralize_en(w)
            tr_sing = NORM_EN_PT.get(singular_base)
            if tr_sing:
                tr = tr_sing  # keep simple singular PT at this level
        result.append(match_casing(w, tr if tr else w))
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
    return "en_pt" if score_en > score_pt else "pt_en"

def translate_item_auto(item):
    direction = detect_direction(item)
    if direction == "pt_en":
        pre = replace_phrases(item, NORM_PH_PT_EN)
        return translate_tokens_pt_en(pre)
    else:
        pre = replace_phrases(item, NORM_PH_EN_PT)
        return translate_tokens_en_pt(pre)

def clean_tail_punct(s):
    return re.sub(r"[,\s\.]+$", "", s).strip()

if __name__ == "__main__":
    print("=== Menu Translator - Level 4 (PT <-> EN, auto-detect + basic plurals) ===")
    print("Instructions:")
    print("- Type ONE menu item per line (Portuguese or English).")
    print("- Accents are optional; trailing comma or dot is accepted.")
    print("- Press empty ENTER to finish.\n")

    items = []
    while True:
        item = input("Item (ENTER to finish): ").strip()
        if not item:
            break
        item = clean_tail_punct(item)
        if item:
            items.append(item)

    if items:
        out = [translate_item_auto(x) for x in items]
        sent = ". ".join(out).strip()
        if not sent.endswith("."):
            sent += "."
        print("\n--- Translation (auto PT <-> EN) ---")
        print(sent)
    else:
        print("\nNo items provided.")
