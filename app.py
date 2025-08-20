import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware import Middleware
from starlette.datastructures import Secret
from starlette.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates

from db import get_session, init_db
from models import Attendee, Event, Order, Tournament
from sqlmodel import Session, select

APP_SECRET = os.getenv("APP_SECRET", "change-me-in-prod")

middleware = [
    Middleware(GZipMiddleware, minimum_size=512),
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
    Middleware(SessionMiddleware, secret_key=APP_SECRET),
]

app = FastAPI(title="LANForge Dashboard", version="1.0.0", middleware=middleware)

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Sicherheitsrelevante HTTP-Header (einfach gehalten)
@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=()"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; font-src 'self' data:;"
    )
    return resp

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    attendees = session.exec(select(Attendee).order_by(Attendee.name)).all()
    events    = session.exec(select(Event).order_by(Event.start_time)).all()
    orders    = session.exec(select(Order).order_by(Order.created_at.desc())).all()
    tourns    = session.exec(select(Tournament).order_by(Tournament.start_time)).all()

    paid_count = sum(1 for a in attendees if a.paid)
    context = {
        "request": request,
        "attendees": attendees,
        "events": events,
        "orders": orders,
        "tournaments": tourns,
        "stats": {
            "attendees": len(attendees),
            "paid": paid_count,
            "unpaid": max(0, len(attendees) - paid_count),
            "orders": len(orders),
            "events": len(events),
            "tournaments": len(tourns),
        }
    }
    return templates.TemplateResponse("index.html", context)

# ---------- Create handlers ----------
@app.post("/attendees/create")
def create_attendee(
    name: str = Form(...),
    paid: Optional[bool] = Form(False),
    bringing: Optional[str] = Form(""),
    notes: Optional[str] = Form(""),
    session: Session = Depends(get_session),
):
    attendee = Attendee(name=name.strip(), paid=bool(paid), bringing=bringing.strip(), notes=notes.strip())
    session.add(attendee)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/attendees/toggle-paid/{attendee_id}")
def toggle_paid(attendee_id: int, session: Session = Depends(get_session)):
    obj = session.get(Attendee, attendee_id)
    if obj:
        obj.paid = not obj.paid
        session.add(obj)
        session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/events/create")
def create_event(
    title: str = Form(...),
    location: str = Form(""),
    start_time: str = Form(...),  # ISO: 2025-08-22T18:00
    session: Session = Depends(get_session),
):
    dt = datetime.fromisoformat(start_time)
    ev = Event(title=title.strip(), location=location.strip(), start_time=dt)
    session.add(ev)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/orders/create")
def create_order(
    item: str = Form(...),
    who: str = Form(""),
    session: Session = Depends(get_session),
):
    order = Order(item=item.strip(), who=who.strip())
    session.add(order)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/orders/mark/{order_id}")
def mark_order(order_id: int, session: Session = Depends(get_session)):
    obj = session.get(Order, order_id)
    if obj:
        obj.done = True
        session.add(obj)
        session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/tournaments/create")
def create_tournament(
    name: str = Form(...),
    game: str = Form(...),
    start_time: str = Form(...),
    rules: str = Form(""),
    session: Session = Depends(get_session),
):
    dt = datetime.fromisoformat(start_time)
    t = Tournament(name=name.strip(), game=game.strip(), start_time=dt, rules=rules.strip())
    session.add(t)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "ok"
