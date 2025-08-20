from sqlmodel import SQLModel, create_engine, Session

# Lokale SQLite-DB im Projektordner
DB_URL = "sqlite:///./lan_dashboard.db"

# Für SQLite nötig, damit mehrere Threads/Worker zugreifen können
engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """
    Erstellt alle Tabellen in der lokalen SQLite-DB, falls sie nicht existieren.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Liefert eine DB-Session für FastAPI-Endpunkte.
    """
    with Session(engine) as session:
        yield session
