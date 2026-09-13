# Kalkulator Kalorii

Backendowa aplikacja REST API przeznaczona do zarządzania produktami, logowania spożytych porcji oraz generowania raportów dotyczących kalorii i makroskładników.

Projekt powstał początkowo jako aplikacja konsolowa, a następnie został rozwinięty do architektury opartej o FastAPI, SQLAlchemy i PostgreSQL.

## Technologie

- Python 3.10+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- pytest

## Struktura projektu

- `src/api.py` - endpointy REST API.
- `src/math_core.py` - logika obliczeniowa aplikacji, m.in. liczenie kalorii i porcji.
- `src/database.py` - obsługa operacji bazodanowych i zapytań.
- `src/models.py` - modele ORM SQLAlchemy.
- `src/schemas.py` - modele Pydantic wykorzystywane przez API.
- `tests/` - testy logiki aplikacji i testy API.
- `alembic/` - migracje bazy danych.

## Funkcjonalność w wersji v0.3

- REST API oparte o FastAPI.
- PostgreSQL jako główna baza danych.
- Obsługa bazy poprzez SQLAlchemy ORM.
- Migracje schematu przy użyciu Alembic.
- Dodawanie, pobieranie, wyszukiwanie i aktualizowanie produktów.
- Soft delete produktów.
- Walidacja danych wejściowych przy użyciu Pydantic.
- Constrainty na poziomie bazy danych.
- Unikalność nazw aktywnych produktów przy użyciu partial unique index.
- Logowanie spożytych porcji produktów.
- Pobieranie logów według identyfikatora oraz daty.
- Usuwanie logów.
- Automatyczne przeliczanie kalorii i makroskładników dla porcji.
- Generowanie dziennego raportu kalorii i makroskładników.
- Raport najczęściej logowanych produktów.
- Raport średniej wagi porcji dla produktów.
- Indeksowanie dat logów.
- Testy API przy użyciu `pytest` i `TestClient`.
- Osobna baza PostgreSQL przeznaczona do testów.

## Wersja v0.2

- Wyliczanie zapotrzebowania kalorycznego na podstawie parametrów użytkownika.
- Dodawanie i usuwanie produktów w lokalnej bazie SQLite.
- Przeglądanie i wyszukiwanie produktów.
- Logowanie spożytych porcji według daty.
- Generowanie dziennego raportu makroskładników.
- Podstawowa obsługa błędów i walidacja danych.

## Wersja v0.1

- Wyliczanie BMR i TDEE na podstawie:
  - wagi,
  - wzrostu,
  - wieku,
  - aktywności,
  - celu.
- Wyszukiwanie produktów i logowanie porcji z przeliczaniem makroskładników.
- Podstawowa walidacja danych wejściowych.

## Uruchomienie

Projekt wymaga skonfigurowanej bazy PostgreSQL.

W pliku `.env` należy ustawić:

    DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/database_name

Następnie uruchomić API:

    uvicorn src.api:app --reload

Dokumentacja API dostępna jest pod:

    /docs

## Testy

Testy korzystają z osobnej bazy PostgreSQL.

W pliku `.env` należy ustawić:

    TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/test_database_name

Uruchomienie testów:

    pytest