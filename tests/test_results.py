import csv
import io

import pytest


@pytest.fixture
def ranked_event(client, make_competition, make_event, make_athlete, make_registration):
    """Fabrique : une épreuve close, un athlète confirmé et un résultat par performance."""

    def _make(unit: str, performances: list[float]) -> dict:
        competition = make_competition(status="open")
        event = make_event(competition["id"], unit=unit)
        registrations = [
            make_registration(event["id"], make_athlete(f"Athlete{i}")["id"])
            for i in range(len(performances))
        ]
        client.patch(f"/competitions/{competition['id']}", json={"status": "closed"})
        for registration, performance in zip(registrations, performances, strict=True):
            response = client.put(
                f"/registrations/{registration['id']}/result", json={"performance": performance}
            )
            assert response.status_code == 200
        return event

    return _make


def test_ranking_orders_times_ascending(client, ranked_event):
    event = ranked_event("time_s", [12.4, 11.9, 12.1])

    response = client.get(f"/events/{event['id']}/ranking")

    assert response.status_code == 200
    ranking = response.json()["data"]
    assert [(e["rank"], e["performance"]) for e in ranking] == [(1, 11.9), (2, 12.1), (3, 12.4)]


def test_ranking_orders_distances_descending(client, ranked_event):
    event = ranked_event("distance_m", [6.2, 6.85, 5.9])

    response = client.get(f"/events/{event['id']}/ranking")

    assert response.status_code == 200
    ranking = response.json()["data"]
    assert [(e["rank"], e["performance"]) for e in ranking] == [(1, 6.85), (2, 6.2), (3, 5.9)]


def test_export_csv_keeps_columns_when_club_contains_comma(
    client, make_competition, make_event, make_athlete, make_registration
):
    competition = make_competition(status="open")
    event = make_event(competition["id"])
    athlete = make_athlete(club="AC Paris, section Sud")
    registration = make_registration(event["id"], athlete["id"])
    client.patch(f"/competitions/{competition['id']}", json={"status": "closed"})
    client.put(f"/registrations/{registration['id']}/result", json={"performance": 11.9})

    response = client.get(f"/competitions/{competition['id']}/results.csv")

    assert response.status_code == 200
    rows = list(csv.reader(io.StringIO(response.text)))
    record = dict(zip(rows[0], rows[1], strict=True))
    assert record["club"] == "AC Paris, section Sud"
    assert record["license_number"] == athlete["license_number"]
    assert record["performance"] == "11.9"
