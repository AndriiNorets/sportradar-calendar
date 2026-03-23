from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    events = relationship("Event", back_populates="sport")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    official_name = Column(String(200))
    abbreviation = Column(String(10))
    country_code = Column(String(10))

    home_events = relationship(
        "Event", foreign_keys="Event._home_team_id", back_populates="home_team"
    )
    away_events = relationship(
        "Event", foreign_keys="Event._away_team_id", back_populates="away_team"
    )


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    capacity = Column(Integer)

    events = relationship("Event", back_populates="venue")


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)

    events = relationship("Event", back_populates="competition")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    _sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    _home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    _away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    _venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    _competition_id = Column(String(100), ForeignKey("competitions.id"), nullable=True)
    date_venue = Column(Date, nullable=False)
    time_venue_utc = Column(Time, nullable=True)
    status = Column(String(20), default="scheduled")
    season = Column(Integer)
    stage_name = Column(String(100))
    description = Column(Text)

    sport = relationship("Sport", back_populates="events")
    home_team = relationship(
        "Team", foreign_keys=[_home_team_id], back_populates="home_events"
    )
    away_team = relationship(
        "Team", foreign_keys=[_away_team_id], back_populates="away_events"
    )
    venue = relationship("Venue", back_populates="events")
    competition = relationship("Competition", back_populates="events")
    result = relationship("Result", back_populates="event", uselist=False)


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    _event_id = Column(Integer, ForeignKey("events.id"), unique=True, nullable=False)
    home_goals = Column(Integer, default=0)
    away_goals = Column(Integer, default=0)
    winner = Column(String(100))

    event = relationship("Event", back_populates="result")
