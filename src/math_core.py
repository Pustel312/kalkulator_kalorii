from datetime import date

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

def calculate_sum(dziennik_posilkow: list[dict])-> dict:
    suma_kalorii = 0
    suma_bialko = 0
    suma_tluszcze = 0
    suma_weglowodany = 0
    for posilek in dziennik_posilkow:
        suma_kalorii += posilek['kalorie']
        suma_bialko += posilek['bialko']
        suma_tluszcze += posilek['tluszcze']
        suma_weglowodany += posilek['weglowodany']
    podsumowanie = {
        "kalorie": suma_kalorii,
        "bialko": suma_bialko,
        "tluszcze": suma_tluszcze,
        "weglowodany": suma_weglowodany
    }
    return podsumowanie
    
def search_products(baza_produktow: list[dict], fraza: str) -> list[dict]:
    wyniki = []
    for produkt in baza_produktow:
        if fraza.lower() in produkt["nazwa"].lower():
            wyniki.append(produkt)
    return wyniki

def get_float_input(komunikat):
    while True:
        try:
            wartosc = float(input(komunikat))
            if wartosc > 0:
                return wartosc
            else:
                print("Błąd! Wartość musi być większa od zera!")
        except ValueError:
            print("Błąd! Wprowadzono niepoprawny tekst. Podaj odpowiednią cyfrę!")
