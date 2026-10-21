# Dossard — projet fil rouge

API de gestion de compétitions sportives : compétitions, épreuves, athlètes, inscriptions, résultats (FastAPI, SQLite, pytest). Ce dépôt sert de terrain de jeu pendant les deux jours de formation Claude Code : chaque module le fait évoluer.

| Module | Ce que vous ferez sur ce dépôt |
|---|---|
| 1 | Lancer Claude Code dessus, écrire son `CLAUDE.md` |
| 2 | Ajouter des endpoints par prompts, refactorer un script historique, comparer des modèles |
| 3 | Créer une skill qui applique les conventions du projet |
| 4 | Hooks de formatage et de sécurité, intégration continue, pull request |
| 5 | Exposer la base à Claude via MCP, packager la configuration en plugin |
| 6 | Sous-agents de test et d'audit, guidelines d'équipe |

## Installation

Python 3.12 ou plus récent. Aucune dépendance système, pas de droits administrateur.

```bash
python -m venv .venv
# macOS / Linux / WSL
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
```

Si PowerShell refuse d'exécuter `Activate.ps1`, autorisez les scripts pour la session en cours : `Set-ExecutionPolicy -Scope Process RemoteSigned`.

## Commandes

```bash
pytest                              # tests (doivent être verts avant tout commit)
ruff check . && ruff format .       # lint + formatage
python scripts/seed.py              # données d'exemple dans data/dossard.db
python scripts/seed.py --reset      # repart d'une base neuve
uvicorn app.main:app --reload       # serveur sur http://localhost:8000 (doc : /docs)
```

Les données d'exemple sont entièrement synthétiques. Sans seed, l'API démarre sur une base vide. Les tests n'utilisent jamais `data/dossard.db` : chacun a sa propre base temporaire.

## Structure

```
app/
  main.py            # application FastAPI + handler d'erreurs global
  errors.py          # ApiError, NotFoundError, ConflictError
  db.py              # chemin de la base, connexion, création du schéma
  schema.sql         # tables et vues
  schemas.py         # modèles Pydantic et énumérations
  categories.py      # catégories d'âge
  ranking.py         # classement d'une épreuve
  repositories/      # accès aux données, un module par entité
  routers/           # endpoints, un module par entité
tests/
  conftest.py        # fixtures : client, make_competition, make_event, make_athlete, make_registration
docs/api.md          # référence des endpoints, à tenir à jour
scripts/
  seed.py            # données d'exemple
data/                # la base SQLite locale (ignorée par Git)
```

Il n'y a volontairement **pas** de `CLAUDE.md` : c'est l'objet du TP 1.2.
