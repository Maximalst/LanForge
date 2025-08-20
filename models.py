from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Attendee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    paid: bool = False
    bringing: str = ""   # z.B. Switch, Mehrfachsteckdose, Snacks
    notes: str = ""

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    location: str = ""
    start_time: datetime

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item: str            # Pizza Margherita 2x, Mate-Kiste etc.
    who: str = ""        # Besteller
    done: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Tournament(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str            # „1v1 Aim“, „Rocket League 2v2“ …
    game: str
    start_time: datetime
    rules: str = ""      # kurze Regeln / Modus
