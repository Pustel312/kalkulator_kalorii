from src.cli import main
from src.database import create_tables

create_tables()

if __name__ == "__main__":
    main()