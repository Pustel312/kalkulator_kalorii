from fastapi import FastAPI, HTTPException
from src.schemas import ProductCreate, ProductResponse, LogCreate, LogResponse
from src.math_core import add_new_product, calculate_portion
from src.database import save_product, load_products, search_products, delete_product, load_products_by_id, save_logs, load_log_by_date, load_log_by_id, delete_log
from datetime import date

app = FastAPI(
    title="Kalkulator kalorii API",
    description="Backendowa aplikacja REST API"
)

@app.get("/healthcheck", tags=["Check"])
def healthcheck():
    return {"status": "ok", "message": "Server is running smoothly"}

@app.post("/products", tags=["Products"], response_model=ProductResponse)
# 1. WEJŚCIE: Pydantic odpytuje JSON-a z sieci, sprawdza warunki (min_length, ge=0)
#    i tworzy obiekt `product` (instancję ProductCreate).
def create_product(product: ProductCreate):

    # 2. PRZELICZENIE: Wyciągamy surowe pola z obiektu Pydantic 
    #    i przekazujemy do czystej funkcji logicznej. 
    #    Wynikiem jest słownik `calculated` zawierający już wyliczone kalorie.
    calculated = add_new_product(
        name=product.name,
        proteins=product.protein,
        fat=product.fat,
        carbohydrates=product.carbs
    )

    # 3. ZAPIS: Słownik trafia do bazy SQLite. 
    #    Baza zapisuje rekord i generuje unikalny klucz główny.
    #    `save_product` zwraca ten klucz dzięki `cursor.lastrowid`.
    product_id = save_product(calculated)

    # 4. WYJŚCIE: Składamy słownik dopasowany nazwami pól pod `ProductResponse`.
    #    FastAPI weryfikuje go ze schematem wyjściowym i oddaje klientowi JSON.
    return {
        "id": product_id,
        "name": calculated["nazwa"],
        "protein": calculated["bialko"],
        "fat": calculated["tluszcze"],
        "carbs": calculated["weglowodany"],
        "calories": calculated["kalorie"]
    }

@app.get("/products", tags=["Products"], response_model=list[ProductResponse])
def get_products():
    raw_products = load_products()

    formatted_products = []
    for product in raw_products:
        formatted_products.append({
            "id": product["id"],
            "name": product["nazwa"],
            "protein": product["bialko"],
            "fat": product["tluszcze"],
            "carbs": product["weglowodany"],
            "calories": product["kalorie"]
        })

    return formatted_products

@app.get("/products/search", tags=["Products"], response_model=list[ProductResponse])
def search_products_endpoint(phrase: str):
    raw_products = search_products(phrase)
    formatted_products = []
    for product in raw_products:
        formatted_products.append({
            "id": product["id"],
            "name": product["nazwa"],
            "protein": product["bialko"],
            "fat": product["tluszcze"],
            "carbs": product["weglowodany"],
            "calories": product["kalorie"]
        })
    return formatted_products

@app.delete("/products/{product_id}", tags=["Products"])
def delete_products_endpoint(product_id: int):
    deletedP = delete_product(product_id)
    if not deletedP:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "ok", "message": "Product is deleted"}

@app.post("/logs", tags=["Logs"], response_model=LogResponse)
def create_log(dane: LogCreate):
    product = load_products_by_id(dane.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    porcja = calculate_portion(product, dane.weight)
    porcja["data"] = str(date.today())
    log_id = save_logs(porcja)
    return {
    "id": log_id,
    "name": porcja["nazwa"],
    "protein": porcja["bialko"],
    "fat": porcja["tluszcze"],
    "carbs": porcja["weglowodany"],
    "calories": porcja["kalorie"],
    "date": porcja["data"]
}

@app.get("/logs", response_model=list[LogResponse], tags=["Logs"])
def get_logs_by_date(target_date: str):
    logs = load_log_by_date(target_date)
    formatted_logs = []
    for log  in logs:
        formatted_logs.append({
            "id": log["id"],
            "name": log["nazwa"],
            "protein": log["bialko"],
            "fat": log["tluszcze"],
            "carbs": log["weglowodany"],
            "calories": log["kalorie"],
            "date": log["data"]
        })
    return formatted_logs

@app.get("/logs/{entry_id}", response_model=LogResponse, tags=["Logs"])
def get_log_by_id(entry_id: int):
    log = load_log_by_id(entry_id)
    if not log:
         raise HTTPException(status_code=404, detail="Log not found")
    return {
            "id": log["id"],
            "name": log["nazwa"],
            "protein": log["bialko"],
            "fat": log["tluszcze"],
            "carbs": log["weglowodany"],
            "calories": log["kalorie"],
            "date": log["data"]
        }

@app.delete("/logs/{entry_id}", tags=["Logs"])
def delete_logs_endpoint(entry_id: int):
    deletedL = delete_log(entry_id)
    if not deletedL:
            raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "ok", "message": "Log is deleted"}
