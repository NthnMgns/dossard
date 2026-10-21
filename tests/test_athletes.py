from datetime import date
from pathlib import Path


def test_create_athlete_returns_201_with_category(client):
    birth_date = date(date.today().year - 30, 3, 2)

    response = client.post(
        "/athletes",
        json={
            "first_name": "Inès",
            "last_name": "Morel",
            "birth_date": birth_date.isoformat(),
            "sex": "F",
            "license_number": "DOS-000042",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["category"] == "SENIOR"
    assert body["club"] is None


def test_create_athlete_rejects_duplicate_license(client, make_athlete):
    athlete = make_athlete()

    response = client.post(
        "/athletes",
        json={
            "first_name": "Hugo",
            "last_name": "Lemaire",
            "birth_date": "1995-05-20",
            "sex": "M",
            "license_number": athlete["license_number"],
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_list_athletes_filters_by_club(client, make_athlete):
    make_athlete("Durand", club="AC Rivebelle")
    make_athlete("Petit", club="Stade Nordval")

    response = client.get("/athletes", params={"club": "AC Rivebelle"})

    assert response.status_code == 200
    assert [a["last_name"] for a in response.json()] == ["Durand"]


CSV_EXEMPLE = Path(__file__).parent / "data" / "licencies_exemple.csv"


def _import(client, content: bytes):
    return client.post("/athletes/import", files={"file": ("licencies.csv", content, "text/csv")})


def test_import_athletes_reports_created_duplicates_and_errors(client):
    response = _import(client, CSV_EXEMPLE.read_bytes())

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 17
    assert body["already_present"] == 1
    assert [e["line"] for e in body["errors"]] == [15, 16]
    athletes = client.get("/athletes").json()
    assert len(athletes) == 17
    margaux = next(a for a in athletes if a["license_number"] == "DOS-900101")
    assert margaux["birth_date"] == "1998-03-14"
    assert margaux["category"] == "SENIOR"
    lebrun = next(a for a in athletes if a["license_number"] == "DOS-900109")
    assert lebrun["club"] is None


def test_import_athletes_twice_creates_nothing(client):
    _import(client, CSV_EXEMPLE.read_bytes())

    body = _import(client, CSV_EXEMPLE.read_bytes()).json()

    assert body["created"] == 0
    assert body["already_present"] == 18


def test_import_athletes_rejects_missing_columns(client):
    response = _import(client, b"nom;prenom\nDupont;Jean\n")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"
