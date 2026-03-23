from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Event, Sport
from app.schemas import EventResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[EventResponse])
def get_events(
    sport: str | None = None,
    date: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Event).options(
        joinedload(Event.sport),
        joinedload(Event.home_team),
        joinedload(Event.away_team),
        joinedload(Event.venue),
        joinedload(Event.competition),
        joinedload(Event.result),
    )

    if sport:
        query = query.join(Event.sport).filter(Sport.name.ilike(sport))

    if date:
        query = query.filter(Event.date_venue == date)

    events = query.order_by(Event.date_venue, Event.time_venue_utc).all()
    return events
