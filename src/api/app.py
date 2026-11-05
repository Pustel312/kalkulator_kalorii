from fastapi import FastAPI

from src.api.logs import router as logs_router
from src.api.products import router as products_router
from src.api.reports import router as reports_router
from src.api.users import router as users_router

app = FastAPI(
    title="Kalkulator kalorii API", description="REST API do zarządzania produktami, posiłkami, dziennikiem żywieniowym i raportami."
)

app.include_router(products_router)
app.include_router(logs_router)
app.include_router(reports_router)
app.include_router(users_router)


@app.get("/healthcheck", tags=["Check"])
def healthcheck():
    return {"status": "ok", "message": "Server is running smoothly"}
