default:
    just --list

install:
    uv sync 
    just create-env

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

create-env:
    cp .env.example .env

test:
    -uv run pytest server/tests

set windows-shell := ["C:\\Program Files\\Git\\bin\\sh.exe","-c"]