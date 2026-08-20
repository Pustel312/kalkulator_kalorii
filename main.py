from src.cli import main
from src.database import create_tables
import uvicorn
from src.api import app


create_tables()


if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
