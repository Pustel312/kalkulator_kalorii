import json
from datetime import date
def load_products():
    try:
        with open("baza.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
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
    except FileNotFoundError:
        with open("dziennik.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_note(dziennik_posilkow):
    with open("dziennik.json", "w", encoding="utf-8") as f:
        json.dump(dziennik_posilkow, f, indent=4)

def food_menu():

    baza_produktow = load_products()
    dziennik_posilkow = load_note()
    is_running = True
    while is_running:
        print("\n--- BAZA PRODUKTÓW I POSIŁKI ---")
        print("1. Dodaj nowy produkt do kartoteki")
        print("2. Zaloguj zjedzony posiłek")
        print("3. Sprawdź bilans dnia")
        print("0. Powrót do menu głównego")
        
        choice = int(input("Wybierz opcję: "))
        
        if choice == 1:
            nazwa = input("Podaj nazwe produktu ")
            bialko = float(input("Ile to ma bialka? "))
            tluszcze = float(input("Ile to ma tluszczy? "))
            wegle = float(input("Ile to ma weglowodanow? "))
            Nowy_produkt = add_new_product(name=nazwa, proteins=bialko, fat=tluszcze, carbohydrates=wegle)
            kalorie = Nowy_produkt["kalorie"]
            print(f"Twój nowo dodany produkt to: {nazwa}, ktory posiada {kalorie} kalorii")
            baza_produktow.append(Nowy_produkt)
            save_products(baza_produktow)
        elif choice == 2:
            if not baza_produktow:
                print("Baza jest pusta!")
            else:
                szukana_fraza = input("Wpisz wyszukiwana fraze ")
                znalezione = search_products(baza_produktow, szukana_fraza)
                if not znalezione:
                    print("Nie znaleziono żadnego produktu spełniającego kryteria")
                else:
                    for idx, produkt in enumerate(znalezione):   
                        print(f"{idx}. {produkt['nazwa']}")                 
                    product_idx = int(input("Wybierz produkt, który chcesz dodać "))
                    if product_idx in range(0, len(znalezione)):
                        product_choice = znalezione[product_idx]
                        weight_choice = int(input("Jaka jest waga produktu? "))
                        porcja = calculate_portion(produkt=product_choice, weight=weight_choice)
                        porcja["data"] = str(date.today())
                        print(f"Twój dodany log to: {porcja['nazwa']}, która posiada: B: {porcja['bialko']}, T: {porcja['tluszcze']}, W: {porcja['weglowodany']}, ktore sie skladaja na {porcja['kalorie']} kalorii.")
                        dziennik_posilkow.append(porcja)
                        save_note(dziennik_posilkow)
                    
        elif choice == 3:
            suma_kalorii = 0
            suma_bialko = 0
            suma_tluszcze = 0
            suma_weglowodany = 0
            dzisiaj = str(date.today())
            for posilek in dziennik_posilkow:
                if posilek["data"] == dzisiaj:
                    suma_kalorii += posilek['kalorie']
                    suma_bialko += posilek['bialko']
                    suma_tluszcze += posilek['tluszcze']
                    suma_weglowodany += posilek['weglowodany']
            print(f"Łączna liczba kalorii to: {suma_kalorii}, BTW to: {suma_bialko}, {suma_tluszcze}, {suma_weglowodany}.")

        elif choice == 0:
            is_running = False

def add_new_product(name: str, proteins: float, fat: float, carbohydrates: float) -> dict:
    calories = (proteins * 4) + (fat * 9) + (carbohydrates * 4)
    produkt = {
        "nazwa": name,
        "bialko": proteins,
        "tluszcze": fat,
        "weglowodany": carbohydrates,
        "kalorie": calories
    }
    return produkt


def calculate_bmr(weight: float, height: float, age: int, gender: str)->float:
    if gender.lower() == "m":
        bmr =  (10*weight)+(6.25*height)-(5*age)+5
    elif gender.lower() == "k":
        bmr =  (10*weight)+(6.25*height)-(5*age)-161
    else:
        raise ValueError("Niepoprawna płeć. Oczekiwano 'm' lub 'k'.") #Zwraca tekst w przypadku niepoprawnych danych wejsciowych
    return bmr

def calculate_tdee(bmr: float, activity_level: float)->float:
    tdee = bmr*activity_level
    return tdee

def calculate_macronutrients(weight: float, tdee: float)-> tuple[float, float, float]:
    proteins = 2*weight
    fat = 1.2*weight
    carbohydrates = (tdee-((proteins*4)+(fat*9)))/4

    return proteins, fat, carbohydrates

def adjust_calories_for_goal(goal: str, tdee: float)->float:
    if goal == "redukcja":
        return tdee - 300.0
    elif goal == "nadwyzka":
       return tdee + 400.0
    return tdee

def calculate_portion(produkt: dict, weight: float)->dict:
    conversion_factor = weight/100
    porcja = {
            "nazwa": produkt["nazwa"],
            "waga": weight,
            "bialko": produkt["bialko"]*conversion_factor,
            "tluszcze": produkt["tluszcze"]*conversion_factor,
            "weglowodany": produkt["weglowodany"]*conversion_factor,
            "kalorie": produkt["kalorie"]*conversion_factor
        }
    return porcja

def search_products(baza_produktow: list[dict], fraza: str) -> list[dict]:
    wyniki = []
    for produkt in baza_produktow:
        if fraza.lower() in produkt["nazwa"].lower():
            wyniki.append(produkt)
    return wyniki