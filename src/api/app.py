from fastapi import FastAPI
from src.api.products import router as products_router
from src.api.logs import router as logs_router
from src.api.reports import router as reports_router
from src.api.users import router as users_router

# # # # # # # # # # # # # # # # # # # # # # # # FASTAPI # # # # # # # # # # # # # # # # # # # # # # # #

app = FastAPI(
    title="Kalkulator kalorii API",
    description="Backendowa aplikacja REST API"
)

app.include_router(products_router)
app.include_router(logs_router)
app.include_router(reports_router)
app.include_router(users_router)

@app.get("/healthcheck", tags=["Check"])
def healthcheck():
    return {"status": "ok", "message": "Server is running smoothly"}