from __future__ import annotations

import csv
import io

from fastapi import APIRouter, UploadFile, status

from app.db import Conn
from app.errors import ApiError
from app.repositories import athletes
from app.repositories.athletes import IMPORT_COLUMNS
from app.schemas import AthleteCreate, AthleteImportReport, AthleteOut

router = APIRouter(prefix="/athletes", tags=["athletes"])


@router.get("", response_model=list[AthleteOut])
def list_athletes(conn: Conn, club: str | None = None) -> list[AthleteOut]:
    return athletes.list_athletes(conn, club=club)


@router.post("", response_model=AthleteOut, status_code=status.HTTP_201_CREATED)
def create_athlete(data: AthleteCreate, conn: Conn) -> AthleteOut:
    return athletes.create_athlete(conn, data)


@router.post("/import", response_model=AthleteImportReport)
def import_athletes(file: UploadFile, conn: Conn) -> AthleteImportReport:
    try:
        text = file.file.read().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ApiError("Le fichier doit être encodé en UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    missing = IMPORT_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ApiError(f"Colonnes manquantes : {', '.join(sorted(missing))}")
    return athletes.import_athletes(conn, reader)
