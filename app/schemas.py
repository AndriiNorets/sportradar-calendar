from datetime import date, time

from pydantic import BaseModel


class SportResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: int
    name: str
    official_name: str | None = None
    abbreviation: str | None = None
    country_code: str | None = None

    model_config = {"from_attributes": True}


class VenueResponse(BaseModel):
    id: int
    name: str
    city: str | None = None
    country: str | None = None
    capacity: int | None = None

    model_config = {"from_attributes": True}


class CompetitionResponse(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class ResultResponse(BaseModel):
    id: int
    home_goals: int
    away_goals: int
    winner: str | None = None

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    id: int
    date_venue: date
    time_venue_utc: time | None = None
    status: str | None = None
    season: int | None = None
    stage_name: str | None = None
    description: str | None = None
    sport: SportResponse
    home_team: TeamResponse | None = None
    away_team: TeamResponse | None = None
    venue: VenueResponse | None = None
    competition: CompetitionResponse | None = None
    result: ResultResponse | None = None

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    date_venue: date
    time_venue_utc: time | None = None
    sport_name: str
    home_team_name: str
    away_team_name: str
    venue_name: str | None = None
    competition_id: str | None = None
    competition_name: str | None = None
    status: str = "scheduled"
    season: int | None = None
    stage_name: str | None = None
    description: str | None = None
