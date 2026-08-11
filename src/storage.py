import json
def load_products():
    try:
        with open("baza.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open("baza.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_products(baza_produktow):
    with open("baza.json", "w", encoding="utf-8") as f:
        json.dump(baza_produktow, f, indent=4)

def load_note():
    try:
        with open("dziennik.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open("dziennik.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_note(dziennik_posilkow):
    with open("dziennik.json", "w", encoding="utf-8") as f:
        json.dump(dziennik_posilkow, f, indent=4)