from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Competition, Event, Sport, Team, Venue
from app.schemas import EventCreate, EventResponse

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


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = (
        db.query(Event)
        .options(
            joinedload(Event.sport),
            joinedload(Event.home_team),
            joinedload(Event.away_team),
            joinedload(Event.venue),
            joinedload(Event.competition),
            joinedload(Event.result),
        )
        .filter(Event.id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    sport = db.query(Sport).filter(Sport.name == payload.sport_name).first()
    if not sport:
        sport = Sport(name=payload.sport_name)
        db.add(sport)
        db.flush()

    home_team = db.query(Team).filter(Team.name == payload.home_team_name).first()
    if not home_team:
        home_team = Team(name=payload.home_team_name)
        db.add(home_team)
        db.flush()

    away_team = db.query(Team).filter(Team.name == payload.away_team_name).first()
    if not away_team:
        away_team = Team(name=payload.away_team_name)
        db.add(away_team)
        db.flush()

    venue = None
    if payload.venue_name:
        venue = db.query(Venue).filter(Venue.name == payload.venue_name).first()
        if not venue:
            venue = Venue(name=payload.venue_name)
            db.add(venue)
            db.flush()

    competition = None
    if payload.competition_id:
        competition = (
            db.query(Competition)
            .filter(Competition.id == payload.competition_id)
            .first()
        )
        if not competition:
            competition = Competition(
                id=payload.competition_id, name=payload.competition_name
            )
            db.add(competition)
            db.flush()

    event = Event(
        _sport_id=sport.id,
        _home_team_id=home_team.id,
        _away_team_id=away_team.id,
        _venue_id=venue.id if venue else None,
        _competition_id=competition.id if competition else None,
        date_venue=payload.date_venue,
        time_venue_utc=payload.time_venue_utc,
        status=payload.status,
        season=payload.season,
        stage_name=payload.stage_name,
        description=payload.description,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return get_event(event.id, db)
