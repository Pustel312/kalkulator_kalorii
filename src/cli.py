from math_core import food_menu, add_new_product, calculate_bmr, calculate_tdee, calculate_macronutrients, adjust_calories_for_goal

def main():
#PODSTAWOWE DANE UZYTKOWNIKA
    weight = float(input("Podaj swoją wagę: "))
    height = float(input("Podaj swój wzrost: "))
    age = float(input("Podaj swój wiek: "))
    gender = input("Jakiej jesteś płci? ('m' lub 'k') ") 

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
    goal_check = input("Jaki jest twój cel? (redukcja, utrzymanie, nadwyzka) ")
    goal = adjust_calories_for_goal(goal=goal_check, tdee=tdee)
#SPRAWDZANIE MAKROELEMENTOW
    protein, fat, carbs = calculate_macronutrients(weight=weight, tdee=goal)
    print(f"Twoje docelowe kalorie wynoszą {goal}, co przekłada się na: {protein}g białka, {fat}g tłuszczów i {carbs}g węglowodanów.")


if __name__ == "__main__":
    main()
    food_menu()
    