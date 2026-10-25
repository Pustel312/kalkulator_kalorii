# Kalkulator Kalorii

Backendowa aplikacja REST API do zarządzania produktami, logowania spożycia
oraz generowania spersonalizowanych raportów żywieniowych.

Projekt wykorzystuje FastAPI, SQLAlchemy, PostgreSQL oraz JWT authentication.

## Technologie

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- pytest
- Docker


### Uruchomienie projektu — Docker

Wymagania: Docker Desktop z uruchomionym Docker Engine.

1. Sklonuj repozytorium i przejdź do katalogu projektu.
2. Utwórz plik `.env.docker` z wymaganymi zmiennymi środowiskowymi (konfiguracja PostgreSQL, testowej bazy danych i JWT)(w pliku `.env.example` rozpisane są przykładowe dane potrzebne do wprowadzenia do `env.docker`).
3. Uruchom środowisko:
```bash
docker compose --env-file .env.docker up -d --build
```

Docker Compose automatycznie:
- Uruchamia PostgreSQL i oczekuje na jego gotowość.
- Wykonuje migracje Alembica.
- Uruchamia aplikację FastAPI.

Dokumentacja API: http://localhost:8000/docs

Uruchomienie testów:
```bash
docker compose --env-file .env.docker run --rm tests
```

Zatrzymanie środowiska:
```bash
docker compose --env-file .env.docker down
```

Dane PostgreSQL są przechowywane w Docker volume i pozostają dostępne po ponownym uruchomieniu środowiska.

## Struktura projektu

src/
├── api/
│   ├── app.py
│   ├── products.py
│   ├── logs.py
│   ├── reports.py
│   └── users.py
├── database/
│   ├── session.py
│   ├── products.py
│   ├── logs.py
│   ├── reports.py
│   └── users.py
├── auth.py
├── security.py
├── models.py
├── schemas.py
├── enums.py
└── math_core.py

tests/
├── api/
│   ├── test_healthcheck.py
│   ├── test_products.py
│   ├── test_logs.py
│   ├── test_reports.py
│   ├── test_users.py
│   └── test_ownership.py
├── common.py
├── helpers.py
├── conftest.py
└── test_math_core.py

## Funkcjonalność w wersji v0.4

### Użytkownicy i autoryzacja

- Rejestracja użytkowników.
- Logowanie użytkowników.
- JWT access tokens.
- Refresh tokens.
- Endpoint `/users/me`.
- Ochrona endpointów przy użyciu aktualnego użytkownika.
- Izolacja danych pomiędzy użytkownikami.

### Profil i personalizacja

- Profil użytkownika zawierający:
  - płeć,
  - wzrost,
  - wagę,
  - datę urodzenia,
  - poziom aktywności,
  - cel masy ciała.
- Obliczanie BMR.
- Obliczanie TDEE.
- Wyliczanie docelowej kaloryczności.
- Wyliczanie zakresów białka, tłuszczu i węglowodanów.
- Spersonalizowany raport dzienny.

### Produkty

- CRUD produktów.
- Soft delete.
- Produkty prywatne i globalne.
- Ownership produktów.
- Produkty złożone z komponentów.
- Automatyczne obliczanie kalorii i makroskładników.

### Logi

- Dodawanie spożytych porcji.
- Pobieranie logów według daty i identyfikatora.
- Usuwanie logów.
- Ownership logów.

### Raporty

- Dzienne spożycie kalorii i makroskładników.
- Pozostałe/przekroczone kalorie względem celu.
- Najczęściej spożywane produkty.
- Średnia wielkość porcji.

### Architektura

- Modularny podział API.
- Modularny podział warstwy database.
- Rozdzielone testy według domen.
- PostgreSQL + SQLAlchemy ORM.
- Migracje Alembic.
- 70 testów automatycznych.