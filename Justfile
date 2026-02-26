default:
    just --list

install:
    uv sync 
    uv run alembic stamp head
    uv run alembic upgrade head
    cp .env.example .env

server:
    uv run fastapi run server/server.py --port 8000

server-dev:
    uv run fastapi dev server/server.py --reload --port 8000

@cli *args="":
    -uv run cli/cli.py {{args}}

lint:
    ruff check . --fix

lint-watch:
    ruff check . --fix --watch

create-migration name="":
    uv run alembic revision --autogenerate -m "{{name}}"

apply-migrations:
    uv run alembic upgrade head

create-env:
    cp .env.example .env

set windows-shell := ["C:\\Program Files\\Git\\bin\\sh.exe","-c"]