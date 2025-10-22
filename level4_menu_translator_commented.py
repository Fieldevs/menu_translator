# level4_menu_translator_commented.py
import re  # Import regex for phrase scanning and punctuation cleanup
import unicodedata  # Import for accent removal and lowercase normalization

# Single-word Portuguese → English glossary (includes some plural entries)
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
    "peixes": "fish",  # fish is uncountable in EN; keep "fish"
    "salada": "salad",
    "sopa": "soup",
    "massa": "pasta",
    "molho": "sauce",
    "tomate": "tomato",
    "batata": "potato",
    "batatas": "potatoes",  # irregular EN plural
    "arroz": "rice",
    "feijão": "beans",   # map singular PT to EN plural (common on menus)
    "feijões": "beans",
    "com": "with",
    "sem": "without",
    "e": "and",
    "de": "of",
}

# Auto-derive EN → PT single-word mapping
EN_PT = {v: k for k, v in PT_EN.items()}  # Reverse dictionary

# Phrase maps (bidirectional) with common plural variations
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
PHRASES_EN_PT = {v: k for k, v in PHRASES_PT_EN.items()}  # Reverse phrase dictionary

# Sets of uncountable nouns for simple plural logic
UNCOUNTABLE_EN = {"rice", "fish", "water", "coffee", "tea", "bread"}
UNCOUNTABLE_PT = {"arroz", "peixe", "água", "agua", "café", "cha", "chá", "pão"}

# Function to normalize strings (lowercase + remove accents)
def normalize(s):
    nfkd = unicodedata.normalize("NFKD", s.lower())  # Decompose accents
    return "".join(c for c in nfkd if not unicodedata.combining(c))  # Strip accents

# Build normalized lookups
NORM_PT_EN = {normalize(k): v for k, v in PT_EN.items()}  # Normalized PT→EN
NORM_EN_PT = {normalize(k): v for k, v in EN_PT.items()}  # Normalized EN→PT
NORM_PH_PT_EN = {normalize(k): v for k, v in PHRASES_PT_EN.items()}  # Normalized phrases PT→EN
NORM_PH_EN_PT = {normalize(k): v for k, v in PHRASES_EN_PT.items()}  # Normalized phrases EN→PT

# Function to mirror capitalization from source to destination
def match_casing(src, dst):
    if src.isupper():  # ALL CAPS → ALL CAPS
        return dst.upper()
    if src.istitle():  # Title Case → Title Case
        return " ".join(w.capitalize() for w in dst.split())
    return dst  # Keep as-is (lower/mixed)

# --- Basic plural helpers (Level 4: simple, not full morphology) ---

def is_plural_pt(word):
    """Return True if Portuguese word looks plural (ends with 's')."""
    b = normalize(word)
    return len(b) > 1 and b.endswith("s")

def depluralize_pt(word):
    """Naive PT singular form by stripping a trailing 's'."""
    b = normalize(word)
    if b.endswith("s") and len(b) > 1:
        return b[:-1]
    return b

def pluralize_en(word):
    """
    Naive EN plural:
    - add 'es' for words ending with s/x/z/ch/sh
    - 'y' after consonant → 'ies'
    - 'potato' → 'potatoes' (explicit special-case)
    - otherwise add 's'
    Uncountables remain unchanged.
    """
    if word in UNCOUNTABLE_EN:
        return word
    if re.search(r"(s|x|z|ch|sh)$", word):
        return word + "es"
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    if word.endswith("potato"):
        return "potatoes"
    return word + "s"

def depluralize_en(word):
    """Naive EN singular by removing common plural endings."""
    w = normalize(word)
    if re.search(r"(ches|shes|xes|zes|ses)$", w):
        return re.sub(r"(ches|shes|xes|zes|ses)$", "", w)
    if w.endswith("ies"):
        return w[:-3] + "y"
    if w.endswith("s") and len(w) > 1:
        return w[:-1]
    return w

# Function to replace phrases (longest-first) using normalized matching
def replace_phrases(text, mapping_norm):
    items = sorted(mapping_norm.items(), key=lambda kv: -len(kv[0]))  # Longest first
    pattern = re.compile(
        r"\b[\wÀ-ÖØ-öø-ÿ]+(?:\s+[\wÀ-ÖØ-öø-ÿ]+)+\b", flags=re.UNICODE
    )  # Multi-word spans
    out = text  # Work on a copy

    for norm_src, dst in items:
        # Whole-line match: replace entire item preserving casing
        if normalize(out) == norm_src:
            return match_casing(out, dst)

        # Otherwise, scan candidate spans and replace those that normalize equal
        def repl(m):
            span = m.group(0)
            if normalize(span) == norm_src:
                return match_casing(span, dst)
            return span

        out = pattern.sub(repl, out)
    return out

# --- Word-by-word passes with basic plural logic ---

def translate_tokens_pt_en(text):
    """
    Translate Portuguese tokens into English:
    - Try exact mapping; if not found and looks plural in PT,
      try singular lookup and then pluralize in EN.
    """
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
    """
    Translate English tokens into Portuguese:
    - Try exact mapping; if not found, attempt to singularize EN
      and map that to PT (keeps simple singular PT at Level 4).
    """
    words = [w for w in text.split() if w]
    result = []
    for w in words:
        base = normalize(w)
        tr = NORM_EN_PT.get(base)
        if tr is None:
            singular_base = depluralize_en(w)
            tr_sing = NORM_EN_PT.get(singular_base)
            if tr_sing:
                tr = tr_sing  # keep singular PT (morphology deferred to next levels)
        result.append(match_casing(w, tr if tr else w))
    return " ".join(result)

# Heuristic to detect translation direction for a given item
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

# Translate a user item with auto-detected direction
def translate_item_auto(item):
    direction = detect_direction(item)
    if direction == "pt_en":
        pre = replace_phrases(item, NORM_PH_PT_EN)  # Phrase pass PT→EN
        return translate_tokens_pt_en(pre)  # Word pass PT→EN
    else:
        pre = replace_phrases(item, NORM_PH_EN_PT)  # Phrase pass EN→PT
        return translate_tokens_en_pt(pre)  # Word pass EN→PT

# Remove trailing punctuation like commas or dots for cleaner input
def clean_tail_punct(s):
    return re.sub(r"[,\s\.]+$", "", s).strip()

# Main program
if __name__ == "__main__":
    print("=== Menu Translator - Level 4 (PT <-> EN, auto-detect + basic plurals) ===")  # Title
    print("Instructions:")  # Usage
    print("- Type ONE menu item per line (Portuguese or English).")
    print("- Accents are optional; trailing comma or dot is accepted.")
    print("- Press ENTER with no input to finish.\n")

    items = []  # Store user items

    while True:  # Input loop
        item = input("Item (ENTER to finish): ").strip()  # Read one line
        if not item:  # Stop on empty line
            break
        item = clean_tail_punct(item)  # Normalize trailing punctuation
        if item:
            items.append(item)  # Collect valid item

    if items:  # If we have items to translate
        out = [translate_item_auto(x) for x in items]  # Translate each
        sent = ". ".join(out).strip()  # Join with dots
        if not sent.endswith("."):  # Ensure final dot
            sent += "."
        print("\n--- Translation (auto PT <-> EN) ---")  # Output header
        print(sent)  # Final result
    else:
        print("\nNo items provided.")  # Empty input message
