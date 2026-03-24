# Entity Relationship Diagram

## Sports Event Calendar — Database Schema

```mermaid
erDiagram
    SPORTS ||--o{ EVENTS : "has"
    TEAMS ||--o{ EVENTS : "home_team"
    TEAMS ||--o{ EVENTS : "away_team"
    VENUES ||--o{ EVENTS : "hosted_at"
    COMPETITIONS ||--o{ EVENTS : "part_of"
    EVENTS ||--o| RESULTS : "has"

    SPORTS {
        int     id    PK
        varchar name  "NOT NULL, UNIQUE"
    }

    TEAMS {
        int     id            PK
        varchar name          "NOT NULL"
        varchar official_name
        varchar abbreviation
        varchar country_code
    }

    VENUES {
        int     id       PK
        varchar name     "NOT NULL"
        varchar city
        varchar country
        int     capacity
    }

    COMPETITIONS {
        varchar id   PK
        varchar name "NOT NULL"
    }

    EVENTS {
        int     id              PK
        int     _sport_id       FK  "NOT NULL → sports.id"
        int     _home_team_id   FK  "→ teams.id"
        int     _away_team_id   FK  "→ teams.id"
        int     _venue_id       FK  "→ venues.id"
        varchar _competition_id FK  "→ competitions.id"
        date    date_venue          "NOT NULL"
        time    time_venue_utc
        varchar status              "default: scheduled"
        int     season
        varchar stage_name
        text    description
    }

    RESULTS {
        int     id          PK
        int     _event_id   FK  "NOT NULL, UNIQUE → events.id"
        int     home_goals      "default: 0"
        int     away_goals      "default: 0"
        varchar winner
    }
```

## Design Decisions

- **3NF normalization** - no repeating groups or transitive dependencies; each entity is in its own table.
- **Teams dual FK** - `events` holds two separate FKs (`_home_team_id`, `_away_team_id`) referencing `teams`, avoiding a junction table for a fixed two-team match structure.
- **Competition ID as varchar** - matches external API identifiers (e.g. `sr:competition:17`) rather than auto-increment integers.
- **Results as 1-to-1** - a separate `results` table with a `UNIQUE` FK keeps the events table clean and allows events without results (scheduled/upcoming).
- **FK naming convention** - underscore-prefixed FK columns (`_sport_id`) distinguish FK fields from regular data fields at a glance.
