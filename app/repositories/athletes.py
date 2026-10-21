from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import date

from pydantic import ValidationError

from app.categories import age_category
from app.errors import ConflictError
from app.schemas import AthleteCreate, AthleteImportError, AthleteImportReport, AthleteOut

IMPORT_COLUMNS = {
    "nom",
    "prenom",
    "date_naissance",
    "sexe",
    "club",
    "licence",
    "certificat_valide_jusqu",
}


def _to_athlete(row: sqlite3.Row) -> AthleteOut:
    birth_date = date.fromisoformat(row["birth_date"])
    certificate = row["medical_certificate_valid_until"]
    return AthleteOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        birth_date=birth_date,
        sex=row["sex"],
        club=row["club"],
        license_number=row["license_number"],
        medical_certificate_valid_until=date.fromisoformat(certificate) if certificate else None,
        category=age_category(birth_date),
    )


def list_athletes(conn: sqlite3.Connection, club: str | None = None) -> list[AthleteOut]:
    sql = "SELECT * FROM athletes"
    params: tuple[str, ...] = ()
    if club is not None:
        sql += " WHERE club = ?"
        params = (club,)
    sql += " ORDER BY last_name, first_name, id"
    return [_to_athlete(row) for row in conn.execute(sql, params)]


def create_athlete(conn: sqlite3.Connection, data: AthleteCreate) -> AthleteOut:
    existing = conn.execute(
        "SELECT id FROM athletes WHERE license_number = ?", (data.license_number,)
    ).fetchone()
    if existing is not None:
        raise ConflictError(f"Licence {data.license_number} déjà enregistrée")

    certificate = data.medical_certificate_valid_until
    cursor = conn.execute(
        "INSERT INTO athletes (first_name, last_name, birth_date, sex, club, license_number,"
        " medical_certificate_valid_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data.first_name,
            data.last_name,
            data.birth_date.isoformat(),
            data.sex.value,
            data.club,
            data.license_number,
            certificate.isoformat() if certificate else None,
        ),
    )
    row = conn.execute("SELECT * FROM athletes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_athlete(row)


def _parse_fr_date(value: str) -> date | None:
    """Convertit jj/mm/aaaa en date ; une valeur vide donne None."""
    value = value.strip()
    if not value:
        return None
    day, month, year = value.split("/")
    return date(int(year), int(month), int(day))


def import_athletes(
    conn: sqlite3.Connection, rows: Iterable[dict[str, str]]
) -> AthleteImportReport:
    """Crée les athlètes du CSV fédération ; l'en-tête est la ligne 1, données dès la 2."""
    created = 0
    already_present = 0
    errors: list[AthleteImportError] = []
    for line, row in enumerate(rows, start=2):
        try:
            birth_date = _parse_fr_date(row["date_naissance"])
            if birth_date is None:
                raise ValueError("date de naissance manquante")
            data = AthleteCreate(
                last_name=row["nom"].strip(),
                first_name=row["prenom"].strip(),
                birth_date=birth_date,
                sex=row["sexe"].strip(),
                club=row["club"].strip() or None,
                license_number=row["licence"].strip(),
                medical_certificate_valid_until=_parse_fr_date(row["certificat_valide_jusqu"]),
            )
            create_athlete(conn, data)
        except ConflictError:
            already_present += 1
        except ValidationError as exc:
            message = "; ".join(
                f"{'.'.join(map(str, e['loc']))} : {e['msg']}" for e in exc.errors()
            )
            errors.append(AthleteImportError(line=line, message=message))
        except (ValueError, KeyError, AttributeError) as exc:
            errors.append(AthleteImportError(line=line, message=str(exc)))
        else:
            created += 1
    return AthleteImportReport(created=created, already_present=already_present, errors=errors)
