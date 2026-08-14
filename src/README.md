KALKULATOR KALORII
Jest to aplikacja przeznaczona do liczenia aktualnego bilansu kalorycznegp, twoich zapotrzebowań, podziału na makroelementy etc.

Kod jest podzielony na określone moduły:
main.py - punkt wejścia do aplikacjo
src/cli.py - interfejs w konsoli, walidacja danych etc. Brak logiki.
src/math_core.py - cała logika aplikacji i wyliczeń, jak BMR, TDEE, porcje etc.
src/database - obsługa zapisu i odczytu danych przy użyciu SQLite.

Wymagania
Python 3.10+
SQLite3

Komenda do uruchomienia aplikacji z głównego katalogu: python main.py.

Funkcjonalność w wersji v0.2
- Wyliczanie zapotrzebowania kalorycznego na podstawie parametrów (waga, wzrost, wiek, cel).
- Dodawanie produktów do lokalnej bazy danych.
- Usuwanie już istniejących produktów z lokalnej bazy danych.
- Możliwość sprawdzenia bazy produktów.
- Wyszukiwanie produktów i logowanie spożytych porcji według daty.
- Generowanie dziennego raportu makroskładników.
- Defensywny kod (odporność na błędy typu ValueError, brakujące pliki i bezpieczne zapytania SQL).

Wersja v0.1
- Wyliczanie BMR i TDEE na podstawie parametrów (waga, wzrost, wiek, aktywność, cel).

- Wyszukiwanie produktów i logowanie porcji z przeliczaniem makro.

- Podstawowa walidacja wejścia (odporność na ValueError i niepoprawne typy danych).