# Set the shell based on the OS
set shell := if os_family() == "windows" { ["powershell.exe", "-c"] } else { ["sh", "-c"] }

# Helper to handle file copying cross-platform
copy_env := if os_family() == "windows" { "if (!(Test-Path .env)) { copy .env.example .env }" } else { "cp -n .env.example .env" }

default:
    just --list

install:
    uv sync 
    # Use -q or similar if you want to ignore errors if already stamped
    -uv run alembic stamp head 
    uv run alembic upgrade head
    {{copy_env}}

server:
    uv run fastapi run server/server.py --port 8000

server-dev:
    uv run fastapi dev server/server.py --reload --port 8000

@cli *args="":
    -uv run cli/cli.py {{args}}

lint:
    uv run ruff check . --fix

lint-watch:
    uv run ruff check . --fix --watch

create-migration name="":
    uv run alembic revision --autogenerate -m "{{name}}"

apply-migrations:
    uv run alembic upgrade head

create-env:
    {{copy_env}}