# level3_menu_translator_commented.py
import re  # Import regex to scan and replace multi-word phrases
import unicodedata  # Import for accent removal and lowercase normalization

# Portuguese → English single-word glossary (menu domain)
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

# Auto-derived English → Portuguese dictionary for single words
EN_PT = {v: k for k, v in PT_EN.items()}  # Reverse mapping for EN->PT

# Phrase-level maps in both directions (pre-pass before word translation)
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
PHRASES_EN_PT = {v: k for k, v in PHRASES_PT_EN.items()}  # Reverse phrase map

# Function to normalize text (lowercase + remove accents)
def normalize(s):
    nfkd = unicodedata.normalize("NFKD", s.lower())  # Decompose accented characters
    return "".join(c for c in nfkd if not unicodedata.combining(c))  # Strip accent marks

# Build normalized dictionaries for robust lookups regardless of accents/case
NORM_PT_EN = {normalize(k): v for k, v in PT_EN.items()}  # Normalized PT single words
NORM_EN_PT = {normalize(k): v for k, v in EN_PT.items()}  # Normalized EN single words
NORM_PH_PT_EN = {normalize(k): v for k, v in PHRASES_PT_EN.items()}  # Normalized PT phrases
NORM_PH_EN_PT = {normalize(k): v for k, v in PHRASES_EN_PT.items()}  # Normalized EN phrases

# Function to mirror basic casing from source token to destination token
def match_casing(src, dst):
    if src.isupper():  # Preserve FULL UPPER
        return dst.upper()
    if src.istitle():  # Preserve Title Case (capitalize each word)
        return " ".join(w.capitalize() for w in dst.split())
    return dst  # Keep original lower/mixed case

# Function to replace known phrases (longest-first) using normalized matching
def replace_phrases(text, mapping_norm):
    items = sorted(mapping_norm.items(), key=lambda kv: -len(kv[0]))  # Longest phrase first
    pattern = re.compile(
        r"\b[\wÀ-ÖØ-öø-ÿ]+(?:\s+[\wÀ-ÖØ-öø-ÿ]+)+\b", flags=re.UNICODE
    )  # Multi-word spans
    out = text  # Work on a copy of the input

    for norm_src, dst in items:
        # If the entire line matches a phrase once normalized, replace all of it
        if normalize(out) == norm_src:
            return match_casing(out, dst)

        # Otherwise, scan candidate spans and replace the ones that match when normalized
        def repl(m):
            span = m.group(0)  # Candidate phrase fragment
            if normalize(span) == norm_src:  # Normalized equality means it's our phrase
                return match_casing(span, dst)  # Replace while preserving casing
            return span  # Keep original if not our phrase

        out = pattern.sub(repl, out)  # Apply the replacement across the line
    return out  # Return the phrase-processed text

# Function to translate words in a line after the phrase pass
def translate_tokens(text, lex_norm, reverse=False):
    words = [w for w in text.split() if w]  # Split line into whitespace-separated tokens
    result = []  # Accumulate translated tokens
    for w in words:
        base = normalize(w)  # Normalize token
        tr = lex_norm.get(base, None)  # Lookup translation
        result.append(match_casing(w, tr if tr is not None else w))  # Preserve casing
    return " ".join(result)  # Join tokens with spaces

# Function to detect which direction to translate (PT->EN or EN->PT)
def detect_direction(text):
    tokens = [w for w in text.split() if w]  # Tokenize by spaces
    if not tokens:
        return "pt_en"  # Default when empty
    score_pt = 0  # Score for PT->EN direction
    score_en = 0  # Score for EN->PT direction

    norm_line = normalize(text)  # Normalized entire line
    if norm_line in NORM_PH_PT_EN:  # Whole-line PT phrase
        score_pt += 3
    if norm_line in NORM_PH_EN_PT:  # Whole-line EN phrase
        score_en += 3

    # Count word hits on each dictionary
    for w in tokens:
        b = normalize(w)
        if b in NORM_PT_EN:
            score_pt += 1
        if b in NORM_EN_PT:
            score_en += 1

    # Choose the higher score; default to PT->EN on ties
    if score_en > score_pt:
        return "en_pt"
    return "pt_en"

# Function to translate a single user-entered item with auto-detected direction
def translate_item_auto(item):
    direction = detect_direction(item)  # Decide PT->EN or EN->PT for this line

    if direction == "pt_en":  # Portuguese to English
        pre = replace_phrases(item, NORM_PH_PT_EN)  # Phrase pre-pass (PT->EN)
        return translate_tokens(pre, NORM_PT_EN, reverse=False)  # Word-level pass
    else:  # English to Portuguese
        pre = replace_phrases(item, NORM_PH_EN_PT)  # Phrase pre-pass (EN->PT)
        return translate_tokens(pre, NORM_EN_PT, reverse=True)  # Word-level pass

# Main program loop
if __name__ == "__main__":
    print("=== Menu Translator - Level 3 (PT <-> EN, auto-detect) ===")  # Title
    print("Instructions:")  # Usage instructions
    print("- Type ONE menu item per line (Portuguese or English).")
    print("- Accents and trailing dots are optional.")
    print("- Press ENTER with no input to finish.\n")
    print("Example sequence:")  # Example inputs
    print("  prato principal")
    print("  french fries")
    print("  agua com gas")
    print("  rice and beans")
    print("  [empty ENTER to finish]\n")

    items = []  # Collected user items

    while True:  # Input loop
        item = input("Item (ENTER to finish): ").strip()  # Read an item
        if not item:  # Empty line ends input
            break
        if item.endswith("."):  # Accept optional trailing dot
            item = item[:-1].strip()
        if item:
            items.append(item)  # Store valid item

    if items:  # If we have items to translate
        out = [translate_item_auto(x) for x in items]  # Translate each item
        print("\n--- Translation (auto PT <-> EN) ---")  # Output header
        print(". ".join(out) + ".")  # Print final dotted line
    else:
        print("\nNo items provided.")  # Message for empty input
