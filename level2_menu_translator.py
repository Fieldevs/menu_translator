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

def normalize(s):
    nfkd = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

NORM_PT_EN = {normalize(k): v for k, v in PT_EN.items()}
NORM_PHRASES = {normalize(k): v for k, v in PHRASES_PT_EN.items()}

def match_casing(src, dst):
    if src.isupper():
        return dst.upper()
    if src.istitle():
        return " ".join(w.capitalize() for w in dst.split())
    return dst

def replace_phrases(text):
    items = sorted(NORM_PHRASES.items(), key=lambda kv: -len(kv[0]))
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

def translate_word(w):
    base = normalize(w)
    return NORM_PT_EN.get(base, w)

def translate_item(pt_phrase):
    pre = replace_phrases(pt_phrase)
    words = [w for w in pre.split() if w]
    translated = [match_casing(w, translate_word(w)) for w in words]
    return " ".join(translated)

if __name__ == "__main__":
    print("=== Menu Translator - Level 2 (PT -> EN) ===")
    print("Instructions:")
    print("- Type ONE menu item per line (Portuguese).")
    print("- Accents and trailing dots are optional.")
    print("- Press empty ENTER to finish.\n")
    print("Example sequence:")
    print("  prato principal")
    print("  agua com gas")
    print("  batata frita")
    print("  arroz e feijao")
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
        out = [translate_item(x) for x in items]
        print("\n--- Translation (PT -> EN) ---")
        print(". ".join(out) + ".")
    else:
        print("\nNo items provided.")
