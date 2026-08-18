from src.math_core import add_new_product, calculate_bmr, calculate_tdee, calculate_macronutrients, adjust_calories_for_goal, calculate_portion, calculate_sum, get_float_input
from src.database import save_product, save_logs, load_products, load_log_by_date, search_products, delete_log, delete_product
from datetime import date
def handle_add_product():
    nazwa = input("Podaj nazwe produktu ")
    bialko = get_float_input("Ile to ma bialka? ")
    tluszcze = get_float_input("Ile to ma tluszczy? ")
    wegle = get_float_input("Ile to ma weglowodanow? ")
    Nowy_produkt = add_new_product(name=nazwa, proteins=bialko, fat=tluszcze, carbohydrates=wegle)
    kalorie = Nowy_produkt["kalorie"]
    print(f"Twój nowo dodany produkt to: {nazwa}, ktory posiada {kalorie} kalorii")
    save_product(Nowy_produkt)

def handle_new_log():
    szukana_fraza = input("Wpisz wyszukiwana fraze ")
    znalezione = search_products(szukana_fraza)
    if not znalezione:
        print("Nie znaleziono żadnego produktu spełniającego kryteria")
    else:
        for idx, produkt in enumerate(znalezione):   
            print(f"{idx}. {produkt['nazwa']}")                 
        while True:
            try:
                product_idx = int(input("Wybierz produkt, który chcesz dodać "))
                if 0 <= product_idx < len(znalezione):
                    product_choice = znalezione[product_idx]
                    weight_choice = get_float_input("Jaka jest waga produktu? ")
                    porcja = calculate_portion(produkt=product_choice, weight=weight_choice)
                    porcja["data"] = str(date.today())
                    print(f"Twój dodany log to: {porcja['nazwa']}, która posiada: B: {porcja['bialko']}, T: {porcja['tluszcze']}, W: {porcja['weglowodany']}, ktore sie skladaja na {porcja['kalorie']} kalorii.")
                    save_logs(porcja)
                    break
                else:
                    print("Produkt nie znajduje się w bazie danych!")
            except ValueError:
                print("To musi być liczba całkowita!")      

def handle_check_day(goal):
    logi = load_log_by_date(str(date.today()))
    raport = calculate_sum(logi)
    print(f"Twoje dzisiejsze makro to: {raport['kalorie']} kalorii, {raport['bialko']} B, {raport['tluszcze']} T, {raport['weglowodany']} W.")
    roznica = goal - raport["kalorie"]
    if roznica > 0:
        print(f"Zostało ci na dzisiaj {roznica} kalorii!")
    else:
        roznica = abs(roznica)
        print(f"Przekroczyłeś dzisiejsze zapotrzebowanie kaloryczne o {roznica} kalorii!")              

def handle_delete_log():
    logi = load_log_by_date(str(date.today()))
    if not logi:
        print("Dziennik jest pusty!")
    else:
        for idx, log in enumerate(logi):
            print(f"{idx}, {log['nazwa']}, {log['kalorie']}")
        try:
            product_dlt = int(input("Wybierz produkt, który chcesz usunąć "))
            if 0 <= product_dlt < len(logi):
                chosen_id = logi[product_dlt]["id"]
                delete_log(chosen_id)
            else:
                print("Podany log nie istnieje!")
        
        except ValueError:
            print("To musi być liczba całkowita!")       

def handle_delete_product():
    products = load_products()
    if not products:
        print("Baza produktów jest pusta!")
    else:
        for idx, product in enumerate(products):
            print(f"{idx}, {product['nazwa']}, {product['kalorie']}")
        try:
            product_dlt = int(input("Wybierz produkt, który chcesz usunąć "))
            if 0 <= product_dlt < len(products):
                chosen_id = products[product_dlt]["id"]
                delete_product(chosen_id)
            else:
                print("Produkt nie znajduje się w bazie danych!")
        except ValueError:
            print("To musi być liczba całkowita!")       

def handle_check_products():
    products = load_products()
    if not products:
        print("Baza produktów jest pusta!")
    else:
        for idx, product in enumerate(products):
            print(f"{idx}, {product['nazwa']}, {product['kalorie']}")
def main():
#PODSTAWOWE DANE UZYTKOWNIKA
    weight = get_float_input("Podaj swoją wagę: ")
    height = get_float_input("Podaj swój wzrost: ")
    age = int(input("Podaj swój wiek: "))
    gender = input("Jakiej jesteś płci? ('m' lub 'k') ").lower().strip()
    while gender not in {"m", "k"}:
        print("Wpisz 'm' lub 'k'!")
        gender = input("Jakiej jesteś płci? ('m' lub 'k') ").lower().strip() 

    bmr = calculate_bmr(weight=weight, height=height, age=age, gender=gender)
    print(f"Twoje BMR wynosi {bmr} kalorii")
#OBLICZANIE ZAPOTRZEBOWANIA TDEE
    pal_map = {
        1: 1.2,
        2: 1.375,
        3: 1.55,
        4: 1.725,
        5: 2.0
    }
    while True:
        try:
            pal = int(input("Jaka jest twoja aktywność? (od 1 do 5):"))
            if pal in pal_map:
                pal_factor = pal_map[pal]
                break
            print("Wybierz liczbę od 1 do 5")
        except ValueError:
            print("To musi być liczba całkowita!")
    tdee = calculate_tdee(bmr=bmr, activity_level=pal_factor)
#SPRAWDZANIE CELU UZYTKOWNIKA
    goal_check = input("Jaki jest twój cel? (redukcja, utrzymanie, nadwyzka) ").lower().strip()
    goal_check_dict = {
        "r": "redukcja",
        "redukcja": "redukcja",
        "u": "utrzymanie",
        "utrzymanie": "utrzymanie",
        "n": "nadwyzka",
        "nadwyzka": "nadwyzka",
        "nadwyżka": "nadwyzka"
    }
    while goal_check not in goal_check_dict:
        print("Błąd! Niepoprawny wybór!")
        goal_check = input("Jaki jest twój cel? (redukcja, utrzymanie, nadwyzka) ").lower().strip()
    goal = adjust_calories_for_goal(goal=goal_check_dict[goal_check], tdee=tdee)
#SPRAWDZANIE MAKROELEMENTOW
    protein, fat, carbs = calculate_macronutrients(weight=weight, tdee=goal)
    print(f"Twoje docelowe kalorie wynoszą {goal}, co przekłada się na: {protein}g białka, {fat}g tłuszczów i {carbs}g węglowodanów.")
    is_running = True
    while is_running:
        print("\n--- BAZA PRODUKTÓW I POSIŁKI ---")
        print("1. Dodaj nowy produkt do kartoteki")
        print("2. Zaloguj zjedzony posiłek")
        print("3. Sprawdź bilans dnia")
        print("4. Usuń wybrany log")
        print("5. Usuń wybrany produkt")
        print("6. Sprawdź bazę produktów")
        print("0. Powrót do menu głównego")
        
        choice = input("Wybierz opcję: ")
        while choice not in {"0", "1", "2", "3", "4", "5", "6"}:
            print("Opcja nie istnieje!")
            choice = input("Wybierz opcję: ")

        if choice == "1":
            handle_add_product()
        elif choice == "2":
            handle_new_log()
        elif choice == "3":
            handle_check_day(goal)
        elif choice == "4":
            handle_delete_log()
        elif choice == "5":             
            handle_delete_product()
        elif choice == "6":
            handle_check_products()
        elif choice == "0":
            is_running = False
