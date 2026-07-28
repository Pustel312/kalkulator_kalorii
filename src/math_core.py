baza_produktow = []
def food_menu():
    is_running = True
    while is_running:
        print("\n--- BAZA PRODUKTÓW I POSIŁKI ---")
        print("1. Dodaj nowy produkt do kartoteki")
        print("2. Zaloguj zjedzony posiłek")
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
        elif choice == 2:
            if not baza_produktow:
                print("Baza jest pusta!")
            else:
                print("\n--- DOSTĘPNE PRODUKTY ---")
                for idx, produkt in enumerate(baza_produktow):
                    print(f"{idx + 1}. {produkt['nazwa']}")
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
