# level2_menu_translator_commented.py
import re  # Import regex for phrase detection
import unicodedata  # Import for accent removal and normalization

# Portuguese → English single-word glossary
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

# Phrase-level PT → EN mappings
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

# Function to normalize strings (lowercase + remove accents)
def normalize(s):
    nfkd = unicodedata.normalize("NFKD", s.lower())  # Decompose accented characters
    return "".join(c for c in nfkd if not unicodedata.combining(c))  # Strip accents

# Create normalized lookup dictionaries
NORM_PT_EN = {normalize(k): v for k, v in PT_EN.items()}  # Normalized single words
NORM_PHRASES = {normalize(k): v for k, v in PHRASES_PT_EN.items()}  # Normalized phrases

# Function to preserve capitalization style from source to translation
def match_casing(src, dst):
    if src.isupper():  # Full uppercase
        return dst.upper()
    if src.istitle():  # Title case
        return " ".join(w.capitalize() for w in dst.split())
    return dst  # Keep as lowercase or mixed case

# Function to replace full phrases before word-by-word translation
def replace_phrases(text):
    items = sorted(NORM_PHRASES.items(), key=lambda kv: -len(kv[0]))  # Longest-first
    pattern = re.compile(r"\b[\wÀ-ÖØ-öø-ÿ]+(?:\s+[\wÀ-ÖØ-öø-ÿ]+)+\b", flags=re.UNICODE)  # Multi-word spans
    out = text  # Start with original text

    for norm_src, dst in items:
        if normalize(out) == norm_src:  # If entire line matches a phrase
            return match_casing(out, dst)

        # Replace phrase segments that match normalized keys
        def repl(m):
            span = m.group(0)
            if normalize(span) == norm_src:
                return match_casing(span, dst)
            return span

        out = pattern.sub(repl, out)
    return out

# Function to translate a single word
def translate_word(w):
    base = normalize(w)  # Normalize input
    return NORM_PT_EN.get(base, w)  # Return translation or original

# Function to translate an entire menu item (supports phrases and casing)
def translate_item(pt_phrase):
    pre = replace_phrases(pt_phrase)  # Phrase pre-pass
    words = [w for w in pre.split() if w]  # Split into words
    translated = [match_casing(w, translate_word(w)) for w in words]  # Translate each word
    return " ".join(translated)  # Join translated words

# Main program execution
if __name__ == "__main__":
    print("=== Menu Translator - Level 2 (PT -> EN) ===")  # Title
    print("Instructions:")  # User instructions
    print("- Type ONE menu item per line (Portuguese).")
    print("- Accents and trailing dots are optional.")
    print("- Press ENTER with no input to finish.\n")
    print("Example sequence:")  # Example input
    print("  prato principal")
    print("  agua com gas")
    print("  batata frita")
    print("  arroz e feijao")
    print("  [empty ENTER to finish]\n")

    items = []  # Initialize list for user items

    while True:  # Input loop
        item = input("Item (ENTER to finish): ").strip()  # Get item
        if not item:  # If blank input, stop
            break
        if item.endswith("."):  # Remove trailing dot if any
            item = item[:-1].strip()
        if item:
            items.append(item)  # Add to list

    if items:  # If user entered items
        out = [translate_item(x) for x in items]  # Translate each
        print("\n--- Translation (PT -> EN) ---")  # Output header
        print(". ".join(out) + ".")  # Print translated list separated by dots
    else:
        print("\nNo items provided.")  # Message if empty input
