import os
from sqlalchemy import create_engine

from declarations import Base

if __name__ == "__main__":
    engine = create_engine(os.getenv("DATABASE_URL"))
    Base.metadata.create_all(engine)
    print("✅ Таблицы успешно созданы в PostgreSQL")
