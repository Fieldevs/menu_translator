
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

def normalize(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

NORM_PT_EN = {normalize(k): v for k, v in PT_EN.items()}

def translate_word(w: str) -> str:
    base = normalize(w)
    return NORM_PT_EN.get(base, w)

def translate_item(pt_phrase: str) -> str:
    words = [w for w in pt_phrase.split() if w]
    translated = [translate_word(w) for w in words]
    return " ".join(translated)

if __name__ == "__main__":
    print("=== Menu Translator - Level 1 (PT -> EN) ===")
    print("Instructions:")
    print("- Type ONE item per line (only the dish/ingredient name).")
    print("- Accents are optional. You may add a trailing dot if you want.")
    print("- Press an empty ENTER to finish.\n")
    print("Example sequence:")
    print("  agua")
    print("  carne")
    print("  salada")
    print("  arroz")
    print("  feijao")
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
