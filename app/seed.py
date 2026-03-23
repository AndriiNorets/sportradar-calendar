import json
import os
import sys
from datetime import date, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Competition, Event, Result, Sport, Team


def get_or_create_sport(db, name: str) -> Sport:
    sport = db.query(Sport).filter(Sport.name == name).first()
    if not sport:
        sport = Sport(name=name)
        db.add(sport)
        db.flush()
    return sport


def get_or_create_team(db, team_data: dict | None) -> Team | None:
    if team_data is None:
        return None
    team = db.query(Team).filter(Team.name == team_data["name"]).first()
    if not team:
        team = Team(
            name=team_data["name"],
            official_name=team_data.get("officialName"),
            abbreviation=team_data.get("abbreviation"),
            country_code=team_data.get("teamCountryCode"),
        )
        db.add(team)
        db.flush()
    return team


def get_or_create_competition(
    db, comp_id: str | None, comp_name: str | None
) -> Competition | None:
    if not comp_id:
        return None
    comp = db.query(Competition).filter(Competition.id == comp_id).first()
    if not comp:
        comp = Competition(id=comp_id, name=comp_name)
        db.add(comp)
        db.flush()
    return comp


def seed_from_json() -> None:
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "data.json"
    )

    if not os.path.exists(json_path):
        print("data/data.json not found — skipping JSON seed.")
        return

    db = SessionLocal()
    try:
        existing = db.query(Event).count()
        if existing > 0:
            print(f"Database already has {existing} events. Skipping JSON seed.")
            return

        with open(json_path) as f:
            data = json.load(f)

        football = get_or_create_sport(db, "Football")

        for item in data["data"]:
            home_team = get_or_create_team(db, item.get("homeTeam"))
            away_team = get_or_create_team(db, item.get("awayTeam"))
            competition = get_or_create_competition(
                db,
                item.get("originCompetitionId"),
                item.get("originCompetitionName"),
            )

            event_date = date.fromisoformat(item["dateVenue"])
            event_time = None
            if item.get("timeVenueUTC"):
                h, m, s = item["timeVenueUTC"].split(":")
                event_time = time(int(h), int(m), int(s))

            event = Event(
                _sport_id=football.id,
                _home_team_id=home_team.id if home_team else None,
                _away_team_id=away_team.id if away_team else None,
                _venue_id=None,
                _competition_id=competition.id if competition else None,
                date_venue=event_date,
                time_venue_utc=event_time,
                status=item.get("status", "scheduled"),
                season=item.get("season"),
                stage_name=item.get("stage", {}).get("name")
                if item.get("stage")
                else None,
            )
            db.add(event)
            db.flush()

            result_data = item.get("result")
            if result_data:
                db.add(
                    Result(
                        _event_id=event.id,
                        home_goals=result_data.get("homeGoals", 0),
                        away_goals=result_data.get("awayGoals", 0),
                        winner=result_data.get("winner"),
                    )
                )

        db.commit()
        print(f"Seeded {len(data['data'])} events from data/data.json.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding from JSON: {e}")
        raise
    finally:
        db.close()


def seed_sample_events() -> None:
    db = SessionLocal()
    try:
        football = get_or_create_sport(db, "Football")
        salzburg = get_or_create_team(db, {"name": "Salzburg"})
        sturm = get_or_create_team(db, {"name": "Sturm"})

        if (
            not db.query(Event)
            .filter_by(_home_team_id=salzburg.id, _away_team_id=sturm.id)
            .first()
        ):
            db.add(
                Event(
                    _sport_id=football.id,
                    _home_team_id=salzburg.id,
                    _away_team_id=sturm.id,
                    date_venue=date(2019, 7, 18),
                    time_venue_utc=time(18, 30),
                    status="played",
                    description="Salzburg vs. Sturm",
                )
            )

        ice_hockey = get_or_create_sport(db, "Ice Hockey")
        kac = get_or_create_team(db, {"name": "KAC"})
        capitals = get_or_create_team(db, {"name": "Capitals"})

        if (
            not db.query(Event)
            .filter_by(_home_team_id=kac.id, _away_team_id=capitals.id)
            .first()
        ):
            db.add(
                Event(
                    _sport_id=ice_hockey.id,
                    _home_team_id=kac.id,
                    _away_team_id=capitals.id,
                    date_venue=date(2019, 10, 23),
                    time_venue_utc=time(9, 45),
                    status="played",
                    description="KAC vs. Capitals",
                )
            )

        db.commit()
        print("Seeded 2 sample events.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding sample events: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding database...")
    seed_from_json()
    seed_sample_events()
    print("Done!")
